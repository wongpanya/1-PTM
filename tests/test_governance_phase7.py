import unittest

import pandas as pd

from src.utils.config import PROJECT_ROOT, load_yaml


class GovernancePhase7Test(unittest.TestCase):
    def test_external_indicator_template_columns(self):
        path = PROJECT_ROOT / "data/reference/annual_external_indicators_template.csv"
        df = pd.read_csv(path)
        self.assertEqual(
            list(df.columns),
            [
                "indicator_year",
                "indicator_type",
                "indicator_name",
                "geography_level",
                "geography_code",
                "field_code",
                "value",
                "unit",
                "source",
                "source_date",
                "update_date",
                "reliability_level",
                "note",
            ],
        )

    def test_viewer_role_cannot_import_or_export(self):
        config = load_yaml("config/governance.yaml")
        viewer = config["roles"]["Viewer"]
        self.assertFalse(viewer["can_import"])
        self.assertFalse(viewer["can_export_aggregate"])
        self.assertFalse(viewer["can_view_audit"])

    def test_governance_minimum_group_size(self):
        config = load_yaml("config/governance.yaml")
        self.assertGreaterEqual(int(config["minimum_group_size"]), 5)
        self.assertEqual(config["export"]["allowed_scope"], "aggregate_only")


if __name__ == "__main__":
    unittest.main()
