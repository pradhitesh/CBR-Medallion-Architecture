import os
from delembic import DataMigration

from src.pipelines.omop import vocab
from config import *

class LoadVocab(DataMigration):
    revision = "e70cee5bb5c9"
    depends_on = ['1b9dc94a6b21']
    description = "load vocab"

    def upgrade(self, conn):
        # Specify the arguments
        db_uri = os.getenv('GOLD_PROD_URI')
        vocab_folder = os.getenv("OMOP_VOCAB_DIR")
        schema_name = 'shared'

        # Run import
        vocab.load(
            db_uri=db_uri,
            vocab_folder=vocab_folder,
            schema_name=schema_name
        )

    def validate(self, conn):
        pass
