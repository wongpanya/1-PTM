from pathlib import Path

import pandas as pd


DEFAULT_DATA_PATH = Path("data/sample/development_sample.csv")
DEFAULT_VALIDATION_PATH = Path("data/sample/validation_data.csv")


def load_dataset(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}")
    return pd.read_csv(data_path)


def load_validation_dataset(path: str | Path = DEFAULT_VALIDATION_PATH) -> pd.DataFrame:
    return load_dataset(path)
