import streamlit as st

from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Policy Recommendation")
render_header("Policy Recommendation", "พื้นที่เตรียมสำหรับข้อเสนอเชิงนโยบาย")

render_database_status()

st.warning("Policy recommendation ยังไม่ถูก implement ใน Phase 3")
st.markdown(
    """
ฐานข้อมูลมีตาราง `policy_recommendations` สำหรับรองรับข้อเสนอใน Phase ถัดไป โดยข้อเสนอทั้งหมดต้องอ้างอิงข้อมูลที่มีและระบุข้อจำกัด
"""
)
