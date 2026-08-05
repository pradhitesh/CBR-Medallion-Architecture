from delembic import DataMigration
from src.pipelines.concepts.load_local_concepts import load_local_concepts
from pathlib import Path
from config import *

class LoadLocalConcept(DataMigration):
    revision = "042bb7273606"
    depends_on = ['da1117d6a8d9', '8ffd83ffb0fb']
    description = "load local concept"

    def upgrade(self, conn):
        csv_path = Path(os.getenv("CBR_LOCAL_CONCEPTS"))
        load_local_concepts(conn.engine, csv_path, schema="shared", mode="replace")

    def validate(self, conn):
        pass
