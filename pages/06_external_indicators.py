import streamlit as st

from src.ingestion.data_access import scalar
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("External Indicators")
render_header("External Indicators", "พื้นที่เตรียมข้อมูลเสริมรายปี")

if render_database_status():
    count = scalar("SELECT COUNT(*) FROM external_indicators") or 0
    st.metric("รายการ template ข้อมูลเสริมรายปี", f"{int(count):,}")

st.markdown(
    """
ข้อมูลเสริมรายปีจะใช้รองรับ:

- ต้นทุนทุน
- ตลาดแรงงาน
- รายได้เฉลี่ย
- GDP/ตัวชี้วัดจังหวัด
- SDGs และ policy priority
"""
)
