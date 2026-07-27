import streamlit as st

from src.ingestion.data_access import scalar
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Overview")
render_header("Overview", "ภาพรวมโครงระบบและฐานข้อมูลกลาง")

if render_database_status():
    cols = st.columns(4)
    cols[0].metric("students", f"{int(scalar('SELECT COUNT(*) FROM students') or 0):,}")
    cols[1].metric("education_records", f"{int(scalar('SELECT COUNT(*) FROM education_records') or 0):,}")
    cols[2].metric("employment_records", f"{int(scalar('SELECT COUNT(*) FROM employment_records') or 0):,}")
    cols[3].metric("external_indicators", f"{int(scalar('SELECT COUNT(*) FROM external_indicators') or 0):,}")

st.markdown(
    """
หน้านี้จะใช้เป็น dashboard ภาพรวมใน Phase ถัดไป ขณะนี้แสดงเฉพาะสถานะฐานข้อมูลกลางและจำนวนระเบียนรวมแบบไม่เปิดเผยข้อมูลรายบุคคล
"""
)
