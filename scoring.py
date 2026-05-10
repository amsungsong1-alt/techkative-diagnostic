"""
Tech-Kative AI-Readiness Diagnostic — Scoring Engine

Pure functions only. No Streamlit dependency. Fully unit-testable.

Public API:
    compute_score_summary(responses) -> dict
    generate_observations(scores)    -> list[str]
"""

from framework import (
    PILLARS,
    PILLAR_ORDER,
    OBSERVATION_RULES,
    PILLAR_ROADMAPS,
    SCORE_SCALE_FACTOR,
    get_pillar,
    get_tier,
    items_for_pillar,
)

# Leverage text for R6 — resolved by highest pillar key
_LEVERAGE_TEXT = {
    "p1": (
        "governance discipline applied to data policies can be extended to include "
        "data quality standards and ownership assignments — converting policy "
        "infrastructure into data management infrastructure."
    ),
    "p2": (
        "data quality and standardisation practices can inform the evidence base "
        "for AI procurement decisions and provide the substrate evidence that "
        "ethics review processes need to assess bias and representativeness."
    ),
    "p3": (
        "organisational change management capability can be applied to ethics "
        "policy rollout and data governance adoption — turning procedural "
        "capacity into governance reach."
    ),
    "p4": (
        "ethical review disciplines — bias assessment, recourse path design, "
        "stakeholder consultation — can be extended to govern data quality "
        "decisions and AI procurement criteria, embedding ethics at the "
        "front end of the procurement cycle."
    ),
}


# ---------------------------------------------------------------------------
# Core scoring functions
# ---------------------------------------------------------------------------

def compute_pillar_scores(responses: dict) -> dict:
    """
    responses: {item_id: int} where int is 1–5.
    Returns {pillar_id: float} — pillar score in 20–100 range.
    Missing responses default to 0 in the mean (treated as absent items).
    """
    scores = {}
    for pillar in PILLARS:
        pid = pillar["id"]
        item_ids = [item["id"] for item in pillar["items"]]
        item_scores = [responses[iid] for iid in item_ids if iid in responses]
        if item_scores:
            scores[pid] = (sum(item_scores) / len(item_scores)) * SCORE_SCALE_FACTOR
        else:
            scores[pid] = 0.0
    return scores


def compute_composite(pillar_scores: dict) -> float:
    """Unweighted mean of the four pillar scores."""
    vals = [pillar_scores[pid] for pid in PILLAR_ORDER]
    return sum(vals) / len(vals)


def compute_score_summary(responses: dict) -> dict:
    """
    Takes the raw responses dict and returns the canonical scores dict
    consumed by generate_observations(), report.py, and app.py.

    Shape:
        {
            "pillar_scores":                dict[str, float],
            "composite":                    float,
            "tier":                         str,
            "lowest_pillar_key":            str,
            "lowest_pillar_name":           str,
            "lowest_item_in_lowest_pillar": {"id": str, "short_label": str, "score": int},
            "highest_pillar_key":           str,
            "spread":                       float,
        }
    """
    pillar_scores = compute_pillar_scores(responses)
    composite = compute_composite(pillar_scores)
    tier = get_tier(composite)["label"]

    lowest_pillar_key = min(PILLAR_ORDER, key=lambda pid: pillar_scores[pid])
    highest_pillar_key = max(PILLAR_ORDER, key=lambda pid: pillar_scores[pid])
    spread = pillar_scores[highest_pillar_key] - pillar_scores[lowest_pillar_key]
    lowest_pillar_name = get_pillar(lowest_pillar_key)["name"]

    lowest_pillar_items = items_for_pillar(lowest_pillar_key)
    lowest_item = min(
        lowest_pillar_items,
        key=lambda item: responses.get(item["id"], 6),
    )
    lowest_item_score = responses.get(lowest_item["id"], 1)

    return {
        "pillar_scores": pillar_scores,
        "composite": composite,
        "tier": tier,
        "lowest_pillar_key": lowest_pillar_key,
        "lowest_pillar_name": lowest_pillar_name,
        "lowest_item_in_lowest_pillar": {
            "id": lowest_item["id"],
            "short_label": lowest_item["short_label"],
            "score": lowest_item_score,
        },
        "highest_pillar_key": highest_pillar_key,
        "spread": spread,
    }


# ---------------------------------------------------------------------------
# Observation rule engine
# ---------------------------------------------------------------------------

