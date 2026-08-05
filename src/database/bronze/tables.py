"""Bronze layer: raw landing tables. Full shared + cohort + orphan schemas,
no exclusions — this is the OMOP CDM as received.

Exposes ``return_tables(schema_type, schema_name)`` which returns a
dynamically generated set of table classes bound to Bronze's own metadata.
"""
from typing import Literal

from sqlalchemy.orm import DeclarativeBase

from src.database.common.base_types import ReturnedTables
from src.database.common.shared_builder import build_shared
from src.database.common.cohort_builder import build_cohort
from src.database.common.orphan_builder import build_orphan


class Base(DeclarativeBase):
    pass


_TABLE_CACHE: dict[tuple[str, str | None], ReturnedTables] = {}


def return_tables(schema_type: Literal['cohort', 'shared', 'orphan'],
                  schema_name: str = None) -> ReturnedTables:
    """Dispatch to the schema_type-specific table builder, cached per
    (schema_type, schema_name). Caching matters because SQLAlchemy Table
    objects can't be redefined on the same MetaData — a second call for an
    already-built schema (e.g. a module that imports it eagerly, plus a
    migration that builds it again) must return the existing tables rather
    than re-declare them.
    """
    cache_key = (schema_type, schema_name)
    if cache_key in _TABLE_CACHE:
        return _TABLE_CACHE[cache_key]

    if schema_type == 'cohort':
        if not schema_name:
            raise ValueError("schema_name is required when schema_type='cohort'")
        result = build_cohort(Base, schema_name=schema_name)
    elif schema_type == 'shared':
        result = build_shared(Base)
    elif schema_type == 'orphan':
        result = build_orphan(Base)
    else:
        raise ValueError(f"Unsupported schema_type: {schema_type}")

    _TABLE_CACHE[cache_key] = result
    return result
