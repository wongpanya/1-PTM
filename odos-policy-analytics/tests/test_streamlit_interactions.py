import unittest

from streamlit.testing.v1 import AppTest


class StreamlitInteractionTest(unittest.TestCase):
    def test_individual_prediction_starts_with_guided_sample_flow(self):
        app = AppTest.from_file(
            "pages/04_risk_forecast.py",
            default_timeout=120,
        )
        app.session_state["risk_forecast_main_tabs_v1"] = (
            ":material/person_search: \u0e1e\u0e22\u0e32\u0e01\u0e23\u0e13\u0e4c"
            "\u0e23\u0e32\u0e22\u0e01\u0e23\u0e13\u0e35"
        )
        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.selectbox), 2)
        self.assertEqual(len(app.selectbox[1].options), 6)
        self.assertGreaterEqual(len(app.segmented_control), 2)
        self.assertEqual(len(app.error), 0)

    def test_overview_handles_filters_with_no_matching_rows(self):
        app = AppTest.from_file("pages/01_overview.py", default_timeout=90).run()
        app.multiselect[0].set_value([2004])
        app.multiselect[1].set_value([4])
        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("ไม่พบข้อมูลตามชุดตัวกรองนี้" in item.value for item in app.warning))

    def test_guided_proportion_handles_same_category_and_group(self):
        app = AppTest.from_file("pages/03_analytics.py", default_timeout=90).run()
        next(
            button
            for button in app.button
            if button.key == "analytics_question_pipeline_v1_proportion_action"
        ).click().run()
        app.selectbox[0].set_value("ประเทศ").run()
        app.selectbox[1].set_value("ประเทศ").run()

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("ไม่แบ่งกลุ่มซ้ำ" in item.value for item in app.info))

    def test_custom_proportion_handles_same_category_and_group(self):
        app = AppTest.from_file("pages/03_analytics.py", default_timeout=90).run()
        app.radio[0].set_value("Custom Visualization").run()
        app.selectbox[0].set_value("100% Stacked Bar").run()
        app.selectbox[1].set_value("ประเทศ").run()
        app.selectbox[2].set_value("ประเทศ").run()

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("ไม่แบ่งกลุ่มซ้ำ" in item.value for item in app.info))


if __name__ == "__main__":
    unittest.main()
