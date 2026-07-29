import streamlit as st

from src.ingestion.data_access import scalar
from src.utils.appearance_v1 import render_appearance
from src.utils.config import load_yaml
from src.utils.metric_surfaces_v2 import render_metric_surface_styles
from src.utils.ui import configure_page, render_database_status, render_header, render_table_status


def prototype_application() -> None:
    configure_page("Prototype Application")
    render_metric_surface_styles()
    render_appearance()

    config = load_yaml("config/app_config.yaml")
    render_header(config["app"]["title"], config["app"]["subtitle_th"])

    if render_database_status():
        total_students = scalar("SELECT COUNT(*) FROM students") or 0
        imported_rows = scalar("SELECT COALESCE(SUM(rows_imported), 0) FROM data_import_log") or 0
        audit_events = scalar("SELECT COUNT(*) FROM audit_logs") or 0

        cols = st.columns(3)
        cols[0].metric("จำนวนระเบียนผู้รับทุนในฐานกลาง", f"{int(total_students):,}")
        cols[1].metric("จำนวนระเบียนที่ import", f"{int(imported_rows):,}")
        cols[2].metric("จำนวน audit events", f"{int(audit_events):,}")

    render_table_status()

    st.subheader("Navigation")
    st.markdown(
        """
ใช้เมนูด้านซ้ายเพื่อเปิด 7 หน้าหลัก:

1. Overview
2. Data Quality
3. Analytics
4. Risk Forecast
5. Policy Recommendation
6. External Indicators
7. Governance
"""
    )

    st.warning(
        "Prototype นี้ใช้เพื่อสาธิตการวิเคราะห์เชิงนโยบาย ผล Risk และ Recommendation "
        "ต้องให้ผู้เชี่ยวชาญตรวจสอบก่อนนำไปใช้จริง"
    )


pages = [
    st.Page(prototype_application, title="Prototype Application", default=True),
    st.Page("pages/01_overview.py", title="Overview", url_path="overview"),
    st.Page("pages/02_data_quality.py", title="Data Quality", url_path="data_quality"),
    st.Page("pages/03_analytics.py", title="Analytics", url_path="analytics"),
    st.Page("pages/04_risk_forecast.py", title="Risk Forecast", url_path="risk_forecast"),
    st.Page("pages/05_policy_recommendation.py", title="Policy Recommendation", url_path="policy_recommendation"),
    st.Page("pages/06_external_indicators.py", title="External Indicators", url_path="external_indicators"),
    st.Page("pages/07_governance.py", title="Governance", url_path="governance"),
    st.Page("pages/08_help_documentation.py", title="Help Documentation", url_path="help_documentation"),
]

selected_page = st.navigation(pages)
selected_page.run()
