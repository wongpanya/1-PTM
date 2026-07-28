import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.metrics import (
    apply_filters,
    grouped_counts,
    income_box_summary,
    income_summary,
    load_analytics_dataset,
    metric_definitions,
    overview_metrics,
    rate_by_group,
    remove_small_groups,
    top_counts,
)
from src.governance.privacy import minimum_group_size
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Analytics")
render_header("Analytics", "KPI และการเปรียบเทียบผลลัพธ์จากข้อมูลที่มีอยู่ใน Prototype")
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset()


df = _load_data()
definitions = metric_definitions()

with st.sidebar:
    st.subheader("ตัวกรอง")
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    country_options = sorted(df["current_country"].dropna().unique().tolist()) if "current_country" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    provinces_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    cohorts = st.multiselect("รุ่น", cohort_options)
    countries = st.multiselect("ประเทศ", country_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)
    provinces = st.multiselect("จังหวัด", provinces_options)
    chart_view = st.selectbox(
        "รูปแบบ Analytics Dashboard",
        [
            "เปรียบเทียบ KPI",
            "สัดส่วน",
            "การกระจายรายได้",
            "แนวโน้มตามรุ่น",
            "Heatmap ประเทศและสาขา",
        ],
    )

filtered = apply_filters(df, cohorts, provinces, countries, field_groups)
metrics = overview_metrics(filtered)
income = income_summary(filtered)

st.caption(f"ผลรายกลุ่มจะแสดงเฉพาะกลุ่มที่มีอย่างน้อย {minimum_group_size():,} ราย เพื่อคุ้มครองข้อมูล")

cols = st.columns(5)
cols[0].metric("Completion Rate", f"{metrics['completion_rate']:.2f}%")
cols[1].metric("Dropout Rate", f"{metrics['scholarship_risk_rate']:.2f}%")
cols[2].metric("Employment Rate", f"{metrics['employment_rate']:.2f}%")
cols[3].metric("Median Income", f"{income['median_income']:,.0f}")
cols[4].metric("Income Records", f"{income['records_with_income']:,}")

if chart_view == "เปรียบเทียบ KPI":
    group_options = {
        "รุ่น": "cohort",
        "ประเทศ": "current_country",
        "กลุ่มสาขา": "current_field_group",
        "จังหวัด": "province",
    }
    target_options = {
        "Completion Rate": "target_graduation_success",
        "Employment Rate": "target_employment_ready",
        "Dropout/Risk Rate": "target_scholarship_risk",
    }
    left, right = st.columns(2)
    with left:
        group_label = st.selectbox("จัดกลุ่มตาม", list(group_options), key="bar_group")
    with right:
        target_label = st.selectbox("KPI ที่เปรียบเทียบ", list(target_options), key="bar_target")
    comparison = remove_small_groups(
        rate_by_group(filtered, group_options[group_label], target_options[target_label])
    ).head(20)
    st.subheader(f"{target_label} ตาม{group_label}")
    if comparison.empty:
        st.info("ไม่มีผลลัพธ์รายกลุ่มที่ผ่านเกณฑ์การปกปิดข้อมูล")
    else:
        st.plotly_chart(
            px.bar(comparison, x=group_options[group_label], y="rate", text_auto=True, labels={"rate": "%", group_options[group_label]: group_label}),
            width="stretch",
        )

elif chart_view == "สัดส่วน":
    category_options = {
        "สถานะการศึกษา": "current_status",
        "สถานะความสอดคล้องงาน": "field_job_fit",
        "ความสอดคล้องกับท้องถิ่น": "local_fit",
        "ประเทศ": "current_country",
        "กลุ่มสาขา": "current_field_group",
    }
    category_label = st.selectbox("แสดงสัดส่วนตาม", list(category_options), key="donut_category")
    category_column = category_options[category_label]
    proportions = remove_small_groups(top_counts(filtered, category_column, 100))
    st.subheader(f"สัดส่วนตาม{category_label}")
    if proportions.empty:
        st.info("ไม่มีผลลัพธ์รายกลุ่มที่ผ่านเกณฑ์การปกปิดข้อมูล")
    else:
        st.plotly_chart(
            px.pie(proportions, names=category_column, values="count", hole=0.45),
            width="stretch",
        )

