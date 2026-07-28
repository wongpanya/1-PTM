import streamlit as st

from src.analytics.metrics import apply_filters, load_analytics_dataset
from src.policy.recommendations import area_recommendations, field_recommendations, recommendation_summary
from src.utils.config import load_yaml
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Policy Recommendation")
render_header("Policy Recommendation", "Ranking ที่ตรวจสอบย้อนกลับได้จากสูตรและน้ำหนักในระบบ")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


df = _load_data()
config = load_yaml("config/policy_recommendation.yaml")["policy_recommendation"]

with st.sidebar:
    st.subheader("ตัวกรอง")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options)
    provinces = st.multiselect("จังหวัด", province_options)
    min_records = st.number_input("จำนวนข้อมูลขั้นต่ำต่อกลุ่ม", min_value=1, max_value=500, value=int(config["minimum_records"]))

    st.subheader("น้ำหนัก Field Recommendation")
    field_weights = {}
    for key, value in config["field_recommendation"]["weights"].items():
        field_weights[key] = st.slider(key, 0, 100, int(value))

    st.subheader("น้ำหนัก Area Allocation")
    area_weights = {}
    for key, value in config["area_based_allocation"]["weights"].items():
        area_weights[key] = st.slider(key, 0, 100, int(value))

filtered = apply_filters(df, cohorts=cohorts, provinces=provinces)
summary = recommendation_summary(filtered)

cols = st.columns(4)
cols[0].metric("ข้อมูลที่ใช้", f"{summary['records']:,}")
cols[1].metric("Completion Rate", f"{summary['completion_rate']:.2f}%")
cols[2].metric("Employment Rate", f"{summary['employment_rate']:.2f}%")
cols[3].metric("Rule Version", config["rule_version"])

st.info("Prototype นี้ไม่สร้างข้อเสนอจากข้อความ AI ลอย ๆ ทุก ranking มาจากสูตร น้ำหนัก และคอลัมน์หลักฐานที่แสดงในหน้านี้")

field_df = field_recommendations(filtered, min_records=int(min_records), weights=field_weights)
area_df = area_recommendations(filtered, min_records=int(min_records), weights=area_weights)

st.subheader("ผลการวิเคราะห์: Field Recommendation Ranking")
field_columns = [
    "current_field_group",
    "records",
    "completion_rate",
    "employment_rate",
    "field_job_fit",
    "income_outcome",
    "local_development_fit",
    "data_completeness",
    "policy_score",
    "analysis_result",
    "formula",
    "weights",
]
if not field_df.empty:
    st.dataframe(field_df[field_columns], width="stretch", hide_index=True)
else:
    st.warning("ไม่มี field group ที่มีจำนวนข้อมูลถึงเกณฑ์ขั้นต่ำ")

st.subheader("ข้อเสนอเชิงนโยบาย: Field Recommendation")
if not field_df.empty:
    st.dataframe(
        field_df[["current_field_group", "policy_score", "policy_recommendation", "limitations_th", "rule_version"]].head(20),
        width="stretch",
        hide_index=True,
    )

st.subheader("ผลการวิเคราะห์: Area-based Allocation Ranking")
area_columns = [
    "province",
    "records",
    "area_success",
    "local_return_fit",
    "external_inequality_need",
    "workforce_demand",
    "external_indicator_status",
    "available_weight",
    "policy_score",
    "analysis_result",
    "formula",
    "weights",
]
if not area_df.empty:
    if "external_indicator_status" in area_df.columns and (area_df["external_indicator_status"] == "not_available_in_prototype").any():
        st.warning("ยังไม่มีตัวชี้วัดภายนอกที่ตรวจสอบแล้วในระดับพื้นที่ จึงไม่นำค่านี้มาคำนวณคะแนน Area Ranking")
    visible_area_columns = [column for column in area_columns if column in area_df.columns]
    st.dataframe(area_df[visible_area_columns], width="stretch", hide_index=True)
else:
    st.warning("ไม่มีพื้นที่ที่มีจำนวนข้อมูลถึงเกณฑ์ขั้นต่ำ")

st.subheader("ข้อเสนอเชิงนโยบาย: Area-based Allocation")
if not area_df.empty:
    st.dataframe(
        area_df[["province", "policy_score", "policy_recommendation", "limitations_th", "rule_version"]].head(20),
        width="stretch",
        hide_index=True,
    )

with st.expander("หลักฐาน สูตร น้ำหนัก และข้อจำกัด"):
    st.write(f"Expert approval: {config['expert_approval_status']}")
    st.write("Field evidence columns")
    st.dataframe([{"column": col} for col in config["field_recommendation"]["evidence_columns"]], width="stretch", hide_index=True)
    st.write("Area evidence columns")
    st.dataframe([{"column": col} for col in config["area_based_allocation"]["evidence_columns"]], width="stretch", hide_index=True)
    st.write("Limitations")
    st.dataframe([{"limitation": item} for item in config["limitations_th"]], width="stretch", hide_index=True)
