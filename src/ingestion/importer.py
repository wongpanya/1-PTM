from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

import pandas as pd

from src.governance.privacy import assert_no_forbidden_columns
from src.utils.config import PROJECT_ROOT
from src.validation.schema import load_validation_schema, validate_dataframe


@dataclass
class ImportResult:
    dataset_name: str
    source_path: str
    output_path: str
    rows: int
    columns: int
    status: str
    errors: int
    warnings: int

    def as_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "source_path": self.source_path,
            "output_path": self.output_path,
            "rows": self.rows,
            "columns": self.columns,
            "status": self.status,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def import_csv(
    source_path: str | Path,
    dataset_name: str,
    output_dir: str | Path = PROJECT_ROOT / "data/processed/imported",
    fail_on_warning: bool = False,
) -> tuple[ImportResult, list[dict]]:
    source = Path(source_path)
    if not source.is_absolute():
        source = PROJECT_ROOT / source
    if not source.exists():
        raise FileNotFoundError(f"Import source not found: {source}")

    output = Path(output_dir)
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    output.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(source)
    assert_no_forbidden_columns(df.columns)

    schema = load_validation_schema()
    issues = [issue.as_dict() for issue in validate_dataframe(df, dataset_name, schema)]
    errors = sum(1 for issue in issues if issue["severity"] == "error")
    warnings = sum(1 for issue in issues if issue["severity"] == "warning")
    status = "failed" if errors or (fail_on_warning and warnings) else "passed"

    target = output / f"{dataset_name}.csv"
    if status == "passed":
        df.to_csv(target, index=False, encoding="utf-8-sig")
    else:
        quarantine = output / f"{dataset_name}.rejected.csv"
        shutil.copyfile(source, quarantine)
        target = quarantine

    return (
        ImportResult(
            dataset_name=dataset_name,
            source_path=str(source),
            output_path=str(target),
            rows=int(len(df)),
            columns=int(len(df.columns)),
            status=status,
            errors=errors,
            warnings=warnings,
        ),
        issues,
    )
