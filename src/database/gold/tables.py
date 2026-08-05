"""Gold layer: business layer data. Derived from Silver —

- no orphan schema
- cohort schemas drop IdentifierError, SourceLog, RedMeasurement,
  RedObservation, cmp_participants
- shared schema drops Assessment, Machine, Instrument, Endpoint, Api, Places

Exposes ``return_tables(schema_type, schema_name)`` which returns a
dynamically generated set of table classes bound to Gold's own metadata.
"""
from typing import Literal

from sqlalchemy.orm import DeclarativeBase

from src.database.common.base_types import ReturnedTables
from src.database.common.shared_builder import build_shared
from src.database.common.cohort_builder import build_cohort

SHARED_EXCLUDE = frozenset({'Assessment', 'Machine', 'Instrument', 'Endpoint', 'Api', 'Places'})
COHORT_EXCLUDE = frozenset({
    'IdentifierError', 'SourceLog', 'red_measurement', 'red_observation', 'cmp_participants',
})


class Base(DeclarativeBase):
    pass


_TABLE_CACHE: dict[tuple[str, str | None], ReturnedTables] = {}


def return_tables(schema_type: Literal['cohort', 'shared'],
                  schema_name: str = None) -> ReturnedTables:
    """Dispatch to the schema_type-specific table builder, cached per
    (schema_type, schema_name). Gold has no 'orphan' schema_type.
    """
    cache_key = (schema_type, schema_name)
    if cache_key in _TABLE_CACHE:
        return _TABLE_CACHE[cache_key]

    if schema_type == 'cohort':
        if not schema_name:
            raise ValueError("schema_name is required when schema_type='cohort'")
        result = build_cohort(Base, schema_name=schema_name, exclude=COHORT_EXCLUDE)
    elif schema_type == 'shared':
        result = build_shared(Base, exclude=SHARED_EXCLUDE)
    else:
        raise ValueError(f"Unsupported schema_type: {schema_type} (gold has no orphan schema)")

    _TABLE_CACHE[cache_key] = result
    return result
