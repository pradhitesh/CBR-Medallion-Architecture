"""Builder for the `shared` schema: OMOP vocab tables + cross-cohort reference
tables (assessments/machines/instruments/endpoints/apis/places).

Single source of truth for all three layers — each layer calls
`build_shared(Base, exclude=...)` with its own Base and its own set of
excluded reference tables, rather than re-declaring the vocab tables.
"""
import dataclasses
from typing import Optional
import datetime
import decimal

from sqlalchemy import (
    Column, Date, DateTime, ForeignKeyConstraint, Integer, Numeric,
    PrimaryKeyConstraint, String, Table, Text, Boolean, UniqueConstraint, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database.common.base_types import ReturnedTables


def build_shared(Base, exclude: frozenset = frozenset()) -> ReturnedTables:
    """`exclude` may drop {'Assessment', 'Machine', 'Instrument', 'Endpoint',
    'Api', 'Places'} — always drop that whole group together. Instrument is
    the only thing FK-ing into Assessment/Machine, Api is the only thing
    FK-ing into Endpoint; dropping any subset that splits those pairs leaves
    a dangling FK.
    """
    t_concept = Table(
        'concept', Base.metadata,
        Column('concept_id', Integer, nullable=False),
        Column('concept_name', String(255), nullable=False),
        Column('domain_id', String(20), nullable=False),
        Column('vocabulary_id', String(20), nullable=False),
        Column('concept_class_id', String(20), nullable=False),
        Column('concept_code', String(50), nullable=False),
        Column('valid_start_date', Date, nullable=False),
        Column('valid_end_date', Date, nullable=False),
        Column('standard_concept', String(1)),
        Column('invalid_reason', String(1)),
        schema='shared'
    )

    t_concept_class = Table(
        'concept_class', Base.metadata,
        Column('concept_class_id', String(20), nullable=False),
        Column('concept_class_name', String(255), nullable=False),
        Column('concept_class_concept_id', Integer, nullable=False),
        schema='shared'
    )

    t_domain = Table(
        'domain', Base.metadata,
        Column('domain_id', String(20), nullable=False),
        Column('domain_name', String(255), nullable=False),
        Column('domain_concept_id', Integer, nullable=False),
        schema='shared'
    )

    t_vocabulary = Table(
        'vocabulary', Base.metadata,
        Column('vocabulary_id', String(20), nullable=False),
        Column('vocabulary_name', String(255), nullable=False),
        Column('vocabulary_concept_id', Integer, nullable=False),
        Column('vocabulary_reference', String(255)),
        Column('vocabulary_version', String(255)),
        schema='shared'
    )

    t_relationship = Table(
        'relationship', Base.metadata,
        Column('relationship_id', String(20), nullable=False),
        Column('relationship_name', String(255), nullable=False),
        Column('is_hierarchical', String(1), nullable=False),
        Column('defines_ancestry', String(1), nullable=False),
        Column('reverse_relationship_id', String(20), nullable=False),
        Column('relationship_concept_id', Integer, nullable=False),
        schema='shared'
    )

    t_concept_ancestor = Table(
        'concept_ancestor', Base.metadata,
        Column('ancestor_concept_id', Integer, nullable=False),
        Column('descendant_concept_id', Integer, nullable=False),
        Column('min_levels_of_separation', Integer, nullable=False),
        Column('max_levels_of_separation', Integer, nullable=False),
        schema='shared'
    )

    t_concept_synonym = Table(
        'concept_synonym', Base.metadata,
        Column('concept_id', Integer, nullable=False),
        Column('concept_synonym_name', String(1000), nullable=False),
        Column('language_concept_id', Integer, nullable=False),
        schema='shared'
    )

    t_drug_strength = Table(
        'drug_strength', Base.metadata,
        Column('drug_concept_id', Integer, nullable=False),
        Column('ingredient_concept_id', Integer, nullable=False),
        Column('amount_value', Numeric),
        Column('amount_unit_concept_id', Integer),
        Column('numerator_value', Numeric),
        Column('numerator_unit_concept_id', Integer),
        Column('denominator_value', Numeric),
        Column('denominator_unit_concept_id', Integer),
        Column('box_size', Integer),
        Column('valid_start_date', Date, nullable=False),
        Column('valid_end_date', Date, nullable=False),
        Column('invalid_reason', String(1)),
        schema='shared'
    )

    t_concept_relationship = Table(
        'concept_relationship', Base.metadata,
        Column('concept_id_1', Integer, nullable=False),
        Column('concept_id_2', Integer, nullable=False),
        Column('relationship_id', String(20), nullable=False),
        Column('valid_start_date', Date, nullable=False),
        Column('valid_end_date', Date, nullable=False),
        Column('invalid_reason', String(1)),
        schema='shared'
    )

    class LocalConcept(Base):
        __tablename__ = 'local_concept'
        __table_args__ = (
            PrimaryKeyConstraint('id'),
            {'schema': 'shared'}
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        cohort: Mapped[Optional[int]] = mapped_column(Integer)
        dataset: Mapped[Optional[str]] = mapped_column(String)
        subgroup: Mapped[Optional[str]] = mapped_column(String)
        source_field_name: Mapped[Optional[str]] = mapped_column(String)
        source_field_description: Mapped[Optional[str]] = mapped_column(String)
        source_field_dtype: Mapped[Optional[str]] = mapped_column(String)
        source_field_range = mapped_column(JSONB)
        source_field_response = mapped_column(JSONB)
        concept_id: Mapped[Optional[int]] = mapped_column(Integer)
        table: Mapped[Optional[str]] = mapped_column(String)
        is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
        created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )
        updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )

    class CohortMapping(Base):
        """Maps a cohort_id to its human-readable name and schema."""
        __tablename__ = 'cohort_mappings'
        __table_args__ = (
            PrimaryKeyConstraint('id'),
            {'schema': 'shared'}
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        cohort_name: Mapped[str] = mapped_column(String(255), nullable=False)
        schema_name: Mapped[str] = mapped_column(Integer, nullable=False, unique=True)
        is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
        created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )
        updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )

    class Places(Base):
        __tablename__ = 'places'
        __table_args__ = (
            PrimaryKeyConstraint('id'),
            {'schema': 'shared'}
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        city: Mapped[Optional[str]] = mapped_column(String(50), nullable=False)
        state: Mapped[Optional[str]] = mapped_column(String(2), nullable=False)
        zip: Mapped[Optional[str]] = mapped_column(String(9), nullable=False)
        latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, nullable=False)
        longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric, nullable=False)
        is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
        created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )
        updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
            DateTime, server_default=text("NOW()")
        )

    classes = {
        'concept': t_concept,
        'concept_class': t_concept_class,
        'domain': t_domain,
        'vocabulary': t_vocabulary,
        'relationship': t_relationship,
        'concept_ancestor': t_concept_ancestor,
        'concept_synonym': t_concept_synonym,
        'drug_strength': t_drug_strength,
        'concept_relationship': t_concept_relationship,
        'LocalConcept': LocalConcept,
        'CohortMapping': CohortMapping,
        'Places': Places
    }

    if 'Assessment' not in exclude:
        class Assessment(Base):
            """Assessment instrument names (e.g. MoCA, MMSE)."""
            __tablename__ = 'assessments'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()"))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()"))

        classes['Assessment'] = Assessment

    if 'Machine' not in exclude:
        class Machine(Base):
            """Data-collection machine names, make and models."""
            __tablename__ = 'machines'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()"))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()"))

        classes['Machine'] = Machine

    if 'Instrument' not in exclude:
        class Instrument(Base):
            """Junction: assessment x machine -> source file contract."""
            __tablename__ = 'instruments'
            __table_args__ = (
                ForeignKeyConstraint(['cohort_id'], ['shared.cohort_mappings.id']),
                ForeignKeyConstraint(['assessment_id'], ['shared.assessments.id']),
                ForeignKeyConstraint(['machine_id'], ['shared.machines.id']),
                ForeignKeyConstraint(['place_id'], ['shared.places.id']),
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            cohort_id: Mapped[int] = mapped_column(Integer, nullable=False)
            assessment_id: Mapped[int] = mapped_column(Integer, nullable=False)
            machine_id: Mapped[int] = mapped_column(Integer, nullable=False)
            place_id: Mapped[int] = mapped_column(Integer, nullable=False)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()"))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()")) 

        classes['Instrument'] = Instrument

    if 'Api' not in exclude:
        class Api(Base):
            """Logical API exposed for data ingestion (e.g., ODK Central, Keystone, CMP, etc.)"""
            __tablename__ = 'apis'
            __table_args__ = (
                ForeignKeyConstraint(['cohort_id'], ['shared.cohort_mappings.id']),
                ForeignKeyConstraint(['assessment_id'], ['shared.assessments.id']),
                PrimaryKeyConstraint('id'),
                UniqueConstraint('cohort_id', 'assessment_id', 'name'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            cohort_id: Mapped[int] = mapped_column(Integer, nullable=False)
            assessment_id: Mapped[int] = mapped_column(Integer, nullable=False)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))

        classes["Api"] = Api

    if 'Endpoint' not in exclude:
        class Endpoint(Base):
            """HTTP endpoint exposed by an API."""
            __tablename__ = 'endpoints'
            __table_args__ = (
                ForeignKeyConstraint(['api_id'], ['shared.apis.id']),
                PrimaryKeyConstraint('id'),
                UniqueConstraint('method', 'path'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            api_id: Mapped[int] = mapped_column(Integer, nullable=False)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            path: Mapped[str] = mapped_column(String(500), nullable=False)
            method: Mapped[str] = mapped_column(String(10), nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))

        classes["Endpoint"] = Endpoint

    return ReturnedTables(Base.metadata, classes)
