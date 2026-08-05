"""silver add cohorts

Revision ID: f2d32a214ea2
Revises: 0ca323cf76df
Create Date: 2026-08-05 22:32:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.pipelines.medallion.schema import create_schema, drop_schema

# revision identifiers, used by Alembic.
revision: str = 'f2d32a214ea2'
down_revision: Union[str, Sequence[str], None] = '0ca323cf76df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_schema(schema_type='cohort', schema_name='cohort_101_data', layer='silver')
    create_schema(schema_type='cohort', schema_name='cohort_102_data', layer='silver')
    create_schema(schema_type='cohort', schema_name='cohort_999_data', layer='silver')
    create_schema(schema_type='cohort', schema_name='cohort_998_data', layer='silver')


def downgrade() -> None:
    """Downgrade schema."""
    drop_schema('cohort_101_data')
    drop_schema('cohort_102_data')
    drop_schema('cohort_999_data')
    drop_schema('cohort_998_data')
