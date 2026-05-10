"""
Tech-Kative AI-Readiness Diagnostic — Main Application

Entry point. Initialises session state, injects CSS, and routes to the
correct screen based on st.session_state.screen.
"""

import json
import os
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

import state
import styles
from email_service import send_all
from framework import INSTITUTION_TYPES, PILLARS, PILLAR_ORDER, all_item_ids, get_pillar
from report import build_report
from scoring import compute_score_summary, generate_observations, generate_roadmap

load_dotenv()


def _load_streamlit_secrets():
    """
    Bridge st.secrets → os.environ so email_service.py stays Streamlit-free.
    On Streamlit Community Cloud, credentials live in st.secrets (configured
    in the Cloud dashboard). Locally they live in .env / os.environ.
    This function copies any missing vars from st.secrets without overwriting
    anything already set by .env.
    """
    _KEYS = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS",
             "FROM_ADDRESS", "TECHKATIVE_INBOX"]
    try:
        for key in _KEYS:
            if key not in os.environ and hasattr(st, "secrets") and key in st.secrets:
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass  # st.secrets not available (e.g. bare import during tests)


# ---------------------------------------------------------------------------
# Page configuration (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI-Readiness Diagnostic — Tech-Kative",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Global setup
# ---------------------------------------------------------------------------

styles.inject_styles()
state.init()
_load_streamlit_secrets()

# Flat ordered list of all 24 items
ALL_ITEMS = [item for pillar in PILLARS for item in pillar["items"]]
TOTAL_ITEMS = len(ALL_ITEMS)

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
        f'<span>Tech-Kative · AI-Readiness Diagnostic</span>'
        f'<span>AI readiness. African context.</span>'
        f"</div>",
        unsafe_allow_html=True,
    )


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
# Screen 1 — Welcome
# ---------------------------------------------------------------------------

def screen_welcome():
    _header()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Institutional Self-Assessment</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## AI-Readiness Diagnostic")
    st.markdown(
        f'<p style="font-size:16px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "A structured instrument for African education institutions to assess their readiness "
        "to govern, deploy, and absorb artificial intelligence responsibly."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="font-size:14px;color:{styles.SLATE};line-height:1.7;">'
        "This diagnostic assesses your institution across four pillars — 24 items in total. "
        "Each item is calibrated against current practice, not aspiration. "
        "Allow approximately <strong>25 minutes</strong> of uninterrupted time. "
        "Your responses are not stored on our servers; your completed profile is delivered by email."
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
    st.markdown("---")

    col_cta, col_space = st.columns([2, 3])
    with col_cta:
        if st.button("Begin the Diagnostic →", type="primary", use_container_width=True):
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
                    "This file does not appear to be a valid Tech-Kative diagnostic draft. "
                    "Please check you have uploaded the correct file."
                )
        except Exception:
            st.error("Could not read the uploaded file. Please ensure it is a valid JSON draft.")

    _footer()


# ---------------------------------------------------------------------------
# Screen 2 — Institutional Profile
# ---------------------------------------------------------------------------

def screen_profile():
    _header()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Step 1 of 2</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Institutional Profile")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "This information is used to personalise your report and to contact you "
        "with your results. Institution name and email address are required."
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
        placeholder="e.g. Lagos State University",
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

    country = st.text_input(
        "Country",
        value=prof.get("country", ""),
        placeholder="e.g. Nigeria",
    )

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
        placeholder="e.g. Deputy Vice-Chancellor (Academic)",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_back, col_fwd = st.columns([1, 2])

    with col_back:
        if st.button("← Back", type="secondary", use_container_width=True):
            st.session_state.profile_errors = {}
            state.go("welcome")

    with col_fwd:
        proceed = st.button(
            "Continue to Assessment →", type="primary", use_container_width=True
        )

    if proceed:
        new_errors = {}
        if not institution_name.strip():
            new_errors["institution_name"] = "Institution name is required."
        if institution_type == "— Select —":
            new_errors["institution_type"] = "Please select an institution type."
        if not contact_email.strip():
            new_errors["contact_email"] = "Email address is required."
        elif "@" not in contact_email or "." not in contact_email.split("@")[-1]:
            new_errors["contact_email"] = "Please enter a valid email address."

        st.session_state.profile_errors = new_errors

        if not new_errors:
            state.set_profile(
                {
                    "institution_name": institution_name.strip(),
                    "institution_type": institution_type,
                    "country":          country.strip(),
                    "contact_name":     contact_name.strip(),
                    "contact_email":    contact_email.strip(),
                    "role":             role.strip(),
                }
            )
            state.go("assessment")
        else:
            st.rerun()

    _footer()


# ---------------------------------------------------------------------------
# Screen 3 — Assessment (one item per render)
# ---------------------------------------------------------------------------

