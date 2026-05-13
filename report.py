"""
Tech-Kative AI-Readiness Diagnostic v2 — HTML Report Builder

Builds a self-contained HTML report. No Streamlit dependency.

Public API:
    build_report(profile, scores, recommendations, responses,
                 regulatory_flags=None) -> str
"""

import math
from datetime import date
from html import escape

from framework import PILLARS, PILLAR_COLOURS, PILLAR_ORDER, get_pillar


# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------

_PRIMARY     = "#8b3fb8"
_NAVY        = "#1a1f3a"
_NAVY_MID    = "#2d2456"
_GREEN       = "#2d8659"
_AMBER       = "#b8651f"
_WASH        = "#faf5fd"
_SLATE       = "#2d3454"
_MUTED       = "#6b7290"
_BORDER      = "#e2e4ee"
_WHITE       = "#ffffff"

_TIER_COLOURS = {
    "Emerging":    _AMBER,
    "Developing":  _PRIMARY,
    "Established": _GREEN,
    "Leading":     _NAVY,
}

_PILLAR_TILE_COLOURS = {
    "p1": _PRIMARY,
    "p2": _NAVY,
    "p3": _GREEN,
    "p4": _AMBER,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _h(text: str) -> str:
    return escape(str(text))


def _score_bar(score: float) -> str:
    pct = max(0, min(100, score))
    return (
        f'<div style="background:{_BORDER};border-radius:3px;height:6px;margin:6px 0 0;">'
        f'<div style="background:{_PRIMARY};width:{pct:.0f}%;height:6px;border-radius:3px;"></div>'
        f"</div>"
    )


def _pillar_tile(pillar_id: str, score: float, tier: str = "") -> str:
    pillar = get_pillar(pillar_id)
    colour = _PILLAR_TILE_COLOURS[pillar_id]
    tier_line = (
        f'<div style="font-size:10px;font-weight:700;color:{colour};margin-top:3px;">'
        f'{_h(tier)}</div>'
        if tier else ""
    )
    return f"""
    <div style="flex:1;min-width:140px;background:{_WHITE};border-radius:6px;
                border-top:3px solid {colour};padding:16px 18px;
                box-shadow:0 1px 4px rgba(0,0,0,0.07);">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.06em;color:{_MUTED};margin-bottom:4px;">
        {_h(pillar['short_name'])}
      </div>
      <div style="font-size:26px;font-weight:700;color:{_SLATE};">{score:.0f}</div>
      <div style="font-size:11px;color:{_MUTED};">/ 100</div>
      {tier_line}
      {_score_bar(score)}
    </div>"""


def _radar_svg(pillar_scores: dict) -> str:
    W, H = 280, 280
    cx, cy = W // 2, H // 2
    r_max = 100
    pids   = ["p1", "p2", "p3", "p4"]
    colours = [_PRIMARY, _NAVY, _GREEN, _AMBER]
    short_labels = ["Data", "Governance", "AI Readiness", "Deployment"]
    n = len(pids)
    angles = [math.pi / 2 - i * (2 * math.pi / n) for i in range(n)]

    def pt(angle, frac):
        x = cx + r_max * frac * math.cos(angle)
        y = cy - r_max * frac * math.sin(angle)
        return x, y

    grid = ""
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(f"{pt(a, frac)[0]:.1f},{pt(a, frac)[1]:.1f}" for a in angles)
        opacity = "0.4" if frac < 1.0 else "0.7"
        grid += f'<polygon points="{pts}" fill="none" stroke="{_BORDER}" stroke-width="1" opacity="{opacity}"/>\n'

    axes = ""
    for angle in angles:
        x, y = pt(angle, 1.0)
        axes += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{_BORDER}" stroke-width="1"/>\n'

    raw = []
    for pid, angle in zip(pids, angles):
        frac = min(1.0, max(0.0, pillar_scores.get(pid, 0) / 100))
        raw.append(pt(angle, frac))
    data_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in raw)
    data = (
        f'<polygon points="{data_pts}" '
        f'fill="rgba(139,63,184,0.18)" stroke="{_PRIMARY}" stroke-width="2"/>\n'
    )

    dots = ""
    for pid, angle, colour in zip(pids, angles, colours):
        frac = min(1.0, max(0.0, pillar_scores.get(pid, 0) / 100))
        x, y = pt(angle, frac)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{colour}"/>\n'

    label_offset = 1.28
    labels = ""
    for label, angle, colour, pid in zip(short_labels, angles, colours, pids):
        lx, ly = pt(angle, label_offset)
        score_val = int(round(pillar_scores.get(pid, 0)))
        anchor = "middle"
        if math.cos(angle) > 0.2:
            anchor = "start"
        elif math.cos(angle) < -0.2:
            anchor = "end"
        labels += (
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'font-family="-apple-system,sans-serif" font-size="10" '
            f'fill="{colour}" font-weight="700">{label} {score_val}</text>\n'
        )

    return (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'{grid}{axes}{data}{dots}{labels}'
        f'</svg>'
    )


