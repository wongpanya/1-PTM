import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pandas as pd

from src.ingestion.database import build_sqlite_from_csvs, expected_tables, table_counts
from src.ingestion.importer import import_csv
from src.utils.config import PROJECT_ROOT


class ImportDatabaseTest(unittest.TestCase):
    def test_import_csv_writes_processed_file(self):
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
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
            self.assertEqual(result.status, "passed")
            self.assertTrue(Path(result.output_path).exists())
            self.assertEqual([issue for issue in issues if issue["severity"] == "error"], [])

    def test_build_sqlite_from_csvs_creates_phase3_schema(self):
        db_path = PROJECT_ROOT / f"data/processed/test_phase3_schema_{uuid4().hex}.sqlite"
        if db_path.exists():
            db_path.unlink()
        db_path = build_sqlite_from_csvs(db_path)
        counts = table_counts(db_path)
        self.assertEqual(sorted(counts.keys()), sorted(expected_tables()))
        self.assertEqual(counts["students"], 3091)
        self.assertEqual(counts["education_records"], 3091)
        self.assertEqual(counts["employment_records"], 3091)
        self.assertEqual(counts["scholarship_status"], 3091)


if __name__ == "__main__":
    unittest.main()
