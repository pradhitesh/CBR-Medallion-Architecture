import os
from delembic import DataMigration

from src.pipelines.omop import vocab
from config import *

class LoadVocab(DataMigration):
    revision = "12d88279d63a"
    depends_on = ['371d5bcbabe6']
    description = "load vocab"

    def upgrade(self, conn):
        # Specify the arguments
        db_uri = os.getenv('BRONZE_PROD_URI')
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
