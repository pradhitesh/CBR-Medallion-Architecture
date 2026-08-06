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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database.common.base_types import ReturnedTables


def build_orphan(Base) -> ReturnedTables:
    class IdentifierErrorOrphan(Base):
        __tablename__ = 'identifier_errors'
        __table_args__ = (
            ForeignKeyConstraint(['source_id'], ['orphan.source_logs.id']),
            PrimaryKeyConstraint('id'),
            {'schema': 'orphan'}
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        source_id: Mapped[int] = mapped_column(Integer, nullable=False)
        cohort:  Mapped[int] = mapped_column(Integer, nullable=True)
        barcode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        visit: Mapped[int] = mapped_column(Integer, nullable=True)
        date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
        subject_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
        original_error: Mapped[Optional[str]] = mapped_column(Text, nullable=False)
        new_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
        data: Mapped[Optional[str]] = mapped_column(JSONB, nullable=False, default={})
        checksum: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
        status: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
        created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))          
        updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
        updated_by: Mapped[Optional[str]] = mapped_column(String(255))

    class SourceLogOrphan(Base):
        __tablename__ = 'source_logs'
        __table_args__ = (
            ForeignKeyConstraint(['instrument_id'], ['shared.instruments.id']),
            ForeignKeyConstraint(['endpoint_id'], ['shared.endpoints.id']),
            PrimaryKeyConstraint('id'),
            {'schema': 'orphan'}
        )

        id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
        instrument_id: Mapped[Optional[int]] = mapped_column(Integer)
        endpoint_id: Mapped[Optional[int]] = mapped_column(Integer)
        source: Mapped[Optional[str]] = mapped_column(String(255))
        format: Mapped[Optional[str]] = mapped_column(String(50))
        is_instrumental: Mapped[Optional[bool]] = mapped_column(Boolean)
        created_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
        updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("NOW()"))
        updated_by: Mapped[Optional[str]] = mapped_column(String(255))

    classes = {
        'IdentifierErrorOrphan': IdentifierErrorOrphan,
        'SourceLogOrphan': SourceLogOrphan
    }

    return ReturnedTables(Base.metadata, classes)
