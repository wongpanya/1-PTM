import streamlit as st

from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Analytics")
render_header("Analytics", "พื้นที่เตรียมสำหรับ descriptive และ diagnostic analytics")

render_database_status()

st.warning("Analytics เชิงลึกยังไม่ถูก implement ใน Phase 3 ตามขอบเขตที่กำหนด")
st.markdown(
    """
สิ่งที่จะเพิ่มใน Phase ถัดไป:

- completion rate ตามรุ่น/พื้นที่/ประเทศ/สาขา
- employment distribution
- income availability
- field-job fit และ local fit
- filter และ drill-down แบบ aggregate
"""
)
