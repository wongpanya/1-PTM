from __future__ import annotations

POLICY_CHART_COLORS = [
    "#7C3AED",
    "#06B6D4",
    "#10B981",
    "#EF4444",
    "#F59E0B",
]

POLICY_CHART_GRADIENT = [
    "#7C3AED",
    "#06B6D4",
    "#10B981",
    "#EF4444",
    "#F59E0B",
]


def style_policy_chart(fig, *, height: int = 360):
    """Apply the shared ODOS dashboard theme to a Plotly figure."""
    fig.update_layout(
        height=height,
        margin={"l": 8, "r": 8, "t": 24, "b": 8},
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font={"family": "Inter, sans-serif", "color": "#1F2937", "size": 13},
        colorway=POLICY_CHART_COLORS,
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"color": "#64748B"},
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#E5EAF2",
            "font": {"color": "#1F2937"},
        },
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#E5EAF2",
        tickfont={"color": "#64748B"},
        title_font={"color": "#475569"},
    )
    fig.update_yaxes(
        gridcolor="#EEF1F6",
        zerolinecolor="#E5EAF2",
        linecolor="#E5EAF2",
        tickfont={"color": "#64748B"},
        title_font={"color": "#475569"},
    )
    return fig
