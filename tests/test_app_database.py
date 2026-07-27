import unittest

from src.ingestion.data_access import database_health, database_status


class AppDatabaseTest(unittest.TestCase):
    def test_database_health(self):
        ok, message = database_health()
        self.assertTrue(ok, message)

    def test_database_status_has_required_tables(self):
        status = database_status()
        self.assertEqual(status["missing_tables"], [])
        self.assertIn("students", status["available_tables"])
        self.assertIn("audit_logs", status["available_tables"])


if __name__ == "__main__":
    unittest.main()
