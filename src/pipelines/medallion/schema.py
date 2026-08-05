from typing import Literal

from alembic import op

_LAYER_MODULES = {}


def _tables_module(layer: str):
    if layer not in _LAYER_MODULES:
        if layer == 'bronze':
            from src.database.bronze import tables as mod
        elif layer == 'silver':
            from src.database.silver import tables as mod
        elif layer == 'gold':
            from src.database.gold import tables as mod
        else:
            raise ValueError(f"Unsupported layer: {layer}")
        _LAYER_MODULES[layer] = mod
    return _LAYER_MODULES[layer]


def create_schema(schema_type: Literal['cohort', 'shared', 'orphan'],
                  schema_name: str=None,
                  layer: Literal['bronze', 'silver', 'gold']='bronze'):
    """Create a schema with all clinical tables + cross-schema FKs to shared,
    for the given layer's database."""
    mod = _tables_module(layer)
    target_schema = schema_name if schema_type == 'cohort' else schema_type
    op.execute(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"')
    tables = mod.return_tables(schema_type=schema_type,
                           schema_name=schema_name)

    # Copy shared tables into the cohort MetaData purely to satisfy FK
    # dependency resolution during create_all's sort phase. They get the
    # same fully-qualified key (`shared.<name>`) and will NOT be re-created
    # because we pass `tables=cohort_only` below.
    cohort_only = list(tables.metadata.tables.values())
    for shared_table in mod.Base.metadata.tables.values():
        if shared_table.key not in tables.metadata.tables:
            shared_table.tometadata(tables.metadata)

    tables.metadata.create_all(bind=op.get_bind(), tables=cohort_only)


def drop_schema(schema_name: str):
    """Drop a cohort schema and all its tables."""
    op.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
