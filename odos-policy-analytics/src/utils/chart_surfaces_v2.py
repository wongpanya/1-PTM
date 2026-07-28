from __future__ import annotations

from itertools import cycle, islice

import streamlit as st


CHART_COLORS = [
    "#7C3AED",
    "#06B6D4",
    "#10B981",
    "#EF4444",
    "#F59E0B",
]

CHART_GRADIENT = [
    [0.00, "#EDE9FE"],
    [0.22, "#8B5CF6"],
    [0.44, "#22D3EE"],
    [0.66, "#34D399"],
    [0.84, "#FBBF24"],
    [1.00, "#FB7185"],
]


def _cycled_colors(length: int, *, offset: int = 0) -> list[str]:
    palette = CHART_COLORS[offset:] + CHART_COLORS[:offset]
    return list(islice(cycle(palette), max(length, 0)))


def _point_count(trace) -> int:
    for field in ("labels", "x", "y", "values"):
        values = getattr(trace, field, None)
        if values is not None:
            try:
                return len(values)
            except TypeError:
                continue
    return 0


def _rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    red, green, blue = (int(value[index : index + 2], 16) for index in (0, 2, 4))
    return f"rgba({red}, {green}, {blue}, {alpha})"


def apply_chart_palette(fig):
    """Apply the five-color ODOS palette according to each Plotly trace type."""
    fig.update_layout(
        colorway=CHART_COLORS,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font={"family": "Inter, sans-serif", "color": "#1F2937", "size": 13},
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": "#E5EAF2",
            "font": {"color": "#1F2937"},
        },
    )

    trace_count = len(fig.data)
    for index, trace in enumerate(fig.data):
        trace_type = getattr(trace, "type", "")
        color = CHART_COLORS[index % len(CHART_COLORS)]
        point_count = _point_count(trace)

        if trace_type in {"bar", "histogram"}:
            trace.marker.color = (
                _cycled_colors(point_count, offset=index)
                if trace_count == 1 and point_count > 1
                else color
            )
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 1

        elif trace_type in {"pie", "funnel", "funnelarea", "treemap", "sunburst"}:
            trace.marker.colors = _cycled_colors(point_count, offset=index)
            trace.marker.line.color = "#FFFFFF"
            trace.marker.line.width = 2

        elif trace_type in {"scatter", "scattergl"}:
            mode = getattr(trace, "mode", "") or ""
            if "lines" in mode:
                trace.line.color = color
            current_marker_color = getattr(trace.marker, "color", None)
            if "markers" in mode and (
                current_marker_color is None or isinstance(current_marker_color, str)
            ):
                trace.marker.color = color
                trace.marker.line.color = "#FFFFFF"
                trace.marker.line.width = 1

        elif trace_type in {"box", "violin"}:
            trace.marker.color = color
            trace.line.color = color
            trace.fillcolor = _rgba(color, 0.16)

        elif trace_type in {"heatmap", "contour", "histogram2d"}:
            trace.colorscale = CHART_GRADIENT

        elif trace_type == "sankey":
            node_count = len(trace.node.label or [])
            node_colors = _cycled_colors(node_count)
            trace.node.color = node_colors
            sources = list(trace.link.source or [])
            trace.link.color = [
                _rgba(node_colors[source % max(node_count, 1)], 0.24)
                for source in sources
            ]

        elif trace_type == "indicator":
            if getattr(trace, "gauge", None):
                trace.gauge.bar.color = color
                if getattr(trace.gauge, "threshold", None):
                    trace.gauge.threshold.line.color = "#EF4444"

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


def render_chart(fig, *, container=None, **kwargs):
    """Render a Plotly figure after applying the shared multicolor palette."""
    target = st if container is None else container
    return target.plotly_chart(apply_chart_palette(fig), **kwargs)
