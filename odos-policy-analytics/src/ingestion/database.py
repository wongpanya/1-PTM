from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from uuid import uuid4

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_yaml


DEFAULT_DB_PATH = PROJECT_ROOT / "data/processed/odos_policy_analytics.sqlite"
SCHEMA_PATH = "config/database_schema.yaml"


def resolve_db_path(db_path: str | Path | None = None) -> Path:
    if db_path is None:
        config = load_yaml(SCHEMA_PATH)
        db_path = config.get("database_path", DEFAULT_DB_PATH)
    db = Path(db_path)
    if not db.is_absolute():
        db = PROJECT_ROOT / db
    return db


def initialize_database(
    db_path: str | Path | None = None,
    sample_path: str | Path | None = None,
    reset: bool = True,
) -> Path:
    db = resolve_db_path(db_path)
    db.parent.mkdir(parents=True, exist_ok=True)
    if reset and db.exists():
        db.unlink()

    schema = load_yaml(SCHEMA_PATH)
    sample = _load_sample(sample_path)
    with sqlite3.connect(db) as conn:
        for table_name, definition in schema["tables"].items():
            _create_table(conn, table_name, definition)
        _seed_core_tables(conn, sample)
        _seed_external_indicators(conn)
        _insert_import_log(conn, sample)
        _insert_audit_log(conn, "database_initialized", f"Initialized prototype database with {len(sample)} rows")
    return db


def build_sqlite_from_csvs(
    db_path: str | Path = DEFAULT_DB_PATH,
    column_mapping_path: str = "config/column_mapping.yaml",
    sample_path: str | Path = PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv",
) -> Path:
    return initialize_database(db_path=db_path, sample_path=sample_path, reset=True)


def ensure_database(db_path: str | Path | None = None) -> Path:
    db = resolve_db_path(db_path)
    if not db.exists():
        initialize_database(db)
    return db


def table_counts(db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, int]:
    db = resolve_db_path(db_path)
    with sqlite3.connect(db) as conn:
        tables = [row[0] for row in conn.execute("select name from sqlite_master where type='table' order by name")]
        return {table: int(conn.execute(f'select count(*) from "{table}"').fetchone()[0]) for table in tables}


def expected_tables() -> list[str]:
    return list(load_yaml(SCHEMA_PATH)["tables"].keys())


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    db = ensure_database(db_path)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def _load_sample(sample_path: str | Path | None) -> pd.DataFrame:
    if sample_path is None:
        app_config = load_yaml("config/app_config.yaml")
        sample_path = app_config["app"]["default_sample"]
    path = Path(sample_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return pd.read_csv(path)


def _create_table(conn: sqlite3.Connection, table_name: str, definition: dict) -> None:
    columns = definition["columns"]
    primary_key = definition.get("primary_key")
    column_defs = []
    for name, column_type in columns.items():
        suffix = " PRIMARY KEY" if name == primary_key else ""
        column_defs.append(f'"{name}" {column_type}{suffix}')
    conn.execute(f'DROP TABLE IF EXISTS "{table_name}"')
    conn.execute(f'CREATE TABLE "{table_name}" ({", ".join(column_defs)})')


def _seed_core_tables(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    table_columns = load_yaml(SCHEMA_PATH)["tables"]
    for table_name in ["students", "education_records", "employment_records", "scholarship_status"]:
        columns = list(table_columns[table_name]["columns"].keys())
        selected = [column for column in columns if column in df.columns]
        df[selected].drop_duplicates().to_sql(table_name, conn, if_exists="append", index=False)

    geo_columns = list(table_columns["geography_reference"]["columns"].keys())
    geography = df[[c for c in geo_columns if c != "geography_key" and c in df.columns]].drop_duplicates().copy()
    geography["geography_key"] = [
        f"GEO{index + 1:05d}" for index in range(len(geography))
    ]
    geography[geo_columns].to_sql("geography_reference", conn, if_exists="append", index=False)


def _seed_external_indicators(conn: sqlite3.Connection) -> None:
    path = PROJECT_ROOT / "data/reference/annual_external_indicators_template.csv"
    if path.exists():
        df = pd.read_csv(path)
        df.to_sql("external_indicators", conn, if_exists="append", index=False)


def _insert_import_log(conn: sqlite3.Connection, sample: pd.DataFrame) -> None:
    conn.execute(
        """
        INSERT INTO data_import_log
        (import_id, source_name, source_path, imported_at, rows_imported, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid4()),
            "modeling_dataset_no_pii",
            "data/sample/modeling_dataset_no_pii.csv",
            datetime.now(timezone.utc).isoformat(),
            int(len(sample)),
            "completed",
            "Initialized from no-PII sample dataset",
        ),
    )


def _insert_audit_log(conn: sqlite3.Connection, event_type: str, detail: str) -> None:
    conn.execute(
        """
        INSERT INTO audit_logs
        (audit_id, event_type, event_time, actor, detail)
        VALUES (?, ?, ?, ?, ?)
        """,
        (str(uuid4()), event_type, datetime.now(timezone.utc).isoformat(), "system", detail),
    )
