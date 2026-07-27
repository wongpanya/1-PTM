from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.governance.audit import append_audit_event
from src.ingestion.database import build_sqlite_from_csvs, table_counts


def main() -> int:
    db_path = build_sqlite_from_csvs()
    counts = table_counts(db_path)
    append_audit_event("database_built", {"db_path": str(db_path), "table_counts": counts})
    print(json.dumps({"db_path": str(db_path), "table_counts": counts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
