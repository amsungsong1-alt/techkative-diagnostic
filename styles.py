"""
Tech-Kative AI-Readiness Diagnostic — Global CSS

Call inject_styles() once at the top of app.py to apply brand styling.
All Streamlit defaults are overridden here.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Brand palette constants (also used by app.py for inline styles)
# ---------------------------------------------------------------------------

PRIMARY  = "#8b3fb8"
NAVY     = "#1a1f3a"
NAVY_MID = "#2d2456"
GREEN    = "#2d8659"
AMBER    = "#b8651f"
WASH     = "#faf5fd"
SLATE    = "#2d3454"
MUTED    = "#6b7290"
BORDER   = "#e2e4ee"
WHITE    = "#ffffff"

PILLAR_COLOURS = {
    "p1": PRIMARY,
    "p2": NAVY,
    "p3": GREEN,
    "p4": AMBER,
}

TIER_COLOURS = {
    "Emerging":    AMBER,
    "Developing":  PRIMARY,
    "Established": GREEN,
    "Leading":     NAVY,
}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = f"""
<style>
/* ── Reset & base ────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
  background-color: #f4f5f9 !important;
}}

[data-testid="stAppViewContainer"] > .main {{
  background-color: #f4f5f9 !important;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stToolbar"] {{ display: none; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stStatusWidget"] {{ display: none; }}

/* ── Main content column ─────────────────────────────────────────────── */
.block-container {{
  max-width: 720px !important;
  padding: 0 24px 80px !important;
  margin: 0 auto !important;
}}

/* ── Typography ──────────────────────────────────────────────────────── */
body, .stMarkdown, .stText, p, label {{
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif !important;
  color: {SLATE} !important;
}}

h1 {{
  font-size: 28px !important;
  font-weight: 700 !important;
  color: {SLATE} !important;
  line-height: 1.25 !important;
  margin-bottom: 8px !important;
}}

h2 {{
  font-size: 20px !important;
  font-weight: 700 !important;
  color: {SLATE} !important;
}}

h3 {{
  font-size: 16px !important;
  font-weight: 700 !important;
  color: {SLATE} !important;
}}

p {{
  font-size: 15px !important;
  line-height: 1.7 !important;
}}

/* ── Persistent header ───────────────────────────────────────────────── */
.tk-header {{
  background: linear-gradient(135deg, {NAVY} 0%, {NAVY_MID} 100%);
  margin: 0 -24px 32px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}}

.tk-header-brand {{
  font-size: 14px;
  font-weight: 700;
  color: #c4a8e0;
  letter-spacing: 0.06em;
}}

/* ── Buttons ─────────────────────────────────────────────────────────── */
.stButton > button {{
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  border-radius: 4px !important;
  padding: 10px 24px !important;
  border: none !important;
  cursor: pointer !important;
  transition: opacity 0.15s ease !important;
}}

/* Primary button — used for "Continue", "Begin", "Submit" */
.stButton[data-testid="primary-btn"] > button,
.stButton > button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"] {{
  background: {PRIMARY} !important;
  color: {WHITE} !important;
}}

.stButton > button[kind="primary"]:hover {{
  opacity: 0.88 !important;
}}

/* Secondary button — "Previous" */
.stButton > button[kind="secondary"],
div[data-testid="stButton"] > button[kind="secondary"] {{
  background: {WHITE} !important;
  color: {PRIMARY} !important;
  border: 1.5px solid {PRIMARY} !important;
}}

/* ── Radio buttons ───────────────────────────────────────────────────── */
[data-testid="stRadio"] > div {{
  gap: 8px !important;
  display: flex !important;
  flex-direction: column !important;
}}

[data-testid="stRadio"] label {{
  display: block !important;
  padding: 12px 16px !important;
  border: 1.5px solid {BORDER} !important;
  border-radius: 6px !important;
  cursor: pointer !important;
  background: {WHITE} !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
  color: {SLATE} !important;
  transition: border-color 0.15s, background 0.15s !important;
}}

[data-testid="stRadio"] label:hover {{
  border-color: {PRIMARY} !important;
  background: {WASH} !important;
}}

/* Selected radio option */
[data-testid="stRadio"] input:checked + div + label,
[data-testid="stRadio"] label:has(input:checked) {{
  border-color: {PRIMARY} !important;
  background: {WASH} !important;
}}

/* Hide only the visual radio circle indicator; the label card remains visible */
[data-testid="stRadio"] [role="radio"] {{
  display: none !important;
}}

/* ── Progress bar ────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div {{
  height: 4px !important;
  border-radius: 2px !important;
}}

[data-testid="stProgress"] > div > div {{
  background: {PRIMARY} !important;
}}

/* ── Text inputs ─────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] textarea {{
  border: 1.5px solid {BORDER} !important;
  border-radius: 6px !important;
  font-size: 14px !important;
  padding: 10px 14px !important;
  color: {SLATE} !important;
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif !important;
}}

[data-testid="stTextInput"] input:focus {{
  border-color: {PRIMARY} !important;
  box-shadow: 0 0 0 3px rgba(139,63,184,0.12) !important;
  outline: none !important;
}}

/* ── Select box ──────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {{
  border: 1.5px solid {BORDER} !important;
  border-radius: 6px !important;
  font-size: 14px !important;
}}

/* ── Divider ─────────────────────────────────────────────────────────── */
hr {{
  border: none !important;
  border-top: 1px solid {BORDER} !important;
  margin: 28px 0 !important;
}}

