"""
Tech-Kative AI-Readiness Diagnostic v2 — Session State Helpers

All reads and writes to st.session_state go through these helpers.
"""

import streamlit as st
from framework import PILOT_CODES, get_scored_questions


# ---------------------------------------------------------------------------
# Canonical screen names
# ---------------------------------------------------------------------------

SCREENS = ["welcome", "consent", "profile", "assessment", "review", "results", "email_sent"]


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init() -> None:
    """Initialise all session state keys if not already present."""
    defaults = {
        "screen":           "welcome",
        "item_index":       0,
        "profile": {
            "institution_name": "",
            "institution_type": "",
            "country":          "",
            "contact_name":     "",
            "contact_email":    "",
            "role":             "",
            "pilot_code":       "",
            "assessment_phase": "",
        },
        "responses":         {},    # {question_id: str (label)}
        "scores":            None,  # set after submission
        "recommendations":   None,  # dict, set with scores
        "regulatory_flags":  None,  # list[dict], set with scores
        "consent_given_at":  None,  # ISO timestamp str
        "pilot_code":        "",
        "assessment_phase":  "",    # "Baseline (Week 1)" | "Post-Pilot (Week 7)"
        "email_sent":        False,
        "report_html":       None,  # str, cached for download
        "draft_loaded":      False,
        "profile_errors":    {},    # {field_key: error_message}
        "completed_pillars": set(), # pillar_ids where all scored questions answered
        "navigation_target": None,  # "review" when editing from review page
        "last_saved_at":     None,  # HH:MM:SS timestamp of last response save
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Screen navigation
# ---------------------------------------------------------------------------

def go(screen: str) -> None:
    st.session_state.screen = screen
    st.rerun()


def go_to_item(index: int) -> None:
    st.session_state.item_index = index
    st.session_state.screen = "assessment"
    st.rerun()


# ---------------------------------------------------------------------------
# Consent
# ---------------------------------------------------------------------------

def get_consent():
    return st.session_state.consent_given_at


def set_consent(ts: str) -> None:
    st.session_state.consent_given_at = ts


def has_consented() -> bool:
    return bool(st.session_state.consent_given_at)


# ---------------------------------------------------------------------------
# Pilot mode
# ---------------------------------------------------------------------------

def get_pilot_code() -> str:
    return st.session_state.pilot_code


def set_pilot_code(code: str) -> None:
    st.session_state.pilot_code = code


def is_pilot_mode() -> bool:
    return st.session_state.pilot_code.upper() in {c.upper() for c in PILOT_CODES}


def get_assessment_phase() -> str:
    return st.session_state.assessment_phase


def set_assessment_phase(phase: str) -> None:
    st.session_state.assessment_phase = phase


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def get_profile() -> dict:
    return st.session_state.profile


def set_profile(profile: dict) -> None:
    st.session_state.profile = profile


def profile_complete() -> bool:
    p = st.session_state.profile
    return bool(p.get("institution_name") and p.get("contact_email"))


# ---------------------------------------------------------------------------
# Assessment responses
# ---------------------------------------------------------------------------

def get_response(question_id: str):
    return st.session_state.responses.get(question_id)


def set_response(question_id: str, value) -> None:
    st.session_state.responses[question_id] = value


def answered_count(country: str = "") -> int:
    """Count answered scored questions for the given country."""
    if not country:
        country = st.session_state.profile.get("country", "")
    scored_ids = {q["id"] for q in get_scored_questions(country)}
    return sum(1 for qid in scored_ids if qid in st.session_state.responses)


def total_scored(country: str = "") -> int:
    if not country:
        country = st.session_state.profile.get("country", "")
    return len(get_scored_questions(country))


def all_answered(country: str = "") -> bool:
    if not country:
        country = st.session_state.profile.get("country", "")
    scored_ids = {q["id"] for q in get_scored_questions(country)}
    return all(qid in st.session_state.responses for qid in scored_ids)


# ---------------------------------------------------------------------------
# Scores and results
# ---------------------------------------------------------------------------

def get_scores() -> dict:
    return st.session_state.scores


def set_scores(scores: dict) -> None:
    st.session_state.scores = scores


def get_recommendations():
    return st.session_state.recommendations


def set_recommendations(recs) -> None:
    st.session_state.recommendations = recs


def get_regulatory_flags():
    return st.session_state.regulatory_flags


def set_regulatory_flags(flags) -> None:
    st.session_state.regulatory_flags = flags


# ---------------------------------------------------------------------------
# Report HTML
# ---------------------------------------------------------------------------

def get_report_html():
    return st.session_state.report_html


def set_report_html(html: str) -> None:
    st.session_state.report_html = html


# ---------------------------------------------------------------------------
# Email status
# ---------------------------------------------------------------------------

def mark_email_sent() -> None:
    st.session_state.email_sent = True


def email_was_sent() -> bool:
    return st.session_state.email_sent


# ---------------------------------------------------------------------------
# Item index
# ---------------------------------------------------------------------------

def current_item_index() -> int:
    return st.session_state.item_index


def set_item_index(index: int) -> None:
    st.session_state.item_index = index


# ---------------------------------------------------------------------------
# Draft save / load
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Completed pillars + navigation target (Priority 2)
# ---------------------------------------------------------------------------

def get_completed_pillars() -> set:
    return st.session_state.completed_pillars


def mark_pillar_complete(pillar_id: str) -> None:
    st.session_state.completed_pillars.add(pillar_id)


def get_navigation_target():
    return st.session_state.navigation_target


def set_navigation_target(target: str) -> None:
    st.session_state.navigation_target = target


def clear_navigation_target() -> None:
    st.session_state.navigation_target = None


# ---------------------------------------------------------------------------
# Autosave timestamp (Priority 5)
# ---------------------------------------------------------------------------

def set_last_saved() -> None:
    from datetime import datetime
    st.session_state.last_saved_at = datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Draft save / load
# ---------------------------------------------------------------------------

def build_draft_payload() -> dict:
    return {
        "version":          2,
        "item_index":       st.session_state.item_index,
        "responses":        st.session_state.responses,
        "profile":          st.session_state.profile,
        "pilot_code":       st.session_state.pilot_code,
        "assessment_phase": st.session_state.assessment_phase,
    }


def load_draft_payload(payload: dict) -> bool:
    if not isinstance(payload, dict):
        return False
    if payload.get("version") not in (1, 2):
        return False
    responses = payload.get("responses", {})
    if not isinstance(responses, dict):
        return False
    item_index = payload.get("item_index", 0)
    if not isinstance(item_index, int) or item_index < 0:
        return False
    st.session_state.responses = responses
    st.session_state.item_index = item_index
    if isinstance(payload.get("profile"), dict):
        st.session_state.profile = payload["profile"]
    if payload.get("pilot_code"):
        st.session_state.pilot_code = payload["pilot_code"]
    if payload.get("assessment_phase"):
        st.session_state.assessment_phase = payload["assessment_phase"]
    st.session_state.draft_loaded = True
    return True
