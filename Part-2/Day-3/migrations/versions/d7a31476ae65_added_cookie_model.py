"""Added Cookie model

Revision ID: d7a31476ae65
Revises: e9338e94314f
Create Date: 2026-03-30 05:17:50.890271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7a31476ae65'
down_revision: Union[str, Sequence[str], None] = 'e9338e94314f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
