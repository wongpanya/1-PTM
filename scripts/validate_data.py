from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.config import PROJECT_ROOT
from src.validation.reporting import write_issues_csv, write_validation_report
from src.validation.schema import load_validation_schema, validate_dataset_file, validation_summary


REPORT_DIR = PROJECT_ROOT / "data/processed/reports"


def main() -> int:
    schema = load_validation_schema()
    all_issues = []
    summaries = []

    for dataset_name, config in schema.get("datasets", {}).items():
        df, issues = validate_dataset_file(config["path"], dataset_name, schema)
        all_issues.extend(issue.as_dict() for issue in issues)
        if df is not None:
            summaries.append(validation_summary(df, dataset_name, schema))

    error_count = sum(1 for issue in all_issues if issue["severity"] == "error")
    warning_count = sum(1 for issue in all_issues if issue["severity"] == "warning")
    report = {
        "status": "passed" if error_count == 0 else "failed",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "error_count": error_count,
        "warning_count": warning_count,
        "datasets": summaries,
        "issues": all_issues,
    }
    write_validation_report(report, REPORT_DIR)
    write_issues_csv(all_issues, REPORT_DIR)

    if error_count:
        print(f"Data validation failed: {error_count} errors, {warning_count} warnings")
        print(f"Report: {REPORT_DIR / 'validation_report.json'}")
        return 1

    print(f"Data validation passed: {warning_count} warnings")
    print(f"Report: {REPORT_DIR / 'validation_report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
