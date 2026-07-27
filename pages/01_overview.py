import plotly.express as px
import streamlit as st

from src.analytics.metrics import overview_metrics, top_counts
from src.ingestion.loaders import load_dataset


st.title("Overview")
df = load_dataset()
metrics = overview_metrics(df)

cols = st.columns(4)
cols[0].metric("ผู้รับทุนทั้งหมด", f"{metrics['total_recipients']:,}")
cols[1].metric("สำเร็จการศึกษา", f"{metrics['completion_count']:,}")
cols[2].metric("Completion Rate", f"{metrics['completion_rate']}%")
cols[3].metric("Scholarship Risk", f"{metrics['scholarship_risk_rate']}%")

left, right = st.columns(2)
with left:
    cohort = top_counts(df, "cohort")
    st.plotly_chart(px.bar(cohort, x="cohort", y="count", title="จำนวนผู้รับทุนตามรุ่น"), use_container_width=True)
with right:
    region = top_counts(df, "region")
    st.plotly_chart(px.bar(region, x="region", y="count", title="จำนวนผู้รับทุนตามภูมิภาค"), use_container_width=True)

st.dataframe(top_counts(df, "current_field_group", 15), use_container_width=True)
