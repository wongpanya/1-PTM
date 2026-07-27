import pandas as pd
import streamlit as st

from src.governance.privacy import FORBIDDEN_COLUMNS, forbidden_columns_present
from src.ingestion.loaders import load_dataset


st.title("Governance")
st.caption("แนวทางธรรมาภิบาลข้อมูลสำหรับ Prototype")

df = load_dataset()
present = forbidden_columns_present(df.columns)

if present:
    st.error(f"พบคอลัมน์ต้องห้าม: {', '.join(present)}")
else:
    st.success("ไม่พบ forbidden direct PII columns ใน sample dataset")

st.subheader("ข้อมูลที่ห้ามแสดงหรือ export")
st.dataframe(pd.DataFrame({"forbidden_column": sorted(FORBIDDEN_COLUMNS)}), use_container_width=True)

st.subheader("Role Concept")
st.table(pd.DataFrame([
    {"role": "Admin", "scope": "จัดการข้อมูลและ config ในสภาพแวดล้อมควบคุม"},
    {"role": "Analyst", "scope": "ดู analytics, risk, recommendation แบบ aggregate"},
    {"role": "Viewer", "scope": "ดู dashboard สรุประดับผู้บริหาร"},
]))
