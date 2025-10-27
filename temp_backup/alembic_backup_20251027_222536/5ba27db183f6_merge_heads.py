"""merge_heads

Revision ID: 5ba27db183f6
Revises: 56334a872cd3, manual_create_produits
Create Date: 2025-10-27 22:24:15.536795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ba27db183f6'
down_revision: Union[str, None] = ('56334a872cd3', 'manual_create_produits')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
