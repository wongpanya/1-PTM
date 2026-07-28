from __future__ import annotations

import sqlite3

import pandas as pd

from src.ingestion.database import expected_tables, get_connection, table_counts


def database_status() -> dict:
    counts = table_counts()
    tables = expected_tables()
    return {
        "expected_tables": tables,
        "available_tables": sorted(counts.keys()),
        "missing_tables": sorted(set(tables).difference(counts.keys())),
        "table_counts": counts,
    }


def read_table(table_name: str, limit: int | None = None) -> pd.DataFrame:
    if table_name not in expected_tables():
        raise ValueError(f"Unknown table: {table_name}")
    query = f'SELECT * FROM "{table_name}"'
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def scalar(query: str) -> int | float | str | None:
    with get_connection() as conn:
        row = conn.execute(query).fetchone()
        if row is None:
            return None
        return row[0]


def database_health() -> tuple[bool, str]:
    try:
        status = database_status()
    except (sqlite3.Error, OSError, ValueError) as exc:
        return False, str(exc)
    if status["missing_tables"]:
        return False, f"Missing tables: {', '.join(status['missing_tables'])}"
    return True, "Database ready"
