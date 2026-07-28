import unittest

from src.cleaning.rules import (
    fit_level,
    government_preference_flag,
    normalize_text,
    parse_income_monthly_estimate,
    parse_iso_date,
    years_between,
)


class CleaningRulesTest(unittest.TestCase):
    def test_normalize_text_handles_errors_and_spaces(self):
        self.assertEqual(normalize_text("  A\n B  "), "A B")
        self.assertIsNone(normalize_text("#NUM!"))
        self.assertIsNone(normalize_text(""))

    def test_fit_level_mapping(self):
        self.assertEqual(fit_level("ไม่สอดคล้อง"), 0)
        self.assertEqual(fit_level("สอดคล้องน้อย"), 1)
        self.assertEqual(fit_level("สอดคล้องปานกลาง"), 2)
        self.assertEqual(fit_level("สอดคล้องมาก"), 3)
        self.assertIsNone(fit_level("N/A"))

    def test_government_preference_flag(self):
        self.assertEqual(government_preference_flag("ต้องการ"), 1)
        self.assertEqual(government_preference_flag("ไม่ต้องการ"), 0)
        self.assertIsNone(government_preference_flag("N/A"))

    def test_parse_income_monthly_estimate(self):
        self.assertEqual(parse_income_monthly_estimate("20,001 - 30,000 บาท"), 25000.5)
        self.assertEqual(parse_income_monthly_estimate("80,001 บาทขึ้นไป"), 80001)
        self.assertIsNone(parse_income_monthly_estimate("#NUM!"))

    def test_parse_iso_date_and_duration(self):
        self.assertEqual(parse_iso_date("2020-01-05"), "2020-01-05")
        self.assertEqual(years_between("2020-01-01", "2021-01-01"), 1.0)
        self.assertIsNone(years_between("2021-01-01", "2020-01-01"))


if __name__ == "__main__":
    unittest.main()
