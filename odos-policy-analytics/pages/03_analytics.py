import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.exporting import build_dashboard_export
from src.analytics.metrics import (
    apply_filters,
    data_quality_summary,
    grouped_counts,
    income_box_summary,
    income_summary,
    load_analytics_dataset,
    load_phase4_issues,
    metric_definitions,
    outcome_by_group,
    overview_metrics,
    readiness_scorecard,
    remove_small_groups,
    top_counts,
)
from src.analytics.visualization import (
    aggregate_histogram,
    aggregate_proportions,
    completeness_matrix,
    funnel_summary,
    pathway_flows,
    question_options,
    readiness_for_fields,
    recommendation_for,
    visualization_config,
)
from src.governance.privacy import (
    aggregate_csv_bytes,
    append_export_log,
    minimum_group_size,
    role_can,
)
from src.utils.appearance_v1 import render_appearance
from src.utils.chart_surfaces_v2 import render_chart
from src.utils.metric_surfaces_v2 import render_metric_surface_styles
from src.utils.metrics_ui import render_metric_grid
from src.utils.selection_pipeline_v1 import render_selection_pipeline
from src.utils.ui import configure_page, render_database_status, render_header


configure_page("Analytics")
render_metric_surface_styles()
render_appearance()
render_header(
    "Analytics",
    "เลือกโหมดและคำถามที่ต้องการตอบ แล้วระบบจะแนะนำ Visualization ที่เหมาะกับข้อมูล",
)
render_database_status()


@st.cache_data(show_spinner=False)
def _load_data():
    return load_analytics_dataset(), load_phase4_issues()


df, issues_df = _load_data()
definitions = metric_definitions()
visual_config = visualization_config()
quality = data_quality_summary(df, issues_df, definitions)

with st.sidebar:
    st.subheader("ตัวกรอง")
    year_options = sorted(df["analysis_year"].dropna().astype(int).unique().tolist()) if "analysis_year" in df else []
    cohort_options = sorted(df["cohort"].dropna().unique().tolist()) if "cohort" in df else []
    country_options = sorted(df["current_country"].dropna().unique().tolist()) if "current_country" in df else []
    field_options = sorted(df["current_field_group"].dropna().unique().tolist()) if "current_field_group" in df else []
    province_options = sorted(df["province"].dropna().unique().tolist()) if "province" in df else []
    district_options = sorted(df["district"].dropna().unique().tolist()) if "district" in df else []
    region_options = sorted(df["region"].dropna().unique().tolist()) if "region" in df else []
    detailed_field_options = sorted(df["current_field"].dropna().unique().tolist()) if "current_field" in df else []
    university_options = (
        sorted(df["standardized_university_name"].dropna().unique().tolist())
        if "standardized_university_name" in df
        else []
    )
    employer_sector_options = (
        sorted(df["employer_sector_code"].dropna().unique().tolist())
        if "employer_sector_code" in df
        else []
    )
    analysis_years = st.multiselect("ปีวิเคราะห์", year_options)
    cohorts = st.multiselect("รุ่น", cohort_options)
    countries = st.multiselect("ประเทศ", country_options)
    field_groups = st.multiselect("กลุ่มสาขา", field_options)
    provinces = st.multiselect("จังหวัด", province_options)
    districts = st.multiselect("อำเภอ", district_options)
    regions = st.multiselect("ภูมิภาค", region_options)
    detailed_fields = st.multiselect("สาขารายละเอียด", detailed_field_options)
    universities = st.multiselect("มหาวิทยาลัยมาตรฐาน", university_options)
    employer_sectors = st.multiselect("รหัสภาคส่วนผู้จ้าง", employer_sector_options)
    st.divider()
    export_role = st.selectbox("สิทธิ์สำหรับ Export", ["Analyst", "Admin", "Viewer"], index=0)

filtered = apply_filters(
    df,
    cohorts=cohorts,
    provinces=provinces,
    countries=countries,
    field_groups=field_groups,
    analysis_years=analysis_years,
    districts=districts,
    regions=regions,
    fields=detailed_fields,
    universities=universities,
    employer_sectors=employer_sectors,
)
if filtered.empty:
    st.warning("ไม่พบข้อมูลตามชุดตัวกรองนี้ กรุณาลดเงื่อนไขหรือเลือกตัวกรองใหม่")
