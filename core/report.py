"""
Tech-Kative Diagnostic — SMKit Instant Diagnostic Report Builder

Uses plotly (already in requirements.txt) for the radar chart.
No external API calls — fully offline-capable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go

if TYPE_CHECKING:
    from core.instant_diagnostic import SchoolDiagnostic, Flag

_PILLAR_NAMES = {
    "p1": "Data Foundations",
    "p2": "Governance & Protection",
    "p3": "AI Readiness",
    "p4": "Responsible Deployment",
}

_PILLAR_COLOURS = {
    "p1": "#8b3fb8",
    "p2": "#1a1f3a",
    "p3": "#2d8659",
    "p4": "#b8651f",
}

_SEV_COLOURS = {
    "high":   "#c0392b",
    "medium": "#d68910",
    "low":    "#239b56",
}


def render_radar(readiness_scores: dict[str, float]) -> go.Figure:
    """
    Return a 4-axis Scatterpolar figure matching the existing app style.
    Axes: Data Foundations · Governance & Protection · AI Readiness · Responsible Deployment
    """
    pids   = ["p1", "p2", "p3", "p4"]
    labels = [_PILLAR_NAMES[p] for p in pids]
    values = [readiness_scores.get(p, 0) for p in pids]

    closed_labels = labels + [labels[0]]
    closed_values = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=closed_values,
        theta=closed_labels,
        fill="toself",
        fillcolor="rgba(139,63,184,0.15)",
        line=dict(color="#8b3fb8", width=2),
        hovertemplate="%{theta}: %{r:.0f}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(250,245,253,0.8)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color="#6b7290"),
                gridcolor="#e2e4ee", linecolor="#e2e4ee",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#2d3454"),
                gridcolor="#e2e4ee", linecolor="#e2e4ee",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=60, r=60, t=40, b=40),
        height=360,
        showlegend=False,
    )
    return fig


def build_feedback_report(school_diag: "SchoolDiagnostic") -> dict:
    """
    Return a structured report dict ready for Streamlit rendering.

    Keys:
        school_name, week_ending, performance_score, perf_delta,
        readiness_scores, readiness_deltas, radar_fig,
        flags, trend_summary, next_steps
    """
    radar_fig = render_radar(school_diag.readiness_scores)

    # Build a short trend summary sentence
    trend_flags = [f for f in school_diag.flags if f.type == "TREND"]
    if trend_flags:
        trend_summary = "; ".join(f.message for f in trend_flags[:2])
    else:
        trend_summary = "No multi-week trends detected in this data set."

    return {
        "school_name":       school_diag.school_name,
        "week_ending":       school_diag.week_ending,
        "performance_score": school_diag.performance_score,
        "perf_delta":        school_diag.perf_delta,
        "readiness_scores":  school_diag.readiness_scores,
        "readiness_deltas":  school_diag.readiness_deltas,
        "radar_fig":         radar_fig,
        "flags":             school_diag.flags,
        "trend_summary":     trend_summary,
        "next_steps":        school_diag.next_steps,
    }
