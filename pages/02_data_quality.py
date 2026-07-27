from pathlib import Path

import streamlit as st

from src.utils.config import PROJECT_ROOT
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Data Quality")
render_header("Data Quality", "โครงหน้าสำหรับรายงานคุณภาพข้อมูล")

render_database_status()

report_path = PROJECT_ROOT / "data/processed/reports/validation_report.md"
if report_path.exists():
    st.markdown(report_path.read_text(encoding="utf-8"))
else:
    st.warning("ยังไม่พบ validation report กรุณารัน `python scripts/validate_data.py`")

st.caption("Phase 3 แสดงเฉพาะรายงาน validation ระดับระบบ ยังไม่ลงรายละเอียด analytics")
