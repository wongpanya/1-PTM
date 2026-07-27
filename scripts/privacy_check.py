from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_COLUMNS = {
    "contact_name",
    "contact_phone",
    "contract_no",
    "employment_cert_doc_no",
    "workplace_address",
    "officer_notes",
    "other_comments",
    "employer",
    "job_title",
    "income_raw",
    "gpa_raw",
}
DATASETS = [
    ROOT / "data/sample/development_sample.csv",
    ROOT / "data/sample/validation_data.csv",
    ROOT / "data/sample/modeling_dataset_no_pii.csv",
]


def main() -> int:
    failures = []
    for path in DATASETS:
        if not path.exists():
            failures.append(f"missing dataset: {path}")
            continue
        df = pd.read_csv(path, nrows=5)
        present = sorted(FORBIDDEN_COLUMNS.intersection(df.columns))
        if present:
            failures.append(f"{path.name}: forbidden columns present {present}")
    raw_files = [p for p in (ROOT / "data/raw").glob("*") if p.name != "README.md"]
    if raw_files:
        failures.append(f"data/raw contains committed/local files: {[p.name for p in raw_files]}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print("Privacy check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
