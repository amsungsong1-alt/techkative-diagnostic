"""Unit tests for scoring.py v2 — yes_no_partial / likert engine."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from scoring import (
    compute_pillar_scores,
    compute_composite,
    compute_score_summary,
    generate_recommendations,
    generate_regulatory_flags,
    all_scored_answered,
)


def _all_yes(country="Ghana"):
    from framework import get_scored_questions
    r = {}
    for q in get_scored_questions(country):
        r[q["id"]] = "Yes" if q["type"] == "yes_no_partial" else "Leading"
    return r


def _all_no(country="Ghana"):
    from framework import get_scored_questions
    r = {}
    for q in get_scored_questions(country):
        r[q["id"]] = "No" if q["type"] == "yes_no_partial" else "Not yet"
    return r


class TestComputePillarScores:

    def test_all_yes_leading_yields_100(self):
        scores = compute_pillar_scores(_all_yes("Ghana"), "Ghana")
        for pid, s in scores.items():
            assert s == pytest.approx(100.0), f"{pid} should be 100"

    def test_all_no_yields_zero(self):
        scores = compute_pillar_scores(_all_no("Ghana"), "Ghana")
        for pid, s in scores.items():
            assert s == pytest.approx(0.0), f"{pid} should be 0"

    def test_empty_responses_yields_zero(self):
        scores = compute_pillar_scores({}, "Ghana")
        for s in scores.values():
            assert s == 0.0

    def test_returns_all_four_pillars(self):
        assert set(compute_pillar_scores({}, "Ghana").keys()) == {"p1", "p2", "p3", "p4"}

    def test_ghana_ignores_nigeria_questions(self):
        # Only answer Nigeria-specific questions; Ghana-specific left blank.
        # Ghana's p2 should be 0 since no Ghana-applicable scored questions answered.
        r = {"gp_5_ng": "Yes", "gp_6_ng": "Yes"}
        assert compute_pillar_scores(r, "Ghana")["p2"] == pytest.approx(0.0)

    def test_nigeria_ignores_ghana_questions(self):
        # Only answer Ghana-specific questions; Nigeria-specific left blank.
        r = {"gp_5_gh": "Yes", "gp_6_gh": "Yes"}
        assert compute_pillar_scores(r, "Nigeria")["p2"] == pytest.approx(0.0)


class TestComputeComposite:

    def test_uniform_100(self):
        assert compute_composite({"p1": 100, "p2": 100, "p3": 100, "p4": 100}) == 100.0

    def test_uniform_0(self):
        assert compute_composite({"p1": 0, "p2": 0, "p3": 0, "p4": 0}) == 0.0

    def test_unweighted_mean(self):
        assert compute_composite({"p1": 100, "p2": 0, "p3": 0, "p4": 0}) == pytest.approx(25.0)


class TestTierAssignment:

    def test_all_no_is_emerging(self):
        assert compute_score_summary(_all_no("Ghana"), "Ghana")["tier"] == "Emerging"

    def test_all_yes_is_leading(self):
        assert compute_score_summary(_all_yes("Ghana"), "Ghana")["tier"] == "Leading"


class TestScoreSummaryStructure:

    def test_required_keys_present(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        required = {"pillar_scores", "composite", "tier", "pillar_tiers",
                    "lowest_pillar_key", "highest_pillar_key", "spread"}
        assert required.issubset(scores.keys())

    def test_pillar_tiers_has_all_four_pillars(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        assert set(scores["pillar_tiers"].keys()) == {"p1", "p2", "p3", "p4"}

    def test_spread_zero_when_uniform(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        assert scores["spread"] == pytest.approx(0.0, abs=0.01)

    def test_lowest_and_highest_are_valid_pillar_keys(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        assert scores["lowest_pillar_key"] in {"p1", "p2", "p3", "p4"}
        assert scores["highest_pillar_key"] in {"p1", "p2", "p3", "p4"}


class TestGenerateRecommendations:

    def test_returns_all_four_pillars(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        recs = generate_recommendations(scores)
        assert set(recs.keys()) == {"p1", "p2", "p3", "p4"}

    def test_each_pillar_has_three_items(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        for pid, r in generate_recommendations(scores).items():
            assert len(r["items"]) == 3

    def test_leading_tier_for_all_yes(self):
        scores = compute_score_summary(_all_yes("Ghana"), "Ghana")
        for r in generate_recommendations(scores).values():
            assert r["tier"] == "Leading"

    def test_emerging_tier_for_all_no(self):
        scores = compute_score_summary(_all_no("Ghana"), "Ghana")
        for r in generate_recommendations(scores).values():
            assert r["tier"] == "Emerging"

    def test_items_are_non_empty_strings(self):
        scores = compute_score_summary(_all_no("Ghana"), "Ghana")
        for r in generate_recommendations(scores).values():
            for item in r["items"]:
                assert isinstance(item, str) and len(item) > 10


class TestRegulatoryFlags:

    def test_no_flags_when_all_yes_ghana(self):
        assert generate_regulatory_flags(_all_yes("Ghana"), "Ghana") == []

    def test_ghana_flag_when_gp5_no(self):
        r = _all_yes("Ghana")
        r["gp_5_gh"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Ghana")]
        assert any("DPC registration" in l for l in labels)

    def test_ghana_flag_when_gp6_no(self):
        r = _all_yes("Ghana")
        r["gp_6_gh"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Ghana")]
        assert any("Privacy Seal" in l for l in labels)

    def test_nigeria_flag_when_gp5_partial(self):
        r = _all_yes("Nigeria")
        r["gp_5_ng"] = "Partial"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Nigeria")]
        assert any("NDPC" in l for l in labels)

    def test_nigeria_flag_when_gp6_no(self):
        r = _all_yes("Nigeria")
        r["gp_6_ng"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Nigeria")]
        assert any("DPO" in l or "Data Protection Officer" in l for l in labels)

    def test_nigeria_flag_when_gp7_no(self):
        r = _all_yes("Nigeria")
        r["gp_7_ng"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Nigeria")]
        assert any("DPIA" in l for l in labels)

    def test_nigeria_flag_when_gp8_no(self):
        r = _all_yes("Nigeria")
        r["gp_8_ng"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Nigeria")]
        assert any("RoPA" in l or "Record of Processing" in l for l in labels)

    def test_sovereignty_flag_when_rd5_no(self):
        r = _all_yes("Ghana")
        r["rd_5"] = "No"
        labels = [f["label"] for f in generate_regulatory_flags(r, "Ghana")]
        assert any("sovereignty" in l.lower() for l in labels)

    def test_ghana_does_not_get_nigeria_flags(self):
        labels = [f["label"] for f in generate_regulatory_flags(_all_no("Ghana"), "Ghana")]
        assert not any("NDPC" in l for l in labels)


class TestAllScoredAnswered:

    def test_true_when_all_answered(self):
        assert all_scored_answered(_all_yes("Ghana"), "Ghana")

    def test_false_when_empty(self):
        assert not all_scored_answered({}, "Ghana")

    def test_open_text_not_required(self):
        r = _all_yes("Ghana")
        for ot in ("df_6", "gp_7", "ar_6", "rd_6"):
            r.pop(ot, None)
        assert all_scored_answered(r, "Ghana")