metrics = overview_metrics(filtered)
income = income_summary(filtered)

mode = st.radio(
    "Visualization Mode",
    visual_config.get("modes", []),
    index=visual_config.get("modes", []).index(visual_config.get("default_mode", "Guided Visualization")),
    horizontal=True,
)
st.caption(
    f"กำลังวิเคราะห์ {len(filtered):,} ระเบียน และแสดงผลรายกลุ่มเมื่อมีอย่างน้อย "
    f"{minimum_group_size():,} ราย | ปีวิเคราะห์ = ปีเริ่มศึกษา "
    "โดยใช้ปีคาดว่าจะสำเร็จและปีเริ่มงานเป็น fallback"
)


def _kpi_strip():
    st.markdown("#### :material/school: ผลลัพธ์การศึกษาและความเสี่ยง")
    st.caption("อ่านผลลัพธ์หลักและสัญญาณที่ควรติดตามก่อนลงรายละเอียดในกราฟ")
    render_metric_grid(
        [
            {
                "label": "สำเร็จการศึกษา",
                "value": f"{metrics['completion_rate']:.2f}%",
            },
            {
                "label": "ออกจากทุนกลางคัน",
                "value": f"{metrics['dropout_rate']:.2f}%",
                "delta": f"{metrics['dropout_count']:,} จาก {len(filtered):,} ราย",
            },
            {
                "label": "ยุติทุน",
                "value": f"{metrics['termination_rate']:.2f}%",
                "delta": f"{metrics['termination_count']:,} จาก {len(filtered):,} ราย",
            },
            {
                "label": "ความเสี่ยงทุน",
                "value": f"{metrics['scholarship_risk_rate']:.2f}%",
                "delta": f"{metrics['scholarship_risk_count']:,} จาก {len(filtered):,} ราย",
            },
        ]
    )

    st.markdown("#### :material/work: การมีงานทำและรายได้")
    render_metric_grid(
        [
            {
                "label": "มีงานทำ",
                "value": f"{metrics['employment_rate']:.2f}%",
            },
            {
                "label": "รายได้เฉลี่ย",
                "value": f"{income['average_income']:,.0f}",
                "delta": "บาทต่อเดือน",
            },
            {
                "label": "รายได้มัธยฐาน",
                "value": f"{income['median_income']:,.0f}",
                "delta": "บาทต่อเดือน",
            },
            {
                "label": "ข้อมูลรายได้",
                "value": f"{income['records_with_income']:,}",
                "delta": "ระเบียนพร้อมวิเคราะห์",
            },
        ]
    )

    st.markdown("#### :material/hub: ความสอดคล้องของงาน")
    render_metric_grid(
        [
            {
                "label": "งานตรงสาขา",
                "value": f"{metrics['field_job_fit_rate']:.2f}%",
                "delta": (
                    f"{metrics['field_job_fit_count']:,} จาก "
                    f"{metrics['field_job_fit_denominator']:,} ราย"
                ),
            },
            {
                "label": "งานสอดคล้องท้องถิ่น",
                "value": f"{metrics['local_fit_rate']:.2f}%",
                "delta": (
                    f"{metrics['local_fit_count']:,} จาก "
                    f"{metrics['local_fit_denominator']:,} ราย"
                ),
            },
        ]
    )


def _render_guidance(question_key: str, category_count: int | None = None):
    recommendation = recommendation_for(question_key, category_count, visual_config)
    readiness = readiness_for_fields(quality, recommendation.get("required_fields", []))
    left, middle, right = st.columns([2, 1, 1])
    left.info(
        f"แนะนำ **{recommendation.get('recommended_chart', '-')}**: "
        f"{recommendation.get('reason_th', '')}"
    )
    middle.metric("Data Readiness", f"{readiness['score']:.1f}%", readiness["status"])
    right.metric("ฟิลด์พร้อมใช้", f"{readiness['available']}/{readiness['required']}")
    if recommendation.get("compatibility_warning"):
        st.warning(recommendation["compatibility_warning"])
    st.caption(
        f"ทางเลือก: {', '.join(recommendation.get('alternatives', []))} | "
        f"ข้อควรระวัง: {recommendation.get('caution_th', '')}"
    )
    return recommendation


