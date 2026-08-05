from delembic import DataMigration
from src.pipelines.concepts.load_local_concepts import load_local_concepts
from pathlib import Path
from config import *

class LoadLocalConcept(DataMigration):
    revision = "6a871c651cf7"
    depends_on = ['e70cee5bb5c9', '1b9dc94a6b21']
    description = "load local concept"

    def upgrade(self, conn):
        csv_path = Path(os.getenv("CBR_LOCAL_CONCEPTS"))
        load_local_concepts(conn.engine, csv_path, schema="shared", mode="replace")

    def validate(self, conn):
        pass
