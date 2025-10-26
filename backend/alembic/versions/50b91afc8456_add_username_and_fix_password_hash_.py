"""add_username_and_fix_password_hash_nullable

Revision ID: 50b91afc8456
Revises: 037b216f2ed1
Create Date: 2025-10-25 23:21:59.274446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50b91afc8456'
down_revision: Union[str, Sequence[str], None] = '037b216f2ed1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add username column and make password_hash nullable."""
    # Add username column (nullable for backward compatibility with existing users)
    # This field is optional and used for display purposes only
    op.add_column('users', sa.Column('username', sa.String(length=255), nullable=True))

    # Make password_hash nullable to support MVP user creation with empty password
    # The JWT authentication system allows API token auth without password
    op.alter_column('users', 'password_hash',
                   existing_type=sa.String(length=255),
                   nullable=True)


def downgrade() -> None:
    """Downgrade schema - remove username and restore password_hash NOT NULL."""
    # Remove username column
    op.drop_column('users', 'username')

    # Restore password_hash as NOT NULL
    # WARNING: This will fail if any users have NULL password_hash
    op.alter_column('users', 'password_hash',
                   existing_type=sa.String(length=255),
                   nullable=False)