def _dimension_options(include_cohort=True):
    options = {
        "ปีวิเคราะห์": "analysis_year",
        "จังหวัด": "province",
        "อำเภอ": "district",
        "ประเทศ": "current_country",
        "กลุ่มสาขา": "current_field_group",
        "สาขารายละเอียด": "current_field",
        "มหาวิทยาลัย": "standardized_university_name",
        "ภาคส่วนผู้จ้าง": "employer_sector_code",
        "ภูมิภาค": "region",
    }
    if include_cohort:
        options = {"รุ่น": "cohort", **options}
    return options


def _category_options():
    return {
        "สถานะการศึกษา": "project_condition_status",
        "ประเภทการประกอบอาชีพ": "employment_type",
        "งานตรงสาขา": "field_job_fit",
        "ความสอดคล้องกับพื้นที่": "local_fit",
        "ประเทศ": "current_country",
        "กลุ่มสาขา": "current_field_group",
    }


def _target_options():
    return {
        "Completion Rate": "target_graduation_success",
        "Employment Rate": "target_employment_ready",
        "Dropout Rate": "target_dropout",
        "Termination Rate": "target_termination",
        "Scholarship Risk Rate": "target_scholarship_risk",
        "Tracking Gap Rate": "target_tracking_risk",
    }


def _dot_plot(dimension_label: str, dimension: str):
    counts = remove_small_groups(top_counts(filtered, dimension, 20)).sort_values("count")
    st.subheader(f"อันดับจำนวนผู้รับทุนตาม{dimension_label}")
    if counts.empty:
        st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        return
    render_chart(
        px.scatter(
            counts,
            x="count",
            y=dimension,
            size="count",
            labels={"count": "จำนวนผู้รับทุน", dimension: dimension_label},
        ),
        width="stretch",
    )


def _line_chart(group_label: str, group_column: str, target_label: str, target_column: str):
    outcomes = outcome_by_group(filtered, group_column)
    rate_column = {
        "target_graduation_success": "completion_rate",
        "target_employment_ready": "employment_rate",
        "target_dropout": "dropout_rate",
        "target_termination": "termination_rate",
        "target_scholarship_risk": "scholarship_risk_rate",
        "target_tracking_risk": "tracking_gap_rate",
    }[target_column]
    st.subheader(f"{target_label} ตาม{group_label}")
    if outcomes.empty:
        st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        return
    render_chart(
        px.line(
            outcomes.sort_values(group_column),
            x=group_column,
            y=rate_column,
            markers=True,
            labels={group_column: group_label, rate_column: f"{target_label} (%)"},
        ),
        width="stretch",
    )


def _box_plot(group_label: str, group_column: str):
    summary = income_box_summary(filtered, group_column).head(20)
    st.subheader(f"การกระจายรายได้ตาม{group_label}")
    if summary.empty:
        st.info("ไม่มีข้อมูลรายได้หรือไม่มีกลุ่มที่ผ่านเกณฑ์")
        return
    figure = go.Figure()
    for _, row in summary.iterrows():
        figure.add_trace(
            go.Box(
                name=str(row[group_column]),
                q1=[row["q1"]],
                median=[row["median"]],
                q3=[row["q3"]],
                lowerfence=[row["minimum"]],
                upperfence=[row["maximum"]],
                boxpoints=False,
            )
        )
    figure.update_layout(yaxis_title="รายได้ประมาณการต่อเดือน", showlegend=False)
    render_chart(figure, width="stretch")


def _bubble_plot(group_label: str, group_column: str):
    outcomes = outcome_by_group(filtered, group_column).head(30)
    st.subheader(f"ความสัมพันธ์ของผลลัพธ์ตาม{group_label}")
    if outcomes.empty:
        st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        return
    render_chart(
        px.scatter(
            outcomes,
            x="completion_rate",
            y="employment_rate",
            size="count",
            color="tracking_gap_rate",
            hover_name=group_column,
            labels={
                "completion_rate": "สำเร็จการศึกษา (%)",
                "employment_rate": "มีงานทำ (%)",
                "tracking_gap_rate": "ติดตามไม่ครบ (%)",
            },
        ),
        width="stretch",
    )