def _regulatory_snapshot_html(flags: list) -> str:
    if not flags:
        return ""
    disclaimer = (
        "The following items represent specific regulatory or sovereignty alignment gaps "
        "based on your responses. These are not legal advice. Refer to Ghana's DPC, "
        "Nigeria's NDPC, or qualified counsel for binding guidance."
    )
    items_html = ""
    for flag in flags:
        items_html += f"""
        <div style="padding:10px 14px;background:#fff8f0;border-left:3px solid {_AMBER};
                    border-radius:0 6px 6px 0;margin-bottom:8px;">
          <strong style="color:{_AMBER};">{_h(flag['label'])}</strong>
          <span style="color:{_SLATE};"> — {_h(flag['description'])}</span>
        </div>"""
    return f"""
    <div style="margin-bottom:12px;font-size:13px;color:{_MUTED};font-style:italic;">
      {_h(disclaimer)}
    </div>
    {items_html}"""


def _recommendations_html(recommendations: dict) -> str:
    if not recommendations:
        return ""
    html = ""
    for pid in PILLAR_ORDER:
        pillar = get_pillar(pid)
        colour = _PILLAR_TILE_COLOURS[pid]
        r      = recommendations.get(pid, {})
        if not r:
            continue
        html += f"""
        <div style="margin-bottom:28px;border-left:3px solid {colour};padding-left:16px;">
          <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.07em;color:{colour};margin-bottom:10px;">
            {_h(pillar['name'])} &nbsp;&middot;&nbsp; Score {r.get('score', 0):.0f}
            &nbsp;&middot;&nbsp; {_h(r.get('tier', ''))}
          </div>"""
        for i, action in enumerate(r.get("items", []), start=1):
            html += f"""
          <div style="padding:12px 16px;background:{_WASH};border-radius:6px;
                      margin-bottom:8px;font-size:13px;line-height:1.65;color:{_SLATE};">
            <strong style="color:{colour};">{i}.</strong> {_h(action)}
          </div>"""
        html += "\n        </div>"
    return html


