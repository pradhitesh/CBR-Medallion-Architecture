"""bronze add cohorts

Revision ID: f1c65aae1546
Revises: 579a2f2a6a26
Create Date: 2026-08-05 16:34:30.566913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.pipelines.medallion.schema import create_schema, drop_schema

# revision identifiers, used by Alembic.
revision: str = 'f1c65aae1546'
down_revision: Union[str, Sequence[str], None] = '579a2f2a6a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    create_schema(schema_type='cohort', schema_name='cohort_101_data')
    create_schema(schema_type='cohort', schema_name='cohort_102_data')
    create_schema(schema_type='cohort', schema_name='cohort_999_data')
    create_schema(schema_type='cohort', schema_name='cohort_998_data')


def downgrade() -> None:
    """Downgrade schema."""
    drop_schema('cohort_101_data')
    drop_schema('cohort_102_data')
    drop_schema('cohort_999_data')
    drop_schema('cohort_998_data')
