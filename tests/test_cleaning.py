import unittest

from src.cleaning.rules import fit_level, government_preference_flag, normalize_text


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


if __name__ == "__main__":
    unittest.main()
