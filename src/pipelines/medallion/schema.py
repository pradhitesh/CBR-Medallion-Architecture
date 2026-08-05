from typing import Literal

from alembic import op
from src.database.tables import return_tables
from src.database.tables import Base as SharedBase

def create_schema(schema_type: Literal['cohort', 'shared', 'orphan'],
                  schema_name: str=None):
    """Create a cohort schema with all clinical tables + cross-schema FKs to shared."""
    target_schema = schema_name if schema_type == 'cohort' else schema_type
    op.execute(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"')
    tables = return_tables(schema_type=schema_type,
                           schema_name=schema_name)

    # Copy shared tables into the cohort MetaData purely to satisfy FK
    # dependency resolution during create_all's sort phase. They get the
    # same fully-qualified key (`shared.<name>`) and will NOT be re-created
    # because we pass `tables=cohort_only` below.
    cohort_only = list(tables.metadata.tables.values())
    for shared_table in SharedBase.metadata.tables.values():
        if shared_table.key not in tables.metadata.tables:
            shared_table.tometadata(tables.metadata)

    tables.metadata.create_all(bind=op.get_bind(), tables=cohort_only)


def drop_schema(schema_name: str):
    """Drop a cohort schema and all its tables."""
    op.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
