from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_yaml


DEFAULT_DB_PATH = PROJECT_ROOT / "data/processed/odos_policy_analytics.sqlite"


def build_sqlite_from_csvs(
    db_path: str | Path = DEFAULT_DB_PATH,
    column_mapping_path: str = "config/column_mapping.yaml",
    sample_path: str | Path = PROJECT_ROOT / "data/sample/modeling_dataset_no_pii.csv",
) -> Path:
    db = Path(db_path)
    if not db.is_absolute():
        db = PROJECT_ROOT / db
    db.parent.mkdir(parents=True, exist_ok=True)

    source = Path(sample_path)
    if not source.is_absolute():
        source = PROJECT_ROOT / source
    df = pd.read_csv(source)
    mapping = load_yaml(column_mapping_path)

    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as conn:
        df.to_sql("modeling_dataset_no_pii", conn, if_exists="replace", index=False)
        for table_name, columns in mapping.get("tables", {}).items():
            selected = [column for column in columns if column in df.columns]
            if selected:
                df[selected].to_sql(table_name, conn, if_exists="replace", index=False)
    return db


def table_counts(db_path: str | Path = DEFAULT_DB_PATH) -> dict[str, int]:
    db = Path(db_path)
    if not db.is_absolute():
        db = PROJECT_ROOT / db
    with sqlite3.connect(db) as conn:
        tables = [row[0] for row in conn.execute("select name from sqlite_master where type='table' order by name")]
        return {table: int(conn.execute(f'select count(*) from "{table}"').fetchone()[0]) for table in tables}
