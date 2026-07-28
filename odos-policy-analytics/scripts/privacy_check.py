from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.config import PROJECT_ROOT, load_yaml


def main() -> int:
    schema = load_yaml("config/validation_schema.yaml")
    forbidden_columns = set(schema.get("forbidden_columns", []))
    failures = []

    for dataset_name, config in schema.get("datasets", {}).items():
        path = PROJECT_ROOT / config["path"]
        if not path.exists():
            failures.append(f"missing dataset: {path}")
            continue
        df = pd.read_csv(path, nrows=5)
        present = sorted(forbidden_columns.intersection(df.columns))
        if present:
            failures.append(f"{dataset_name}: forbidden columns present {present}")

    raw_files = [p for p in (PROJECT_ROOT / "data/raw").glob("*") if p.name != "README.md"]
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
