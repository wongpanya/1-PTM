from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.governance.audit import append_audit_event
from src.ingestion.importer import import_csv
from src.utils.config import PROJECT_ROOT
from src.validation.reporting import write_issues_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import no-PII CSV data into processed prototype storage.")
    parser.add_argument("--source", default="data/sample/modeling_dataset_no_pii.csv", help="Source CSV path.")
    parser.add_argument("--dataset-name", default="modeling_dataset_no_pii", help="Dataset name for processed output.")
    parser.add_argument("--output-dir", default="data/processed/imported", help="Processed output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result, issues = import_csv(args.source, args.dataset_name, args.output_dir)
    except Exception as exc:
        append_audit_event("import_failed", {"source": args.source, "error": str(exc)})
        print(f"Import failed: {exc}")
        return 1

    report_dir = PROJECT_ROOT / "data/processed/reports"
    write_issues_csv(issues, report_dir)
    audit_path = append_audit_event("import_completed", result.as_dict() | {"issue_count": len(issues)})
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    print(f"Audit log: {audit_path}")
    return 0 if result.status == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
