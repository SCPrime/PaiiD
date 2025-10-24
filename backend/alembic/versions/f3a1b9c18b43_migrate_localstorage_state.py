"""migrate_localstorage_state

Revision ID: f3a1b9c18b43
Revises: c8e4f9b52d31
Create Date: 2025-10-14 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f3a1b9c18b43"
down_revision: str | Sequence[str] | None = "c8e4f9b52d31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema to persist migrated localStorage state."""

    # Add external_id to users for mapping browser-generated identifiers
    op.add_column(
        "users",
        sa.Column("external_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_users_external_id"), "users", ["external_id"], unique=True
    )

    # Add client_strategy_id to strategies so we can de-duplicate migrated data
    op.add_column(
        "strategies",
        sa.Column("client_strategy_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        op.f("ix_strategies_client_strategy_id"),
        "strategies",
        ["client_strategy_id"],
        unique=True,
    )

    # User settings table (one row per user)
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("settings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_user_settings_user_id"),
    )
    op.create_index(
        op.f("ix_user_settings_user_id"), "user_settings", ["user_id"], unique=False
    )

    # User profile snapshots (supports multiple profile types per user)
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("profile_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "profile_type",
            name="uq_user_profiles_user_profile",
        ),
    )
    op.create_index(
        op.f("ix_user_profiles_profile_type"),
        "user_profiles",
        ["profile_type"],
        unique=False,
    )

    # Order history records migrated from the browser
    op.create_table(
        "order_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("client_order_id", sa.String(length=100), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("order_type", sa.String(length=20), nullable=False),
        sa.Column("limit_price", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, default="pending"),
        sa.Column("is_dry_run", sa.Boolean(), nullable=False, default=False),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "client_order_id", name="uq_order_history_client_order_id"
        ),
    )
    op.create_index(
        op.f("ix_order_history_user_id"), "order_history", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Revert schema changes."""

    op.drop_index(op.f("ix_order_history_user_id"), table_name="order_history")
    op.drop_table("order_history")

    op.drop_index(op.f("ix_user_profiles_profile_type"), table_name="user_profiles")
    op.drop_table("user_profiles")

    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_table("user_settings")

    op.drop_index(
        op.f("ix_strategies_client_strategy_id"), table_name="strategies"
    )
    op.drop_column("strategies", "client_strategy_id")

    op.drop_index(op.f("ix_users_external_id"), table_name="users")
    op.drop_column("users", "external_id")
