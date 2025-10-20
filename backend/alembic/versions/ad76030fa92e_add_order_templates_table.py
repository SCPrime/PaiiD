"""add_order_templates_table

Revision ID: ad76030fa92e
Revises: 0952a611cdfb
Create Date: 2025-10-13 15:22:50.670142

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "ad76030fa92e"
down_revision: str | Sequence[str] | None = "0952a611cdfb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create order_templates table
    op.create_table(
        "order_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("order_type", sa.String(length=20), nullable=False),
        sa.Column("limit_price", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_templates_id"), "order_templates", ["id"], unique=False)
    op.create_index(op.f("ix_order_templates_name"), "order_templates", ["name"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop order_templates table
    op.drop_index(op.f("ix_order_templates_name"), table_name="order_templates")
    op.drop_index(op.f("ix_order_templates_id"), table_name="order_templates")
    op.drop_table("order_templates")
