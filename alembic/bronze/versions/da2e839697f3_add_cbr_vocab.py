"""add cbr vocab

Revision ID: da2e839697f3
Revises: f1c65aae1546
Create Date: 2026-08-07 13:27:19.749376

"""
import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da2e839697f3'
down_revision: Union[str, Sequence[str], None] = 'f1c65aae1546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SCHEMA = "shared"
# See issue: https://github.com/pradhitesh/CBR-OMOP-Development/issues/29
VOCAB_CONCEPT_ID = 2000099999


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text(f"""
        INSERT INTO {SCHEMA}.concept (
            concept_id,
            concept_name,
            domain_id,
            vocabulary_id,
            concept_class_id,
            standard_concept,
            concept_code,
            valid_start_date,
            valid_end_date,
            invalid_reason
        ) VALUES (
            :concept_id,
            'CBR-SANSCOG Vocabulary',
            'Metadata',
            'Vocabulary',
            'Vocabulary',
            NULL,
            'CBR',
            :today,
            '2099-12-31',
            NULL
        )
    """), {"concept_id": VOCAB_CONCEPT_ID, "today": datetime.date.today()})

    conn.execute(sa.text(f"""
        INSERT INTO {SCHEMA}.vocabulary (
            vocabulary_id,
            vocabulary_name,
            vocabulary_reference,
            vocabulary_version,
            vocabulary_concept_id
        ) VALUES (
            'CBR',
            'CBR-SANSCOG Custom Vocabulary',
            'https://cbr-iisc.ac.in/',
            'v1.0',
            :vocab_concept_id
        )
    """), {"vocab_concept_id": VOCAB_CONCEPT_ID})


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(f"DELETE FROM {SCHEMA}.vocabulary WHERE vocabulary_id = 'CBR'"))
    conn.execute(sa.text(f"DELETE FROM {SCHEMA}.concept WHERE concept_id = :concept_id"),
                 {"concept_id": VOCAB_CONCEPT_ID})