def _sankey(source_label: str, source_column: str, target_label: str, target_column: str):
    flows = pathway_flows(filtered, source_column, target_column)
    st.subheader(f"เส้นทางจาก{source_label}ไปยัง{target_label}")
    if flows.empty:
        st.info("ไม่มี flow ที่ผ่านเกณฑ์การปกปิด")
        return
    source_nodes = [f"S::{value}" for value in flows["source"].astype(str).unique()]
    target_nodes = [f"T::{value}" for value in flows["target"].astype(str).unique()]
    nodes = source_nodes + target_nodes
    node_index = {node: index for index, node in enumerate(nodes)}
    figure = go.Figure(
        go.Sankey(
            node={"label": [node.split("::", 1)[1] for node in nodes]},
            link={
                "source": [node_index[f"S::{value}"] for value in flows["source"].astype(str)],
                "target": [node_index[f"T::{value}"] for value in flows["target"].astype(str)],
                "value": flows["count"].tolist(),
            },
        )
    )
    render_chart(figure, width="stretch")


def _missingness_heatmap(group_label: str, group_column: str):
    fields = [
        "employment_type",
        "work_start_date",
        "income_monthly_est",
        "field_job_fit_level",
        "local_fit_level",
    ]
    matrix_rows = completeness_matrix(filtered, group_column, fields).head(30)
    st.subheader(f"ความครบถ้วนข้อมูลติดตามตาม{group_label}")
    if matrix_rows.empty:
        st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        return
    matrix = matrix_rows.set_index(group_column)[fields]
    render_chart(
        px.imshow(
            matrix,
            text_auto=".0f",
            aspect="auto",
            zmin=0,
            zmax=100,
            labels={"x": "ฟิลด์ติดตาม", "y": group_label, "color": "Completeness (%)"},
        ),
        width="stretch",
    )


def _dumbbell(group_label: str, group_column: str):
    outcomes = outcome_by_group(filtered, group_column).head(20).sort_values("completion_rate")
    st.subheader(f"ช่องว่าง Completion และ Employment ตาม{group_label}")
    if outcomes.empty:
        st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        return
    figure = go.Figure()
    for _, row in outcomes.iterrows():
        figure.add_trace(
            go.Scatter(
                x=[row["completion_rate"], row["employment_rate"]],
                y=[str(row[group_column]), str(row[group_column])],
                mode="lines",
                line={"color": "#A7B0B8", "width": 3},
                hoverinfo="skip",
                showlegend=False,
            )
        )
    figure.add_trace(
        go.Scatter(
            x=outcomes["completion_rate"],
            y=outcomes[group_column].astype(str),
            mode="markers",
            name="Completion",
            marker={"size": 11, "color": "#167D9A"},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=outcomes["employment_rate"],
            y=outcomes[group_column].astype(str),
            mode="markers",
            name="Employment",
            marker={"size": 11, "color": "#D65A45"},
        )
    )
    figure.update_layout(xaxis_title="อัตรา (%)", yaxis_title=group_label)
    render_chart(figure, width="stretch")