def screen_assessment():
    _header()

    item_index = state.current_item_index()
    item       = ALL_ITEMS[item_index]
    item_id    = item["id"]
    pillar     = get_pillar(item["pillar_id"])
    colour     = pillar["colour"]

    # ── Progress ──────────────────────────────────────────────────────────
    answered = state.answered_count()
    st.progress(answered / TOTAL_ITEMS)
    st.markdown(
        f'<p style="font-size:12px;color:{styles.MUTED};margin-top:4px;">'
        f'<strong>{answered}</strong> of {TOTAL_ITEMS} items answered'
        f' &nbsp;·&nbsp; Item {item_index + 1} of {TOTAL_ITEMS}'
        f' &nbsp;·&nbsp; Pillar: {pillar["name"]}'
        f"</p>",
        unsafe_allow_html=True,
    )

    # ── Pillar tag ────────────────────────────────────────────────────────
    st.markdown(
        f'<span class="pillar-tag" style="background:{colour};">{pillar["name"]}</span>',
        unsafe_allow_html=True,
    )

    # ── Question ──────────────────────────────────────────────────────────
    st.markdown(f"### {item['question']}")
    st.markdown(
        f'<p class="help-text">{item["help_text"]}</p>',
        unsafe_allow_html=True,
    )

    # ── Radio options ─────────────────────────────────────────────────────
    options = [opt["label"] for opt in item["options"]]
    stored_score = state.get_response(item_id)
    stored_index = (stored_score - 1) if stored_score is not None else None

    selected_label = st.radio(
        "Select one option:",
        options=options,
        index=stored_index,
        key=f"radio_{item_id}",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Navigation ────────────────────────────────────────────────────────
    col_prev, col_next = st.columns(2)

    with col_prev:
        prev_label = "← Previous" if item_index > 0 else "← Back to Profile"
        prev_btn = st.button(prev_label, key="btn_prev", type="secondary", use_container_width=True)

    with col_next:
        next_label = "Continue →" if item_index < TOTAL_ITEMS - 1 else "Review Responses →"
        next_btn = st.button(next_label, key="btn_next", type="primary", use_container_width=True)

    # ── Button handlers ───────────────────────────────────────────────────
    if next_btn:
        if selected_label is None:
            st.error("Please select one of the options above before continuing.")
        else:
            score = next(
                opt["score"] for opt in item["options"] if opt["label"] == selected_label
            )
            state.set_response(item_id, score)
            if item_index + 1 >= TOTAL_ITEMS:
                state.go("review")
            else:
                state.set_item_index(item_index + 1)
                st.rerun()

    if prev_btn:
        if item_index == 0:
            state.go("profile")
        else:
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

    _footer()


# ---------------------------------------------------------------------------
# Screen 4 — Review
# ---------------------------------------------------------------------------

def screen_review():
    _header()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<p style="font-size:12px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{styles.PRIMARY};">Step 2 of 2 — Review</p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Review Your Responses")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};line-height:1.7;">'
        "Check your responses below. Select Edit on any item to return to it and change your answer. "
        "When you are satisfied, submit the assessment to receive your profile."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    responses    = st.session_state.responses
    global_index = 0

    for pillar in PILLARS:
        colour = pillar["colour"]
        st.markdown(
            f'<div style="font-size:12px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:{colour};margin:20px 0 8px;">'
            f"{pillar['name']} — {len(pillar['items'])} items</div>",
            unsafe_allow_html=True,
        )

        for item in pillar["items"]:
            stored_score = responses.get(item["id"])
            if stored_score:
                option_label  = item["options"][stored_score - 1]["label"]
                answered_flag = f"{stored_score}/5"
            else:
                option_label  = "Not yet answered"
                answered_flag = "—"

            col_content, col_edit = st.columns([5, 1])
            with col_content:
                st.markdown(
                    f'<div style="padding:8px 0;border-bottom:1px solid {styles.BORDER};">'
                    f'<div style="font-size:12px;font-weight:700;color:{styles.MUTED};">'
                    f"Item {item['id']} &nbsp;·&nbsp; {item['short_label']}"
                    f' &nbsp;<span style="color:{colour};font-weight:700;">[{answered_flag}]</span>'
                    f"</div>"
                    f'<div style="font-size:12px;color:{styles.SLATE};margin-top:3px;">'
                    f"{option_label}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            with col_edit:
                if st.button("Edit", key=f"edit_{item['id']}"):
                    state.go_to_item(global_index)

            global_index += 1

    st.markdown("<br>", unsafe_allow_html=True)

    missing = [iid for iid in all_item_ids() if iid not in responses]
    if missing:
        st.warning(
            f"{len(missing)} item(s) have not yet been answered. "
            "Please complete all items before submitting."
        )

    col_back, col_submit = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Assessment", type="secondary", use_container_width=True):
            state.set_item_index(TOTAL_ITEMS - 1)
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
    p = scores["pillar_scores"]
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
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color=styles.MUTED),
                gridcolor=styles.BORDER,
                linecolor=styles.BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color=styles.SLATE),
                gridcolor=styles.BORDER,
                linecolor=styles.BORDER,
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
        height=340,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


_ROADMAP_BAND_LABELS = {"low": "Foundation-building", "mid": "Consolidating", "high": "Advancing"}


