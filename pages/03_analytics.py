import plotly.express as px
import streamlit as st

from src.analytics.metrics import top_counts
from src.ingestion.loaders import load_dataset


st.title("Analytics")
df = load_dataset()

dimension = st.selectbox(
    "เลือกมิติการวิเคราะห์",
    ["cohort", "province", "region", "current_country", "current_field_group", "employment_type"],
)
counts = top_counts(df, dimension, 20)
st.plotly_chart(px.bar(counts, x=dimension, y="count", title=f"จำนวนตาม {dimension}"), use_container_width=True)

if "income_monthly_est" in df:
    st.subheader("รายได้โดยประมาณ")
    st.plotly_chart(px.histogram(df, x="income_monthly_est", nbins=30, title="Income Monthly Estimate"), use_container_width=True)

st.subheader("ความสอดคล้องงาน")
cols = st.columns(2)
cols[0].dataframe(top_counts(df, "field_job_fit"), use_container_width=True)
cols[1].dataframe(top_counts(df, "local_fit"), use_container_width=True)
