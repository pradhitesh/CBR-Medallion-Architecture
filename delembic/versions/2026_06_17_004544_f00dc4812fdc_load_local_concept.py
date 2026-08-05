from delembic import DataMigration
from src.pipelines.concepts.load_local_concepts import load_local_concepts
from pathlib import Path
from config import *

class LoadLocalConcept(DataMigration):
    revision = "f00dc4812fdc"
    depends_on = ['12d88279d63a', '371d5bcbabe6']
    description = "load local concept"

    def upgrade(self, conn):
        csv_path = Path(os.getenv("CBR_LOCAL_CONCEPTS"))
        load_local_concepts(conn.engine, csv_path, schema="shared", mode="replace")
        
    def validate(self, conn):
        pass
