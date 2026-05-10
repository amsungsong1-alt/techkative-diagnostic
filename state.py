"""
Tech-Kative AI-Readiness Diagnostic — Session State Helpers

All reads and writes to st.session_state go through these helpers.
Keeps app.py clean and makes state shape explicit.
"""

import streamlit as st
from framework import all_item_ids, PILLAR_ORDER


# ---------------------------------------------------------------------------
# Canonical screen names
# ---------------------------------------------------------------------------

SCREENS = ["welcome", "profile", "assessment", "review", "results", "email_sent"]


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init() -> None:
    """Initialise all session state keys if not already present. Call once at app startup."""
    defaults = {
        "screen":       "welcome",
        "item_index":   0,
        "profile": {
            "institution_name": "",
            "institution_type": "",
            "country":          "",
            "contact_name":     "",
            "contact_email":    "",
            "role":             "",
        },
        "responses":     {},   # {item_id: int 1–5}
        "scores":        None, # set after assessment completion
        "observations":  None, # list[str], set with scores
        "roadmap":       None, # dict, set with scores
        "email_sent":    False,
        "report_html":   None, # str, cached for download
        "draft_loaded":  False,
        "profile_errors": {},  # {field_key: error_message} for inline validation
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
    """Navigate to a specific assessment item (0-based index)."""
    st.session_state.item_index = index
    st.session_state.screen = "assessment"
    st.rerun()


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

def get_response(item_id: str):
    """Return the stored score for an item, or None if not answered."""
    return st.session_state.responses.get(item_id)


def set_response(item_id: str, score: int) -> None:
    st.session_state.responses[item_id] = score


def all_answered() -> bool:
    """True if all 24 items have a recorded response."""
    ids = all_item_ids()
    return all(iid in st.session_state.responses for iid in ids)


def answered_count() -> int:
    return len(st.session_state.responses)


def total_items() -> int:
    return len(all_item_ids())


# ---------------------------------------------------------------------------
# Scores and observations
# ---------------------------------------------------------------------------

def get_scores() -> dict:
    return st.session_state.scores


def set_scores(scores: dict) -> None:
    st.session_state.scores = scores


def get_observations() -> list:
    return st.session_state.observations or []


def set_observations(observations: list) -> None:
    st.session_state.observations = observations


def get_roadmap():
    return st.session_state.roadmap


def set_roadmap(roadmap: dict) -> None:
    st.session_state.roadmap = roadmap


# ---------------------------------------------------------------------------
# Report HTML (cached for download button)
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
# Utility: item_index accessors
# ---------------------------------------------------------------------------

def current_item_index() -> int:
    return st.session_state.item_index


def set_item_index(index: int) -> None:
    st.session_state.item_index = index


# ---------------------------------------------------------------------------
# Draft save / load
# ---------------------------------------------------------------------------

def build_draft_payload() -> dict:
    """Serialise current progress for download as a JSON draft file."""
    return {
        "version": 1,
        "item_index": st.session_state.item_index,
        "responses": st.session_state.responses,
        "profile": st.session_state.profile,
    }


def load_draft_payload(payload: dict) -> bool:
    """
    Load a previously saved draft into session state.
    Returns True if valid and applied, False otherwise.
    """
    if not isinstance(payload, dict):
        return False
    if payload.get("version") != 1:
        return False
    responses = payload.get("responses", {})
    if not isinstance(responses, dict):
        return False
    for v in responses.values():
        if not isinstance(v, int) or v < 1 or v > 5:
            return False
    item_index = payload.get("item_index", 0)
    if not isinstance(item_index, int) or item_index < 0:
        return False
    st.session_state.responses = responses
    st.session_state.item_index = item_index
    if isinstance(payload.get("profile"), dict):
        st.session_state.profile = payload["profile"]
    st.session_state.draft_loaded = True
    return True
