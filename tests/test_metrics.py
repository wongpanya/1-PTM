import unittest

import pandas as pd

from src.analytics.metrics import overview_metrics, safe_rate, top_counts


class MetricsTest(unittest.TestCase):
    def test_safe_rate(self):
        self.assertEqual(safe_rate(1, 4), 25.0)
        self.assertEqual(safe_rate(1, 0), 0.0)

    def test_overview_metrics(self):
        df = pd.DataFrame({
            "odos_uid": ["a", "b"],
            "target_graduation_success": [1, 0],
            "target_scholarship_risk": [0, 1],
            "target_tracking_risk": [0, 1],
            "income_monthly_est": [10000, None],
            "gpa_numeric": [3.0, None],
        })
        metrics = overview_metrics(df)
        self.assertEqual(metrics["total_recipients"], 2)
        self.assertEqual(metrics["completion_rate"], 50.0)
        self.assertEqual(metrics["income_availability_rate"], 50.0)

    def test_top_counts(self):
        df = pd.DataFrame({"region": ["A", "A", None]})
        result = top_counts(df, "region")
        self.assertEqual(list(result.columns), ["region", "count"])
        self.assertEqual(result.iloc[0]["count"], 2)


if __name__ == "__main__":
    unittest.main()
