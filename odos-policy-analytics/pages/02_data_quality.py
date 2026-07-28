import plotly.express as px
import streamlit as st

from src.analytics.metrics import (
    data_quality_summary,
    group_readiness_summary,
    load_analytics_dataset,
    load_phase4_issues,
    metric_definitions,
    readiness_scorecard,
)
from src.governance.privacy import minimum_group_size
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Data Quality")
render_header(
    "Data Quality",
    "ตรวจความพร้อมของข้อมูลสำหรับ Dashboard, Analytics, Policy และ ML พร้อมเหตุผลระดับตัวแปร",
)
render_database_status()


@st.cache_data(show_spinner=False)
def _load_quality_inputs():
    return load_analytics_dataset(), load_phase4_issues(), metric_definitions()


df, issues_df, definitions = _load_quality_inputs()
quality = data_quality_summary(df, issues_df, definitions)
scorecard = readiness_scorecard(quality, definitions)
quality_config = definitions.get("data_quality", {})

score_columns = st.columns(4)
for column, item in zip(score_columns, scorecard.to_dict("records")):
    column.metric(
        f"{item['use_case']} Readiness",
        f"{item['readiness_score']:.1f}%",
        f"{item['ready_fields']}/{item['required_fields']} ฟิลด์ผ่านเกณฑ์",
    )

st.caption(
    "คะแนนคำนวณจาก Completeness 70% และ Validity 30% ตาม config/metrics.yaml "
    f"ผลรายกลุ่มแสดงเมื่อมีอย่างน้อย {minimum_group_size():,} ราย"
)
st.warning(
    "ML Readiness ในหน้านี้หมายถึงความพร้อมด้านข้อมูลเท่านั้น ไม่ใช่ค่าความแม่นยำของโมเดล "
    "และ target แบบ rule-based ยังต้องได้รับการรับรองจากผู้เชี่ยวชาญก่อนทดลอง ML"
)

readiness_tab, fields_tab, groups_tab, collection_tab = st.tabs(
    ["ภาพรวมความพร้อม", "เหตุผลรายตัวแปร", "เปรียบเทียบกลุ่มข้อมูล", "ข้อมูลที่ต้องเก็บเพิ่ม"]
)

with readiness_tab:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("คะแนนตามวัตถุประสงค์")
        st.plotly_chart(
            px.bar(
                scorecard,
                x="use_case",
                y="readiness_score",
                color="status",
                text_auto=".1f",
                range_y=[0, 100],
                labels={"use_case": "การใช้งาน", "readiness_score": "คะแนนความพร้อม"},
            ),
            width="stretch",
        )
    with right:
        status_counts = quality["readiness_status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        st.subheader("สถานะของตัวแปร")
        st.plotly_chart(
            px.bar(
                status_counts,
                x="count",
                y="status",
                orientation="h",
                text_auto=True,
                labels={"count": "จำนวนฟิลด์", "status": "สถานะ"},
            ),
            width="stretch",
        )

    left, right = st.columns(2)
    with left:
        missing = quality.sort_values("missing_count", ascending=False).head(20)
        st.subheader("ค่าว่างสูงสุด")
        st.plotly_chart(
            px.bar(
                missing,
                x="field",
                y="missing_rate",
                text_auto=".1f",
                labels={"field": "ตัวแปร", "missing_rate": "ค่าว่าง (%)"},
            ),
            width="stretch",
        )
    with right:
        issues = quality.sort_values("format_or_standard_issues", ascending=False).head(20)
        st.subheader("ปัญหารูปแบบและความสัมพันธ์")
        st.plotly_chart(
            px.bar(
                issues,
                x="field",
                y="format_or_standard_issues",
                text_auto=True,
                labels={"field": "ตัวแปร", "format_or_standard_issues": "จำนวน Issue"},
            ),
            width="stretch",
        )

with fields_tab:
    status_options = sorted(quality["readiness_status"].dropna().unique().tolist())
    selected_status = st.multiselect("กรองตามสถานะ", status_options)
    field_view = quality
    if selected_status:
        field_view = field_view[field_view["readiness_status"].isin(selected_status)]

    st.dataframe(
        field_view[
            [
                "field",
                "dtype",
                "expected_type",
                "completeness_rate",
                "validity_rate",
                "quality_score",
                "dashboard_ready",
                "analytics_ready",
                "policy_ready",
                "ml_feature",
                "ml_target",
                "aggregate_only",
                "ml_leakage_risk",
                "readiness_status",
                "cleaning_action",
                "cleaning_reason",
            ]
        ],
        width="stretch",
        hide_index=True,
    )
    st.caption(
        "ML feature และ ML target แยกจากกันชัดเจน; target และตัวแปรที่เกิดหลังผลลัพธ์จะไม่ถูกจัดเป็น feature"
    )

with groups_tab:
    group_labels = {
        "รุ่น": "cohort",
        "จังหวัด": "province",
        "ประเทศ": "current_country",
        "กลุ่มสาขา": "current_field_group",
    }
    selected_label = st.selectbox("มิติเปรียบเทียบ", list(group_labels))
    group_column = group_labels[selected_label]
    grouped_quality = group_readiness_summary(df, group_column, definitions)
    if grouped_quality.empty:
        st.info("ยังไม่มีข้อมูลกลุ่มที่ผ่านเกณฑ์การปกปิด")
    else:
        long_quality = grouped_quality.melt(
            id_vars=[group_column, "count"],
            value_vars=["dashboard_readiness", "policy_readiness", "ml_readiness"],
            var_name="readiness_type",
            value_name="score",
        )
        st.plotly_chart(
            px.bar(
                long_quality,
                x=group_column,
                y="score",
                color="readiness_type",
                barmode="group",
                range_y=[0, 100],
                labels={"score": "ความพร้อม (%)", group_column: selected_label},
            ),
            width="stretch",
        )
        st.dataframe(grouped_quality, width="stretch", hide_index=True)

with collection_tab:
    fields_to_collect = quality_config.get("fields_to_collect", [])
    st.subheader("ตัวแปรที่ควรเก็บเพิ่มในรอบถัดไป")
    st.dataframe(
        [{"field": field, "status": "ยังไม่มีในชุดข้อมูลปัจจุบัน"} for field in fields_to_collect],
        width="stretch",
        hide_index=True,
    )

    if not issues_df.empty and {"field", "code"}.issubset(issues_df.columns):
        st.subheader("Issue ที่ต้องแก้ไขในต้นทาง")
        issue_summary = (
            issues_df.groupby(["field", "code"], dropna=False)
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )
        st.dataframe(issue_summary, width="stretch", hide_index=True)

with st.expander("นิยาม Data Readiness"):
    st.markdown(
        """
- **Completeness:** สัดส่วนรายการที่ไม่เป็นค่าว่าง
- **Validity:** สัดส่วนที่ไม่พบปัญหารูปแบบ มาตรฐาน หรือความสัมพันธ์จาก Phase 4
- **Dashboard/Analytics/Policy Readiness:** คุณภาพของฟิลด์ที่ระบุสำหรับการใช้งานแต่ละแบบ
- **ML Readiness:** คุณภาพของ candidate features และ targets โดยแยกตัวแปรเสี่ยง data leakage ออกจาก feature
- **Aggregate only:** ใช้ได้เฉพาะผลรวมและต้องปกปิดกลุ่มขนาดเล็ก
"""
    )
