"""
Tech-Kative AI-Readiness Diagnostic v2 — Main Application

Entry point. Initialises session state, injects CSS, and routes to the
correct screen based on st.session_state.screen.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

import db
import session_store
import state
import styles
from core.i18n import LANGUAGES, audio_path as _i18n_audio_path, t as _i18n_t
from core.instant_diagnostic import analyse_school
from core.report import build_feedback_report, render_radar as _smkit_radar
from core.smkit_ingest import load_entries as _smkit_load
from email_service import send_all
from framework import (
    COUNTRY_OPTIONS,
    INSTITUTION_TYPES,
    PILLAR_INTRODUCTIONS,
    PILOT_CODES,
    PILLARS,
    PILLAR_ORDER,
    PRIVACY_NOTICE_PARAGRAPHS,
    FOUR_OPTION_LIKERT,
    YES_NO_OPTIONS,
    get_pillar,
    get_questions_for_user,
    get_scored_questions,
)
from report import build_report, build_pdf_report
from scoring import (
    compute_score_summary,
    generate_recommendations,
    generate_regulatory_flags,
)

load_dotenv()


def _load_streamlit_secrets():
    _KEYS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
             "FROM_ADDRESS", "TECHKATIVE_INBOX"]
    try:
        for key in _KEYS:
            if key not in os.environ and hasattr(st, "secrets") and key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI-Readiness Diagnostic — Tech-Kative",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

styles.inject_styles()
state.init()
_load_streamlit_secrets()

# Priority 2 — URL token resume (runs once per browser session)
if not st.session_state.get("_token_checked"):
    st.session_state._token_checked = True
    _url_token = st.query_params.get("token", "")
    if _url_token:
        _url_payload = session_store.load(_url_token)
        if _url_payload:
            state.load_draft_payload(_url_payload)
            st.session_state.session_token = _url_token
    if not st.session_state.get("session_token"):
        st.session_state.session_token = session_store.new_token()

_LOGO = Path("assets/logo.png")


# ---------------------------------------------------------------------------
# Shared UI components
# ---------------------------------------------------------------------------

def _header():
    if _LOGO.exists():
        col_logo, col_brand = st.columns([1, 7])
        with col_logo:
            st.image(str(_LOGO), width=100)
        with col_brand:
            st.markdown(
                f'<div style="padding:10px 0 0;font-size:13px;font-weight:700;'
                f'color:{styles.MUTED};letter-spacing:0.07em;">'
                f"TECH-KATIVE &nbsp;·&nbsp; AI-READINESS DIAGNOSTIC</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div class="tk-header">'
            f'<span class="tk-header-brand">TECH-KATIVE &nbsp;·&nbsp; AI-READINESS DIAGNOSTIC</span>'
            f"</div>",
            unsafe_allow_html=True,
        )


def _footer():
    st.markdown(
        f'<div class="tk-footer">'
        f'<span>Tech-Kative · AI-Readiness Diagnostic v2</span>'
        f'<span style="font-size:11px;color:{styles.MUTED};">'
        f'Ghana Act 843 §30(4) &nbsp;·&nbsp; Nigeria GAID 2025 Art. 18 &nbsp;·&nbsp;'
        f'<a href="mailto:info@techkative.com" style="color:{styles.MUTED};">info@techkative.com</a>'
        f'</span></div>',
        unsafe_allow_html=True,
    )


def _pilot_banner():
    if state.is_pilot_mode():
        phase = state.get_assessment_phase()
        code  = state.get_pilot_code()
        st.markdown(
            f'<div style="background:#e8f4e8;border-left:4px solid {styles.GREEN};'
            f'padding:8px 16px;margin-bottom:16px;border-radius:0 4px 4px 0;'
            f'font-size:13px;color:{styles.NAVY};">'
            f'Pilot Mode: Tech-Kative × Standbasis Joint Pilot (June – July 2026)'
            f' &nbsp;·&nbsp; {phase} &nbsp;·&nbsp; Code: {code}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _sidebar():
    """Priority 5 — autosave indicator always visible in sidebar."""
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:13px;font-weight:700;color:{styles.NAVY};'
            f'margin-bottom:8px;">Tech-Kative Diagnostic</div>',
            unsafe_allow_html=True,
        )
        ts = st.session_state.get("last_saved_at")
        if ts:
            st.markdown(f"🟢 **Last saved:** {ts}")
        else:
            st.markdown("⚪ Not yet saved")


# Priority 3 — recommendation priority colours (mirrored from report.py for Streamlit display)
_REC_RED    = "#c0392b"
_REC_AMBER  = "#d68910"
_REC_GREEN  = "#239b56"
_REC_PRIORITY_ORDER = {"RED": 0, "AMBER": 1, "GREEN": 2}
_REC_RED_TRIGGERS = {
    "Act 843", "§27", "NDPC", "DPO", "DPC Privacy Seal",
    "GAID 2025", "DPIA", "Africa Declaration", "sovereignty", "data sovereignty",
}

def _rec_priority(item_text: str, tier: str) -> tuple:
    if tier == "Emerging":
        return ("RED", _REC_RED, "High Priority")
    if any(t in item_text for t in _REC_RED_TRIGGERS):
        return ("RED", _REC_RED, "High Priority")
    if tier == "Developing":
        return ("AMBER", _REC_AMBER, "Medium Priority")
    return ("GREEN", _REC_GREEN, "Low Priority")


def _pillar_pill(pillar: dict):
    colour = pillar["colour"]
    st.markdown(
        f'<div class="pillar-pill" style="border-left-color:{colour};">'
        f'<h4 style="color:{colour};">{pillar["name"]}</h4>'
        f'<p>{pillar["description"]}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _score_bar_html(score: float, colour: str) -> str:
    pct = max(0, min(100, score))
    return (
        f'<div style="background:{styles.BORDER};border-radius:3px;height:5px;margin-top:8px;">'
        f'<div style="background:{colour};width:{pct:.0f}%;height:5px;border-radius:3px;"></div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Audio onboarding widget — backed by core/i18n.py
# ---------------------------------------------------------------------------

# Language display names for the selectbox (maps lang code → label)
_LANG_LABELS = {"en": "English", "tw": "Twi (DRAFT)", "dag": "Dagbani (DRAFT)"}


# ---------------------------------------------------------------------------
# Screen 1 — Welcome + Consent (merged, Priority 1)
# ---------------------------------------------------------------------------

def screen_welcome_consent():
    _header()
    _mode_tabs()

    st.markdown("<br>", unsafe_allow_html=True)

    # Language selector + audio voice button (core/i18n.py)
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    _lang_codes = list(_LANG_LABELS.keys())
    _lang_idx   = _lang_codes.index(st.session_state.get("lang", "en"))
    _lang_sel   = st.selectbox(
        "Language · Kasa · Zaŋ",
        options=_lang_codes,
        format_func=lambda k: _LANG_LABELS[k],
        index=_lang_idx,
        label_visibility="collapsed",
    )
    st.session_state.lang = _lang_sel
    _ap = _i18n_audio_path(_lang_sel)
    if _ap.exists():
        st.audio(str(_ap))
    else:
        # Show text intro + an audio placeholder button
        st.info(_i18n_t("welcome_intro", _lang_sel))
        if st.button(_i18n_t("audio_btn", _lang_sel), key="audio_placeholder_btn"):
            st.caption("Audio recording coming soon — transcript shown above.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Institutional Self-Assessment</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Know your school's AI readiness in 15 minutes — and what to do next.")
    st.markdown(
        f'<p style="font-size:15px;color:{styles.SLATE};line-height:1.7;">'
        "A free 4-pillar diagnostic for African school heads — grounded in the Data Protection "
        "Act 2012 (Act 843) and Africa's declared AI principles. No login. Works on any Android."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:{styles.MUTED};margin-bottom:8px;">The Four Pillars</p>',
        unsafe_allow_html=True,
    )

    for pillar in PILLARS:
        _pillar_pill(pillar)

    st.markdown("<br>", unsafe_allow_html=True)

    # Privacy notice (Priority 1 — inline expander)
    with st.expander("Privacy Notice — read before proceeding"):
        for para in PRIVACY_NOTICE_PARAGRAPHS:
            st.markdown(para)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(
        f'<p style="font-size:11px;color:{styles.MUTED};line-height:1.6;">'
        "Ghana: Act 843 §18 (lawful processing) &amp; §30(4) (cross-border). "
        "Nigeria: NDPA 2023 &amp; GAID 2025 Art. 18. "
        "Continental: Africa Declaration on AI, Kigali, 4 April 2025."
        "</p>",
        unsafe_allow_html=True,
    )

    agreed = st.checkbox(
        "I have read and accept the Privacy Notice above, and confirm I have authority "
        "to complete this diagnostic on behalf of my institution."
    )

    col_cta, col_space = st.columns([2, 3])
    with col_cta:
        if st.button(
            "I consent and continue →",
            type="primary",
            use_container_width=True,
            disabled=not agreed,
        ):
            state.set_consent(datetime.now(timezone.utc).isoformat())
            state.go("profile")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;color:{styles.MUTED};margin-bottom:6px;">'
        "Returning user? Upload a previously saved draft to resume where you left off."
        "</p>",
        unsafe_allow_html=True,
    )
    uploaded = st.file_uploader(
        "Upload saved draft",
        type=["json"],
        key="draft_uploader",
        label_visibility="collapsed",
    )
    if uploaded is not None:
        try:
            payload = json.loads(uploaded.read().decode("utf-8"))
            if state.load_draft_payload(payload):
                st.success("Draft loaded. Resuming your assessment.")
                state.go("assessment")
            else:
                st.error(
                    "This file does not appear to be a valid Tech-Kative diagnostic draft."
                )
        except Exception:
            st.error("Could not read the uploaded file. Please ensure it is a valid JSON draft.")

    _footer()


# ---------------------------------------------------------------------------
# Screen 3 — Institutional Profile
# ---------------------------------------------------------------------------

def screen_profile():
    _header()
    _pilot_banner()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Step 1 of 2</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Institutional Profile")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "This information is used to personalise your report. "
        "Institution name, country, and email address are required."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    prof = state.get_profile()
    field_errors = st.session_state.get("profile_errors", {})

    def _field_error(key: str):
        msg = field_errors.get(key)
        if msg:
            st.markdown(
                f'<p style="color:#c0392b;font-size:13px;margin-top:-10px;margin-bottom:8px;">'
                f"{msg}</p>",
                unsafe_allow_html=True,
            )

    institution_name = st.text_input(
        "Institution name *",
        value=prof.get("institution_name", ""),
        placeholder="e.g. Accra Girls' Senior High School",
    )
    _field_error("institution_name")

    institution_type = st.selectbox(
        "Institution type *",
        options=["— Select —"] + INSTITUTION_TYPES,
        index=(
            INSTITUTION_TYPES.index(prof["institution_type"]) + 1
            if prof.get("institution_type") in INSTITUTION_TYPES
            else 0
        ),
    )
    _field_error("institution_type")

    # Country — locked after assessment begins (Priority 11)
    current_country = prof.get("country", "")
    country_locked  = bool(state.get_response("df_1"))
    if country_locked:
        country = current_country
        st.markdown(
            f'<div style="margin-bottom:8px;">'
            f'<label style="font-size:14px;font-weight:600;color:{styles.SLATE};">Country</label><br>'
            f'<span style="font-size:14px;color:{styles.SLATE};">{country}</span> '
            f'<span style="font-size:12px;color:{styles.MUTED};">(locked after assessment begins)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        country_index = (
            COUNTRY_OPTIONS.index(current_country) + 1
            if current_country in COUNTRY_OPTIONS
            else 0
        )
        country = st.selectbox(
            "Country *",
            options=["— Select country —"] + COUNTRY_OPTIONS,
            index=country_index,
        )
        _field_error("country")

    contact_name = st.text_input(
        "Your name",
        value=prof.get("contact_name", ""),
        placeholder="e.g. Dr Adaeze Okoye",
    )

    contact_email = st.text_input(
        "Email address *",
        value=prof.get("contact_email", ""),
        placeholder="your.name@institution.edu",
    )
    _field_error("contact_email")

    role = st.text_input(
        "Your role",
        value=prof.get("role", ""),
        placeholder="e.g. Deputy Headteacher",
    )

    region = st.text_input(
        "Region / State",
        value=prof.get("region", ""),
        placeholder="e.g. Greater Accra / Lagos State",
    )

    # Pilot code section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:{styles.MUTED};">Pilot participants only</p>',
        unsafe_allow_html=True,
    )
    pilot_code_input = st.text_input(
        "Pilot code (if applicable)",
        value=state.get_pilot_code(),
        placeholder="Enter pilot code provided by Tech-Kative",
    )

    assessment_phase_input = ""
    if pilot_code_input.strip().upper() in {c.upper() for c in PILOT_CODES}:
        st.info(
            "✓ Pilot Mode: Tech-Kative × Standbasis Joint Pilot (June – July 2026)"
        )
        assessment_phase_input = st.selectbox(
            "Assessment phase *",
            options=["Baseline (Week 1)", "Post-Pilot (Week 7)"],
            index=(
                0
                if state.get_assessment_phase() in ("", "Baseline (Week 1)")
                else 1
            ),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col_back, col_fwd = st.columns([1, 2])
    with col_back:
        if st.button("← Back", type="secondary", use_container_width=True):
            st.session_state.profile_errors = {}
            state.go("welcome")
    with col_fwd:
        proceed = st.button(
            "Start my readiness check →", type="primary", use_container_width=True
        )

    if proceed:
        new_errors = {}
        if not institution_name.strip():
            new_errors["institution_name"] = "Institution name is required."
        if institution_type == "— Select —":
            new_errors["institution_type"] = "Please select an institution type."
        if not country_locked and country == "— Select country —":
            new_errors["country"] = "Please select a country."
        if not contact_email.strip():
            new_errors["contact_email"] = "Email address is required."
        elif "@" not in contact_email or "." not in contact_email.split("@")[-1]:
            new_errors["contact_email"] = "Please enter a valid email address."

        st.session_state.profile_errors = new_errors

        if not new_errors:
            code = pilot_code_input.strip().upper()
            state.set_pilot_code(code if code in {c.upper() for c in PILOT_CODES} else "")
            state.set_assessment_phase(assessment_phase_input)
            state.set_profile({
                "institution_name":  institution_name.strip(),
                "institution_type":  institution_type,
                "country":           country,
                "region":            region.strip(),
                "contact_name":      contact_name.strip(),
                "contact_email":     contact_email.strip(),
                "role":              role.strip(),
                "pilot_code":        state.get_pilot_code(),
                "assessment_phase":  state.get_assessment_phase(),
                "consent_given_at":  state.get_consent(),
                "session_token":     st.session_state.get("session_token", ""),
            })
            _token = st.session_state.get("session_token", "")
            if _token:
                try:
                    session_store.save(_token, state.build_draft_payload())
                except Exception:
                    pass
            state.go("assessment")
        else:
            st.rerun()

    # Resume link — show once profile is saved
    _token = st.session_state.get("session_token", "")
    if _token and state.profile_complete():
        _base_url = (
            (st.secrets.get("APP_URL", "") if hasattr(st, "secrets") else "")
            or "https://techkative-diagnostic.streamlit.app"
        )
        with st.expander("💾 Save your progress to return later"):
            st.caption(
                f"Bookmark or copy this link to resume your diagnostic from this point:"
            )
            st.code(f"{_base_url}?token={_token}", language=None)
            st.caption(
                "This link is valid for 7 days. Your progress is also saved automatically "
                "after each section — or use the Save Draft button on the questions screen."
            )

    _footer()


# ---------------------------------------------------------------------------
# Screen 4 — Assessment (one question per render)
# ---------------------------------------------------------------------------

def screen_assessment():
    _header()
    _pilot_banner()
    _sidebar()

    country      = state.get_profile().get("country", "")
    user_qs      = get_questions_for_user(country)
    scored_qs    = get_scored_questions(country)
    item_index   = state.current_item_index()

    # Guard: clamp index to valid range
    if item_index >= len(user_qs):
        item_index = len(user_qs) - 1
        state.set_item_index(item_index)

    question = user_qs[item_index]
    qid      = question["id"]
    pillar   = get_pillar(question["pillar_id"])
    colour   = pillar["colour"]

    # Priority 7 — first question index in this pillar
    pillar_first_index = next(
        i for i, q in enumerate(user_qs) if q["pillar_id"] == question["pillar_id"]
    )
    show_prev = item_index > pillar_first_index

    # Priority 6 — progress bar with % complete
    answered = state.answered_count(country)
    total    = len(scored_qs)
    pct_int  = int(answered / total * 100) if total else 0
    st.progress(answered / total if total else 0)
    st.markdown(
        f'<p style="font-size:12px;color:{styles.MUTED};margin-top:4px;">'
        f"Question {item_index + 1} of {len(user_qs)}"
        f" &nbsp;·&nbsp; <strong>{answered} of {total}</strong> scored answered"
        f" ({pct_int}% complete)"
        f"</p>",
        unsafe_allow_html=True,
    )

    # ── Pillar tag ────────────────────────────────────────────────────────
    st.markdown(
        f'<span class="pillar-tag" style="background:{colour};">{pillar["name"]}</span>',
        unsafe_allow_html=True,
    )
    if question["type"] == "open_text":
        st.markdown(
            f'<span style="font-size:11px;color:{styles.MUTED};margin-left:8px;">'
            f"Optional — not scored</span>",
            unsafe_allow_html=True,
        )

    # Priority 8 — pillar intro on first question of each pillar
    if item_index == pillar_first_index:
        intro = PILLAR_INTRODUCTIONS.get(question["pillar_id"], "")
        if intro:
            st.info(intro)

    # ── Question text ─────────────────────────────────────────────────────
    st.markdown(f"### {question['text']}")

    hint = question.get("hint", "")
    if hint:
        st.markdown(
            f'<p style="font-size:13px;color:{styles.MUTED};font-style:italic;'
            f'line-height:1.7;margin:8px 0 20px;padding:10px 14px;'
            f'background:#faf5fd;border-radius:6px;border-left:3px solid {colour}55;">'
            f'{hint}</p>',
            unsafe_allow_html=True,
        )

    # ── Input by type ─────────────────────────────────────────────────────
    came_from_review = state.get_navigation_target() == "review"
    is_last          = item_index >= len(user_qs) - 1
    stored           = state.get_response(qid)

    def _advance():
        pillar_qs_scored = [q for q in scored_qs if q["pillar_id"] == question["pillar_id"]]
        if all(state.get_response(q["id"]) for q in pillar_qs_scored):
            state.mark_pillar_complete(question["pillar_id"])
            try:
                session_store.save(
                    st.session_state.get("session_token", ""),
                    state.build_draft_payload(),
                )
            except Exception:
                pass
        if came_from_review:
            state.clear_navigation_target()
            state.go("review")
        elif is_last:
            state.go("review")
        else:
            state.set_item_index(item_index + 1)
            st.rerun()

    if question["type"] in ("yes_no_partial", "likert"):
        options = YES_NO_OPTIONS if question["type"] == "yes_no_partial" else FOUR_OPTION_LIKERT
        cols    = st.columns(len(options))
        clicked = None
        for i, (col, opt) in enumerate(zip(cols, options)):
            with col:
                if st.button(
                    opt,
                    key=f"opt_{qid}_{i}",
                    type="primary" if stored == opt else "secondary",
                    use_container_width=True,
                ):
                    clicked = opt

        if clicked is not None:
            state.set_response(qid, clicked)
            state.set_last_saved()
            _advance()

        st.markdown("<br>", unsafe_allow_html=True)
        if show_prev:
            if st.button("← Previous", key="btn_prev", type="secondary"):
                state.set_item_index(item_index - 1)
                st.rerun()

    else:  # open_text
        selected = st.text_area(
            "Your response (optional):",
            value=stored or "",
            key=f"text_{qid}",
            height=120,
            max_chars=400,
            help="Optional. 1-3 sentences is ideal.",
            label_visibility="collapsed",
            placeholder="Type your response here (not scored — for report context only).",
        )
        st.caption(f"{len(selected or '')} / 400 characters")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        if came_from_review:
            next_label = "Save & Return to Review →"
        elif is_last:
            next_label = "Review Responses →"
        else:
            next_label = "Continue →"

        if show_prev:
            col_prev, col_next = st.columns(2)
            with col_prev:
                prev_btn = st.button("← Previous", key="btn_prev", type="secondary", use_container_width=True)
            with col_next:
                next_btn = st.button(next_label, key="btn_next", type="primary", use_container_width=True)
        else:
            next_btn = st.button(next_label, key="btn_next", type="primary", use_container_width=True)
            prev_btn = False

        if next_btn:
            if selected:
                state.set_response(qid, selected)
                state.set_last_saved()
            _advance()

        if prev_btn:
            state.set_item_index(item_index - 1)
            st.rerun()

    # ── Save Draft ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    draft_json = json.dumps(state.build_draft_payload(), ensure_ascii=False, indent=2)
    st.download_button(
        label="Save Draft (.json)",
        data=draft_json.encode("utf-8"),
        file_name="techkative-diagnostic-draft.json",
        mime="application/json",
        type="secondary",
        help="Download your progress and resume later by uploading this file on the welcome screen.",
    )
    _resume_token = st.session_state.get("session_token", "")
    if _resume_token:
        try:
            _app_url = (
                st.secrets.get("APP_URL", "")
                if hasattr(st, "secrets") else ""
            ) or "https://techkative-diagnostic.streamlit.app"
        except Exception:
            _app_url = "https://techkative-diagnostic.streamlit.app"
        st.caption(f"Resume link (saved automatically after each pillar): `{_app_url}?token={_resume_token}`")

    _footer()


# ---------------------------------------------------------------------------
# Screen 5 — Review
# ---------------------------------------------------------------------------

def screen_review():
    _header()
    _pilot_banner()
    _sidebar()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Step 2 of 2 — Review</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Review Your Responses")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "Check your responses below. Click <strong>Edit</strong> beside any answer to change it — "
        "you will be taken back here automatically after saving. When satisfied, submit to receive your profile."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    country   = state.get_profile().get("country", "")
    user_qs   = get_questions_for_user(country)
    responses = st.session_state.responses

    for pillar in PILLARS:
        colour = pillar["colour"]
        pqs    = [q for q in user_qs if q["pillar_id"] == pillar["id"]]
        if not pqs:
            continue

        st.markdown(
            f'<div style="font-size:14px;font-weight:700;color:{colour};'
            f'margin:20px 0 4px;border-left:3px solid {colour};padding-left:10px;">'
            f'{pillar["name"]} — {len(pqs)} questions</div>',
            unsafe_allow_html=True,
        )

        for q in pqs:
            stored       = responses.get(q["id"])
            q_global_idx = next(i for i, uq in enumerate(user_qs) if uq["id"] == q["id"])

            if q["type"] == "open_text":
                answer_text   = stored[:100] + "…" if stored and len(stored) > 100 else (stored or "Not answered (optional)")
                answer_colour = styles.MUTED
            elif stored:
                answer_text   = stored
                answer_colour = styles.PRIMARY
            else:
                answer_text   = "Not yet answered"
                answer_colour = "#c0392b"

            col_q, col_edit = st.columns([8, 2], vertical_alignment="center")
            with col_q:
                st.markdown(
                    f'<div style="padding:10px 0 10px 13px;border-bottom:1px solid {styles.BORDER};'
                    f'border-left:2px solid {colour}22;">'
                    f'<div style="font-size:12px;color:{styles.MUTED};line-height:1.5;margin-bottom:4px;">'
                    f'{q["text"]}</div>'
                    f'<div style="font-size:13px;font-weight:600;color:{answer_colour};">'
                    f'{answer_text}</div></div>',
                    unsafe_allow_html=True,
                )
            with col_edit:
                if st.button("Edit", key=f"edit_q_{q['id']}", use_container_width=True):
                    state.set_navigation_target("review")
                    state.go_to_item(q_global_idx)

    st.markdown("<br>", unsafe_allow_html=True)

    scored_ids = {q["id"] for q in get_scored_questions(country)}
    missing = [qid for qid in scored_ids if qid not in responses]
    if missing:
        st.warning(
            f"{len(missing)} required item(s) have not been answered. "
            "Please complete all required items before submitting."
        )

    col_back, col_submit = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Assessment", type="secondary", use_container_width=True):
            state.set_item_index(len(user_qs) - 1)
            state.go("assessment")
    with col_submit:
        if st.button(
            "Submit Assessment →",
            type="primary",
            use_container_width=True,
            disabled=bool(missing),
        ):
            state.go("results")

    _footer()


# ---------------------------------------------------------------------------
# Results helpers
# ---------------------------------------------------------------------------

def _render_radar(scores: dict) -> None:
    p      = scores["pillar_scores"]
    labels = [get_pillar(pid)["short_name"] for pid in PILLAR_ORDER]
    values = [p[pid] for pid in PILLAR_ORDER]
    closed_labels = labels + [labels[0]]
    closed_values = values + [values[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=closed_values,
        theta=closed_labels,
        fill="toself",
        fillcolor="rgba(139,63,184,0.15)",
        line=dict(color=styles.PRIMARY, width=2),
        hovertemplate="%{theta}: %{r:.0f}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(250,245,253,0.8)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=10, color=styles.MUTED),
                gridcolor=styles.BORDER, linecolor=styles.BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=styles.SLATE),
                gridcolor=styles.BORDER, linecolor=styles.BORDER,
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


_TIER_BAND_LABELS = {
    "Emerging": "Emerging", "Developing": "Developing",
    "Established": "Established", "Leading": "Leading",
}


def _render_recommendations(recommendations: dict) -> None:
    st.markdown("### Recommended Actions by Pillar")
    # Priority 3 — priority legend
    st.markdown(
        f'<div style="margin-bottom:16px;padding:10px 14px;background:{styles.WASH};'
        f'border-radius:6px;display:flex;flex-wrap:wrap;gap:4px;align-items:center;">'
        f'<span style="font-size:11px;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.06em;color:{styles.MUTED};margin-right:12px;">Priority:</span>'
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:12px;'
        f'color:{styles.SLATE};margin-right:14px;">'
        f'<span style="width:12px;height:12px;border-radius:2px;background:{_REC_RED};'
        f'display:inline-block;"></span>High</span>'
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:12px;'
        f'color:{styles.SLATE};margin-right:14px;">'
        f'<span style="width:12px;height:12px;border-radius:2px;background:{_REC_AMBER};'
        f'display:inline-block;"></span>Medium</span>'
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:12px;'
        f'color:{styles.SLATE};">'
        f'<span style="width:12px;height:12px;border-radius:2px;background:{_REC_GREEN};'
        f'display:inline-block;"></span>Low</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    for pid in PILLAR_ORDER:
        pillar = get_pillar(pid)
        colour = styles.PILLAR_COLOURS[pid]
        r      = recommendations.get(pid, {})
        if not r:
            continue
        tier  = r.get("tier", "")
        items = r.get("items", [])
        # Sort by priority: RED → AMBER → GREEN
        classified = [(action, _rec_priority(action, tier)) for action in items]
        classified.sort(key=lambda x: _REC_PRIORITY_ORDER[x[1][0]])

        st.markdown(
            f'<div style="margin-bottom:6px;font-size:12px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.07em;color:{colour};'
            f'border-left:3px solid {colour};padding-left:10px;margin-top:20px;">'
            f'{pillar["name"]} &nbsp;·&nbsp; Score {r.get("score", 0):.0f} &nbsp;·&nbsp; {tier}'
            f"</div>",
            unsafe_allow_html=True,
        )
        for action, (priority_key, priority_colour, priority_label) in classified:
            st.markdown(
                f'<div style="padding:10px 14px;background:{styles.WASH};border-radius:6px;'
                f'margin-bottom:8px;font-size:13px;line-height:1.65;color:{styles.SLATE};'
                f'border-left:4px solid {priority_colour};">'
                f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.05em;color:{priority_colour};display:block;margin-bottom:4px;">'
                f'{priority_label}</span>'
                f'{action}'
                f"</div>",
                unsafe_allow_html=True,
            )


def _render_regulatory_flags(flags: list, country: str) -> None:
    if not flags:
        return
    st.markdown("### Regulatory Compliance Snapshot")
    st.markdown(
        f'<p style="font-size:13px;font-style:italic;color:{styles.MUTED};margin-bottom:12px;">'
        "The following items represent specific regulatory or sovereignty alignment gaps based "
        "on your responses. These are not legal advice. Refer to Ghana's DPC, Nigeria's NDPC, "
        "or qualified counsel for binding guidance."
        "</p>",
        unsafe_allow_html=True,
    )
    for flag in flags:
        st.markdown(
            f'<div style="padding:10px 14px;background:#fff8f0;'
            f'border-left:3px solid {styles.AMBER};border-radius:0 6px 6px 0;'
            f'margin-bottom:8px;font-size:13px;color:{styles.SLATE};">'
            f'<strong style="color:{styles.AMBER};">{flag["label"]}</strong>'
            f' — {flag["description"]}'
            f"</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Screen 6 — Results
# ---------------------------------------------------------------------------

def screen_results():
    _header()
    _pilot_banner()

    country   = state.get_profile().get("country", "")
    responses = st.session_state.responses

    # ── Compute on first render only ──────────────────────────────────────
    if state.get_scores() is None:
        with st.spinner("Computing your readiness profile…"):
            scores       = compute_score_summary(responses, country)
            recs         = generate_recommendations(scores)
            flags        = generate_regulatory_flags(responses, country)
            report_html  = build_report(
                profile=state.get_profile(),
                scores=scores,
                recommendations=recs,
                responses=responses,
                regulatory_flags=flags,
            )
            state.set_scores(scores)
            state.set_recommendations(recs)
            state.set_regulatory_flags(flags)
            state.set_report_html(report_html)
            # Persist to Supabase (silent on failure)
            db.save_assessment(
                profile=state.get_profile(),
                scores=scores,
                flags=flags,
                responses=responses,
            )

    scores      = state.get_scores()
    recs        = state.get_recommendations()
    flags       = state.get_regulatory_flags()
    profile     = state.get_profile()
    report_html = state.get_report_html()

    composite = scores["composite"]
    tier      = scores["tier"]
    p         = scores["pillar_scores"]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Your Readiness Profile</p>',
        unsafe_allow_html=True,
    )

    # ── Composite tier banner ─────────────────────────────────────────────
    tier_colour = styles.TIER_COLOURS.get(tier, styles.PRIMARY)
    st.markdown(
        f'<div class="tier-banner">'
        f'<div>'
        f'<div class="tier-score-big">{composite:.0f}</div>'
        f'<div style="font-size:13px;color:#a89cc8;margin-top:2px;">/ 100</div>'
        f'</div>'
        f'<div>'
        f'<div class="tier-label-big">{tier}</div>'
        f'<div class="tier-sub">Composite readiness tier &nbsp;·&nbsp; unweighted mean of four pillars</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pillar score tiles ────────────────────────────────────────────────
    cols = st.columns(4)
    for i, pid in enumerate(PILLAR_ORDER):
        pillar = get_pillar(pid)
        score  = p[pid]
        colour = styles.PILLAR_COLOURS[pid]
        ptier  = scores["pillar_tiers"][pid]
        with cols[i]:
            st.markdown(
                f'<div class="score-tile" style="border-top-color:{colour};">'
                f'<div class="score-tile-name">{pillar["short_name"]}</div>'
                f'<div class="score-tile-value">{score:.0f}'
                f'<span class="score-tile-denom">/100</span></div>'
                f'<div style="font-size:10px;color:{colour};font-weight:700;margin-top:4px;">'
                f'{ptier}</div>'
                + _score_bar_html(score, colour)
                + "</div>",
                unsafe_allow_html=True,
            )

    # ── Radar chart ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _render_radar(scores)

    # ── Regulatory flags ──────────────────────────────────────────────────
    if flags:
        st.markdown("---")
        _render_regulatory_flags(flags, country)

    st.markdown("---")

    # ── Recommendations ───────────────────────────────────────────────────
    if recs:
        _render_recommendations(recs)
        st.markdown("---")

    # ── Download ──────────────────────────────────────────────────────────
    if report_html:
        _sidebar()
        st.subheader("Download Your Report")
        st.markdown(
            "A complete HTML report with your pillar scores, recommendations, "
            "and regulatory compliance snapshot."
        )
        org_raw       = profile.get("institution_name", "report")
        org_sanitized = re.sub(r"[^A-Za-z0-9]", "_", org_raw).strip("_") or "report"
        date_str      = datetime.now().strftime("%Y%m%d")
        fname         = f"TechKative_Diagnostic_{org_sanitized}_{date_str}.html"
        try:
            _pdf_bytes = build_pdf_report(
                profile=profile, scores=scores,
                recommendations=recs, responses=responses,
                regulatory_flags=flags or [],
            )
            _pdf_ok = True
        except Exception:
            _pdf_bytes = None
            _pdf_ok = False
        col_html, col_pdf = st.columns(2)
        with col_html:
            if st.download_button(
                label="📥 Download HTML",
                data=report_html.encode("utf-8"),
                file_name=fname,
                mime="text/html",
                type="primary",
            ):
                st.session_state.report_downloaded = True
        with col_pdf:
            if _pdf_ok and _pdf_bytes:
                st.download_button(
                    label="📄 Download PDF",
                    data=_pdf_bytes,
                    file_name=fname.replace(".html", ".pdf"),
                    mime="application/pdf",
                    type="secondary",
                )
            else:
                st.caption("PDF unavailable (reportlab not installed).")
        if st.session_state.get("report_downloaded", False):
            st.success("✓ Report downloaded successfully. Check your Downloads folder.")
        st.caption(
            "After downloading, share the report by attaching it to an email or message. "
            "To request a new copy or delete your data, contact info@techkative.com."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stage 2 CTA ───────────────────────────────────────────────────────
    st.markdown(
        f'<div class="stage2-block">'
        f'<div style="font-size:16px;font-weight:700;color:{styles.SLATE};margin-bottom:10px;">'
        "Recommended Next Step: Stage 2 Diagnostic Engagement"
        "</div>"
        f'<p style="font-size:14px;color:{styles.MUTED};line-height:1.7;margin-bottom:0;">'
        "This diagnostic provides a first-pass profile of your institution's AI-readiness posture. "
        "A Stage 2 Engagement with Tech-Kative offers a structured deep-dive: facilitated sessions "
        "with your leadership team, gap analysis against sector benchmarks, and a prioritised "
        "roadmap for your specific operating context."
        "</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if not state.email_was_sent():
        with st.form("stage2_form", clear_on_submit=False):
            st.markdown(
                f'<p style="font-size:13px;font-weight:700;color:{styles.SLATE};margin-bottom:4px;">'
                "Send your report and request a Stage 2 conversation</p>",
                unsafe_allow_html=True,
            )
            s2_name    = st.text_input("Your name",     value=profile.get("contact_name", ""))
            s2_email   = st.text_input("Email address", value=profile.get("contact_email", ""))
            s2_message = st.text_area(
                "Message (optional)",
                placeholder="Tell us briefly about your institution's context or questions.",
                height=100,
            )
            submitted = st.form_submit_button(
                "Send Request and Receive Report →", type="primary"
            )

        if submitted:
            with st.spinner("Sending your report…"):
                send_profile = {**profile, "contact_name": s2_name, "contact_email": s2_email}
                respondent_ok, _ = send_all(
                    profile=send_profile,
                    scores=scores,
                    report_html=report_html or "",
                )
            if respondent_ok:
                state.mark_email_sent()
                state.go("email_sent")
            else:
                st.error(
                    "There was a problem sending your report. "
                    "Download it using the button above and contact info@techkative.com."
                )
    else:
        st.success("Your report has been sent. Check your inbox.")

    _footer()


# ---------------------------------------------------------------------------
# Screen 7 — Email Sent
# ---------------------------------------------------------------------------

def screen_email_sent():
    _header()
    _pilot_banner()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Thank you.")
    st.markdown(
        f'<p style="font-size:16px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "Your readiness profile and request have been received."
        "</p>",
        unsafe_allow_html=True,
    )

    profile = state.get_profile()
    scores  = state.get_scores()

    if scores:
        st.markdown(
            f'<p style="font-size:15px;color:{styles.SLATE};line-height:1.7;">'
            f"Your composite score is <strong>{scores['composite']:.0f} / 100</strong>, "
            f"placing <strong>{profile.get('institution_name', 'your institution')}</strong> "
            f"at the <strong>{scores['tier']}</strong> tier."
            f"</p>",
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="background:{styles.WASH};border-radius:8px;padding:20px 24px;'
        f'margin:20px 0;border:1px solid {styles.BORDER};">'
        f'<p style="font-size:14px;color:{styles.SLATE};margin:0 0 10px;font-weight:700;">'
        "What happens next</p>"
        f'<ul style="font-size:14px;color:{styles.MUTED};line-height:1.9;margin:0;padding-left:18px;">'
        f"<li>Your HTML report has been sent to {profile.get('contact_email', 'your email address')}.</li>"
        f"<li>A Tech-Kative advisor will be in touch within 2 business days.</li>"
        f"<li>You can also download your report directly from the previous screen.</li>"
        f"</ul></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:14px;color:{styles.MUTED};">'
        f"Questions? Contact us at "
        f'<a href="mailto:info@techkative.com" style="color:{styles.PRIMARY};">info@techkative.com</a>.'
        f"</p>",
        unsafe_allow_html=True,
    )

    _footer()


# ---------------------------------------------------------------------------
# Screen — SMKit Diary: Instant Diagnostic (Objective A)
# ---------------------------------------------------------------------------

_SMKIT_SEV_COLOURS = {"high": "#c0392b", "medium": "#d68910", "low": "#239b56"}
_SMKIT_TYPE_LABELS = {"RISK": "⚠ Risk", "GAP": "◎ Gap", "TREND": "↗ Trend"}


def _mode_tabs():
    """Two-button mode switcher rendered at the top of welcome and SMKit screens."""
    mode = st.session_state.get("app_mode", "questionnaire")
    col_q, col_s = st.columns(2)
    with col_q:
        if st.button(
            "📋  Questionnaire",
            type="primary" if mode != "smkit" else "secondary",
            use_container_width=True,
            key="mode_btn_q",
        ):
            st.session_state.app_mode = "questionnaire"
            st.rerun()
    with col_s:
        if st.button(
            "📊  SMKit Instant Diagnostic",
            type="primary" if mode == "smkit" else "secondary",
            use_container_width=True,
            key="mode_btn_s",
        ):
            st.session_state.app_mode = "smkit"
            st.rerun()
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


def screen_smkit():
    _header()
    _mode_tabs()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">SMKit Diary — Instant Diagnostic</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## School Readiness from Your Diary Data")
    st.markdown(
        f'<p style="font-size:14px;color:{styles.MUTED};line-height:1.7;">'
        "Upload a JSON or CSV export from the Standbasis SMKit Headteacher Diary (one school, "
        "one or more weeks). The engine runs offline — no data leaves your browser."
        "</p>",
        unsafe_allow_html=True,
    )

    _sample_path = Path(__file__).parent / "sample_smkit_entries.json"
    if _sample_path.exists():
        st.download_button(
            "📥 Download sample data (3 weeks, one school)",
            data=_sample_path.read_bytes(),
            file_name="sample_smkit_entries.json",
            mime="application/json",
            type="secondary",
            help="Save this file to your device, then upload it below to see a live demo.",
        )

    st.markdown(
        f'<p style="font-size:12px;color:{styles.MUTED};margin-top:4px;">'
        "⚠ Upload the SMKit diary JSON/CSV — <strong>not</strong> your downloaded diagnostic "
        "report (HTML) or questionnaire draft (JSON)."
        "</p>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload SMKit diary export (JSON or CSV)",
        type=["json", "csv"],
        key="smkit_uploader",
    )

    if uploaded is None:
        st.info("Upload a file above to see your school's instant diagnostic report.")
        _footer()
        return

    # Pre-check: reject HTML files before attempting parse
    _peek = uploaded.read(64)
    uploaded.seek(0)
    if _peek.lstrip().startswith(b"<") or uploaded.name.lower().endswith(".html"):
        st.error(
            "Wrong file uploaded. This appears to be an HTML diagnostic report, not an "
            "SMKit diary export.\n\n"
            "Click **'📥 Download sample data'** above, save the JSON file to your device, "
            "then upload that file here."
        )
        _footer()
        return

    try:
        entries = _smkit_load(uploaded)
    except ValueError as e:
        st.error(str(e))
        _footer()
        return

    if not entries:
        st.warning("No valid diary entries found in the uploaded file.")
        _footer()
        return

    diag   = analyse_school(entries)
    report = build_feedback_report(diag)

    # ── Performance score ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    perf       = report["performance_score"]
    perf_delta = report["perf_delta"]
    delta_txt  = (
        f" (+{perf_delta:.1f} vs last week)" if perf_delta and perf_delta > 0
        else (f" ({perf_delta:.1f} vs last week)" if perf_delta and perf_delta < 0 else "")
    )
    tier_colour = styles.GREEN if perf >= 75 else (styles.AMBER if perf >= 50 else "#c0392b")
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{styles.NAVY} 0%,{styles.NAVY_MID} 100%);'
        f'border-radius:8px;padding:24px 32px;margin-bottom:20px;display:flex;align-items:center;gap:28px;">'
        f'<div><div style="font-size:52px;font-weight:700;color:{styles.WHITE};line-height:1;">'
        f'{perf:.0f}</div>'
        f'<div style="font-size:13px;color:#a89cc8;margin-top:2px;">/100 performance{delta_txt}</div>'
        f'</div>'
        f'<div><div style="font-size:14px;font-weight:700;color:#c4a8e0;margin-bottom:4px;">'
        f'{report["school_name"]}</div>'
        f'<div style="font-size:13px;color:#a89cc8;">Week ending {report["week_ending"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Readiness radar ───────────────────────────────────────────────────
    st.markdown("### AI-Readiness Profile")
    st.plotly_chart(report["radar_fig"], use_container_width=True)

    # Pillar score tiles
    rcols = st.columns(4)
    pids  = ["p1", "p2", "p3", "p4"]
    pnames = ["Data Foundations", "Governance", "AI Readiness", "Responsible"]
    pcolours = [styles.PRIMARY, styles.NAVY, styles.GREEN, styles.AMBER]
    for i, (pid, pname, pc) in enumerate(zip(pids, pnames, pcolours)):
        score  = report["readiness_scores"].get(pid, 0)
        rdelta = report["readiness_deltas"].get(pid)
        with rcols[i]:
            d_str = (f"+{rdelta:.0f}" if rdelta and rdelta > 0
                     else (f"{rdelta:.0f}" if rdelta else "—"))
            st.markdown(
                f'<div style="background:{styles.WHITE};border-radius:6px;border-top:3px solid {pc};'
                f'padding:14px 16px;box-shadow:0 1px 4px rgba(0,0,0,0.07);text-align:center;">'
                f'<div style="font-size:10px;font-weight:700;text-transform:uppercase;color:{styles.MUTED};">'
                f'{pname}</div>'
                f'<div style="font-size:24px;font-weight:700;color:{styles.SLATE};">{score:.0f}</div>'
                f'<div style="font-size:10px;color:{styles.MUTED};">/100 &nbsp;·&nbsp; {d_str}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Flags ─────────────────────────────────────────────────────────────
    if report["flags"]:
        st.markdown("---")
        st.markdown("### Flags")
        for flag in report["flags"]:
            colour   = _SMKIT_SEV_COLOURS.get(flag.severity, styles.MUTED)
            type_lbl = _SMKIT_TYPE_LABELS.get(flag.type, flag.type)
            st.markdown(
                f'<div style="padding:10px 14px;background:{styles.WASH};border-radius:6px;'
                f'margin-bottom:8px;border-left:4px solid {colour};">'
                f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.05em;color:{colour};">{type_lbl} · {flag.severity.upper()}</span>'
                f'<div style="font-size:13px;color:{styles.SLATE};margin-top:4px;line-height:1.6;">'
                f'{flag.message}</div>'
                f'<div style="font-size:11px;color:{styles.MUTED};margin-top:3px;">Evidence: {flag.evidence}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Trend summary ─────────────────────────────────────────────────────
    if report["trend_summary"]:
        st.markdown(
            f'<p style="font-size:13px;font-style:italic;color:{styles.MUTED};margin-top:8px;">'
            f'{report["trend_summary"]}</p>',
            unsafe_allow_html=True,
        )

    # ── Next steps ────────────────────────────────────────────────────────
    if report["next_steps"]:
        st.markdown("---")
        st.markdown("### What to do next")
        for step in report["next_steps"]:
            st.markdown(
                f'<div style="padding:10px 14px;background:{styles.WASH};border-radius:6px;'
                f'margin-bottom:8px;font-size:13px;color:{styles.SLATE};line-height:1.65;'
                f'border-left:3px solid {styles.PRIMARY};">{step}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Questionnaire", type="secondary"):
        st.session_state.pop("smkit_uploader", None)
        st.session_state.app_mode = "questionnaire"
        st.rerun()

    _footer()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

_SCREENS = {
    "welcome":    screen_welcome_consent,
    "profile":    screen_profile,
    "pillars":    screen_assessment,   # canonical name per v3.0 spec
    "assessment": screen_assessment,   # legacy alias (saved sessions, draft files)
    "review":     screen_review,
    "results":    screen_results,
    "email_sent": screen_email_sent,
    "smkit":      screen_smkit,
}

current_screen = st.session_state.get("screen", "welcome")
if current_screen == "welcome":
    if st.session_state.get("app_mode") == "smkit":
        screen_smkit()
    else:
        screen_welcome_consent()
else:
    _SCREENS.get(current_screen, screen_welcome_consent)()
