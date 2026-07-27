import pandas as pd
import streamlit as st

from src.ingestion.loaders import load_dataset
from src.risk.scoring import score_row


st.title("Risk & Forecast")
st.caption("คะแนนใน Prototype เป็น decision support และต้องแสดงเหตุผลเสมอ")

df = load_dataset()
scored = []
for _, row in df.iterrows():
    result = score_row(row.to_dict())
    scored.append({
        "odos_uid": row["odos_uid"],
        "cohort": row.get("cohort"),
        "province": row.get("province"),
        "current_field_group": row.get("current_field_group"),
        "risk_score": result["risk_score"],
        "explanations": "; ".join(c["explanation_th"] for c in result["components"]),
    })

risk_df = pd.DataFrame(scored).sort_values("risk_score", ascending=False)
st.metric("ค่าเฉลี่ย Risk Score", round(risk_df["risk_score"].mean(), 2))
st.dataframe(risk_df.head(50), use_container_width=True)
