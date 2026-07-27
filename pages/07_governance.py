from pathlib import Path
import json

import pandas as pd
import streamlit as st

from src.analytics.metrics import grouped_counts, load_analytics_dataset
from src.governance.audit import DEFAULT_AUDIT_LOG
from src.governance.privacy import (
    FORBIDDEN_COLUMNS,
    aggregate_csv_bytes,
    find_pii_in_text,
    mask_pii_dataframe,
    minimum_group_size,
    suppress_small_groups,
)
from src.ingestion.data_access import scalar
from src.utils.config import PROJECT_ROOT, load_yaml
from src.utils.ui import configure_page, render_database_status, render_header


def _read_jsonl(path: str | Path) -> list[dict]:
    log_path = Path(path)
    if not log_path.is_absolute():
        log_path = PROJECT_ROOT / log_path
    if not log_path.exists():
        return []
    rows = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line})
    return rows


configure_page("Governance")
render_header("Governance", "ธรรมาภิบาลข้อมูล Privacy Controls และ Audit Trail สำหรับ Prototype")

governance = load_yaml("config/governance.yaml")
roles = governance["roles"]

with st.sidebar:
    role = st.selectbox("Role Mockup", list(roles.keys()), index=2)
    st.caption(roles[role]["description_th"])

st.info(governance["prototype_notice_th"])

if render_database_status():
    audit_count = scalar("SELECT COUNT(*) FROM audit_logs") or 0
    import_count = scalar("SELECT COUNT(*) FROM data_import_log") or 0
    cols = st.columns(3)
    cols[0].metric("Database audit logs", f"{int(audit_count):,}")
    cols[1].metric("Database import logs", f"{int(import_count):,}")
    cols[2].metric("Minimum Group Size", minimum_group_size())

st.subheader("Role Matrix")
role_rows = [{"role": name, **settings} for name, settings in roles.items()]
st.dataframe(role_rows, width="stretch", hide_index=True)

st.subheader("Data Use Notice")
st.dataframe([{"notice": item} for item in governance["data_use_notice"]], width="stretch", hide_index=True)

st.subheader("ข้อมูลที่ห้ามแสดงหรือ Export")
st.dataframe([{"forbidden_column": column} for column in sorted(FORBIDDEN_COLUMNS)], width="stretch", hide_index=True)

df = load_analytics_dataset()
aggregate = grouped_counts(df, ["province", "current_field_group"], 100)
masked_aggregate = suppress_small_groups(aggregate)

st.subheader("Minimum Group Size Masking")
st.caption("กลุ่มที่มีจำนวนน้อยกว่าเกณฑ์จะถูกปกปิดก่อนแสดงผลหรือ export")
st.dataframe(masked_aggregate.head(100), width="stretch", hide_index=True)

st.subheader("PII Masking Demo")
demo_df = pd.DataFrame({
    "province": ["ตัวอย่าง"],
    "contact_phone": ["0812345678"],
    "note": ["ติดต่อ test@example.com"],
    "count": [10],
})
masked_demo = mask_pii_dataframe(demo_df)
st.dataframe(masked_demo, width="stretch", hide_index=True)

st.subheader("Audit Log")
if roles[role]["can_view_audit"]:
    audit_rows = _read_jsonl(DEFAULT_AUDIT_LOG)
    export_rows = _read_jsonl(PROJECT_ROOT / governance["export"]["export_log_path"])
    tabs = st.tabs(["Audit Log", "Export Log"])
    with tabs[0]:
        st.dataframe(audit_rows[-100:], width="stretch", hide_index=True)
    with tabs[1]:
        st.dataframe(export_rows[-100:], width="stretch", hide_index=True)
else:
    st.warning("Role นี้ไม่มีสิทธิ์ดู audit/export log")

if roles[role]["can_export_aggregate"]:
    st.download_button(
        "Export Masked Aggregate CSV",
        data=aggregate_csv_bytes(masked_aggregate, "governance_masked_aggregate.csv", role),
        file_name="governance_masked_aggregate.csv",
        mime="text/csv",
    )
else:
    st.caption("Role นี้ไม่มีสิทธิ์ export ข้อมูล")

with st.expander("Privacy Self Check"):
    csv_text = masked_aggregate.to_csv(index=False)
    findings = find_pii_in_text(csv_text)
    if findings:
        st.error(f"พบ pattern ที่อาจเป็น PII: {', '.join(findings)}")
    else:
        st.success("ไม่พบ pattern เบอร์โทร อีเมล หรือเลข 13 หลักใน aggregate ที่เตรียม export")
