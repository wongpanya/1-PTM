import unittest

import pandas as pd

from src.governance.privacy import (
    aggregate_csv_bytes,
    assert_aggregate_export,
    assert_no_forbidden_columns,
    assert_no_pii_text,
    find_pii_in_text,
    forbidden_columns_present,
    mask_pii_dataframe,
    suppress_small_groups,
)


class PrivacyTest(unittest.TestCase):
    def test_forbidden_columns_present(self):
        self.assertEqual(forbidden_columns_present(["odos_uid", "contact_phone"]), ["contact_phone"])

    def test_assert_no_forbidden_columns_raises(self):
        with self.assertRaises(ValueError):
            assert_no_forbidden_columns(["odos_uid", "contract_no"])

    def test_assert_no_forbidden_columns_passes(self):
        self.assertIsNone(assert_no_forbidden_columns(["odos_uid", "province"]))

    def test_mask_pii_dataframe_removes_forbidden_columns_and_patterns(self):
        df = pd.DataFrame({
            "province": ["A"],
            "contact_phone": ["081" + "234" + "5678"],
            "note": ["email " + "test" + "@example.com"],
            "count": [10],
        })
        masked = mask_pii_dataframe(df)
        self.assertNotIn("contact_phone", masked.columns)
        self.assertIn("[MASKED]", masked.iloc[0]["note"])

    def test_find_pii_in_text(self):
        findings = find_pii_in_text("โทร " + "081" + "234" + "5678" + " และ " + "test" + "@example.com")
        self.assertIn("thai_phone", findings)
        self.assertIn("email", findings)
        with self.assertRaises(ValueError):
            assert_no_pii_text("081" + "234" + "5678")

    def test_suppress_small_groups(self):
        df = pd.DataFrame({"province": ["A", "B"], "count": [3, 8]})
        result = suppress_small_groups(df, min_size=5)
        self.assertEqual(result.iloc[0]["province"], "ปกปิด")
        self.assertEqual(result.iloc[0]["count"], "<5")
        self.assertTrue(bool(result.iloc[0]["suppressed"]))

    def test_aggregate_export_requires_aggregate_column(self):
        with self.assertRaises(ValueError):
            assert_aggregate_export(pd.DataFrame({"province": ["A"]}))

    def test_aggregate_csv_bytes_masks_pii_like_values(self):
        df = pd.DataFrame({"province": ["081" + "234" + "5678"], "count": [10]})
        exported = aggregate_csv_bytes(df, "masked.csv", "Analyst").decode("utf-8-sig")
        self.assertIn("[MASKED]", exported)
        self.assertNotIn("081" + "234" + "5678", exported)

    def test_aggregate_csv_bytes_rejects_forbidden_columns(self):
        df = pd.DataFrame({"contact_phone": ["081" + "234" + "5678"], "count": [10]})
        with self.assertRaises(ValueError):
            aggregate_csv_bytes(df, "bad.csv", "Analyst")

    def test_aggregate_csv_bytes_passes_safe_aggregate(self):
        df = pd.DataFrame({"province": ["A"], "count": [10]})
        exported = aggregate_csv_bytes(df, "safe.csv", "Analyst")
        self.assertIn("province", exported.decode("utf-8-sig"))

    def test_aggregate_csv_bytes_denies_viewer(self):
        df = pd.DataFrame({"province": ["A"], "count": [10]})
        with self.assertRaises(PermissionError):
            aggregate_csv_bytes(df, "viewer.csv", "Viewer")


if __name__ == "__main__":
    unittest.main()
