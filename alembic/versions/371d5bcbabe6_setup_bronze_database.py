"""setup bronze database

Revision ID: 371d5bcbabe6
Revises: 
Create Date: 2026-08-05 13:43:06.375516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.pipelines.medallion.schema import create_schema, drop_schema

# revision identifiers, used by Alembic.
revision: str = '371d5bcbabe6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_schema(schema_type='shared')
    create_schema(schema_type='orphan')
    create_schema(schema_type='cohort', schema_name='cohort_101_data')
    create_schema(schema_type='cohort', schema_name='cohort_102_data')


def downgrade() -> None:
    """Downgrade schema."""
    drop_schema('shared')
    drop_schema('orphan')
    drop_schema('cohort_101_data')
    drop_schema('cohort_102_data')