def generate_roadmap(scores: dict) -> dict:
    """
    Return per-pillar actionable roadmap items based on score band.

    Args:
        scores: output of compute_score_summary()

    Returns:
        {p1..p4: {"band": "low"|"mid"|"high", "score": float, "items": list[str]}}
    """
    p = scores["pillar_scores"]
    roadmap = {}
    for pid in PILLAR_ORDER:
        score = p[pid]
        if score < 50:
            band = "low"
        elif score < 75:
            band = "mid"
        else:
            band = "high"
        roadmap[pid] = {
            "band": band,
            "score": score,
            "items": PILLAR_ROADMAPS[pid][band],
        }
    return roadmap


def generate_observations(scores: dict) -> list:
    """
    Deterministic rule engine. Evaluates R1–R6 in order.
    Always returns 2–4 observation strings.

    Rules:
        R1 — always fires (lowest pillar + item spotlight)
        R2 — p1 >= 60 AND p2 < 50 (policy strong, data weak)
        R3 — p1 - p4 >= 20 (ethics below governance)
        R4 — p3 is lowest AND composite >= 50 AND composite - p3 >= 15
        R5 — forced fallback when R2/R3/R4 all miss; also fires when spread < 15
        R6 — highest pillar >= 70 AND spread >= 20 (leverage strongest pillar)
    """
    p = scores["pillar_scores"]
    composite = scores["composite"]
    tier = scores["tier"]
    spread = scores["spread"]
    lowest_key = scores["lowest_pillar_key"]
    li = scores["lowest_item_in_lowest_pillar"]

    observations = []
    r2_fired = r3_fired = r4_fired = False

    # R1 — unconditional
    r1 = OBSERVATION_RULES[0]
    observations.append(
        r1["template"].format(
            LOWEST_PILLAR_NAME=scores["lowest_pillar_name"],
            LOWEST_PILLAR_SCORE=f"{p[lowest_key]:.0f}",
            LOWEST_ITEM_SHORT_LABEL=li["short_label"],
            LOWEST_ITEM_ID=li["id"],
            LOWEST_ITEM_SCORE=li["score"],
        )
    )

    # R2 — policy strong, data weak
    r2 = OBSERVATION_RULES[1]
    if p["p1"] >= 60 and p["p2"] < 50:
        gap = p["p1"] - p["p2"]
        observations.append(
            r2["template"].format(
                P1_SCORE=f"{p['p1']:.0f}",
                P2_SCORE=f"{p['p2']:.0f}",
                GAP=f"{gap:.0f}",
            )
        )
        r2_fired = True

    # R3 — ethics below governance
    r3 = OBSERVATION_RULES[2]
    if p["p1"] - p["p4"] >= 20:
        observations.append(
            r3["template"].format(
                P4_SCORE=f"{p['p4']:.0f}",
                P1_SCORE=f"{p['p1']:.0f}",
                P1_MINUS_P4=f"{p['p1'] - p['p4']:.0f}",
            )
        )
        r3_fired = True

    # R4 — capacity drag on an otherwise strong profile
    r4 = OBSERVATION_RULES[3]
    if (
        lowest_key == "p3"
        and composite >= 50
        and (composite - p["p3"]) >= 15
    ):
        drag = composite - p["p3"]
        observations.append(
            r4["template"].format(
                TIER=tier,
                COMPOSITE=f"{composite:.0f}",
                P3_SCORE=f"{p['p3']:.0f}",
                DRAG=f"{drag:.0f}",
            )
        )
        r4_fired = True

    # R5 — balanced profile; forced fallback to guarantee >= 2 observations
    r5 = OBSERVATION_RULES[4]
    if not (r2_fired or r3_fired or r4_fired):
        variant = "A" if composite >= 60 else "B"
        observations.append(
            r5["template"][variant].format(
                SPREAD=f"{spread:.0f}",
                COMPOSITE=f"{composite:.0f}",
                TIER=tier,
            )
        )

    # R6 — highest pillar as cross-pillar leverage point
    r6 = OBSERVATION_RULES[5]
    highest_key = scores["highest_pillar_key"]
    if p[highest_key] >= 70 and spread >= 20 and len(observations) < 4:
        highest_pillar = get_pillar(highest_key)
        observations.append(
            r6["template"].format(
                HIGHEST_PILLAR_NAME=highest_pillar["name"],
                HIGHEST_PILLAR_SCORE=f"{p[highest_key]:.0f}",
                HIGHEST_PILLAR_SHORT=highest_pillar["short_name"],
                HIGHEST_PILLAR_LEVERAGE_TEXT=_LEVERAGE_TEXT[highest_key],
            )
        )

    return observations[:4]
