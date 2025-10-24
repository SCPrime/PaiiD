"""extend order templates for advanced orders

Revision ID: 0e3b9c3f5e4a
Revises: ad76030fa92e
Create Date: 2025-10-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0e3b9c3f5e4a"
down_revision = "ad76030fa92e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "order_templates",
        sa.Column("asset_class", sa.String(length=20), nullable=False, server_default="stock"),
    )
    op.add_column(
        "order_templates",
        sa.Column("option_type", sa.String(length=10), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("strike_price", sa.Float(), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("expiration_date", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("order_class", sa.String(length=20), nullable=False, server_default="simple"),
    )
    op.add_column(
        "order_templates",
        sa.Column("take_profit", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("stop_loss", postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("trail_price", sa.Float(), nullable=True),
    )
    op.add_column(
        "order_templates",
        sa.Column("trail_percent", sa.Float(), nullable=True),
    )

    # Remove server defaults now that existing rows have been backfilled
    op.alter_column("order_templates", "asset_class", server_default=None)
    op.alter_column("order_templates", "order_class", server_default=None)


def downgrade() -> None:
    op.drop_column("order_templates", "trail_percent")
    op.drop_column("order_templates", "trail_price")
    op.drop_column("order_templates", "stop_loss")
    op.drop_column("order_templates", "take_profit")
    op.drop_column("order_templates", "order_class")
    op.drop_column("order_templates", "expiration_date")
    op.drop_column("order_templates", "strike_price")
    op.drop_column("order_templates", "option_type")
    op.drop_column("order_templates", "asset_class")
