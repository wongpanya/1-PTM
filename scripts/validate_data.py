from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATASETS = [
    ROOT / "data/sample/development_sample.csv",
    ROOT / "data/sample/validation_data.csv",
]
REQUIRED_COLUMNS = {
    "odos_uid",
    "cohort",
    "province",
    "project_condition_status",
    "current_field_group",
    "employment_type",
    "target_graduation_success",
    "target_scholarship_risk",
    "target_tracking_risk",
    "target_employment_ready",
    "target_field_mismatch",
    "target_local_mismatch",
}


def validate_dataset(path: Path) -> list[str]:
    errors = []
    if not path.exists():
        return [f"missing dataset: {path}"]
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        errors.append(f"{path.name}: missing columns {sorted(missing)}")
    if df.empty:
        errors.append(f"{path.name}: dataset is empty")
    if "odos_uid" in df and df["odos_uid"].duplicated().any():
        errors.append(f"{path.name}: duplicated odos_uid")
    return errors


def main() -> int:
    errors = []
    for path in DATASETS:
        errors.extend(validate_dataset(path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Data validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