def _render_roadmap(roadmap: dict) -> None:
    st.markdown("### Recommended Actions by Pillar")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};margin-bottom:16px;">'
        "The following actions are calibrated to your score in each pillar. "
        "Select one or two per pillar and complete them before adding more."
        "</p>",
        unsafe_allow_html=True,
    )
    for pid in PILLAR_ORDER:
        pillar = get_pillar(pid)
        colour = styles.PILLAR_COLOURS[pid]
        r = roadmap[pid]
        band_label = _ROADMAP_BAND_LABELS[r["band"]]
        st.markdown(
            f'<div style="margin-bottom:24px;border-left:3px solid {colour};padding-left:16px;">'
            f'<div style="font-size:12px;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:{colour};margin-bottom:6px;">'
            f'{pillar["name"]} &nbsp;·&nbsp; Score {r["score"]:.0f} &nbsp;·&nbsp; {band_label}'
            f"</div>",
            unsafe_allow_html=True,
        )
        for i, action in enumerate(r["items"], start=1):
            st.markdown(
                f'<div style="padding:10px 14px;background:{styles.WASH};border-radius:6px;'
                f'margin-bottom:8px;font-size:13px;line-height:1.65;color:{styles.SLATE};">'
                f'<strong style="color:{colour};">{i}.</strong> {action}'
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Screen 5 — Results
# ---------------------------------------------------------------------------

def screen_results():
    _header()

    # ── Compute on first render only ──────────────────────────────────────
    if state.get_scores() is None:
        with st.spinner("Computing your readiness profile…"):
            responses    = st.session_state.responses
            scores       = compute_score_summary(responses)
            observations = generate_observations(scores)
            roadmap      = generate_roadmap(scores)
            report_html  = build_report(
                profile=state.get_profile(),
                scores=scores,
                observations=observations,
                responses=responses,
                roadmap=roadmap,
            )
            state.set_scores(scores)
            state.set_observations(observations)
            state.set_roadmap(roadmap)
            state.set_report_html(report_html)

    scores       = state.get_scores()
    observations = state.get_observations()
    roadmap      = state.get_roadmap()
    profile      = state.get_profile()
    report_html  = state.get_report_html()

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
        with cols[i]:
            st.markdown(
                f'<div class="score-tile" style="border-top-color:{colour};">'
                f'<div class="score-tile-name">{pillar["short_name"]}</div>'
                f'<div class="score-tile-value">{score:.0f}'
                f'<span class="score-tile-denom">/100</span></div>'
                + _score_bar_html(score, colour)
                + "</div>",
                unsafe_allow_html=True,
            )

    # ── Radar chart ───────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _render_radar(scores)

    st.markdown("---")

    # ── Narrative observations ────────────────────────────────────────────
    st.markdown("### Profile Observations")
    st.markdown(
        f'<p style="font-size:14px;font-style:italic;color:{styles.MUTED};margin-bottom:16px;">'
        "The following observations reflect your specific response pattern."
        "</p>",
        unsafe_allow_html=True,
    )
    for obs in observations:
        st.markdown(
            f'<div class="obs-card">{obs}</div>',
            unsafe_allow_html=True,
        )

    # ── Per-pillar roadmap ────────────────────────────────────────────────
    if roadmap:
        st.markdown("---")
        _render_roadmap(roadmap)

    st.markdown("---")

    # ── Download ──────────────────────────────────────────────────────────
    if report_html:
        fname = (
            "tech-kative-diagnostic-"
            + profile.get("institution_name", "report").lower().replace(" ", "-").replace(",", "")
            + ".html"
        )
        st.download_button(
            label="Download Report (HTML)",
            data=report_html.encode("utf-8"),
            file_name=fname,
            mime="text/html",
            type="secondary",
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
                "Request a Stage 2 conversation</p>",
                unsafe_allow_html=True,
            )
            s2_name    = st.text_input("Your name",     value=profile.get("contact_name", ""))
            s2_email   = st.text_input("Email address", value=profile.get("contact_email", ""))
            s2_message = st.text_area(
                "Message (optional)",
                placeholder=(
                    "Tell us briefly about your institution's context, "
                    "current priorities, or any specific questions."
                ),
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
# Screen 6 — Email Sent
# ---------------------------------------------------------------------------

def screen_email_sent():
    _header()

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
        composite = scores["composite"]
        tier      = scores["tier"]
        st.markdown(
            f'<p style="font-size:15px;color:{styles.SLATE};line-height:1.7;">'
            f"Your composite score is <strong>{composite:.0f} / 100</strong>, "
            f"placing <strong>{profile.get('institution_name', 'your institution')}</strong> "
            f"at the <strong>{tier}</strong> tier."
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
        f"<li>A Tech-Kative advisor will be in touch within 2 business days to discuss your profile.</li>"
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
# Router
# ---------------------------------------------------------------------------

_SCREENS = {
    "welcome":    screen_welcome,
    "profile":    screen_profile,
    "assessment": screen_assessment,
    "review":     screen_review,
    "results":    screen_results,
    "email_sent": screen_email_sent,
}

current_screen = st.session_state.get("screen", "welcome")
_SCREENS.get(current_screen, screen_welcome)()
