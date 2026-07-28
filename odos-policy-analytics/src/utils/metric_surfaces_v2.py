from __future__ import annotations

import streamlit as st


_DARK_METRIC_RULES = """
    .stApp div[data-testid="stMetric"],
    .stApp div[data-testid="stHorizontalBlock"]
        > div[data-testid="stColumn"]:nth-child(n)
        div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #182235 0%, #111827 100%) !important;
        border-color: #334155 !important;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18) !important;
    }

    .stApp div[data-testid="stMetricLabel"] {
        color: #A8B5C7 !important;
    }

    .stApp div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
    }

    .stApp div[data-testid="stMetricDelta"] {
        background-color: #202C40 !important;
        border-color: #3B4A61 !important;
    }
"""


def render_metric_surface_styles() -> None:
    """Apply colorful, consistent KPI surfaces to every Streamlit metric."""
    theme = st.session_state.get("odos_appearance_theme_v1", "Light")
    if theme == "Dark":
        dark_rules = _DARK_METRIC_RULES
    elif theme == "System":
        dark_rules = f"@media (prefers-color-scheme: dark) {{{_DARK_METRIC_RULES}}}"
    else:
        dark_rules = ""

    st.html(
        f"""
        <style>
        .stApp div[data-testid="stMetric"] {{
            position: relative;
            min-height: 8rem;
            padding: 1.05rem 1.15rem 1rem;
            overflow: hidden;
            background: linear-gradient(145deg, #FFFFFF 0%, #F3EDFF 100%) !important;
            border: 1px solid #DED3F8 !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 22px rgba(76, 29, 149, 0.08) !important;
        }}

        .stApp div[data-testid="stMetric"]::before {{
            position: absolute;
            inset: 0 0 auto;
            display: block !important;
            height: 4px;
            background: linear-gradient(90deg, #7C3AED 0%, #8B5CF6 100%) !important;
            content: "";
        }}

        .stApp div[data-testid="stMetricLabel"] {{
            color: #596579 !important;
            font-size: 0.84rem !important;
            font-weight: 600 !important;
            line-height: 1.35 !important;
        }}

        .stApp div[data-testid="stMetricLabel"]::before {{
            display: none !important;
        }}

        .stApp div[data-testid="stMetricValue"] {{
            color: #1F2937 !important;
            font-size: 1.78rem !important;
            font-weight: 700 !important;
            line-height: 1.15 !important;
            white-space: normal !important;
            overflow-wrap: anywhere !important;
        }}

        .stApp div[data-testid="stMetricDelta"] {{
            width: fit-content;
            max-width: 100%;
            margin-top: 0.42rem;
            padding: 0.16rem 0.5rem;
            border: 1px solid rgba(124, 58, 237, 0.14) !important;
            border-radius: 999px;
            background-color: rgba(255, 255, 255, 0.78) !important;
            font-size: 0.76rem !important;
            font-weight: 600 !important;
            line-height: 1.3 !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"] {{
            background: linear-gradient(145deg, #FFFFFF 0%, #E7F9FC 100%) !important;
            border-color: #CDEEF4 !important;
            box-shadow: 0 8px 22px rgba(6, 182, 212, 0.08) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 2)
            div[data-testid="stMetric"]::before {{
            background: linear-gradient(90deg, #06B6D4 0%, #22D3EE 100%) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"] {{
            background: linear-gradient(145deg, #FFFFFF 0%, #E8FAF3 100%) !important;
            border-color: #CFEFE2 !important;
            box-shadow: 0 8px 22px rgba(16, 185, 129, 0.08) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 3)
            div[data-testid="stMetric"]::before {{
            background: linear-gradient(90deg, #10B981 0%, #34D399 100%) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"] {{
            background: linear-gradient(145deg, #FFFFFF 0%, #FFF4DE 100%) !important;
            border-color: #F5E2B8 !important;
            box-shadow: 0 8px 22px rgba(245, 158, 11, 0.08) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(4n + 4)
            div[data-testid="stMetric"]::before {{
            background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 100%) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(5n)
            div[data-testid="stMetric"] {{
            background: linear-gradient(145deg, #FFFFFF 0%, #FEEBEC 100%) !important;
            border-color: #F8D2D5 !important;
            box-shadow: 0 8px 22px rgba(239, 68, 68, 0.08) !important;
        }}

        .stApp div[data-testid="stHorizontalBlock"]
            > div[data-testid="stColumn"]:nth-child(5n)
            div[data-testid="stMetric"]::before {{
            background: linear-gradient(90deg, #EF4444 0%, #FB7185 100%) !important;
        }}

        {dark_rules}

        @media (max-width: 768px) {{
            .stApp div[data-testid="stMetric"] {{
                min-height: 7.35rem;
            }}

            .stApp div[data-testid="stMetricValue"] {{
                font-size: 1.55rem !important;
            }}
        }}
        </style>
        """
    )
