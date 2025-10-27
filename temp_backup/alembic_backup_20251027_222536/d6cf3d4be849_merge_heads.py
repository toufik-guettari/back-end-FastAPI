"""merge_heads

Revision ID: d6cf3d4be849
Revises: 5ba27db183f6
Create Date: 2025-10-27 22:24:58.908767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6cf3d4be849'
down_revision: Union[str, None] = '5ba27db183f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
