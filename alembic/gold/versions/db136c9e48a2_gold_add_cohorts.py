"""gold add cohorts

Revision ID: db136c9e48a2
Revises: 2f8ad1fbead9
Create Date: 2026-08-05 22:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.pipelines.medallion.schema import create_schema, drop_schema

# revision identifiers, used by Alembic.
revision: str = 'db136c9e48a2'
down_revision: Union[str, Sequence[str], None] = '2f8ad1fbead9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_schema(schema_type='cohort', schema_name='cohort_101_data', layer='gold')
    create_schema(schema_type='cohort', schema_name='cohort_102_data', layer='gold')
    create_schema(schema_type='cohort', schema_name='cohort_999_data', layer='gold')
    create_schema(schema_type='cohort', schema_name='cohort_998_data', layer='gold')


def downgrade() -> None:
    """Downgrade schema."""
    drop_schema('cohort_101_data')
    drop_schema('cohort_102_data')
    drop_schema('cohort_999_data')
    drop_schema('cohort_998_data')