def _guided_view():
    options = question_options(visual_config)
    question_details = {
        "ranking": (
            ":material/leaderboard:",
            "เปรียบเทียบจำนวนและค้นหากลุ่มที่มีค่าสูงหรือต่ำ",
        ),
        "proportion": (
            ":material/donut_large:",
            "ดูองค์ประกอบและสัดส่วนของแต่ละกลุ่ม",
        ),
        "trend": (
            ":material/show_chart:",
            "ติดตามการเปลี่ยนแปลงของผลลัพธ์ตามช่วงเวลา",
        ),
        "distribution": (
            ":material/bar_chart:",
            "ตรวจการกระจาย ค่ากลาง และช่วงของข้อมูล",
        ),
        "relationship": (
            ":material/bubble_chart:",
            "สำรวจความสัมพันธ์ระหว่างผลลัพธ์หลายตัว",
        ),
        "pathway": (
            ":material/account_tree:",
            "ดูเส้นทางจากสถานะเริ่มต้นไปยังผลลัพธ์",
        ),
        "geography": (
            ":material/map:",
            "เปรียบเทียบผลลัพธ์ตามจังหวัดหรือพื้นที่",
        ),
        "missingness": (
            ":material/data_alert:",
            "ค้นหากลุ่มและฟิลด์ที่ยังติดตามข้อมูลไม่ครบ",
        ),
        "multi_kpi": (
            ":material/compare_arrows:",
            "เปรียบเทียบหลายตัวชี้วัดในมุมมองเดียว",
        ),
    }
    selected_label = render_selection_pipeline(
        "คำถามที่ต้องการวิเคราะห์",
        [
            {
                "id": key,
                "value": label,
                "title": label,
                "description": question_details[key][1],
                "meta": "ระบบเลือกกราฟที่เหมาะสมให้อัตโนมัติ",
                "icon": question_details[key][0],
            }
            for label, key in options.items()
        ],
        state_key="analytics_question_pipeline_v1",
        default=next(iter(options)),
        columns=3,
    )
    question_key = options[selected_label]

    if question_key == "ranking":
        dimensions = _dimension_options()
        dimension_label = st.selectbox("จัดอันดับตาม", list(dimensions), key="guided_rank_dimension")
        _render_guidance(question_key)
        _dot_plot(dimension_label, dimensions[dimension_label])

    elif question_key == "proportion":
        categories = _category_options()
        dimensions = _dimension_options()
        left, right = st.columns(2)
        category_label = left.selectbox("สัดส่วนของ", list(categories), key="guided_prop_category")
        group_label = right.selectbox("เปรียบเทียบตาม", list(dimensions), key="guided_prop_group")
        category_column = categories[category_label]
        group_column = dimensions[group_label]
        if category_column == group_column:
            st.info("หมวดหมู่และมิติเปรียบเทียบเป็นข้อมูลเดียวกัน จึงคำนวณเป็นสัดส่วนรวมโดยไม่แบ่งกลุ่มซ้ำ")
        category_count = int(filtered[category_column].dropna().nunique()) if category_column in filtered else 0
        _render_guidance(question_key, category_count)
        proportions = aggregate_proportions(filtered, category_column, group_column)
        if proportions.empty:
            st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        else:
            render_chart(
                px.bar(
                    proportions,
                    x=group_column,
                    y="percent",
                    color=category_column,
                    labels={group_column: group_label, "percent": "สัดส่วน (%)", category_column: category_label},
                ),
                width="stretch",
            )

    elif question_key == "trend":
        targets = _target_options()
        target_label = st.selectbox("KPI", list(targets), key="guided_trend_target")
        _render_guidance(question_key)
        _line_chart("รุ่น", "cohort", target_label, targets[target_label])

    elif question_key == "distribution":
        dimensions = _dimension_options()
        group_label = st.selectbox("เปรียบเทียบตาม", list(dimensions), key="guided_box_group")
        _render_guidance(question_key)
        _box_plot(group_label, dimensions[group_label])

    elif question_key == "relationship":
        dimensions = _dimension_options()
        group_label = st.selectbox("วิเคราะห์ความสัมพันธ์ตาม", list(dimensions), key="guided_bubble_group")
        _render_guidance(question_key)
        _bubble_plot(group_label, dimensions[group_label])

    elif question_key == "pathway":
        source_options = {"สถานะการศึกษา": "project_condition_status", "ประเทศ": "current_country", "กลุ่มสาขา": "current_field_group"}
        target_options = {"ประเภทการประกอบอาชีพ": "employment_type", "งานตรงสาขา": "field_job_fit", "ความสอดคล้องกับพื้นที่": "local_fit"}
        left, right = st.columns(2)
        source_label = left.selectbox("จุดเริ่มต้น", list(source_options), key="guided_flow_source")
        target_label = right.selectbox("ผลลัพธ์", list(target_options), key="guided_flow_target")
        _render_guidance(question_key)
        _sankey(source_label, source_options[source_label], target_label, target_options[target_label])

    elif question_key == "geography":
        _render_guidance(question_key)
        _bubble_plot("จังหวัด", "province")

    elif question_key == "missingness":
        dimensions = _dimension_options()
        group_label = st.selectbox("ตรวจข้อมูลขาดตาม", list(dimensions), key="guided_missing_group")
        _render_guidance(question_key)
        _missingness_heatmap(group_label, dimensions[group_label])

    elif question_key == "multi_kpi":
        dimensions = _dimension_options()
        group_label = st.selectbox("เปรียบเทียบ KPI ตาม", list(dimensions), key="guided_dumbbell_group")
        _render_guidance(question_key)
        _dumbbell(group_label, dimensions[group_label])


