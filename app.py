import streamlit as st

from src.analytics.metrics import overview_metrics
from src.ingestion.loaders import load_dataset


st.set_page_config(
    page_title="ODOS Policy Analytics",
    page_icon="ODOS",
    layout="wide",
)

st.title("ODOS Policy Analytics Prototype")
st.caption("ระบบต้นแบบเพื่อสาธิตการวิเคราะห์ข้อมูลผู้รับทุนเชิงนโยบาย")

df = load_dataset()
metrics = overview_metrics(df)

st.info(
    "Prototype นี้เป็นระบบสนับสนุนการวิเคราะห์เชิงนโยบาย "
    "ไม่ใช่ระบบตัดสินใจจัดสรรทุนอัตโนมัติ และแสดงผลแบบ aggregate เป็นหลัก"
)

cols = st.columns(4)
cols[0].metric("จำนวนผู้รับทุน", f"{metrics['total_recipients']:,}")
cols[1].metric("อัตราสำเร็จการศึกษา", f"{metrics['completion_rate']}%")
cols[2].metric("อัตราความเสี่ยงทุน", f"{metrics['scholarship_risk_rate']}%")
cols[3].metric("ข้อมูลรายได้ที่ใช้ได้", f"{metrics['income_availability_rate']}%")

st.subheader("หน้าในระบบ")
st.markdown(
    """
- Overview
- Data Quality
- Analytics
- Risk & Forecast
- Policy Recommendation
- External Indicators
- Governance
"""
)
