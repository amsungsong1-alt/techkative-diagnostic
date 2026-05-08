"""
Tech-Kative AI-Readiness Diagnostic — HTML Report Builder

Builds a self-contained HTML report from the completed assessment.
Used as both an email attachment and a browser download.
No Streamlit dependency.

Public API:
    build_report(profile, scores, observations, responses) -> str
"""

from datetime import date
from html import escape

from framework import PILLARS, PILLAR_COLOURS, get_pillar


# ---------------------------------------------------------------------------
# Colour and style constants (self-contained — no styles.py dependency)
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
    "Pre-foundational": _AMBER,
    "Foundational":     _PRIMARY,
    "Developing":       _GREEN,
    "Mature":           _NAVY,
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
    """HTML-escape a string."""
    return escape(str(text))


def _score_bar(score: float) -> str:
    """Render a thin coloured progress bar for a pillar score (0–100)."""
    pct = max(0, min(100, score))
    return (
        f'<div style="background:{_BORDER};border-radius:3px;height:6px;margin:6px 0 0;">'
        f'<div style="background:{_PRIMARY};width:{pct:.0f}%;height:6px;border-radius:3px;"></div>'
        f"</div>"
    )


def _pillar_tile(pillar_id: str, score: float) -> str:
    pillar = get_pillar(pillar_id)
    colour = _PILLAR_TILE_COLOURS[pillar_id]
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
      {_score_bar(score)}
    </div>"""


def _observation_block(obs_list: list) -> str:
    items = ""
    for obs in obs_list:
        items += f"""
        <div style="margin-bottom:18px;padding:18px 20px;background:{_WASH};
                    border-left:3px solid {_PRIMARY};border-radius:0 6px 6px 0;">
          <p style="margin:0;font-size:14px;line-height:1.7;color:{_SLATE};">{_h(obs)}</p>
        </div>"""
    return items


def _profile_rows(profile: dict) -> str:
    rows = [
        ("Institution",  profile.get("institution_name", "")),
        ("Type",         profile.get("institution_type", "")),
        ("Country",      profile.get("country", "")),
        ("Contact",      profile.get("contact_name", "")),
        ("Email",        profile.get("contact_email", "")),
        ("Role",         profile.get("role", "")),
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
    observations: list,
    responses: dict,
) -> str:
    """
    Build and return a self-contained HTML report string.

    Args:
        profile:      institutional profile dict from session state
        scores:       output of scoring.compute_score_summary()
        observations: output of scoring.generate_observations()
        responses:    raw item_id → score dict (unused in HTML but retained for future use)

    Returns:
        Complete HTML document as a string.
    """
    composite   = scores["composite"]
    tier        = scores["tier"]
    tier_colour = _TIER_COLOURS.get(tier, _PRIMARY)
    pillar_scrs = scores["pillar_scores"]
    _d          = date.today()
    today       = f"{_d.day} {_d.strftime('%B')} {_d.year}"

    # Pillar tiles
    tiles_html = ""
    for pid in ["p1", "p2", "p3", "p4"]:
        tiles_html += _pillar_tile(pid, pillar_scrs[pid])

    # Pillar detail rows (for the response summary section)
    pillar_details = ""
    for pillar in PILLARS:
        pid = pillar["id"]
        colour = _PILLAR_TILE_COLOURS[pid]
        pillar_details += f"""
        <div style="margin-bottom:24px;">
          <div style="font-size:12px;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.07em;color:{colour};margin-bottom:8px;">
            {_h(pillar['name'])} — {pillar_scrs[pid]:.0f} / 100
          </div>"""
        for item in pillar["items"]:
            item_score = responses.get(item["id"], "—")
            option_label = ""
            if isinstance(item_score, int):
                option_label = item["options"][item_score - 1]["label"]
            pillar_details += f"""
          <div style="padding:8px 0;border-bottom:1px solid {_BORDER};">
            <div style="font-size:12px;font-weight:600;color:{_SLATE};margin-bottom:2px;">
              {_h(item['id'])} &nbsp;{_h(item['short_label'])}
            </div>
            <div style="font-size:12px;color:{_MUTED};">
              Rated <strong>{item_score}/5</strong> — {_h(option_label)}
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
    .header-brand {{
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #c4a8e0;
      margin-bottom: 12px;
    }}
    .header-title {{
      font-size: 24px;
      font-weight: 700;
      color: {_WHITE};
      margin-bottom: 4px;
    }}
    .header-subtitle {{
      font-size: 14px;
      color: #a89cc8;
    }}
    .section {{
      padding: 32px 40px;
      border-bottom: 1px solid {_BORDER};
    }}
    .section:last-child {{ border-bottom: none; }}
    .section-label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: {_MUTED};
      margin-bottom: 16px;
    }}
    .tier-banner {{
      background: linear-gradient(135deg, {_NAVY} 0%, {_NAVY_MID} 100%);
      border-radius: 6px;
      padding: 24px 28px;
      display: flex;
      align-items: center;
      gap: 24px;
    }}
    .tier-score {{
      font-size: 48px;
      font-weight: 700;
      color: {_WHITE};
      line-height: 1;
    }}
    .tier-label {{
      font-size: 20px;
      font-weight: 700;
      color: #c4a8e0;
    }}
    .tier-sub {{
      font-size: 13px;
      color: #a89cc8;
      margin-top: 4px;
    }}
    .tiles {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .footer {{
      background: {_WASH};
      padding: 20px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .footer-brand {{
      font-size: 12px;
      font-weight: 700;
      color: {_MUTED};
    }}
    .footer-date {{
      font-size: 12px;
      color: {_MUTED};
    }}
    .stage2-block {{
      background: {_WASH};
      border: 1px solid {_BORDER};
      border-radius: 6px;
      padding: 24px 28px;
    }}
    .stage2-heading {{
      font-size: 16px;
      font-weight: 700;
      color: {_SLATE};
      margin-bottom: 8px;
    }}
    .stage2-body {{
      font-size: 14px;
      color: {_MUTED};
      line-height: 1.7;
      margin-bottom: 14px;
    }}
    .stage2-cta {{
      display: inline-block;
      background: {_PRIMARY};
      color: {_WHITE};
      font-size: 13px;
      font-weight: 700;
      padding: 10px 20px;
      border-radius: 4px;
      text-decoration: none;
    }}
    a {{ color: {_PRIMARY}; }}
  </style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <div class="header">
    <div class="header-brand">Tech-Kative · AI-Readiness Diagnostic</div>
    <div class="header-title">{_h(profile.get('institution_name', 'Institutional Assessment'))}</div>
    <div class="header-subtitle">
      {_h(profile.get('institution_type', ''))}
      {' · ' + _h(profile.get('country', '')) if profile.get('country') else ''}
    </div>
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

  <!-- Narrative observations -->
  <div class="section">
    <div class="section-label">Profile Observations</div>
    {_observation_block(observations)}
  </div>

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

  <!-- Response detail -->
  <div class="section">
    <div class="section-label">Full Response Record</div>
    {pillar_details}
  </div>

  <!-- Footer -->
  <div class="footer">
    <div class="footer-brand">Tech-Kative · AI-Readiness Diagnostic</div>
    <div class="footer-date">Generated {_h(today)}</div>
  </div>

</div>
</body>
</html>"""

    return html