def _custom_view():
    chart_questions = {
        "Dot Plot": "ranking",
        "Treemap": "ranking",
        "100% Stacked Bar": "proportion",
        "Donut Chart": "proportion",
        "Line Chart": "trend",
        "Bubble Plot": "relationship",
        "Aggregate Box Plot": "distribution",
        "Aggregate Histogram": "distribution",
        "Heatmap": "missingness",
        "Sankey Diagram": "pathway",
        "Funnel Chart": "pathway",
        "Dumbbell Plot": "multi_kpi",
    }
    chart = st.selectbox("เลือก Visualization", list(chart_questions))
    question_key = chart_questions[chart]
    dimensions = _dimension_options()
    group_label = st.selectbox("มิติหลัก", list(dimensions), key="custom_group")
    group_column = dimensions[group_label]

    if chart == "Dot Plot":
        _render_guidance(question_key)
        _dot_plot(group_label, group_column)
    elif chart == "Treemap":
        _render_guidance(question_key)
        counts = remove_small_groups(top_counts(filtered, group_column, 30))
        if not counts.empty:
            render_chart(px.treemap(counts, path=[group_column], values="count"), width="stretch")
    elif chart in {"100% Stacked Bar", "Donut Chart"}:
        categories = _category_options()
        category_label = st.selectbox("หมวดหมู่", list(categories), key="custom_category")
        category_column = categories[category_label]
        if category_column == group_column:
            st.info("หมวดหมู่และมิติหลักเป็นข้อมูลเดียวกัน จึงคำนวณเป็นสัดส่วนรวมโดยไม่แบ่งกลุ่มซ้ำ")
        category_count = int(filtered[category_column].dropna().nunique()) if category_column in filtered else 0
        recommendation = _render_guidance(question_key, category_count)
        proportions = aggregate_proportions(filtered, category_column, None if chart == "Donut Chart" else group_column)
        if proportions.empty:
            st.info("ไม่มีกลุ่มที่ผ่านเกณฑ์การปกปิด")
        elif chart == "Donut Chart" and category_count <= 5:
            render_chart(px.pie(proportions, names=category_column, values="count", hole=0.45), width="stretch")
        else:
            if chart == "Donut Chart":
                st.warning(f"ระบบเปลี่ยนเป็น {recommendation['recommended_chart']} เนื่องจากมีหมวดหมู่มากเกินไป")
                proportions = aggregate_proportions(filtered, category_column, group_column)
            render_chart(
                px.bar(proportions, x=group_column, y="percent", color=category_column),
                width="stretch",
            )
    elif chart == "Line Chart":
        targets = _target_options()
        target_label = st.selectbox("KPI", list(targets), key="custom_line_target")
        _render_guidance(question_key)
        _line_chart(group_label, group_column, target_label, targets[target_label])
    elif chart == "Bubble Plot":
        _render_guidance(question_key)
        _bubble_plot(group_label, group_column)
    elif chart == "Aggregate Box Plot":
        _render_guidance(question_key)
        _box_plot(group_label, group_column)
    elif chart == "Aggregate Histogram":
        _render_guidance(question_key)
        histogram = aggregate_histogram(filtered, "income_monthly_est")
        if histogram.empty:
            st.info("ข้อมูลรายได้ไม่เพียงพอ")
        else:
            render_chart(px.bar(histogram, x="bin", y="count", labels={"bin": "ช่วงรายได้", "count": "จำนวน"}), width="stretch")
    elif chart == "Heatmap":
        _render_guidance(question_key)
        _missingness_heatmap(group_label, group_column)
    elif chart == "Sankey Diagram":
        targets = {"ประเภทการประกอบอาชีพ": "employment_type", "งานตรงสาขา": "field_job_fit", "ความสอดคล้องกับพื้นที่": "local_fit"}
        target_label = st.selectbox("ผลลัพธ์ปลายทาง", list(targets), key="custom_flow_target")
        _render_guidance(question_key)
        _sankey(group_label, group_column, target_label, targets[target_label])
    elif chart == "Funnel Chart":
        _render_guidance(question_key)
        funnel = funnel_summary(filtered)
        render_chart(px.funnel(funnel, x="count", y="stage", hover_data=["rate_from_total"]), width="stretch")
    elif chart == "Dumbbell Plot":
        _render_guidance(question_key)
        _dumbbell(group_label, group_column)


