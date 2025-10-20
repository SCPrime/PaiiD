"""add_ai_recommendations_table

Revision ID: c8e4f9b52d31
Revises: ad76030fa92e
Create Date: 2025-10-15 04:30:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op


# revision identifiers, used by Alembic.
revision = "c8e4f9b52d31"
down_revision = "ad76030fa92e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ai_recommendations table"""
    op.create_table(
        "ai_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("recommendation_type", sa.String(length=20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("analysis_data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("suggested_entry_price", sa.Float(), nullable=True),
        sa.Column("suggested_stop_loss", sa.Float(), nullable=True),
        sa.Column("suggested_take_profit", sa.Float(), nullable=True),
        sa.Column("suggested_position_size", sa.Float(), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("market_context", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
        sa.Column("execution_price", sa.Float(), nullable=True),
        sa.Column("actual_pnl", sa.Float(), nullable=True),
        sa.Column("actual_pnl_percent", sa.Float(), nullable=True),
        sa.Column("accuracy_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_recommendations_id"), "ai_recommendations", ["id"], unique=False)
    op.create_index(
        op.f("ix_ai_recommendations_symbol"), "ai_recommendations", ["symbol"], unique=False
    )
    op.create_index(
        op.f("ix_ai_recommendations_recommendation_type"),
        "ai_recommendations",
        ["recommendation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_recommendations_status"), "ai_recommendations", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_ai_recommendations_created_at"), "ai_recommendations", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Drop ai_recommendations table"""
    op.drop_index(op.f("ix_ai_recommendations_created_at"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_status"), table_name="ai_recommendations")
    op.drop_index(
        op.f("ix_ai_recommendations_recommendation_type"), table_name="ai_recommendations"
    )
    op.drop_index(op.f("ix_ai_recommendations_symbol"), table_name="ai_recommendations")
    op.drop_index(op.f("ix_ai_recommendations_id"), table_name="ai_recommendations")
    op.drop_table("ai_recommendations")
