import unittest

from src.governance.privacy import assert_no_forbidden_columns, forbidden_columns_present


class PrivacyTest(unittest.TestCase):
    def test_forbidden_columns_present(self):
        self.assertEqual(forbidden_columns_present(["odos_uid", "contact_phone"]), ["contact_phone"])

    def test_assert_no_forbidden_columns_raises(self):
        with self.assertRaises(ValueError):
            assert_no_forbidden_columns(["odos_uid", "contract_no"])

    def test_assert_no_forbidden_columns_passes(self):
        self.assertIsNone(assert_no_forbidden_columns(["odos_uid", "province"]))


if __name__ == "__main__":
    unittest.main()
