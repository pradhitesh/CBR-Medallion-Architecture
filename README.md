# CBR-Medallion-Architecture

OMOP CDM-based medallion architecture for CBR cohort data. Schema migrations via Alembic, data migrations via Delembic, on Postgres.

## Setup

### 1. Python environment (3.14)

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Secrets

Copy the example and fill in real values:

```bash
cp secrets.env.example secrets.env
```

`secrets.env` keys:

| Key | Purpose |
|---|---|
| `BRONZE_PROD_URI` | Bronze layer Postgres URI |
| `SILVER_PROD_URI` | Silver layer Postgres URI |
| `GOLD_PROD_URI` | Gold layer Postgres URI |
| `OMOP_VOCAB_DIR` | Path to extracted OMOP vocab CSVs (Athena download) |
| `CBR_LOCAL_CONCEPTS` | Path to local concept mapping CSV |

Loaded automatically by [config.py](config.py) via `python-dotenv` for alembic, delembic, and `src`.

### 3. Download assets

Pulls mapping files, OMOP vocab zip, and codebooks from the CBR Data Assets API into `assets/`:

```bash
python -m src.asset.download

# codebooks only
python -m src.asset.download -c True
```

## Project layout

```
alembic/            schema migrations (tables, schemas, constraints)
delembic/           data migrations (vocab load, local concept load)
src/database/       SQLAlchemy table defs (OMOP CDM + shared/local tables), return_tables()
src/pipelines/
  medallion/schema.py   create_schema/drop_schema (cohort/shared/orphan schemas)
  omop/vocab.py         load Athena vocab CSVs -> shared.* tables
  concepts/load_local_concepts.py   load local_concept CSV/Excel -> shared.local_concept
src/asset/          asset + codebook download from CBR Data Assets API
assets/             downloaded codebooks, mappings, OMOP vocab CSVs
pipeline.yaml       ordered migration targets (alembic + delembic steps)
```

## Migrations

Schema (Alembic):

```bash
alembic upgrade head
```

Data (Delembic):

```bash
delembic upgrade head
```

`pipeline.yaml` records the intended run order across both tools (schema -> data -> schema head -> data head).
