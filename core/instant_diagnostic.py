"""
Tech-Kative Diagnostic — SMKit Instant Diagnostic Engine

Pure-Python, offline-capable. No external API calls.
All weights and thresholds are in the CONFIG block below — tune without touching logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.smkit_ingest import DiaryEntry

# ---------------------------------------------------------------------------
# CONFIG — all weights and thresholds in one place
# ---------------------------------------------------------------------------

CONFIG = {
    # Performance score weights (must sum to 1.0)
    "perf_attendance_weight":   0.50,
    "perf_staff_weight":        0.30,
    "perf_delivery_weight":     0.20,

    # Readiness: Data Foundations (p1) — record_keeping scores (0–100)
    "rk_scores": {
        "digital_system": 100,
        "spreadsheet":     67,
        "paper":           33,
        "none":             0,
    },

    # Readiness: Governance (p2) — sub-weights (must sum to 1.0)
    "gov_consent_weight":   0.40,
    "gov_storage_weight":   0.40,
    "gov_safeguard_weight": 0.20,
    # data_storage scores (0–100)
    "storage_scores": {
        "cloud":           100,
        "school_device":    80,
        "personal_device":  40,
        "paper":            20,
        "none":              0,
    },
    # safeguarding: 0 incidents = full score; each incident reduces by this amount
    "safeguard_penalty_per_incident": 25,

    # Readiness: AI Readiness (p3) — sub-weights
    "ai_tools_weight":        0.50,
    "ai_digitisation_weight": 0.50,
    # meaningful ai_tools_used: any non-empty, non-"none" entry scores full
    "ai_tools_score_if_used": 100,

    # Readiness: Responsible Deployment (p4) — sub-weights
    "resp_policy_weight":   0.50,
    "resp_consent_weight":  0.30,
    "resp_safeguard_weight": 0.20,

    # Risk thresholds
    "attendance_risk_threshold": 0.70,
    "staff_risk_threshold":      0.80,
}

# ---------------------------------------------------------------------------
# Flag dataclass
# ---------------------------------------------------------------------------

@dataclass
class Flag:
    type:     str   # "RISK" | "GAP" | "TREND"
    pillar:   str   # pillar_id or "performance"
    severity: str   # "high" | "medium" | "low"
    message:  str
    evidence: str


@dataclass
class SchoolDiagnostic:
    school_id:         str
    school_name:       str
    week_ending:       date
    performance_score: float
    readiness_scores:  dict[str, float]   # pillar_id → 0–100
    perf_delta:        float | None       # vs prior week, None if first week
    readiness_deltas:  dict[str, float | None]
    flags:             list[Flag]
    next_steps:        list[str]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def score_performance(entry: "DiaryEntry") -> float:
    attendance = _safe_rate(entry.attendance_present, entry.enrolment)
    staff      = _safe_rate(entry.staff_present, entry.staff_total)
    delivery   = _safe_rate(entry.lessons_delivered, entry.lessons_planned)
    raw = (
        CONFIG["perf_attendance_weight"] * attendance
        + CONFIG["perf_staff_weight"]    * staff
        + CONFIG["perf_delivery_weight"] * delivery
    )
    return round(min(100.0, max(0.0, raw * 100)), 1)


def score_readiness(entry: "DiaryEntry") -> dict[str, float]:
    rk = CONFIG["rk_scores"].get(entry.record_keeping, 0)

    # p2 Governance
    consent_score   = 100.0 if entry.consent_on_file else 0.0
    storage_score   = float(CONFIG["storage_scores"].get(entry.data_storage, 0))
    safeguard_score = max(0.0, 100.0 - entry.safeguarding_incidents * CONFIG["safeguard_penalty_per_incident"])
    p2 = (
        CONFIG["gov_consent_weight"]   * consent_score
        + CONFIG["gov_storage_weight"] * storage_score
        + CONFIG["gov_safeguard_weight"] * safeguard_score
    )

    # p3 AI Readiness
    meaningful_tools = [t for t in entry.ai_tools_used if t and t.lower() not in ("none", "")]
    ai_tool_score = float(CONFIG["ai_tools_score_if_used"]) if meaningful_tools else 0.0
    digitisation_score = float(CONFIG["rk_scores"].get(entry.record_keeping, 0))
    p3 = (
        CONFIG["ai_tools_weight"]        * ai_tool_score
        + CONFIG["ai_digitisation_weight"] * digitisation_score
    )

    # p4 Responsible Deployment
    policy_score = 100.0 if entry.ai_policy_in_place else 0.0
    p4 = (
        CONFIG["resp_policy_weight"]     * policy_score
        + CONFIG["resp_consent_weight"]  * consent_score
        + CONFIG["resp_safeguard_weight"] * safeguard_score
    )

    return {
        "p1": round(float(rk), 1),
        "p2": round(p2, 1),
        "p3": round(p3, 1),
        "p4": round(p4, 1),
    }


# ---------------------------------------------------------------------------
# Flagging
# ---------------------------------------------------------------------------

def flag_entry(entry: "DiaryEntry", history: list["DiaryEntry"]) -> list[Flag]:
    flags: list[Flag] = []

    att_rate  = _safe_rate(entry.attendance_present, entry.enrolment)
    staff_rate = _safe_rate(entry.staff_present, entry.staff_total)

    # ── RISK flags ──
    if att_rate < CONFIG["attendance_risk_threshold"]:
        pct = f"{att_rate:.0%}"
        flags.append(Flag(
            type="RISK", pillar="performance", severity="high",
            message=f"Attendance rate is {pct} — below the {CONFIG['attendance_risk_threshold']:.0%} threshold.",
            evidence=f"attendance_present={entry.attendance_present}, enrolment={entry.enrolment}",
        ))

    if staff_rate < CONFIG["staff_risk_threshold"]:
        pct = f"{staff_rate:.0%}"
        flags.append(Flag(
            type="RISK", pillar="performance", severity="medium",
            message=f"Staff presence rate is {pct} — below the {CONFIG['staff_risk_threshold']:.0%} threshold.",
            evidence=f"staff_present={entry.staff_present}, staff_total={entry.staff_total}",
        ))

    if entry.safeguarding_incidents > 0:
        flags.append(Flag(
            type="RISK", pillar="p2", severity="high",
            message=f"{entry.safeguarding_incidents} safeguarding incident(s) recorded this week.",
            evidence=f"safeguarding_incidents={entry.safeguarding_incidents}",
        ))

    meaningful_tools = [t for t in entry.ai_tools_used if t and t.lower() not in ("none", "")]
    if meaningful_tools and not entry.consent_on_file:
        tools_str = ", ".join(meaningful_tools)
        flags.append(Flag(
            type="RISK", pillar="p2", severity="high",
            message=(
                f"AI tools in use ({tools_str}) without data-protection consent on file. "
                "This is a high-severity data-protection risk under Ghana's Data Protection "
                "Act, 2012 (Act 843 §18 — lawful processing basis) and Nigeria's NDPA 2023. "
                "Obtain and document consent immediately."
            ),
            evidence=f"ai_tools_used={entry.ai_tools_used}, consent_on_file=False",
        ))

    # ── GAP flags ──
    if entry.record_keeping in ("none", "paper"):
        flags.append(Flag(
            type="GAP", pillar="p1", severity="medium",
            message=f"Record-keeping is '{entry.record_keeping}' — a Data Foundations gap. Move to a spreadsheet or digital system.",
            evidence=f"record_keeping={entry.record_keeping}",
        ))

    if not entry.consent_on_file:
        flags.append(Flag(
            type="GAP", pillar="p2", severity="medium",
            message="No data-protection consent on file for learner data. Required under Act 843 §18 (Ghana) and NDPA 2023 (Nigeria).",
            evidence="consent_on_file=False",
        ))

    if not entry.ai_policy_in_place:
        flags.append(Flag(
            type="GAP", pillar="p4", severity="low",
            message="No AI policy in place. Without a written policy, responsible deployment cannot be demonstrated.",
            evidence="ai_policy_in_place=False",
        ))

    # ── TREND flags (require at least 2 prior weeks) ──
    prior = sorted(history, key=lambda e: e.week_ending)
    if len(prior) >= 2:
        _att_rates = [_safe_rate(e.attendance_present, e.enrolment) for e in prior]
        if all(_att_rates[i] > _att_rates[i + 1] for i in range(len(_att_rates) - 1)):
            weeks = len(prior)
            flags.append(Flag(
                type="TREND", pillar="performance", severity="high",
                message=f"Attendance has declined for {weeks + 1} consecutive weeks. Investigate causes immediately.",
                evidence=f"weekly rates: {[f'{r:.0%}' for r in _att_rates]} → {att_rate:.0%}",
            ))

        _del_rates = [_safe_rate(e.lessons_delivered, e.lessons_planned) for e in prior]
        if all(_del_rates[i] > _del_rates[i + 1] for i in range(len(_del_rates) - 1)):
            flags.append(Flag(
                type="TREND", pillar="p1", severity="medium",
                message=f"Lesson delivery rate has declined for {weeks + 1} consecutive weeks.",
                evidence=f"weekly rates: {[f'{r:.0%}' for r in _del_rates]}",
            ))

        # Positive trend: readiness improving
        if len(prior) >= 1:
            prev_rk = CONFIG["rk_scores"].get(prior[-1].record_keeping, 0)
            curr_rk = CONFIG["rk_scores"].get(entry.record_keeping, 0)
            if curr_rk > prev_rk:
                flags.append(Flag(
                    type="TREND", pillar="p1", severity="low",
                    message=f"Record-keeping improved from '{prior[-1].record_keeping}' to '{entry.record_keeping}' — positive readiness trend.",
                    evidence=f"prev={prior[-1].record_keeping}, current={entry.record_keeping}",
                ))

    return flags


# ---------------------------------------------------------------------------
# Next-step recommendations keyed to lowest pillar
# ---------------------------------------------------------------------------

_NEXT_STEPS: dict[str, list[str]] = {
    "p1": [
        "Adopt a shared digital spreadsheet for attendance, enrolment, and exam records.",
        "Appoint a data clerk or lead teacher responsible for record accuracy.",
        "Set a weekly check: all teachers submit records in the same format by Friday.",
    ],
    "p2": [
        "Obtain signed data-protection consent from parents/guardians before collecting or processing learner data.",
        "Register with Ghana's DPC (dataprotection.org.gh) or Nigeria's NDPC (ndpc.gov.ng) as required.",
        "Create a one-page data-protection policy and post it in the staff room.",
    ],
    "p3": [
        "Identify one specific problem AI could help solve — e.g., SMS alerts for absentees.",
        "Evaluate one AI tool critically: ask the vendor where data is stored and how consent is handled.",
        "Identify a staff member to oversee AI tool adoption and receive basic training.",
    ],
    "p4": [
        "Draft a one-page AI policy: what tools are permitted, who oversees them, and how decisions are reviewed.",
        "Ensure no AI tool is used without data-protection consent and a human review step.",
        "Create a simple complaints process for students/parents to challenge AI-assisted decisions.",
    ],
}

_PILLAR_NAMES = {
    "p1": "Data Foundations",
    "p2": "Governance & Protection",
    "p3": "AI Readiness",
    "p4": "Responsible Deployment",
}


def _next_steps_for_lowest(readiness: dict[str, float]) -> list[str]:
    lowest = min(readiness, key=readiness.get)
    return _NEXT_STEPS.get(lowest, [])


# ---------------------------------------------------------------------------
# Top-level analysis
# ---------------------------------------------------------------------------

def analyse_school(entries: list["DiaryEntry"]) -> SchoolDiagnostic:
    """
    Sort entries by date, compute latest scores, deltas, flags, and next steps.
    Returns a SchoolDiagnostic for the most recent week.
    """
    sorted_entries = sorted(entries, key=lambda e: e.week_ending)
    latest = sorted_entries[-1]
    history = sorted_entries[:-1]

    perf  = score_performance(latest)
    ready = score_readiness(latest)
    flags = flag_entry(latest, history)

    # Sort flags: high → medium → low, then RISK → GAP → TREND
    sev_order  = {"high": 0, "medium": 1, "low": 2}
    type_order = {"RISK": 0, "GAP": 1, "TREND": 2}
    flags.sort(key=lambda f: (sev_order[f.severity], type_order[f.type]))

    # Deltas vs prior week
    perf_delta: float | None = None
    ready_deltas: dict[str, float | None] = {p: None for p in ("p1", "p2", "p3", "p4")}
    if history:
        prev = history[-1]
        prev_perf  = score_performance(prev)
        prev_ready = score_readiness(prev)
        perf_delta = round(perf - prev_perf, 1)
        ready_deltas = {p: round(ready[p] - prev_ready[p], 1) for p in ready}

    return SchoolDiagnostic(
        school_id=latest.school_id,
        school_name=latest.school_name,
        week_ending=latest.week_ending,
        performance_score=perf,
        readiness_scores=ready,
        perf_delta=perf_delta,
        readiness_deltas=ready_deltas,
        flags=flags,
        next_steps=_next_steps_for_lowest(ready),
    )