elif chart_view == "การกระจายรายได้":
    group_options = {"กลุ่มสาขา": "current_field_group", "ประเทศ": "current_country", "จังหวัด": "province"}
    group_label = st.selectbox("เปรียบเทียบรายได้ตาม", list(group_options), key="box_group")
    group_column = group_options[group_label]
    box_summary = income_box_summary(filtered, group_column)
    st.subheader(f"Box Plot รายได้รายเดือนตาม{group_label}")
    if box_summary.empty:
        st.info("ไม่มีข้อมูลรายได้หรือไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิดข้อมูล")
    else:
        figure = go.Figure()
        for _, row in box_summary.head(20).iterrows():
            figure.add_trace(
                go.Box(
                    name=str(row[group_column]),
                    q1=[row["q1"]],
                    median=[row["median"]],
                    q3=[row["q3"]],
                    lowerfence=[row["minimum"]],
                    upperfence=[row["maximum"]],
                    boxpoints=False,
                    hovertemplate="กลุ่ม: %{x}<br>Q1: %{q1:,.0f}<br>Median: %{median:,.0f}<br>Q3: %{q3:,.0f}<extra></extra>",
                )
            )
        figure.update_layout(yaxis_title="รายได้ต่อเดือนโดยประมาณ", showlegend=False)
        st.plotly_chart(figure, width="stretch")
        st.dataframe(box_summary.head(20), width="stretch", hide_index=True)

elif chart_view == "แนวโน้มตามรุ่น":
    rate_frames = []
    for metric_label, target_column in {
        "Completion Rate": "target_graduation_success",
        "Employment Rate": "target_employment_ready",
        "Dropout/Risk Rate": "target_scholarship_risk",
    }.items():
        rates = remove_small_groups(rate_by_group(filtered, "cohort", target_column))
        rates["metric"] = metric_label
        rate_frames.append(rates)
    trend = pd.concat(rate_frames, ignore_index=True)
    st.subheader("แนวโน้มผลลัพธ์ตามรุ่น")
    if trend.empty:
        st.info("ไม่มีผลลัพธ์รายรุ่นที่ผ่านเกณฑ์การปกปิดข้อมูล")
    else:
        st.plotly_chart(
            px.line(trend, x="cohort", y="rate", color="metric", markers=True, labels={"rate": "%", "cohort": "รุ่น", "metric": "KPI"}),
            width="stretch",
        )
        st.caption("กราฟนี้เปรียบเทียบผลลัพธ์ระหว่างรุ่น ไม่ใช่อนุกรมเวลาติดตามรายบุคคล")

elif chart_view == "Heatmap ประเทศและสาขา":
    heatmap_rows = remove_small_groups(grouped_counts(filtered, ["current_country", "current_field_group"], 1000))
    st.subheader("Heatmap จำนวนผู้รับทุนตามประเทศและกลุ่มสาขา")
    if heatmap_rows.empty:
        st.info("ไม่มีผลลัพธ์รายกลุ่มที่ผ่านเกณฑ์การปกปิดข้อมูล")
    else:
        heatmap = heatmap_rows.pivot(index="current_country", columns="current_field_group", values="count")
        st.plotly_chart(
            px.imshow(heatmap, text_auto=True, aspect="auto", labels={"x": "กลุ่มสาขา", "y": "ประเทศ", "color": "จำนวน"}),
            width="stretch",
        )
        st.caption("ช่องว่างอาจหมายถึงไม่พบข้อมูลหรือกลุ่มมีจำนวนน้อยกว่าเกณฑ์และถูกปกปิด")

with st.expander("นิยาม KPI ที่ใช้ในหน้านี้"):
    rows = []
    for key in [
        "completion_rate",
        "dropout_rate",
        "employment_rate",
        "income_distribution",
        "field_job_fit_rate",
        "local_development_fit_rate",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)
