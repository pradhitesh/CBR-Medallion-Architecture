"""SQLAlchemy models for cohort-specific clinical tables.

Exposes ``return_tables(schema_name: str)`` which returns a dynamically
generated set of table classes bound to the specified schema name.
"""

from typing import Optional
import datetime
import decimal

from sqlalchemy import (
    BigInteger, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer,
    Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, SmallInteger, Boolean, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Literal
class ReturnedTables:
    def __init__(self, metadata, classes):
        self.metadata = metadata
        for k, v in classes.items():
            setattr(self, k, v)

class Base(DeclarativeBase):
    pass


def return_tables(schema_type: Literal['cohort', 'shared', 'orphan'], schema_name: str = None) -> ReturnedTables:
    """Build ORM classes/tables scoped to one schema_type only.

    Base.metadata is module-level and persists across calls in the same
    process (schema.py relies on this to collect previously-built shared
    tables when creating a cohort schema). Each schema_type branch below
    defines ONLY the classes/tables it needs, so unrelated tables never
    get added to Base.metadata under the wrong schema.
    """
    if schema_type == 'cohort':
        if not schema_name:
            raise ValueError("schema_name is required when schema_type='cohort'")

        class LocalBase(DeclarativeBase):
            metadata = Base.metadata

        class Cohort(LocalBase):
            __tablename__ = 'cohort'
            __table_args__ = (
                PrimaryKeyConstraint('cohort_definition_id'),
                {'schema': schema_name}
            )

            cohort_definition_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            subject_id: Mapped[int] = mapped_column(Integer, nullable=False)
            cohort_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            cohort_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

        t_cdm_source = Table(
            'cdm_source', Base.metadata,
            Column('cdm_source_name', String(255), nullable=False),
            Column('cdm_source_abbreviation', String(25), nullable=False),
            Column('cdm_holder', String(255), nullable=False),
            Column('source_description', Text),
            Column('source_documentation_reference', String(255)),
            Column('cdm_etl_reference', String(255)),
            Column('source_release_date', Date, nullable=False),
            Column('cdm_release_date', Date, nullable=False),
            Column('cdm_version', String(10)),
            Column('cdm_version_concept_id', Integer, nullable=False),
            Column('vocabulary_version', String(20), nullable=False),
            ForeignKeyConstraint(['cdm_version_concept_id'], ['shared.concept.concept_id']),
            schema=schema_name
        )

        t_cohort_definition = Table(
            'cohort_definition', Base.metadata,
            Column('cohort_definition_id', Integer, nullable=False),
            Column('cohort_definition_name', String(255), nullable=False),
            Column('cohort_definition_description', Text),
            Column('definition_type_concept_id', Integer, nullable=False),
            Column('cohort_definition_syntax', Text),
            Column('subject_concept_id', Integer, nullable=False),
            Column('cohort_initiation_date', Date),
            ForeignKeyConstraint(['cohort_definition_id'], [f'{schema_name}.cohort.cohort_definition_id']),
            ForeignKeyConstraint(['definition_type_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['subject_concept_id'], ['shared.concept.concept_id']),
            schema=schema_name
        )

        class Cost(LocalBase):
            __tablename__ = 'cost'
            __table_args__ = (
                ForeignKeyConstraint(['cost_domain_id'], ['shared.domain.domain_id']),
                ForeignKeyConstraint(['cost_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['currency_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['drg_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['revenue_code_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('cost_id'),
                Index('idx_cost_event_id', 'cost_event_id'),
                {'schema': schema_name}
            )

            cost_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            cost_event_id: Mapped[int] = mapped_column(Integer, nullable=False)
            cost_domain_id: Mapped[str] = mapped_column(String(20), nullable=False)
            cost_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            currency_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            total_charge: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            total_paid: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_by_payer: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_by_patient: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_patient_copay: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_patient_coinsurance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_patient_deductible: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_by_primary: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_ingredient_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            paid_dispensing_fee: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            payer_plan_period_id: Mapped[Optional[int]] = mapped_column(Integer)
            amount_allowed: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            revenue_code_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            revenue_code_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            drg_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            drg_source_value: Mapped[Optional[str]] = mapped_column(String(3))

        t_fact_relationship = Table(
            'fact_relationship', Base.metadata,
            Column('domain_concept_id_1', Integer, nullable=False),
            Column('fact_id_1', Integer, nullable=False),
            Column('domain_concept_id_2', Integer, nullable=False),
            Column('fact_id_2', Integer, nullable=False),
            Column('relationship_concept_id', Integer, nullable=False),
            ForeignKeyConstraint(['domain_concept_id_1'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['domain_concept_id_2'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['relationship_concept_id'], ['shared.concept.concept_id']),
            Index('idx_fact_relationship_id1', 'domain_concept_id_1'),
            Index('idx_fact_relationship_id2', 'domain_concept_id_2'),
            Index('idx_fact_relationship_id3', 'relationship_concept_id'),
            schema=schema_name
        )

        class Location(LocalBase):
            __tablename__ = 'location'
            __table_args__ = (
                ForeignKeyConstraint(['country_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('location_id'),
                Index('idx_location_id_1', 'location_id'),
                {'schema': schema_name}
            )

            location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            address_1: Mapped[Optional[str]] = mapped_column(String(50))
            address_2: Mapped[Optional[str]] = mapped_column(String(50))
            city: Mapped[Optional[str]] = mapped_column(String(50))
            state: Mapped[Optional[str]] = mapped_column(String(2))
            zip: Mapped[Optional[str]] = mapped_column(String(9))
            county: Mapped[Optional[str]] = mapped_column(String(20))
            location_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            country_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            country_source_value: Mapped[Optional[str]] = mapped_column(String(80))
            latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)

            care_site: Mapped[list['CareSite']] = relationship('CareSite', back_populates='location')
            person: Mapped[list['Person']] = relationship('Person', back_populates='location')

        class Metadata(LocalBase):
            __tablename__ = 'metadata'
            __table_args__ = (
                ForeignKeyConstraint(['metadata_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['metadata_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['value_as_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('metadata_id'),
                Index('idx_metadata_concept_id_1', 'metadata_concept_id'),
                {'schema': schema_name}
            )

            metadata_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            metadata_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            metadata_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            name: Mapped[str] = mapped_column(String(250), nullable=False)
            value_as_string: Mapped[Optional[str]] = mapped_column(String(250))
            value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            metadata_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            metadata_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

        class NoteNlp(LocalBase):
            __tablename__ = 'note_nlp'
            __table_args__ = (
                ForeignKeyConstraint(['note_nlp_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['note_nlp_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['section_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('note_nlp_id'),
                Index('idx_note_nlp_concept_id_1', 'note_nlp_concept_id'),
                Index('idx_note_nlp_note_id_1', 'note_id'),
                {'schema': schema_name}
            )

            note_nlp_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            note_id: Mapped[int] = mapped_column(Integer, nullable=False)
            lexical_variant: Mapped[str] = mapped_column(String(250), nullable=False)
            nlp_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            section_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            snippet: Mapped[Optional[str]] = mapped_column(String(250))
            offset: Mapped[Optional[str]] = mapped_column(String(50))
            note_nlp_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            note_nlp_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            nlp_system: Mapped[Optional[str]] = mapped_column(String(250))
            nlp_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            term_exists: Mapped[Optional[str]] = mapped_column(String(1))
            term_temporal: Mapped[Optional[str]] = mapped_column(String(50))
            term_modifiers: Mapped[Optional[str]] = mapped_column(String(2000))

        t_source_to_concept_map = Table(
            'source_to_concept_map', Base.metadata,
            Column('source_code', String(50), nullable=False),
            Column('source_concept_id', Integer, nullable=False),
            Column('source_vocabulary_id', String(20), nullable=False),
            Column('source_code_description', String(255)),
            Column('target_concept_id', Integer, nullable=False),
            Column('target_vocabulary_id', String(20), nullable=False),
            Column('valid_start_date', Date, nullable=False),
            Column('valid_end_date', Date, nullable=False),
            Column('invalid_reason', String(1)),
            ForeignKeyConstraint(['source_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['target_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['target_vocabulary_id'], ['shared.vocabulary.vocabulary_id']),
            Index('idx_source_to_concept_map_1', 'source_vocabulary_id'),
            Index('idx_source_to_concept_map_2', 'target_vocabulary_id'),
            Index('idx_source_to_concept_map_3', 'target_concept_id'),
            Index('idx_source_to_concept_map_c', 'source_code'),
            schema=schema_name
        )

        class CareSite(LocalBase):
            __tablename__ = 'care_site'
            __table_args__ = (
                ForeignKeyConstraint(['location_id'], [f'{schema_name}.location.location_id']),
                ForeignKeyConstraint(['place_of_service_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('care_site_id'),
                Index('idx_care_site_id_1', 'care_site_id'),
                {'schema': schema_name}
            )

            care_site_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            care_site_name: Mapped[Optional[str]] = mapped_column(String(255))
            place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            location_id: Mapped[Optional[int]] = mapped_column(Integer)
            care_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            place_of_service_source_value: Mapped[Optional[str]] = mapped_column(String(50))

            location: Mapped[Optional['Location']] = relationship('Location', back_populates='care_site')
            provider: Mapped[list['Provider']] = relationship('Provider', back_populates='care_site')
            person: Mapped[list['Person']] = relationship('Person', back_populates='care_site')
            visit_occurrence: Mapped[list['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='care_site')
            visit_detail: Mapped[list['VisitDetail']] = relationship('VisitDetail', back_populates='care_site')

        class Provider(LocalBase):
            __tablename__ = 'provider'
            __table_args__ = (
                ForeignKeyConstraint(['care_site_id'], [f'{schema_name}.care_site.care_site_id']),
                ForeignKeyConstraint(['gender_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['gender_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['specialty_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['specialty_source_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('provider_id'),
                Index('idx_provider_id_1', 'provider_id'),
                {'schema': schema_name}
            )

            provider_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            provider_name: Mapped[Optional[str]] = mapped_column(String(255))
            npi: Mapped[Optional[str]] = mapped_column(String(20))
            dea: Mapped[Optional[str]] = mapped_column(String(20))
            specialty_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
            year_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
            gender_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            provider_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            specialty_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            specialty_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            gender_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            care_site: Mapped[Optional['CareSite']] = relationship('CareSite', back_populates='provider')
            person: Mapped[list['Person']] = relationship('Person', back_populates='provider')
            visit_occurrence: Mapped[list['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='provider')
            visit_detail: Mapped[list['VisitDetail']] = relationship('VisitDetail', back_populates='provider')
            condition_occurrence: Mapped[list['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='provider')
            device_exposure: Mapped[list['DeviceExposure']] = relationship('DeviceExposure', back_populates='provider')
            drug_exposure: Mapped[list['DrugExposure']] = relationship('DrugExposure', back_populates='provider')
            measurement: Mapped[list['Measurement']] = relationship('Measurement', back_populates='provider')
            note: Mapped[list['Note']] = relationship('Note', back_populates='provider')
            observation: Mapped[list['Observation']] = relationship('Observation', back_populates='provider')
            procedure_occurrence: Mapped[list['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='provider')

        class Person(LocalBase):
            __tablename__ = 'person'
            __table_args__ = (
                ForeignKeyConstraint(['care_site_id'], [f'{schema_name}.care_site.care_site_id']),
                ForeignKeyConstraint(['ethnicity_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['ethnicity_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['gender_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['gender_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['location_id'], [f'{schema_name}.location.location_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['race_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['race_source_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('person_id'),
                Index('idx_gender', 'gender_concept_id'),
                Index('idx_person_id', 'person_id'),
                {'schema': schema_name}
            )

            person_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            gender_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            year_of_birth: Mapped[int] = mapped_column(Integer, nullable=False)
            race_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            ethnicity_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            month_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
            day_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
            birth_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            location_id: Mapped[Optional[int]] = mapped_column(Integer)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
            person_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            gender_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            race_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            race_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            ethnicity_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            ethnicity_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            care_site: Mapped[Optional['CareSite']] = relationship('CareSite', back_populates='person')
            location: Mapped[Optional['Location']] = relationship('Location', back_populates='person')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='person')
            condition_era: Mapped[list['ConditionEra']] = relationship('ConditionEra', back_populates='person')
            dose_era: Mapped[list['DoseEra']] = relationship('DoseEra', back_populates='person')
            drug_era: Mapped[list['DrugEra']] = relationship('DrugEra', back_populates='person')
            episode: Mapped[list['Episode']] = relationship('Episode', back_populates='person')
            observation_period: Mapped[list['ObservationPeriod']] = relationship('ObservationPeriod', back_populates='person')
            payer_plan_period: Mapped[list['PayerPlanPeriod']] = relationship('PayerPlanPeriod', back_populates='person')
            specimen: Mapped[list['Specimen']] = relationship('Specimen', back_populates='person')
            visit_occurrence: Mapped[list['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='person')
            visit_detail: Mapped[list['VisitDetail']] = relationship('VisitDetail', back_populates='person')
            condition_occurrence: Mapped[list['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='person')
            device_exposure: Mapped[list['DeviceExposure']] = relationship('DeviceExposure', back_populates='person')
            drug_exposure: Mapped[list['DrugExposure']] = relationship('DrugExposure', back_populates='person')
            measurement: Mapped[list['Measurement']] = relationship('Measurement', back_populates='person')
            note: Mapped[list['Note']] = relationship('Note', back_populates='person')
            observation: Mapped[list['Observation']] = relationship('Observation', back_populates='person')
            procedure_occurrence: Mapped[list['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='person')

        class ConditionEra(LocalBase):
            __tablename__ = 'condition_era'
            __table_args__ = (
                ForeignKeyConstraint(['condition_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                PrimaryKeyConstraint('condition_era_id'),
                Index('idx_condition_era_concept_id_1', 'condition_concept_id'),
                Index('idx_condition_era_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            condition_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            condition_era_start_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
            condition_era_end_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
            condition_occurrence_count: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='condition_era')

        t_death = Table(
            'death', Base.metadata,
            Column('person_id', Integer, nullable=False),
            Column('death_date', Date, nullable=False),
            Column('death_datetime', DateTime),
            Column('death_type_concept_id', Integer),
            Column('cause_concept_id', Integer),
            Column('cause_source_value', String(50)),
            Column('cause_source_concept_id', Integer),
            ForeignKeyConstraint(['cause_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['cause_source_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['death_type_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
            Index('idx_death_person_id_1', 'person_id'),
            schema=schema_name
        )

        class DoseEra(LocalBase):
            __tablename__ = 'dose_era'
            __table_args__ = (
                ForeignKeyConstraint(['drug_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['unit_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('dose_era_id'),
                Index('idx_dose_era_concept_id_1', 'drug_concept_id'),
                Index('idx_dose_era_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            unit_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            dose_value: Mapped[decimal.Decimal] = mapped_column(Numeric, nullable=False)
            dose_era_start_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
            dose_era_end_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

            person: Mapped['Person'] = relationship('Person', back_populates='dose_era')

        class DrugEra(LocalBase):
            __tablename__ = 'drug_era'
            __table_args__ = (
                ForeignKeyConstraint(['drug_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                PrimaryKeyConstraint('drug_era_id'),
                Index('idx_drug_era_concept_id_1', 'drug_concept_id'),
                Index('idx_drug_era_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_era_start_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
            drug_era_end_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
            drug_exposure_count: Mapped[Optional[int]] = mapped_column(Integer)
            gap_days: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='drug_era')

        class Episode(LocalBase):
            __tablename__ = 'episode'
            __table_args__ = (
                ForeignKeyConstraint(['episode_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['episode_object_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['episode_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['episode_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                PrimaryKeyConstraint('episode_id'),
                {'schema': schema_name}
            )

            episode_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
            person_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
            episode_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            episode_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            episode_object_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            episode_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            episode_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            episode_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            episode_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            episode_parent_id: Mapped[Optional[int]] = mapped_column(BigInteger)
            episode_number: Mapped[Optional[int]] = mapped_column(Integer)
            episode_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            episode_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='episode')

        class ObservationPeriod(LocalBase):
            __tablename__ = 'observation_period'
            __table_args__ = (
                ForeignKeyConstraint(['period_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                PrimaryKeyConstraint('observation_period_id'),
                Index('idx_observation_period_id_1', 'person_id'),
                {'schema': schema_name}
            )

            observation_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            observation_period_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            observation_period_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            period_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

            person: Mapped['Person'] = relationship('Person', back_populates='observation_period')

        class PayerPlanPeriod(LocalBase):
            __tablename__ = 'payer_plan_period'
            __table_args__ = (
                ForeignKeyConstraint(['payer_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['payer_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['plan_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['plan_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['sponsor_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['sponsor_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['stop_reason_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['stop_reason_source_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('payer_plan_period_id'),
                Index('idx_period_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            payer_plan_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            payer_plan_period_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            payer_plan_period_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            payer_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            payer_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            payer_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            plan_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            plan_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            plan_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            sponsor_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            sponsor_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            sponsor_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            family_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            stop_reason_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            stop_reason_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            stop_reason_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='payer_plan_period')

        class Specimen(LocalBase):
            __tablename__ = 'specimen'
            __table_args__ = (
                ForeignKeyConstraint(['anatomic_site_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['disease_status_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['specimen_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['specimen_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['unit_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('specimen_id'),
                Index('idx_specimen_concept_id_1', 'specimen_concept_id'),
                Index('idx_specimen_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            specimen_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            specimen_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            specimen_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            specimen_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            specimen_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            anatomic_site_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            disease_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            specimen_source_id: Mapped[Optional[str]] = mapped_column(String(50))
            specimen_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            anatomic_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            disease_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))

            person: Mapped['Person'] = relationship('Person', back_populates='specimen')

        class VisitOccurrence(LocalBase):
            __tablename__ = 'visit_occurrence'
            __table_args__ = (
                ForeignKeyConstraint(['admitted_from_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['care_site_id'], [f'{schema_name}.care_site.care_site_id']),
                ForeignKeyConstraint(['discharged_to_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['preceding_visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['visit_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_type_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('visit_occurrence_id'),
                Index('idx_visit_concept_id_1', 'visit_concept_id'),
                Index('idx_visit_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            visit_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            visit_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            visit_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            visit_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            visit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            preceding_visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)

            care_site: Mapped[Optional['CareSite']] = relationship('CareSite', back_populates='visit_occurrence')
            person: Mapped['Person'] = relationship('Person', back_populates='visit_occurrence')
            preceding_visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', remote_side=[visit_occurrence_id], back_populates='preceding_visit_occurrence_reverse')
            preceding_visit_occurrence_reverse: Mapped[list['VisitOccurrence']] = relationship('VisitOccurrence', remote_side=[preceding_visit_occurrence_id], back_populates='preceding_visit_occurrence')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='visit_occurrence')
            visit_detail: Mapped[list['VisitDetail']] = relationship('VisitDetail', back_populates='visit_occurrence')
            condition_occurrence: Mapped[list['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='visit_occurrence')
            device_exposure: Mapped[list['DeviceExposure']] = relationship('DeviceExposure', back_populates='visit_occurrence')
            drug_exposure: Mapped[list['DrugExposure']] = relationship('DrugExposure', back_populates='visit_occurrence')
            measurement: Mapped[list['Measurement']] = relationship('Measurement', back_populates='visit_occurrence')
            note: Mapped[list['Note']] = relationship('Note', back_populates='visit_occurrence')
            observation: Mapped[list['Observation']] = relationship('Observation', back_populates='visit_occurrence')
            procedure_occurrence: Mapped[list['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='visit_occurrence')

        t_episode_event = Table(
            'episode_event', Base.metadata,
            Column('episode_id', BigInteger, nullable=False),
            Column('event_id', BigInteger, nullable=False),
            Column('episode_event_field_concept_id', Integer, nullable=False),
            ForeignKeyConstraint(['episode_event_field_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['episode_id'], [f'{schema_name}.episode.episode_id']),
            schema=schema_name
        )

        class VisitDetail(LocalBase):
            __tablename__ = 'visit_detail'
            __table_args__ = (
                ForeignKeyConstraint(['admitted_from_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['care_site_id'], [f'{schema_name}.care_site.care_site_id']),
                ForeignKeyConstraint(['discharged_to_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['parent_visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['preceding_visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['visit_detail_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('visit_detail_id'),
                Index('idx_visit_det_concept_id_1', 'visit_detail_concept_id'),
                Index('idx_visit_det_occ_id', 'visit_occurrence_id'),
                Index('idx_visit_det_person_id_1', 'person_id'),
                {'schema': schema_name}
            )

            visit_detail_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_detail_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_detail_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            visit_detail_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            visit_detail_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_occurrence_id: Mapped[int] = mapped_column(Integer, nullable=False)
            visit_detail_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            visit_detail_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            visit_detail_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            preceding_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            parent_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)

            care_site: Mapped[Optional['CareSite']] = relationship('CareSite', back_populates='visit_detail')
            parent_visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[parent_visit_detail_id], back_populates='parent_visit_detail_reverse')
            parent_visit_detail_reverse: Mapped[list['VisitDetail']] = relationship('VisitDetail', remote_side=[parent_visit_detail_id], foreign_keys=[parent_visit_detail_id], back_populates='parent_visit_detail')
            person: Mapped['Person'] = relationship('Person', back_populates='visit_detail')
            preceding_visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[preceding_visit_detail_id], back_populates='preceding_visit_detail_reverse')
            preceding_visit_detail_reverse: Mapped[list['VisitDetail']] = relationship('VisitDetail', remote_side=[preceding_visit_detail_id], foreign_keys=[preceding_visit_detail_id], back_populates='preceding_visit_detail')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='visit_detail')
            visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', back_populates='visit_detail')
            condition_occurrence: Mapped[list['ConditionOccurrence']] = relationship('ConditionOccurrence', back_populates='visit_detail')
            device_exposure: Mapped[list['DeviceExposure']] = relationship('DeviceExposure', back_populates='visit_detail')
            drug_exposure: Mapped[list['DrugExposure']] = relationship('DrugExposure', back_populates='visit_detail')
            measurement: Mapped[list['Measurement']] = relationship('Measurement', back_populates='visit_detail')
            note: Mapped[list['Note']] = relationship('Note', back_populates='visit_detail')
            observation: Mapped[list['Observation']] = relationship('Observation', back_populates='visit_detail')
            procedure_occurrence: Mapped[list['ProcedureOccurrence']] = relationship('ProcedureOccurrence', back_populates='visit_detail')

        class ConditionOccurrence(LocalBase):
            __tablename__ = 'condition_occurrence'
            __table_args__ = (
                ForeignKeyConstraint(['condition_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['condition_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['condition_status_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['condition_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('condition_occurrence_id'),
                Index('idx_condition_concept_id_1', 'condition_concept_id'),
                Index('idx_condition_person_id_1', 'person_id'),
                Index('idx_condition_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            condition_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            condition_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            condition_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            condition_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            condition_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            condition_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            condition_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            condition_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            stop_reason: Mapped[Optional[str]] = mapped_column(String(20))
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            condition_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            condition_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            condition_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))

            person: Mapped['Person'] = relationship('Person', back_populates='condition_occurrence')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='condition_occurrence')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='condition_occurrence')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='condition_occurrence')

        class DeviceExposure(LocalBase):
            __tablename__ = 'device_exposure'
            __table_args__ = (
                ForeignKeyConstraint(['device_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['device_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['device_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['unit_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['unit_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('device_exposure_id'),
                Index('idx_device_concept_id_1', 'device_concept_id'),
                Index('idx_device_person_id_1', 'person_id'),
                Index('idx_device_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            device_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            device_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            device_exposure_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            device_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            device_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            device_exposure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            device_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            unique_device_id: Mapped[Optional[str]] = mapped_column(String(255))
            production_id: Mapped[Optional[str]] = mapped_column(String(255))
            quantity: Mapped[Optional[int]] = mapped_column(Integer)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            device_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            device_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='device_exposure')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='device_exposure')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='device_exposure')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='device_exposure')

        class DrugExposure(LocalBase):
            __tablename__ = 'drug_exposure'
            __table_args__ = (
                ForeignKeyConstraint(['drug_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['drug_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['drug_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['route_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('drug_exposure_id'),
                Index('idx_drug_concept_id_1', 'drug_concept_id'),
                Index('idx_drug_person_id_1', 'person_id'),
                Index('idx_drug_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            drug_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_exposure_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            drug_exposure_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            drug_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            drug_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            drug_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            verbatim_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            stop_reason: Mapped[Optional[str]] = mapped_column(String(20))
            refills: Mapped[Optional[int]] = mapped_column(Integer)
            quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            days_supply: Mapped[Optional[int]] = mapped_column(Integer)
            sig: Mapped[Optional[str]] = mapped_column(Text)
            route_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            lot_number: Mapped[Optional[str]] = mapped_column(String(50))
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            drug_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            drug_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            route_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            dose_unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))

            person: Mapped['Person'] = relationship('Person', back_populates='drug_exposure')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='drug_exposure')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='drug_exposure')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='drug_exposure')

        class Measurement(LocalBase):
            __tablename__ = 'measurement'
            __table_args__ = (
                ForeignKeyConstraint(['meas_event_field_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['measurement_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['measurement_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['measurement_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['operator_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['unit_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['unit_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['value_as_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('measurement_id'),
                Index('idx_measurement_concept_id_1', 'measurement_concept_id'),
                Index('idx_measurement_person_id_1', 'person_id'),
                Index('idx_measurement_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            measurement_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            measurement_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            measurement_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            measurement_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            measurement_time: Mapped[Optional[str]] = mapped_column(String(10))
            operator_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            range_low: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            range_high: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            measurement_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            measurement_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            value_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            measurement_event_id: Mapped[Optional[int]] = mapped_column(BigInteger)
            meas_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='measurement')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='measurement')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='measurement')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='measurement')

        class Note(LocalBase):
            __tablename__ = 'note'
            __table_args__ = (
                ForeignKeyConstraint(['encoding_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['language_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['note_class_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['note_event_field_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['note_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('note_id'),
                Index('idx_note_concept_id_1', 'note_type_concept_id'),
                Index('idx_note_person_id_1', 'person_id'),
                Index('idx_note_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            note_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            note_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            note_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            note_class_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            note_text: Mapped[str] = mapped_column(Text, nullable=False)
            encoding_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            language_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            note_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            note_title: Mapped[Optional[str]] = mapped_column(String(250))
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            note_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            note_event_id: Mapped[Optional[int]] = mapped_column(BigInteger)
            note_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='note')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='note')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='note')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='note')

        class Observation(LocalBase):
            __tablename__ = 'observation'
            __table_args__ = (
                ForeignKeyConstraint(['obs_event_field_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['observation_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['observation_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['observation_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['qualifier_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['unit_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['value_as_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('observation_id'),
                Index('idx_observation_concept_id_1', 'observation_concept_id'),
                Index('idx_observation_person_id_1', 'person_id'),
                Index('idx_observation_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            observation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            observation_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            observation_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            observation_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            observation_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            value_as_string: Mapped[Optional[str]] = mapped_column(String(60))
            value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            qualifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            observation_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            observation_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            qualifier_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            value_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            observation_event_id: Mapped[Optional[int]] = mapped_column(BigInteger)
            obs_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

            person: Mapped['Person'] = relationship('Person', back_populates='observation')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='observation')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='observation')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='observation')

        class ProcedureOccurrence(LocalBase):
            __tablename__ = 'procedure_occurrence'
            __table_args__ = (
                ForeignKeyConstraint(['modifier_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['person_id'], [f'{schema_name}.person.person_id']),
                ForeignKeyConstraint(['procedure_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['procedure_source_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['procedure_type_concept_id'], ['shared.concept.concept_id']),
                ForeignKeyConstraint(['provider_id'], [f'{schema_name}.provider.provider_id']),
                ForeignKeyConstraint(['visit_detail_id'], [f'{schema_name}.visit_detail.visit_detail_id']),
                ForeignKeyConstraint(['visit_occurrence_id'], [f'{schema_name}.visit_occurrence.visit_occurrence_id']),
                PrimaryKeyConstraint('procedure_occurrence_id'),
                Index('idx_procedure_concept_id_1', 'procedure_concept_id'),
                Index('idx_procedure_person_id_1', 'person_id'),
                Index('idx_procedure_visit_id_1', 'visit_occurrence_id'),
                {'schema': schema_name}
            )

            procedure_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            person_id: Mapped[int] = mapped_column(Integer, nullable=False)
            procedure_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            procedure_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            procedure_type_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            procedure_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            procedure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
            procedure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
            modifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            quantity: Mapped[Optional[int]] = mapped_column(Integer)
            provider_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
            visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
            procedure_source_value: Mapped[Optional[str]] = mapped_column(String(50))
            procedure_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            modifier_source_value: Mapped[Optional[str]] = mapped_column(String(50))

            person: Mapped['Person'] = relationship('Person', back_populates='procedure_occurrence')
            provider: Mapped[Optional['Provider']] = relationship('Provider', back_populates='procedure_occurrence')
            visit_detail: Mapped[Optional['VisitDetail']] = relationship('VisitDetail', back_populates='procedure_occurrence')
            visit_occurrence: Mapped[Optional['VisitOccurrence']] = relationship('VisitOccurrence', back_populates='procedure_occurrence')

        class RedMeasurement(LocalBase):
            __tablename__ = 'red_measurement'
            __table_args__ = (
                ForeignKeyConstraint(['measurement_id'], [f'{schema_name}.measurement.measurement_id'], ondelete='CASCADE', name='red_measurement_measurement_id_fkey'),
                PrimaryKeyConstraint('measurement_id', name='red_measurement_pkey'),
                {'schema': schema_name}
            )

            measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            appointment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
            field_name: Mapped[str] = mapped_column(Text, nullable=False)
            created_by: Mapped[int] = mapped_column(SmallInteger, nullable=False)
            created_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
            status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("'0'::smallint"))
            original_value: Mapped[Optional[str]] = mapped_column(Text)
            original_error: Mapped[Optional[str]] = mapped_column(Text)
            new_value: Mapped[Optional[str]] = mapped_column(Text)
            new_error: Mapped[Optional[str]] = mapped_column(Text)
            updated_by: Mapped[Optional[int]] = mapped_column(SmallInteger)
            updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


        class RedObservation(LocalBase):
            __tablename__ = 'red_observation'
            __table_args__ = (
                ForeignKeyConstraint(['observation_id'], [f'{schema_name}.observation.observation_id'], ondelete='CASCADE', name='red_observation_observation_id_fkey'),
                PrimaryKeyConstraint('observation_id', name='red_observation_pkey'),
                {'schema': schema_name}
            )

            observation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            appointment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
            field_name: Mapped[str] = mapped_column(Text, nullable=False)
            created_by: Mapped[int] = mapped_column(SmallInteger, nullable=False)
            created_on: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
            status: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("'0'::smallint"))
            original_value: Mapped[Optional[str]] = mapped_column(Text)
            original_error: Mapped[Optional[str]] = mapped_column(Text)
            new_value: Mapped[Optional[str]] = mapped_column(Text)
            new_error: Mapped[Optional[str]] = mapped_column(Text)
            updated_by: Mapped[Optional[int]] = mapped_column(SmallInteger)
            updated_on: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

        t_cmp_participants = Table(
            'cmp_participants', Base.metadata,
            Column('barcode', Text, nullable=False),
            Column('subject_id', Text, nullable=False),
            UniqueConstraint('barcode', 'subject_id', name='uq_cmp_participants_barcode_subject_id'),
            schema=schema_name
        )

        class IdentifierError(LocalBase):
            __tablename__ = 'identifier_errors'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': schema_name}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            subject_id: Mapped[Optional[str]] = mapped_column(String(50))
            data: Mapped[Optional[str]] = mapped_column(Text)
            instruments_source_id: Mapped[Optional[str]] = mapped_column(String(255))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            created_by: Mapped[Optional[str]] = mapped_column(String(255))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            updated_by: Mapped[Optional[str]] = mapped_column(String(255))
            status: Mapped[Optional[str]] = mapped_column(String(50))
            cohort: Mapped[Optional[int]] = mapped_column(Integer)

        class SourceLog(LocalBase):
            __tablename__ = 'source_logs'
            __table_args__ = (
                ForeignKeyConstraint(['instrument_cat'], ['shared.instruments.id']),
                ForeignKeyConstraint(['api_catalogue_id'], ['shared.apis.id']),
                PrimaryKeyConstraint('id'),
                {'schema': schema_name}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            instrument_cat: Mapped[Optional[int]] = mapped_column(Integer)
            api_catalogue_id: Mapped[Optional[int]] = mapped_column(Integer)
            source: Mapped[Optional[str]] = mapped_column(String(255))
            file_format: Mapped[Optional[str]] = mapped_column(String(50))
            created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            modified_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            subjects_in_file: Mapped[Optional[int]] = mapped_column(Integer)
            subjects_passed: Mapped[Optional[int]] = mapped_column(Integer)
            subjects_failed: Mapped[Optional[int]] = mapped_column(Integer)
            fdc_id: Mapped[Optional[str]] = mapped_column(String(255))
            is_instrumentals: Mapped[Optional[bool]] = mapped_column(Boolean)

        classes = {
                'Cohort': Cohort,
                'cdm_source': t_cdm_source,
                'cohort_definition': t_cohort_definition,
                'Cost': Cost,
                'fact_relationship': t_fact_relationship,
                'Location': Location,
                'Metadata': Metadata,
                'NoteNlp': NoteNlp,
                'source_to_concept_map': t_source_to_concept_map,
                'CareSite': CareSite,
                'Provider': Provider,
                'Person': Person,
                'ConditionEra': ConditionEra,
                'death': t_death,
                'DoseEra': DoseEra,
                'DrugEra': DrugEra,
                'Episode': Episode,
                'ObservationPeriod': ObservationPeriod,
                'PayerPlanPeriod': PayerPlanPeriod,
                'Specimen': Specimen,
                'VisitOccurrence': VisitOccurrence,
                'episode_event': t_episode_event,
                'VisitDetail': VisitDetail,
                'ConditionOccurrence': ConditionOccurrence,
                'DeviceExposure': DeviceExposure,
                'DrugExposure': DrugExposure,
                'Measurement': Measurement,
                'Note': Note,
                'Observation': Observation,
                'ProcedureOccurrence': ProcedureOccurrence,
                'red_measurement': RedMeasurement,
                'red_observation': RedObservation,
                'cmp_participants': t_cmp_participants,
                'IdentifierError': IdentifierError,
                'SourceLog': SourceLog,
        }

    elif schema_type == 'shared':

        class Concept(Base):
            __tablename__ = 'concept'
            __table_args__ = (
                ForeignKeyConstraint(['concept_class_id'], ['shared.concept_class.concept_class_id']),
                ForeignKeyConstraint(['domain_id'], ['shared.domain.domain_id']),
                ForeignKeyConstraint(['vocabulary_id'], ['shared.vocabulary.vocabulary_id']),
                PrimaryKeyConstraint('concept_id'),
                Index('idx_concept_class_id', 'concept_class_id'),
                Index('idx_concept_code', 'concept_code'),
                Index('idx_concept_concept_id', 'concept_id'),
                Index('idx_concept_domain_id', 'domain_id'),
                Index('idx_concept_vocabluary_id', 'vocabulary_id'),
                {'schema': 'shared'}
            )

            concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            concept_name: Mapped[str] = mapped_column(String(255), nullable=False)
            domain_id: Mapped[str] = mapped_column(String(20), nullable=False)
            vocabulary_id: Mapped[str] = mapped_column(String(20), nullable=False)
            concept_class_id: Mapped[str] = mapped_column(String(20), nullable=False)
            concept_code: Mapped[str] = mapped_column(String(50), nullable=False)
            valid_start_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            valid_end_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
            standard_concept: Mapped[Optional[str]] = mapped_column(String(1))
            invalid_reason: Mapped[Optional[str]] = mapped_column(String(1))

            concept_class: Mapped['ConceptClass'] = relationship('ConceptClass', foreign_keys=[concept_class_id], back_populates='concept_concept_class')
            domain: Mapped['Domain'] = relationship('Domain', foreign_keys=[domain_id], back_populates='concept_domain')
            vocabulary: Mapped['Vocabulary'] = relationship('Vocabulary', foreign_keys=[vocabulary_id], back_populates='concept_vocabulary')
            concept_class_concept_class_concept: Mapped[list['ConceptClass']] = relationship('ConceptClass', foreign_keys='[ConceptClass.concept_class_concept_id]', back_populates='concept_class_concept')
            domain_domain_concept: Mapped[list['Domain']] = relationship('Domain', foreign_keys='[Domain.domain_concept_id]', back_populates='domain_concept')
            vocabulary_vocabulary_concept: Mapped[list['Vocabulary']] = relationship('Vocabulary', foreign_keys='[Vocabulary.vocabulary_concept_id]', back_populates='vocabulary_concept')
            relationship_: Mapped[list['Relationship']] = relationship('Relationship', back_populates='relationship_concept')


        class ConceptClass(Base):
            __tablename__ = 'concept_class'
            __table_args__ = (
                ForeignKeyConstraint(['concept_class_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('concept_class_id'),
                Index('idx_concept_class_class_id', 'concept_class_id'),
                {'schema': 'shared'}
            )

            concept_class_id: Mapped[str] = mapped_column(String(20), primary_key=True)
            concept_class_name: Mapped[str] = mapped_column(String(255), nullable=False)
            concept_class_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

            concept_concept_class: Mapped[list['Concept']] = relationship('Concept', foreign_keys='[Concept.concept_class_id]', back_populates='concept_class')
            concept_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_class_concept_id], back_populates='concept_class_concept_class_concept')


        class Domain(Base):
            __tablename__ = 'domain'
            __table_args__ = (
                ForeignKeyConstraint(['domain_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('domain_id'),
                Index('idx_domain_domain_id', 'domain_id'),
                {'schema': 'shared'}
            )

            domain_id: Mapped[str] = mapped_column(String(20), primary_key=True)
            domain_name: Mapped[str] = mapped_column(String(255), nullable=False)
            domain_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

            concept_domain: Mapped[list['Concept']] = relationship('Concept', foreign_keys='[Concept.domain_id]', back_populates='domain')
            domain_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[domain_concept_id], back_populates='domain_domain_concept')


        class Vocabulary(Base):
            __tablename__ = 'vocabulary'
            __table_args__ = (
                ForeignKeyConstraint(['vocabulary_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('vocabulary_id'),
                Index('idx_vocabulary_vocabulary_id', 'vocabulary_id'),
                {'schema': 'shared'}
            )

            vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
            vocabulary_name: Mapped[str] = mapped_column(String(255), nullable=False)
            vocabulary_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)
            vocabulary_reference: Mapped[Optional[str]] = mapped_column(String(255))
            vocabulary_version: Mapped[Optional[str]] = mapped_column(String(255))

            concept_vocabulary: Mapped[list['Concept']] = relationship('Concept', foreign_keys='[Concept.vocabulary_id]', back_populates='vocabulary')
            vocabulary_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[vocabulary_concept_id], back_populates='vocabulary_vocabulary_concept')


        class Relationship(Base):
            """The OMOP ``relationship`` table."""
            __tablename__ = 'relationship'
            __table_args__ = (
                ForeignKeyConstraint(['relationship_concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('relationship_id'),
                Index('idx_relationship_rel_id', 'relationship_id'),
                {'schema': 'shared'}
            )

            relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True)
            relationship_name: Mapped[str] = mapped_column(String(255), nullable=False)
            is_hierarchical: Mapped[str] = mapped_column(String(1), nullable=False)
            defines_ancestry: Mapped[str] = mapped_column(String(1), nullable=False)
            reverse_relationship_id: Mapped[str] = mapped_column(String(20), nullable=False)
            relationship_concept_id: Mapped[int] = mapped_column(Integer, nullable=False)

            relationship_concept: Mapped['Concept'] = relationship('Concept', back_populates='relationship_')


        t_concept_ancestor = Table(
            'concept_ancestor', Base.metadata,
            Column('ancestor_concept_id', Integer, nullable=False),
            Column('descendant_concept_id', Integer, nullable=False),
            Column('min_levels_of_separation', Integer, nullable=False),
            Column('max_levels_of_separation', Integer, nullable=False),
            ForeignKeyConstraint(['ancestor_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['descendant_concept_id'], ['shared.concept.concept_id']),
            Index('idx_concept_ancestor_id_1', 'ancestor_concept_id'),
            Index('idx_concept_ancestor_id_2', 'descendant_concept_id'),
            schema='shared'
        )


        t_concept_synonym = Table(
            'concept_synonym', Base.metadata,
            Column('concept_id', Integer, nullable=False),
            Column('concept_synonym_name', String(1000), nullable=False),
            Column('language_concept_id', Integer, nullable=False),
            ForeignKeyConstraint(['concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['language_concept_id'], ['shared.concept.concept_id']),
            Index('idx_concept_synonym_id', 'concept_id'),
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
            ForeignKeyConstraint(['amount_unit_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['denominator_unit_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['drug_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['ingredient_concept_id'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['numerator_unit_concept_id'], ['shared.concept.concept_id']),
            Index('idx_drug_strength_id_1', 'drug_concept_id'),
            Index('idx_drug_strength_id_2', 'ingredient_concept_id'),
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
            ForeignKeyConstraint(['concept_id_1'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['concept_id_2'], ['shared.concept.concept_id']),
            ForeignKeyConstraint(['relationship_id'], ['shared.relationship.relationship_id']),
            Index('idx_concept_relationship_id_1', 'concept_id_1'),
            Index('idx_concept_relationship_id_2', 'concept_id_2'),
            Index('idx_concept_relationship_id_3', 'relationship_id'),
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


        # ---------------------------------------------------------------------------
        # OMOP - concept_mapping (non-standard, CBR extension)
        # Maps source field values to OMOP concept_ids
        # ---------------------------------------------------------------------------

        class ConceptMapping(Base):
            __tablename__ = 'concept_mapping'
            __table_args__ = (
                ForeignKeyConstraint(['concept_id'], ['shared.concept.concept_id']),
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            source_vocabulary_id: Mapped[Optional[str]] = mapped_column(String(20))
            source_code: Mapped[Optional[str]] = mapped_column(String(50))
            source_concept_name: Mapped[Optional[str]] = mapped_column(String(255))
            concept_id: Mapped[Optional[int]] = mapped_column(Integer)
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()")
            )

        class CohortMapping(Base):
            """Maps a cohort_id to its human-readable name and schema."""
            __tablename__ = 'cohort_mappings'
            __table_args__ = (
                PrimaryKeyConstraint('cohort_id'),
                {'schema': 'shared'}
            )

            cohort_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            cohort_name: Mapped[str] = mapped_column(String(255), nullable=False)
            schema_name: Mapped[str] = mapped_column(String(63), nullable=False)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
                DateTime, server_default=text("NOW()")
            )

        class Assessment(Base):
            """Assessment instrument names (e.g. MoCA, MMSE)."""
            __tablename__ = 'assessments'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))


        class Machine(Base):
            """Data-collection machine names."""
            __tablename__ = 'machines'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))


        class Instrument(Base):
            """Junction: assessment x machine x cohort -> source file contract."""
            __tablename__ = 'instruments'
            __table_args__ = (
                ForeignKeyConstraint(['assessment_id'], ['shared.assessments.id']),
                ForeignKeyConstraint(['machine_id'], ['shared.machines.id']),
                ForeignKeyConstraint(['cohort_id'], ['shared.cohort_mappings.cohort_id']),
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            assessment_id: Mapped[int] = mapped_column(Integer, nullable=False)
            machine_id: Mapped[int] = mapped_column(Integer, nullable=False)
            cohort_id: Mapped[int] = mapped_column(Integer, nullable=False)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))


        class Endpoint(Base):
            """API endpoint names registered for the BRAID portal."""
            __tablename__ = 'endpoints'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            path: Mapped[str] = mapped_column(String(500), nullable=False)
            method: Mapped[str] = mapped_column(String(10), nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))


        class Api(Base):
            """Endpoint relationships: groups endpoints into logical APIs."""
            __tablename__ = 'apis'
            __table_args__ = (
                ForeignKeyConstraint(['endpoint_id'], ['shared.endpoints.id']),
                PrimaryKeyConstraint('id'),
                {'schema': 'shared'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            name: Mapped[str] = mapped_column(String(255), nullable=False)
            endpoint_id: Mapped[int] = mapped_column(Integer, nullable=False)
            description: Mapped[Optional[str]] = mapped_column(Text)
            is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))

        class Places(Base):
            __tablename__ = 'places'
            __table_args__ = (
                PrimaryKeyConstraint('location_id'),
                {'schema': 'shared'}
            )

            location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
            city: Mapped[Optional[str]] = mapped_column(String(50))
            state: Mapped[Optional[str]] = mapped_column(String(2))
            zip: Mapped[Optional[str]] = mapped_column(String(9))
            county: Mapped[Optional[str]] = mapped_column(String(20))
            latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
            longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)

        classes = {
                'Concept': Concept,
                'ConceptClass': ConceptClass,
                'Domain': Domain,
                'Vocabulary': Vocabulary,
                'Relationship': Relationship,
                'concept_ancestor': t_concept_ancestor,
                'concept_synonym': t_concept_synonym,
                'drug_strength': t_drug_strength,
                'concept_relationship': t_concept_relationship,
                'LocalConcept': LocalConcept,
                'ConceptMapping': ConceptMapping,
                'CohortMapping': CohortMapping,
                'Assessment': Assessment,
                'Machine': Machine,
                'Instrument': Instrument,
                'Endpoint': Endpoint,
                'Api': Api,
                'Places': Places,
        }

    elif schema_type == 'orphan':

        class IdentifierErrorOrphan(Base):
            __tablename__ = 'identifier_errors_orphan'
            __table_args__ = (
                PrimaryKeyConstraint('id'),
                {'schema': 'orphan'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            subject_id: Mapped[Optional[str]] = mapped_column(String(50))
            data: Mapped[Optional[str]] = mapped_column(Text)
            instruments_source_id: Mapped[Optional[str]] = mapped_column(String(255))
            created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            created_by: Mapped[Optional[str]] = mapped_column(String(255))
            updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            updated_by: Mapped[Optional[str]] = mapped_column(String(255))
            status: Mapped[Optional[str]] = mapped_column(String(50))
            cohort: Mapped[Optional[int]] = mapped_column(Integer)

        class SourceLogOrphan(Base):
            __tablename__ = 'source_logs_orphan'
            __table_args__ = (
                ForeignKeyConstraint(['instrument_cat'], ['shared.instruments.id']),
                ForeignKeyConstraint(['api_catalogue_id'], ['shared.apis.id']),
                PrimaryKeyConstraint('id'),
                {'schema': 'orphan'}
            )

            id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
            instrument_cat: Mapped[Optional[int]] = mapped_column(Integer)
            api_catalogue_id: Mapped[Optional[int]] = mapped_column(Integer)
            source: Mapped[Optional[str]] = mapped_column(String(255))
            file_format: Mapped[Optional[str]] = mapped_column(String(50))
            created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            modified_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
            subjects_in_file: Mapped[Optional[int]] = mapped_column(Integer)
            subjects_passed: Mapped[Optional[int]] = mapped_column(Integer)
            subjects_failed: Mapped[Optional[int]] = mapped_column(Integer)
            fdc_id: Mapped[Optional[str]] = mapped_column(String(255))
            is_instrumentals: Mapped[Optional[bool]] = mapped_column(Boolean)

        classes = {
                'IdentifierErrorOrphan': IdentifierErrorOrphan,
                'SourceLogOrphan': SourceLogOrphan
        }

    else:
        raise ValueError(f"Unsupported schema_type: {schema_type}")

    return ReturnedTables(Base.metadata, classes)
