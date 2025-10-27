"""test_migration

Revision ID: 56334a872cd3
Revises: 9d358a87c15c
Create Date: 2025-10-27 22:09:16.239064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56334a872cd3'
down_revision: Union[str, None] = '9d358a87c15c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
