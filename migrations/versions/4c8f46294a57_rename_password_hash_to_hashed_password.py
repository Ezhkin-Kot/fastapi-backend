"""Rename password_hash to hashed_password

Revision ID: 4c8f46294a57
Revises: 84fcf779b1dc
Create Date: 2026-04-25 00:16:50.136479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c8f46294a57'
down_revision: Union[str, Sequence[str], None] = '84fcf779b1dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'password_hash', new_column_name='hashed_password', existing_type=sa.String(255))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'hashed_password', new_column_name='password_hash', existing_type=sa.String(255))
