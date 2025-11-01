"""add strategy execution records table

Revision ID: 2712c6442e2a
Revises: 50b91afc8456
Create Date: 2025-10-30 17:21:34.824881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2712c6442e2a'
down_revision: Union[str, Sequence[str], None] = '50b91afc8456'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'strategy_execution_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('strategy_type', sa.String(length=50), nullable=False),
        sa.Column('market_key', sa.String(length=50), nullable=False),
        sa.Column('trade_summary', sa.JSON(), nullable=False),
        sa.Column('execution_summary', sa.JSON(), nullable=False),
        sa.Column('execution', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_strategy_execution_records_id'),
        'strategy_execution_records',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_strategy_execution_records_user_id'),
        'strategy_execution_records',
        ['user_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_strategy_execution_records_strategy_type'),
        'strategy_execution_records',
        ['strategy_type'],
        unique=False
    )
    op.create_index(
        op.f('ix_strategy_execution_records_created_at'),
        'strategy_execution_records',
        ['created_at'],
        unique=False
    )
    op.create_index(
        'idx_strategy_exec_user_created',
        'strategy_execution_records',
        ['user_id', 'created_at'],
        unique=False
    )
    op.create_index(
        'idx_strategy_exec_strategy',
        'strategy_execution_records',
        ['strategy_type', 'created_at'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_strategy_exec_strategy', table_name='strategy_execution_records')
    op.drop_index('idx_strategy_exec_user_created', table_name='strategy_execution_records')
    op.drop_index(
        op.f('ix_strategy_execution_records_created_at'),
        table_name='strategy_execution_records'
    )
    op.drop_index(
        op.f('ix_strategy_execution_records_strategy_type'),
        table_name='strategy_execution_records'
    )
    op.drop_index(
        op.f('ix_strategy_execution_records_user_id'),
        table_name='strategy_execution_records'
    )
    op.drop_index(
        op.f('ix_strategy_execution_records_id'),
        table_name='strategy_execution_records'
    )
    op.drop_table('strategy_execution_records')
