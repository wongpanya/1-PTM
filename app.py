import streamlit as st

from src.ingestion.data_access import scalar
from src.utils.config import load_yaml
from src.utils.ui import configure_page, render_database_status, render_header, render_table_status


configure_page("Home")

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
4. Risk & Forecast
5. Policy Recommendation
6. External Indicators
7. Governance
"""
)

st.warning("Prototype นี้ใช้เพื่อสาธิตการวิเคราะห์เชิงนโยบาย ผล Risk และ Recommendation ต้องให้ผู้เชี่ยวชาญตรวจสอบก่อนนำไปใช้จริง")