def _profile_rows(profile: dict) -> str:
    rows = [
        ("Institution",      profile.get("institution_name", "")),
        ("Type",             profile.get("institution_type", "")),
        ("Country",          profile.get("country", "")),
        ("Contact",          profile.get("contact_name", "")),
        ("Email",            profile.get("contact_email", "")),
        ("Role",             profile.get("role", "")),
        ("Assessment phase", profile.get("assessment_phase", "")),
    ]
    html = ""
    for label, value in rows:
        if value:
            html += f"""
            <tr>
              <td style="padding:6px 12px 6px 0;font-size:13px;color:{_MUTED};
                         white-space:nowrap;vertical-align:top;font-weight:600;">
                {_h(label)}
              </td>
              <td style="padding:6px 0;font-size:13px;color:{_SLATE};">{_h(value)}</td>
            </tr>"""
    return html


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_report(
    profile: dict,
    scores: dict,
    recommendations: dict,
    responses: dict,
    regulatory_flags: list = None,
    roadmap: dict = None,  # ignored — backward compat param
) -> str:
    composite    = scores["composite"]
    tier         = scores["tier"]
    tier_colour  = _TIER_COLOURS.get(tier, _PRIMARY)
    pillar_scrs  = scores["pillar_scores"]
    pillar_tiers = scores.get("pillar_tiers", {})
    _d           = date.today()
    today        = f"{_d.day} {_d.strftime('%B')} {_d.year}"

    # Pilot header line
    pilot_code = profile.get("pilot_code", "")
    pilot_line = ""
    if pilot_code:
        phase = profile.get("assessment_phase", "")
        pilot_line = (
            f'<div class="header-subtitle" style="margin-top:8px;color:#a89cc8;font-size:13px;">'
            f'Pilot: Tech-Kative × Standbasis Joint Pilot'
            f'{" · " + _h(phase) + " Assessment" if phase else ""}'
            f'</div>'
        )

    # Pillar tiles
    tiles_html = ""
    for pid in ["p1", "p2", "p3", "p4"]:
        tiles_html += _pillar_tile(pid, pillar_scrs[pid], pillar_tiers.get(pid, ""))

    # Radar SVG
    radar_svg = _radar_svg(pillar_scrs)

    # Regulatory snapshot
    reg_html = _regulatory_snapshot_html(regulatory_flags or [])

    # Recommendations
    rec_html = _recommendations_html(recommendations or {})

    # Full response detail
    pillar_details = ""
    for pillar in PILLARS:
        pid    = pillar["id"]
        colour = _PILLAR_TILE_COLOURS[pid]
        pillar_details += f"""
        <div style="margin-bottom:24px;">
          <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.07em;color:{colour};margin-bottom:8px;">
            {_h(pillar['name'])} — {pillar_scrs[pid]:.0f} / 100
          </div>"""
        # Only show questions for the user's country (approximate: show non-conditional + matching)
        country = profile.get("country", "")
        from framework import get_questions_for_user
        pillar_qs = [q for q in get_questions_for_user(country) if q["pillar_id"] == pid]
        for q in pillar_qs:
            resp = responses.get(q["id"])
            tag = "(optional)" if q["type"] == "open_text" else f"{resp or '—'}"
            pillar_details += f"""
          <div style="padding:8px 0;border-bottom:1px solid {_BORDER};">
            <div style="font-size:12px;font-weight:600;color:{_SLATE};margin-bottom:2px;">
              {_h(q['id'])} &nbsp; <span style="color:{_MUTED};font-weight:400;">{_h(q['text'][:80])}...</span>
            </div>
            <div style="font-size:12px;color:{_MUTED};">
              Response: <strong>{_h(tag)}</strong>
            </div>
          </div>"""
        pillar_details += "</div>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI-Readiness Diagnostic Report — {_h(profile.get('institution_name', 'Institution'))}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
      background: #f4f5f9;
      color: {_SLATE};
      line-height: 1.6;
    }}
    .wrapper {{
      max-width: 720px;
      margin: 32px auto;
      background: {_WHITE};
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 16px rgba(0,0,0,0.09);
    }}
    .header {{
      background: linear-gradient(135deg, {_NAVY} 0%, {_NAVY_MID} 100%);
      padding: 36px 40px 32px;
      color: {_WHITE};
    }}
    .header-brand {{ font-size:13px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#c4a8e0;margin-bottom:12px; }}
    .header-title {{ font-size:24px;font-weight:700;color:{_WHITE};margin-bottom:4px; }}
    .header-subtitle {{ font-size:14px;color:#a89cc8; }}
    .section {{ padding:32px 40px;border-bottom:1px solid {_BORDER}; }}
    .section:last-child {{ border-bottom:none; }}
    .section-label {{ font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{_MUTED};margin-bottom:16px; }}
    .tier-banner {{ background:linear-gradient(135deg,{_NAVY} 0%,{_NAVY_MID} 100%);border-radius:6px;padding:24px 28px;display:flex;align-items:center;gap:24px; }}
    .tier-score {{ font-size:48px;font-weight:700;color:{_WHITE};line-height:1; }}
    .tier-label {{ font-size:20px;font-weight:700;color:#c4a8e0; }}
    .tier-sub {{ font-size:13px;color:#a89cc8;margin-top:4px; }}
    .tiles {{ display:flex;gap:12px;flex-wrap:wrap; }}
    .footer {{ background:{_WASH};padding:20px 40px;display:flex;justify-content:space-between;align-items:center; }}
    .footer-brand {{ font-size:12px;font-weight:700;color:{_MUTED}; }}
    .footer-date {{ font-size:12px;color:{_MUTED}; }}
    .stage2-block {{ background:{_WASH};border:1px solid {_BORDER};border-radius:6px;padding:24px 28px; }}
    .stage2-heading {{ font-size:16px;font-weight:700;color:{_SLATE};margin-bottom:8px; }}
    .stage2-body {{ font-size:14px;color:{_MUTED};line-height:1.7;margin-bottom:14px; }}
    .stage2-cta {{ display:inline-block;background:{_PRIMARY};color:{_WHITE};font-size:13px;font-weight:700;padding:10px 20px;border-radius:4px;text-decoration:none; }}
    a {{ color:{_PRIMARY}; }}
  </style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <div class="header">
    <div class="header-brand">Tech-Kative · AI-Readiness Diagnostic v2</div>
    <div class="header-title">{_h(profile.get('institution_name', 'Institutional Assessment'))}</div>
    <div class="header-subtitle">
      {_h(profile.get('institution_type', ''))}
      {' · ' + _h(profile.get('country', '')) if profile.get('country') else ''}
    </div>
    {pilot_line}
  </div>

  <!-- Profile -->
  <div class="section">
    <div class="section-label">Respondent Profile</div>
    <table style="border-collapse:collapse;width:100%;">
      {_profile_rows(profile)}
    </table>
  </div>

  <!-- Composite tier -->
  <div class="section">
    <div class="section-label">Composite Readiness Profile</div>
    <div class="tier-banner">
      <div>
        <div class="tier-score">{composite:.0f}</div>
        <div style="font-size:12px;color:#a89cc8;margin-top:2px;">/ 100</div>
      </div>
      <div>
        <div class="tier-label">{_h(tier)}</div>
        <div class="tier-sub">Unweighted composite across four pillars</div>
      </div>
    </div>
  </div>

  <!-- Pillar tiles -->
  <div class="section">
    <div class="section-label">Pillar Scores</div>
    <div class="tiles">
      {tiles_html}
    </div>
  </div>

  <!-- Radar chart -->
  <div class="section">
    <div class="section-label">Readiness Profile — Radar View</div>
    <div style="display:flex;justify-content:center;padding:8px 0;">
      {radar_svg}
    </div>
  </div>

  <!-- Regulatory Compliance Snapshot -->
  {f'<div class="section"><div class="section-label">Regulatory Compliance Snapshot</div>{reg_html}</div>' if reg_html else ''}

  <!-- Recommendations -->
  {f'<div class="section"><div class="section-label">Recommended Actions by Pillar</div>{rec_html}</div>' if rec_html else ''}

  <!-- Stage 2 -->
  <div class="section">
    <div class="stage2-block">
      <div class="stage2-heading">Recommended Next Step: Stage 2 Diagnostic Engagement</div>
      <div class="stage2-body">
        This diagnostic provides a first-pass profile of your institution's AI-readiness posture.
        A Stage 2 Engagement with Tech-Kative offers a structured deep-dive: facilitated sessions
        with your leadership team, gap analysis against sector benchmarks, and a prioritised
        roadmap for your specific operating context.
      </div>
      <a class="stage2-cta" href="mailto:info@techkative.com?subject=Stage 2 Diagnostic Enquiry — {_h(profile.get('institution_name', ''))}">
        Request a Stage 2 Conversation
      </a>
    </div>
  </div>

  <!-- Full response detail -->
  <div class="section">
    <div class="section-label">Full Response Record</div>
    {pillar_details}
  </div>

  <!-- Footer -->
  <div class="footer">
    <div class="footer-brand">Tech-Kative · AI-Readiness Diagnostic v2 · info@techkative.com</div>
    <div class="footer-date">Generated {_h(today)}</div>
  </div>

</div>
</body>
</html>"""

    return html
