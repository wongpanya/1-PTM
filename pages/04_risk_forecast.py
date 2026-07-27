import streamlit as st

from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Risk & Forecast")
render_header("Risk & Forecast", "พื้นที่เตรียมสำหรับคะแนนความเสี่ยงและการพยากรณ์")

render_database_status()

st.warning("Risk scoring และ forecast ยังไม่ถูกเปิดใช้งานใน Phase 3")
st.markdown(
    """
ฐานข้อมูลมีตาราง `risk_scores` สำหรับรองรับผลลัพธ์ใน Phase ถัดไป โดยทุกคะแนนต้องมี component scores และคำอธิบาย
"""
)
