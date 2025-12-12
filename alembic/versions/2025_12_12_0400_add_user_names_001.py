"""add user names

Revision ID: add_user_names_001
Revises: 04a9d7f7b5a1
Create Date: 2025-12-12 04:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_names_001'
down_revision: Union[str, None] = '04a9d7f7b5a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add first_name and last_name columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    # Remove first_name and last_name columns
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
