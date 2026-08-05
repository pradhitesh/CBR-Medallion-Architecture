"""Builder for the `orphan` schema — a landing spot for identifier_errors /
source_logs rows that can't yet be attributed to a cohort. Bronze-only:
Silver and Gold drop the orphan schema entirely.
"""
from typing import Optional
import datetime

from sqlalchemy import (
    Boolean, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint,
    String, Text, text
)
from sqlalchemy.orm import Mapped, mapped_column

from src.database.common.base_types import ReturnedTables


def build_orphan(Base) -> ReturnedTables:
    class IdentifierErrorOrphan(Base):
        __tablename__ = 'identifier_errors'
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
        __tablename__ = 'source_logs'
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

    return ReturnedTables(Base.metadata, classes)
