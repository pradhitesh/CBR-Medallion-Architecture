"""
src/pipelines/load_vocab.py

The script populates 9 OMOP vocabulary tables using 
OMOP CSV files downloaded from https://athena.ohdsi.org.

The script assumes that 9 OMOP vocabular tables are already created.
See alembic/2026_06_08_141923_b106cefae7bd_bootstrap_shared.py
"""
import argparse
import sys
import os
import logging
import psycopg

from pathlib import Path
from sqlalchemy import create_engine
from config import *

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True,
)

# Define OMOP Table and OMOP CSV mappings
VOCAB_TABLES = [
    ("DOMAIN.csv", "domain"),
    ("VOCABULARY.csv", "vocabulary"),
    ("CONCEPT_CLASS.csv", "concept_class"),
    ("RELATIONSHIP.csv", "relationship"),
    ("CONCEPT.csv", "concept"),
    ("CONCEPT_RELATIONSHIP.csv", "concept_relationship"),
    ("CONCEPT_ANCESTOR.csv", "concept_ancestor"),
    ("CONCEPT_SYNONYM.csv", "concept_synonym"),
    ("DRUG_STRENGTH.csv", "drug_strength"),
]

# Define COPY function
def copy_vocab_csvs(raw_conn: "psycopg.Connection", 
                    vocab_dir: Path, 
                    schema: str = "shared") -> None:
    """COPY the 9 Athena CSVs into ``<schema>.<table>``.

    Tab-delimited, no quoting (Athena uses backspace as QUOTE so embedded quotes
    in concept names don't break parsing).
    """
    # Check if all CSV files are intact
    missing = [fn for fn, _ in VOCAB_TABLES if not (vocab_dir / fn).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing vocab files:\n" + "\n".join(f"  - {x}" for x in missing)
        )

    try:
        # Connect to database
        with raw_conn.cursor() as cur:
            for filename, table in VOCAB_TABLES:
                filepath = vocab_dir / filename
                logging.info(f"Loading: {filename} -> {schema}.{table}")
                with open(filepath, "r", encoding="utf-8") as f:
                    # Read header for explicit column list (the CSV column order
                    # may not match the table's natural order).
                    header_line = f.readline().strip()
                    columns = header_line.split("\t")
                    col_str = ", ".join(f'"{c.lower()}"' for c in columns)

                    copy_sql = f"""
                        COPY {schema}.{table} ({col_str})
                        FROM STDIN
                        WITH (FORMAT csv, DELIMITER E'\\t', QUOTE E'\\b', HEADER true)
                    """
                    f.seek(0)
                    with cur.copy(copy_sql) as copy:
                        while data := f.read(1024 * 1024):
                            copy.write(data)
    except Exception as e:
        logging.exception(
            "Vocab tables cannot be loaded due to %s", e
        )
        raise
    
def load(db_uri: str, 
         vocab_folder: str, 
         schema_name: str = "shared"):
    
    # Load db_uri
    if not db_uri:
        db_uri = os.getenv('OMOP_DB_URI')
        logging.info(f"db_uri was not specified. Procedding with default.")

    # Check if db_uri was properly loaded from .env file
    if not db_uri:
        raise ValueError(f"Could not find db_uri. Please specify db_uri.")
        
    # Check if vocab_folder is a directory
    if not Path(vocab_folder).is_dir():
        raise NotADirectoryError(f"vocab_dir is not a directory: {vocab_folder}")
    
    # Create SQL DB engine
    engine = create_engine(db_uri)
    try:
        # Connect to database    
        with engine.begin() as conn:
            raw_conn = conn.connection.driver_connection
            copy_vocab_csvs(raw_conn, Path(vocab_folder), schema_name)

        logging.info(f"Done. Vocab loaded into {schema_name}.")

    except Exception:
        logging.exception(
            "Vocab tables cannot be loaded to %s",
            schema_name,
        )
        raise

    finally:
        engine.dispose()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load 9 OMOP Vocab CSV files onto database. It assumes that 9 OMOP vocab tables are already added."
    )

    parser.add_argument(
        "-d", "--db_uri",
        required=True,
        type=str,
        metavar="PATH",
        help="Database URI to where the vocab tables will be added (e.g, postgresql+psycopg://user:password@localhost:5432/database)",
    )

    parser.add_argument(
        "-v", "--vocab_folder",
        required=True,
        type=Path,
        metavar="PATH",
        help="Folder containing the 9 Athena CSV files (e.g. vocabulary_download_v5_{...}).",
    )

    parser.add_argument(
        "-s", "--schema_name",
        default="shared",
        metavar="NAME",
        help="Target schema (default: shared).",
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    load(
        db_uri=args.db_uri,
        vocab_folder=args.vocab_folder,
        schema_name=args.schema_name
    )
