"""
Tech-Kative Diagnostic — SMKit Instant Diagnostic Report Builder

Uses plotly (already in requirements.txt) for the radar chart.
No external API calls — fully offline-capable.
"""

from __future__ import annotations

from datetime import date
from html import escape
from io import BytesIO
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


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

_SEV_LABELS = {"high": "High Priority", "medium": "Medium Priority", "low": "Low Priority"}
_TYPE_LABELS = {"RISK": "⚠ Risk", "GAP": "◎ Gap", "TREND": "↗ Trend"}


def build_smkit_html_report(r: dict) -> str:
    """
    Build a self-contained HTML report from a build_feedback_report() dict.
    Mirrors the questionnaire report style. Returns HTML string.
    """
    h = escape
    school   = h(r["school_name"])
    week     = h(str(r["week_ending"]))
    perf     = r["performance_score"]
    scores   = r["readiness_scores"]
    flags    = r["flags"]
    steps    = r["next_steps"]
    trend    = h(r["trend_summary"])
    year     = date.today().year

    # Pillar score table rows
    pillar_rows = ""
    for pid, name in _PILLAR_NAMES.items():
        s   = scores.get(pid, 0)
        col = _PILLAR_COLOURS[pid]
        bar = f'<div style="background:#e2e4ee;border-radius:3px;height:6px;margin-top:4px;">' \
              f'<div style="background:{col};width:{s:.0f}%;height:6px;border-radius:3px;"></div></div>'
        pillar_rows += f"""
        <tr>
          <td style="padding:8px 12px;font-size:13px;font-weight:600;color:#2d3454;">
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                         background:{col};margin-right:8px;vertical-align:middle;"></span>{h(name)}
          </td>
          <td style="padding:8px 12px;font-size:22px;font-weight:700;color:#2d3454;">{s:.0f}</td>
          <td style="padding:8px 12px;font-size:12px;color:#6b7290;">/ 100{bar}</td>
        </tr>"""

    # Flags
    flag_rows = ""
    for f in flags:
        sc = _SEV_COLOURS.get(f.severity, "#6b7290")
        tl = _TYPE_LABELS.get(f.type, f.type)
        sl = _SEV_LABELS.get(f.severity, f.severity)
        flag_rows += f"""
        <div style="padding:10px 14px;border-left:4px solid {sc};background:#faf5fd;
                    border-radius:0 6px 6px 0;margin-bottom:10px;">
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.05em;color:{sc};margin-bottom:4px;">{tl} · {sl}</div>
          <div style="font-size:13px;color:#2d3454;line-height:1.6;">{h(f.message)}</div>
          <div style="font-size:11px;color:#6b7290;margin-top:3px;">Evidence: {h(f.evidence)}</div>
        </div>"""

    # Next steps
    step_items = "".join(
        f'<li style="margin-bottom:8px;font-size:13px;color:#2d3454;line-height:1.6;">{h(s)}</li>'
        for s in steps
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SMKit Instant Diagnostic — {school}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
          background:#f4f5f9; margin:0; padding:24px; color:#2d3454; }}
  .card {{ background:#fff; border-radius:8px; padding:24px 28px; margin-bottom:20px;
           box-shadow:0 1px 4px rgba(0,0,0,0.07); }}
  h1 {{ font-size:22px; font-weight:700; margin:0 0 4px; }}
  h2 {{ font-size:16px; font-weight:700; margin:0 0 14px; color:#2d3454; }}
  table {{ width:100%; border-collapse:collapse; }}
  th {{ background:#faf5fd; padding:8px 12px; font-size:11px; font-weight:700;
        text-transform:uppercase; letter-spacing:0.06em; color:#6b7290; text-align:left; }}
  td {{ border-bottom:1px solid #e2e4ee; }}
  footer {{ font-size:11px; color:#6b7290; text-align:center; margin-top:32px;
            border-top:1px solid #e2e4ee; padding-top:12px; }}
</style>
</head>
<body>
<div style="background:linear-gradient(135deg,#1a1f3a 0%,#2d2456 100%);
            border-radius:8px;padding:24px 28px;margin-bottom:20px;color:#fff;">
  <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
              color:#c4a8e0;margin-bottom:6px;">TECH-KATIVE · SMKIT INSTANT DIAGNOSTIC</div>
  <h1>{school}</h1>
  <div style="font-size:13px;color:#a89cc8;">Week ending {week}</div>
  <div style="margin-top:16px;display:flex;align-items:baseline;gap:8px;">
    <span style="font-size:52px;font-weight:700;line-height:1;">{perf:.0f}</span>
    <span style="font-size:14px;color:#a89cc8;">/ 100 &nbsp;performance score</span>
  </div>
</div>

<div class="card">
  <h2>AI-Readiness by Pillar</h2>
  <table>
    <thead><tr><th>Pillar</th><th>Score</th><th>/ 100</th></tr></thead>
    <tbody>{pillar_rows}</tbody>
  </table>
</div>

{'<div class="card"><h2>Flags</h2>' + flag_rows + '</div>' if flags else ''}

<div class="card">
  <h2>Trend Summary</h2>
  <p style="font-size:13px;color:#6b7290;font-style:italic;margin:0;">{trend}</p>
</div>

{'<div class="card"><h2>What to do next</h2><ul>' + step_items + '</ul></div>' if steps else ''}

<footer>
  Ghana Data Protection Act, 2012 (Act 843) §30(4) &nbsp;·&nbsp;
  Nigeria GAID 2025 Article 18 &nbsp;·&nbsp;
  Not legal advice. &copy; Tech-Kative {year}
</footer>
</body>
</html>"""


# ---------------------------------------------------------------------------
# PDF report
# ---------------------------------------------------------------------------

def build_smkit_pdf_report(r: dict) -> bytes:
    """Build a PDF version of the SMKit report using reportlab. Returns bytes."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
        )
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. Add 'reportlab>=4.0.0' to requirements.txt."
        )

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
          leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    S   = getSampleStyleSheet()
    story = []

    foot_style = ParagraphStyle("smkit_foot", parent=S["Normal"], fontSize=7,
                                textColor=colors.HexColor("#6b7290"))

    story.append(Paragraph("Tech-Kative · SMKit Instant Diagnostic", S["Title"]))
    story.append(Paragraph(r["school_name"], S["Heading2"]))
    story.append(Paragraph(f"Week ending: {r['week_ending']}", S["Normal"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"<b>Performance Score: {r['performance_score']:.0f} / 100</b>", S["Heading3"]))
    story.append(Spacer(1, 0.4*cm))

    # Pillar table
    tdata = [["Pillar", "Score / 100"]]
    for pid, name in _PILLAR_NAMES.items():
        tdata.append([name, f"{r['readiness_scores'].get(pid, 0):.0f}"])
    t = Table(tdata, colWidths=[12*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#1a1f3a")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e4ee")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#faf5fd"), colors.white]),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    # Flags
    if r["flags"]:
        story.append(Paragraph("Flags", S["Heading3"]))
        for f in r["flags"]:
            tl = _TYPE_LABELS.get(f.type, f.type)
            sl = _SEV_LABELS.get(f.severity, f.severity)
            story.append(Paragraph(f"<b>{tl} · {sl}:</b> {f.message}", S["Normal"]))
            story.append(Spacer(1, 0.15*cm))

    # Trend
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Trend Summary", S["Heading3"]))
    story.append(Paragraph(r["trend_summary"], S["Normal"]))

    # Next steps
    if r["next_steps"]:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("What to do next", S["Heading3"]))
        for step in r["next_steps"]:
            story.append(Paragraph(f"• {step}", S["Normal"]))
            story.append(Spacer(1, 0.1*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f"Ghana Data Protection Act, 2012 (Act 843) §30(4) · "
        f"Nigeria GAID 2025 Article 18 · Not legal advice. "
        f"© Tech-Kative {date.today().year}",
        foot_style,
    ))

    doc.build(story)
    return buf.getvalue()
