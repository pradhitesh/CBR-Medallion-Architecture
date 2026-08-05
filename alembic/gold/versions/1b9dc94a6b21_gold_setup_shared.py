"""gold setup shared

Revision ID: 1b9dc94a6b21
Revises:
Create Date: 2026-08-05 22:33:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.pipelines.medallion.schema import create_schema, drop_schema

# revision identifiers, used by Alembic.
revision: str = '1b9dc94a6b21'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_schema(schema_type='shared', layer='gold')


def downgrade() -> None:
    """Downgrade schema."""
    drop_schema('shared')