/* ── Pillar tag chip ─────────────────────────────────────────────────── */
.pillar-tag {{
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 20px;
  margin-bottom: 12px;
  color: {WHITE};
}}

/* ── Help text ───────────────────────────────────────────────────────── */
.help-text {{
  font-size: 13px !important;
  font-style: italic;
  color: {MUTED} !important;
  line-height: 1.65 !important;
  margin-bottom: 20px !important;
}}

/* ── Pillar pill (welcome screen) ────────────────────────────────────── */
.pillar-pill {{
  background: {WHITE};
  border-radius: 8px;
  padding: 16px 18px;
  margin-bottom: 10px;
  border-left: 4px solid;
}}

.pillar-pill h4 {{
  font-size: 14px !important;
  font-weight: 700 !important;
  margin: 0 0 4px !important;
  color: {SLATE} !important;
}}

.pillar-pill p {{
  font-size: 13px !important;
  color: {MUTED} !important;
  margin: 0 !important;
  line-height: 1.5 !important;
}}

/* ── Results: tier banner ────────────────────────────────────────────── */
.tier-banner {{
  background: linear-gradient(135deg, {NAVY} 0%, {NAVY_MID} 100%);
  border-radius: 8px;
  padding: 28px 32px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 28px;
}}

.tier-score-big {{
  font-size: 56px;
  font-weight: 700;
  color: {WHITE};
  line-height: 1;
}}

.tier-label-big {{
  font-size: 22px;
  font-weight: 700;
  color: #c4a8e0;
}}

.tier-sub {{
  font-size: 13px;
  color: #a89cc8;
  margin-top: 4px;
}}

/* ── Results: pillar score tile ──────────────────────────────────────── */
.score-tile {{
  background: {WHITE};
  border-radius: 8px;
  padding: 18px 20px;
  border-top: 3px solid;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  flex: 1;
  min-width: 130px;
}}

.score-tile-name {{
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: {MUTED};
  margin-bottom: 6px;
}}

.score-tile-value {{
  font-size: 28px;
  font-weight: 700;
  color: {SLATE};
}}

.score-tile-denom {{
  font-size: 13px;
  color: {MUTED};
}}

/* ── Observation card ────────────────────────────────────────────────── */
.obs-card {{
  background: {WASH};
  border-left: 3px solid {PRIMARY};
  border-radius: 0 6px 6px 0;
  padding: 18px 20px;
  margin-bottom: 14px;
  font-size: 14px;
  line-height: 1.75;
  color: {SLATE};
}}

/* ── Stage 2 block ───────────────────────────────────────────────────── */
.stage2-block {{
  background: {WASH};
  border: 1px solid {BORDER};
  border-radius: 8px;
  padding: 24px 28px;
  margin-top: 8px;
}}

/* ── Footer ──────────────────────────────────────────────────────────── */
.tk-footer {{
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: {WHITE};
  border-top: 1px solid {BORDER};
  padding: 10px 24px;
  font-size: 12px;
  color: {MUTED};
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}}

/* ── Review screen response row ──────────────────────────────────────── */
.review-row {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid {BORDER};
}}

.review-row-id {{
  font-size: 11px;
  font-weight: 700;
  color: {MUTED};
  min-width: 28px;
  padding-top: 2px;
}}

.review-row-content {{
  flex: 1;
}}

.review-row-label {{
  font-size: 13px;
  font-weight: 600;
  color: {SLATE};
  margin-bottom: 2px;
}}

.review-row-response {{
  font-size: 12px;
  color: {MUTED};
}}

/* ── Success / info alerts ───────────────────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: 6px !important;
  font-size: 14px !important;
}}

/* ── Radio labels: wrap cleanly at all widths ────────────────────────── */
[data-testid="stRadio"] label {{
  white-space: normal !important;
  word-break: break-word !important;
  overflow-wrap: break-word !important;
}}

/* ── Mobile responsive (@640px) ─────────────────────────────────────── */
@media (max-width: 640px) {{
  .block-container {{
    padding: 0 12px 80px !important;
  }}

  [data-testid="stRadio"] label {{
    padding: 10px 12px !important;
    font-size: 13px !important;
  }}

  .stButton > button {{
    min-height: 44px !important;
    font-size: 13px !important;
    padding: 12px 16px !important;
  }}

  [data-testid="column"] {{
    min-width: 100% !important;
  }}

  .tier-score-big {{
    font-size: 40px !important;
  }}

  .tier-banner {{
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
    padding: 20px !important;
  }}

  .tk-header {{
    padding: 12px 16px !important;
    margin: 0 -12px 20px !important;
  }}
}}
</style>
"""


def inject_styles() -> None:
    """Inject global brand CSS into the Streamlit app. Call once at app startup."""
    st.markdown(_CSS, unsafe_allow_html=True)
