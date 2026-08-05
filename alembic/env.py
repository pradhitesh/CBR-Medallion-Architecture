import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy import create_engine, pool, inspect
from alembic import context

from src.database.tables import Base as SharedBase
from src.database.tables import return_tables
from config import *

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Read the DB URL directly from env to avoid configparser's `%`-interpolation
DB_URL = os.getenv('BRONZE_PROD_URI')

# Always build the shared tables onto SharedBase.metadata, regardless of
# which migrations actually run this invocation — later revisions (e.g.
# cohort schemas) declare cross-schema FKs to shared.* that must resolve
# even when 371d5bcbabe6 (which builds them via create_schema) isn't
# part of this run.
return_tables(schema_type='shared')

# The target metadata is a list of metadatas
target_metadata = [SharedBase.metadata]
TRACKED_SCHEMAS = {'shared'}

def discover_cohorts(connection):
    inspector = inspect(connection)
    schemas = inspector.get_schema_names()
    for schema in schemas:
        if schema.startswith("cohort_"):
            tables = return_tables(schema_type='cohort', schema_name=schema)
            target_metadata.append(tables.metadata)
            TRACKED_SCHEMAS.add(schema)

def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in TRACKED_SCHEMAS
    return True

def run_migrations_offline() -> None:
    # In offline mode we can't inspect the DB, so we only track shared by default
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_name=include_name,
        version_table="alembic_version",
        version_table_schema="public",
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(DB_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        discover_cohorts(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_name=include_name,
            compare_type=True,
            version_table="alembic_version",
            version_table_schema="public",
        )
        with context.begin_transaction():
            context.run_migrations()
        connection.commit()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
