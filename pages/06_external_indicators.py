from pathlib import Path

import pandas as pd
import streamlit as st


st.title("External Indicators")
st.caption("ข้อมูลเสริมรายปีสำหรับ ROI/SROI, workforce demand และ national impact")

template_path = Path("data/reference/annual_external_indicators_template.csv")
if template_path.exists():
    template = pd.read_csv(template_path)
    st.dataframe(template, use_container_width=True)
else:
    st.warning("ยังไม่พบ template ข้อมูลเสริมรายปี")

st.markdown(
    """
ข้อมูลเสริมใน Prototype เป็น template ก่อน เช่น:

- ต้นทุนทุนรายปี/ประเทศ/สาขา
- ตลาดแรงงานและความต้องการกำลังคน
- รายได้เฉลี่ยตามสาขา/พื้นที่
- GDP หรือตัวชี้วัดจังหวัด
- SDGs และ policy priority
"""
)