def _executive_view():
    _kpi_strip()
    st.subheader("สถานะผลลัพธ์เทียบเกณฑ์อ้างอิงของ Prototype")
    target = 80
    columns = st.columns(3)
    for column, label, value in zip(
        columns,
        ["Completion", "Employment", "Data Follow-up"],
        [
            metrics["completion_rate"],
            metrics["employment_rate"],
            100 - metrics["tracking_risk_rate"],
        ],
    ):
        figure = go.Figure(
            go.Indicator(
                mode="number+gauge",
                value=value,
                number={"suffix": "%"},
                title={"text": label},
                gauge={
                    "shape": "bullet",
                    "axis": {"range": [0, 100]},
                    "threshold": {"line": {"color": "#D65A45", "width": 3}, "value": target},
                    "bar": {"color": "#167D9A"},
                },
            )
        )
        figure.update_layout(height=170, margin={"l": 20, "r": 20, "t": 50, "b": 20})
        render_chart(figure, container=column, width="stretch")
    st.caption("เกณฑ์ 80% เป็นค่าอ้างอิงสำหรับสาธิต Visualization เท่านั้น ยังไม่ใช่เป้าหมายนโยบายที่รับรองแล้ว")

    left, right = st.columns([1, 1])
    with left:
        st.subheader("เส้นทางผลลัพธ์รวม")
        funnel = funnel_summary(filtered)
        render_chart(px.funnel(funnel, x="count", y="stage", hover_data=["rate_from_total"]), width="stretch")
    with right:
        _dumbbell("รุ่น", "cohort")


def _data_quality_view():
    scorecard = readiness_scorecard(quality, definitions)
    columns = st.columns(4)
    for column, item in zip(columns, scorecard.to_dict("records")):
        column.metric(item["use_case"], f"{item['readiness_score']:.1f}%", item["status"])
    dimensions = _dimension_options()
    group_label = st.selectbox("ตรวจความครบถ้วนตาม", list(dimensions), key="quality_mode_group")
    _render_guidance("missingness")
    _missingness_heatmap(group_label, dimensions[group_label])
    st.subheader("ฟิลด์ที่ต้องปรับปรุงก่อน Visualization")
    field_view = quality.sort_values(["quality_score", "missing_rate"]).head(20)
    st.dataframe(
        field_view[["field", "quality_score", "missing_rate", "readiness_status", "cleaning_reason"]],
        width="stretch",
        hide_index=True,
    )


if mode == "Executive View":
    _executive_view()
elif mode == "Guided Visualization":
    _guided_view()
elif mode == "Custom Visualization":
    _custom_view()
elif mode == "Data Quality View":
    _data_quality_view()

with st.expander("นิยาม KPI ที่ใช้ในหน้านี้"):
    rows = []
    for key in [
        "completion_rate",
        "dropout_rate",
        "termination_rate",
        "scholarship_risk_rate",
        "employment_rate",
        "income_distribution",
        "average_income",
        "median_income",
        "field_job_fit_rate",
        "local_development_fit_rate",
    ]:
        item = definitions["metrics"][key]
        rows.append({"kpi": item["label_th"], "formula": item["formula"], "definition": item["definition_th"]})
    st.dataframe(rows, width="stretch", hide_index=True)

st.subheader("Export รายงาน Aggregate ตาม Filter")
export_name = "analytics_filtered_aggregate.csv"
export_report = build_dashboard_export(filtered, "Analytics")
if role_can(export_role, "can_export_aggregate"):
    export_data = aggregate_csv_bytes(export_report, export_name, export_role, log_export=False)
    if st.download_button(
        "Export Analytics Aggregate CSV",
        data=export_data,
        file_name=export_name,
        mime="text/csv",
    ):
        append_export_log(export_name, export_role, len(export_report), list(export_report.columns))
else:
    st.caption("Viewer ไม่มีสิทธิ์ Export ข้อมูล")
