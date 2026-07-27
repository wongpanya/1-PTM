from pathlib import Path

import pandas as pd

from src.ingestion.database import build_sqlite_from_csvs, table_counts
from src.ingestion.importer import import_csv


def test_import_csv_writes_processed_file(tmp_path):
    source = tmp_path / "sample.csv"
    pd.DataFrame({
        "odos_uid": ["ODOS00001"],
        "cohort": [1],
        "province": ["A"],
        "project_condition_status": ["สำเร็จการศึกษา"],
        "current_field_group": ["field"],
        "employment_type": ["ภาครัฐ"],
        "target_graduation_success": [1],
        "target_scholarship_risk": [0],
        "target_tracking_risk": [0],
        "target_employment_ready": [1],
        "target_field_mismatch": [0],
        "target_local_mismatch": [0],
    }).to_csv(source, index=False)

    result, issues = import_csv(source, "test_dataset", tmp_path / "out")
    assert result.status == "passed"
    assert Path(result.output_path).exists()
    assert not [issue for issue in issues if issue["severity"] == "error"]


def test_build_sqlite_from_csvs(tmp_path):
    source = tmp_path / "sample.csv"
    pd.DataFrame({
        "odos_uid": ["ODOS00001", "ODOS00002"],
        "cohort": [1, 2],
        "province": ["A", "B"],
        "project_condition_status": ["สำเร็จการศึกษา", "ลาออก"],
        "current_field_group": ["field", "field"],
        "employment_type": ["ภาครัฐ", "ภาคเอกชน"],
    }).to_csv(source, index=False)
    db_path = build_sqlite_from_csvs(tmp_path / "test.sqlite", sample_path=source)
    counts = table_counts(db_path)
    assert counts["modeling_dataset_no_pii"] == 2
