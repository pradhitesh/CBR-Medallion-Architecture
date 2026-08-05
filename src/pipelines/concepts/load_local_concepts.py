"""Load local_concept CSV/Excel into shared.local_concept.

Modes:
  replace  — TRUNCATE then bulk-insert all rows (default, always idempotent).
  upsert   — INSERT … ON CONFLICT (id) DO UPDATE SET … (requires 'id' column in file).
             created_at is preserved; updated_at is refreshed to NOW().

Run:
    python src/pipelines/load_local_concepts.py path/to/local_concept.csv
    python src/pipelines/load_local_concepts.py path/to/local_concept.xlsx --mode upsert
    python src/pipelines/load_local_concepts.py path/to/local_concept.csv --schema shared --dry-run

Requires:
    OMOP_DB_URI environment variable (set via .env / config.py).
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from config import *
from src.database.bronze.tables import return_tables

LocalConcept = return_tables(schema_type='shared').LocalConcept

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,
)
log = logging.getLogger(__name__)

TABLE_COLS: set[str] = {c.name for c in LocalConcept.__table__.columns}
SERVER_DEFAULT_COLS = {"created_at", "updated_at", "is_active"}
UPSERT_PRESERVE = {"id", "created_at"}

# Build per-column coercers from SQLAlchemy types (all CSV values arrive as str)
_BOOL_TRUTHY = {"true", "1", "yes", "t"}
_BOOL_FALSY  = {"false", "0", "no", "f"}

def _make_coercers() -> dict[str, callable]:
    from sqlalchemy import Boolean, Integer
    coercers = {}
    for col in LocalConcept.__table__.columns:
        if isinstance(col.type, Boolean):
            def _bool(v, _=None):
                if v is None:
                    return None
                s = str(v).strip().lower()
                if s in _BOOL_TRUTHY:
                    return True
                if s in _BOOL_FALSY:
                    return False
                raise ValueError(f"Cannot coerce {v!r} to bool")
            coercers[col.name] = _bool
        elif isinstance(col.type, Integer):
            def _int(v, _=None):
                if v is None:
                    return None
                try:
                    return int(float(str(v).strip()))
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot coerce {v!r} to int")
            coercers[col.name] = _int
    return coercers

_COERCERS = _make_coercers()


def _coerce_row(row: dict) -> dict:
    result = {}
    for k, v in row.items():
        if v is None or v == "":
            result[k] = None
        elif k in _COERCERS:
            result[k] = _COERCERS[k](v)
        else:
            result[k] = v
    return result


def _read_file(path: Path) -> pl.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pl.read_csv(path, infer_schema_length=0, null_values=["", "NULL", "null", "None"])
    elif suffix in (".xlsx", ".xls"):
        df = pl.read_excel(path)
        # Excel gives typed columns; cast everything to str then let the DB coerce
        df = df.with_columns([pl.col(c).cast(pl.Utf8, strict=False) for c in df.columns])
    else:
        raise ValueError(f"Unsupported file type: {suffix!r} (expected .csv / .xlsx / .xls)")
    return df


def _normalize(df: pl.DataFrame) -> pl.DataFrame:
    """Lowercase and strip column names."""
    return df.rename({c: c.strip().lower() for c in df.columns})


def load_local_concepts(
    engine,
    file_path: Path,
    schema: str = "shared",
    mode: str = "replace",
    dry_run: bool = False,
) -> dict:
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    # 1. Read + normalize
    df = _read_file(file_path)
    df = _normalize(df)

    if df.is_empty():
        log.warning("File is empty — nothing to load.")
        return {"mode": mode, "rows": 0}

    row_count = len(df)
    log.info("Read %d rows from %s", row_count, file_path.name)

    # 2. Column validation
    csv_cols = set(df.columns)
    unknown = csv_cols - TABLE_COLS
    if unknown:
        log.warning("Ignoring unknown columns (not in table): %s", sorted(unknown))

    load_cols = sorted(csv_cols & TABLE_COLS)
    if not load_cols:
        raise ValueError(f"No valid table columns in file. Table has: {sorted(TABLE_COLS)}")

    log.info("Columns to load: %s", load_cols)

    if mode == "upsert" and "id" not in csv_cols:
        raise ValueError("--mode upsert requires an 'id' column in the file.")

    # 3. Build row dicts (only table columns, with type coercion)
    rows: list[dict] = [
        _coerce_row({k: row[k] for k in load_cols})
        for row in df.select(load_cols).to_dicts()
    ]

    if dry_run:
        log.info("[dry-run] Would %s %d rows. No DB changes made.", mode, len(rows))
        return {"mode": mode, "rows": len(rows), "dry_run": True}

    # 4. Execute in batches (psycopg limit: 65535 params per query)
    table = LocalConcept.__table__
    n_cols = len(load_cols)
    batch_size = max(1, 65535 // n_cols)

    def _batches(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i : i + size]

    with engine.begin() as conn:
        if mode == "replace":
            log.info("Truncating %s.local_concept (RESTART IDENTITY) ...", schema)
            conn.execute(text(f"TRUNCATE TABLE {schema}.local_concept RESTART IDENTITY CASCADE"))
            for batch in _batches(rows, batch_size):
                conn.execute(table.insert(), batch)
            log.info("Inserted %d rows.", len(rows))
            return {"mode": mode, "inserted": len(rows)}

        elif mode == "upsert":
            total_rowcount = 0
            for batch in _batches(rows, batch_size):
                stmt = pg_insert(table).values(batch)
                update_set = {
                    c: stmt.excluded[c]
                    for c in load_cols
                    if c not in UPSERT_PRESERVE
                }
                update_set["updated_at"] = text("NOW()")
                stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=update_set)
                result = conn.execute(stmt)
                total_rowcount += result.rowcount
            log.info("Upserted %d rows (rowcount=%d).", len(rows), total_rowcount)
            return {"mode": mode, "rows": len(rows), "rowcount": total_rowcount}

    return {}  # unreachable


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load local_concept CSV/Excel into shared.local_concept (idempotent).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", type=Path, help="CSV or Excel file to load.")
    parser.add_argument(
        "--schema", default="shared",
        help="Target schema (default: shared).",
    )
    parser.add_argument(
        "--mode", choices=["replace", "upsert"], default="replace",
        help=(
            "replace = TRUNCATE then insert all rows (default, always safe). "
            "upsert = insert new rows, update changed rows by id."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Read and validate the file but make no DB changes.",
    )
    args = parser.parse_args()

    uri = os.getenv("BRONZE_PROD_URI")
    if not uri:
        sys.exit("OMOP_DB_URI environment variable not set.")

    engine = create_engine(uri)
    result = load_local_concepts(
        engine,
        args.file,
        schema=args.schema,
        mode=args.mode,
        dry_run=args.dry_run,
    )
    log.info("Result: %s", result)


if __name__ == "__main__":
    main()
