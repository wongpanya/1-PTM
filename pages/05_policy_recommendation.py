import streamlit as st

from src.ingestion.loaders import load_dataset
from src.policy.recommendations import field_recommendations


st.title("Policy Recommendation")
st.caption("ข้อเสนอเป็นการสนับสนุนการวิเคราะห์ ไม่ใช่คำสั่งจัดสรรทุนอัตโนมัติ")

df = load_dataset()
recommendations = field_recommendations(df)

st.subheader("สาขาที่มีสัญญาณเชิงนโยบายดี")
st.dataframe(recommendations, use_container_width=True)

st.info(
    "คะแนนนี้ใช้ completion, employment readiness และ field-job fit จากข้อมูลที่มีใน Prototype "
    "ยังไม่รวมต้นทุนทุน ตลาดแรงงาน GDP หรือ SDGs รายปี"
)
