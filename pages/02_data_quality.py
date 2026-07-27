import plotly.express as px
import streamlit as st

from src.ingestion.loaders import load_dataset
from src.validation.data_quality import completeness_table


st.title("Data Quality")
df = load_dataset()
quality = completeness_table(df)

st.metric("จำนวน Field", len(df.columns))
st.metric("จำนวน Records", len(df))

st.plotly_chart(
    px.bar(quality.head(20), x="completeness_pct", y="field", orientation="h", title="20 fields ที่ completeness ต่ำสุด"),
    use_container_width=True,
)
st.dataframe(quality, use_container_width=True)
