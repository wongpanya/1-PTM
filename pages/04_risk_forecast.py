import plotly.express as px
import pandas as pd
import streamlit as st

from src.analytics.metrics import apply_filters, load_analytics_dataset
from src.risk.scoring import graduation_dataframe, score_dataframe, score_row
from src.utils.config import load_yaml
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Risk & Forecast")
render_header("Risk & Forecast", "Rule-based Risk Score และ Graduation Success รุ่น Prototype")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


df = _load_data()
rules = load_yaml("config/risk_rules.yaml")
risk_config = rules["risk_score"]

with st.sidebar:
    st.subheader("ตัวกรอง")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options)
    provinces = st.multiselect("จังหวัด", province_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)

filtered = apply_filters(df, cohorts=cohorts, provinces=provinces, field_groups=field_groups)
risk_df = score_dataframe(filtered)
graduation_df = graduation_dataframe(filtered)

cols = st.columns(4)
cols[0].metric("จำนวนที่ประเมิน", f"{len(risk_df):,}")
cols[1].metric("คะแนนเฉลี่ย", f"{risk_df['risk_score'].mean():.2f}" if not risk_df.empty else "0.00")
cols[2].metric("High Risk", f"{int((risk_df['risk_level'] == 'High').sum()):,}" if not risk_df.empty else "0")
cols[3].metric("Rule Version", rules["risk_score"]["rule_version"])

left, right = st.columns(2)
with left:
    st.subheader("Risk Level Distribution")
    level_counts = risk_df["risk_level"].value_counts().reset_index() if not risk_df.empty else None
    if level_counts is not None:
        level_counts.columns = ["risk_level", "count"]
        st.plotly_chart(px.bar(level_counts, x="risk_level", y="count", text_auto=True), width="stretch")

with right:
    st.subheader("Graduation Status")
    status_counts = graduation_df["graduation_status_label"].value_counts().reset_index() if not graduation_df.empty else None
    if status_counts is not None:
        status_counts.columns = ["graduation_status", "count"]
        st.plotly_chart(px.bar(status_counts, x="graduation_status", y="count", text_auto=True), width="stretch")

st.subheader("ปัจจัยที่ทำให้เกิดคะแนน")
component_rows = []
for _, record in filtered.iterrows():
    result = score_row(record.to_dict(), config=risk_config)
    for component in result["components"]:
        if component["triggered"]:
            component_rows.append({"component": component["component"], "score": component["score"], "explanation": component["explanation_th"]})
if component_rows:
    component_df = (
        pd.DataFrame(component_rows)
        .groupby(["component", "score", "explanation"])
        .size()
        .reset_index(name="triggered_count")
        .sort_values("triggered_count", ascending=False)
    )
    st.dataframe(component_df, width="stretch", hide_index=True)
else:
    st.info("ไม่พบปัจจัยความเสี่ยงในชุดที่กรอง")

st.subheader("ผลการวิเคราะห์ Risk แบบ Aggregate")
display_columns = ["cohort", "province", "current_country", "current_field_group", "risk_score", "risk_level", "triggered_components", "rule_version", "calculated_at"]
st.dataframe(risk_df[display_columns].head(200), width="stretch", hide_index=True)

with st.expander("Rule-based Graduation Success และ ML Roadmap"):
    st.dataframe(graduation_df.drop(columns=["odos_uid"], errors="ignore").head(200), width="stretch", hide_index=True)
    st.markdown("**Explainable ML ยังไม่เปิดใช้ใน Prototype รอบนี้**")
    st.dataframe(
        [{"requirement": item} for item in rules["graduation_success"]["ml_readiness"]["requirements"]],
        width="stretch",
        hide_index=True,
    )

with st.expander("ข้อจำกัดของผลลัพธ์และสถานะการรับรอง"):
    st.write(f"Risk approval: {rules['risk_score']['expert_approval_status']}")
    st.write(f"Graduation rule version: {rules['graduation_success']['rule_version']}")
    st.dataframe([{"limitation": item} for item in rules["risk_score"]["limitations_th"]], width="stretch", hide_index=True)
