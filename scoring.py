"""
Tech-Kative AI-Readiness Diagnostic v2 — Scoring Engine

Pure functions only. No Streamlit dependency. Fully unit-testable.

Public API:
    compute_score_summary(responses, country)  -> dict
    generate_recommendations(scores)           -> dict
    generate_regulatory_flags(responses, country) -> list[dict]
"""

from framework import (
    PILLARS,
    PILLAR_ORDER,
    RECOMMENDATIONS,
    YES_NO_SCORES,
    LIKERT_SCORES,
    get_scored_questions,
    get_tier,
)


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def compute_pillar_scores(responses: dict, country: str) -> dict:
    """
    responses: {question_id: str} — label chosen by the user.
    country:   used to include country-conditional questions.
    Returns {pillar_id: float} in 0-100 range.
    """
    scored_qs = get_scored_questions(country)
    scores = {}
    for pillar in PILLARS:
        pid = pillar["id"]
        pillar_qs = [q for q in scored_qs if q["pillar_id"] == pid]
        raw = []
        for q in pillar_qs:
            ans = responses.get(q["id"])
            if ans is None:
                continue
            if q["type"] == "yes_no_partial":
                raw.append(YES_NO_SCORES.get(ans, 0.0))
            elif q["type"] == "likert":
                raw.append(LIKERT_SCORES.get(ans, 0.0))
        scores[pid] = (sum(raw) / len(raw) * 100) if raw else 0.0
    return scores


def compute_composite(pillar_scores: dict) -> float:
    """Unweighted mean of the four pillar scores."""
    vals = [pillar_scores[pid] for pid in PILLAR_ORDER]
    return sum(vals) / len(vals)


def compute_score_summary(responses: dict, country: str) -> dict:
    """
    Returns the canonical scores dict consumed by the app, report, and db.

    Shape:
        {
            "pillar_scores":   dict[str, float],   # 0-100 per pillar
            "composite":       float,               # 0-100
            "tier":            str,                 # composite tier label
            "pillar_tiers":    dict[str, str],      # per-pillar tier labels
            "lowest_pillar_key":  str,
            "highest_pillar_key": str,
            "spread":          float,
        }
    """
    pillar_scores = compute_pillar_scores(responses, country)
    composite = compute_composite(pillar_scores)
    tier = get_tier(composite)["label"]

    pillar_tiers = {pid: get_tier(pillar_scores[pid])["label"] for pid in PILLAR_ORDER}
    lowest_pillar_key  = min(PILLAR_ORDER, key=lambda pid: pillar_scores[pid])
    highest_pillar_key = max(PILLAR_ORDER, key=lambda pid: pillar_scores[pid])
    spread = pillar_scores[highest_pillar_key] - pillar_scores[lowest_pillar_key]

    return {
        "pillar_scores":      pillar_scores,
        "composite":          composite,
        "tier":               tier,
        "pillar_tiers":       pillar_tiers,
        "lowest_pillar_key":  lowest_pillar_key,
        "highest_pillar_key": highest_pillar_key,
        "spread":             spread,
    }


# ---------------------------------------------------------------------------
# Recommendations (tier-based, replaces old rule-based observation engine)
# ---------------------------------------------------------------------------

def generate_recommendations(scores: dict) -> dict:
    """
    Return per-pillar recommendations based on each pillar's tier.

    Returns:
        {pid: {"tier": str, "score": float, "items": list[str]}}
    """
    p = scores["pillar_scores"]
    recs = {}
    for pid in PILLAR_ORDER:
        score = p[pid]
        tier = get_tier(score)["label"]
        recs[pid] = {
            "tier":  tier,
            "score": score,
            "items": RECOMMENDATIONS[pid][tier],
        }
    return recs


# ---------------------------------------------------------------------------
# Regulatory compliance flags
# ---------------------------------------------------------------------------

def generate_regulatory_flags(responses: dict, country: str) -> list:
    """
    Returns a list of flag dicts: [{"label": str, "description": str}]
    based on responses to country-specific governance questions and rd_5.
    """
    flags = []

    if country == "Ghana":
        if responses.get("gp_5_gh") in ("No", "Partial"):
            flags.append({
                "label": "DPC registration under Act 843 §27",
                "description": "not confirmed",
            })
        if responses.get("gp_6_gh") == "No":
            flags.append({
                "label": "DPC Privacy Seal",
                "description": "application not in progress",
            })

    elif country == "Nigeria":
        if responses.get("gp_5_ng") in ("No", "Partial"):
            flags.append({
                "label": "NDPC registration / DCPMI classification",
                "description": "not confirmed",
            })
        if responses.get("gp_6_ng") in ("No", "Partial"):
            flags.append({
                "label": "Data Protection Officer (DPO)",
                "description": "not formally designated",
            })
        if responses.get("gp_7_ng") in ("No", "Partial"):
            flags.append({
                "label": "Data Protection Impact Assessment (DPIA)",
                "description": "not completed for high-risk processing activities (GAID 2025)",
            })
        if responses.get("gp_8_ng") in ("No", "Partial"):
            flags.append({
                "label": "Record of Processing Activities (RoPA)",
                "description": "not maintained or not updated biannually (NDPA 2023 / GAID 2025)",
            })

    if responses.get("rd_5") == "No":
        flags.append({
            "label": "Data sovereignty",
            "description": (
                "institution data not stored on locally governed infrastructure "
                "(Africa Declaration on AI alignment gap — Kigali, 4 April 2025)"
            ),
        })

    return flags


# ---------------------------------------------------------------------------
# Progress helper (used by state.py / app.py)
# ---------------------------------------------------------------------------

def count_answered(responses: dict, country: str) -> int:
    """Count how many scored questions have been answered."""
    from framework import get_scored_questions
    ids = {q["id"] for q in get_scored_questions(country)}
    return sum(1 for qid in ids if qid in responses)


def all_scored_answered(responses: dict, country: str) -> bool:
    """True if every scored question has a response."""
    from framework import all_scored_question_ids
    return all(qid in responses for qid in all_scored_question_ids(country))
