"""Unit tests for scoring.py — pillar scores, composite, tier, and score summary."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from framework import PILLARS
from scoring import compute_pillar_scores, compute_composite, compute_score_summary


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def uniform_responses(score_map: dict) -> dict:
    """
    Build a full 24-item responses dict.
    score_map: {pillar_id: score_1_to_5}; missing pillars default to 3.
    """
    responses = {}
    for pillar in PILLARS:
        pid = pillar["id"]
        score = score_map.get(pid, 3)
        for item in pillar["items"]:
            responses[item["id"]] = score
    return responses


def all_scores(score: int) -> dict:
    """All 24 items set to the same score."""
    return uniform_responses({"p1": score, "p2": score, "p3": score, "p4": score})


# ---------------------------------------------------------------------------
# compute_pillar_scores
# ---------------------------------------------------------------------------

class TestComputePillarScores:
    def test_all_ones_yields_twenty(self):
        scores = compute_pillar_scores(all_scores(1))
        for pid in ["p1", "p2", "p3", "p4"]:
            assert scores[pid] == pytest.approx(20.0)

    def test_all_fives_yields_hundred(self):
        scores = compute_pillar_scores(all_scores(5))
        for pid in ["p1", "p2", "p3", "p4"]:
            assert scores[pid] == pytest.approx(100.0)

    def test_all_threes_yields_sixty(self):
        scores = compute_pillar_scores(all_scores(3))
        for pid in ["p1", "p2", "p3", "p4"]:
            assert scores[pid] == pytest.approx(60.0)

    def test_mixed_pillar_scores(self):
        responses = uniform_responses({"p1": 4, "p2": 2, "p3": 3, "p4": 1})
        scores = compute_pillar_scores(responses)
        assert scores["p1"] == pytest.approx(80.0)
        assert scores["p2"] == pytest.approx(40.0)
        assert scores["p3"] == pytest.approx(60.0)
        assert scores["p4"] == pytest.approx(20.0)

    def test_formula_mean_times_scale_factor(self):
        # 6 items: scores 1,2,3,4,5,3 → mean=3.0 → score=60
        responses = {}
        pillar = PILLARS[0]  # p1
        scores_list = [1, 2, 3, 4, 5, 3]
        for item, s in zip(pillar["items"], scores_list):
            responses[item["id"]] = s
        # Fill other pillars with 3
        for p in PILLARS[1:]:
            for item in p["items"]:
                responses[item["id"]] = 3
        result = compute_pillar_scores(responses)
        assert result["p1"] == pytest.approx(60.0)

    def test_empty_responses_yields_zero(self):
        scores = compute_pillar_scores({})
        for pid in ["p1", "p2", "p3", "p4"]:
            assert scores[pid] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# compute_composite
# ---------------------------------------------------------------------------

class TestComputeComposite:
    def test_uniform_composite(self):
        pillar_scores = {"p1": 60.0, "p2": 60.0, "p3": 60.0, "p4": 60.0}
        assert compute_composite(pillar_scores) == pytest.approx(60.0)

    def test_mixed_composite(self):
        pillar_scores = {"p1": 80.0, "p2": 40.0, "p3": 60.0, "p4": 20.0}
        assert compute_composite(pillar_scores) == pytest.approx(50.0)

    def test_unweighted_mean(self):
        # Composite is unweighted mean of 4 pillar scores regardless of item count
        pillar_scores = {"p1": 100.0, "p2": 20.0, "p3": 60.0, "p4": 60.0}
        assert compute_composite(pillar_scores) == pytest.approx(60.0)


# ---------------------------------------------------------------------------
# Tier assignment (via compute_score_summary)
# ---------------------------------------------------------------------------

class TestTierAssignment:
    def _tier_for_uniform_score(self, score: int) -> str:
        return compute_score_summary(all_scores(score))["tier"]

    def test_all_ones_is_pre_foundational(self):
        assert self._tier_for_uniform_score(1) == "Pre-foundational"

    def test_all_twos_is_foundational(self):
        # all 2s → pillar scores = 40, composite = 40 → Foundational
        assert self._tier_for_uniform_score(2) == "Foundational"

    def test_all_threes_is_developing(self):
        # all 3s → pillar scores = 60, composite = 60 → Developing
        assert self._tier_for_uniform_score(3) == "Developing"

    def test_all_fives_is_mature(self):
        # all 5s → pillar scores = 100, composite = 100 → Mature
        assert self._tier_for_uniform_score(5) == "Mature"

    def test_tier_boundary_foundational_lower(self):
        # composite = 40 → Foundational (lower boundary)
        summary = compute_score_summary(all_scores(2))
        assert summary["composite"] == pytest.approx(40.0)
        assert summary["tier"] == "Foundational"

    def test_tier_boundary_developing_lower(self):
        # composite = 60 → Developing (lower boundary)
        summary = compute_score_summary(all_scores(3))
        assert summary["composite"] == pytest.approx(60.0)
        assert summary["tier"] == "Developing"

    def test_tier_boundary_mature_lower(self):
        # composite = 80 → Mature (lower boundary)
        summary = compute_score_summary(all_scores(4))
        assert summary["composite"] == pytest.approx(80.0)
        assert summary["tier"] == "Mature"


# ---------------------------------------------------------------------------
# compute_score_summary — structural validation
# ---------------------------------------------------------------------------

class TestScoreSummaryStructure:
    def test_required_keys_present(self):
        summary = compute_score_summary(all_scores(3))
        expected_keys = {
            "pillar_scores",
            "composite",
            "tier",
            "lowest_pillar_key",
            "lowest_pillar_name",
            "lowest_item_in_lowest_pillar",
            "highest_pillar_key",
            "spread",
        }
        assert expected_keys == set(summary.keys())

    def test_lowest_item_has_required_fields(self):
        summary = compute_score_summary(all_scores(3))
        li = summary["lowest_item_in_lowest_pillar"]
        assert "id" in li
        assert "short_label" in li
        assert "score" in li

    def test_lowest_pillar_key_is_correct(self):
        responses = uniform_responses({"p1": 4, "p2": 1, "p3": 3, "p4": 3})
        summary = compute_score_summary(responses)
        assert summary["lowest_pillar_key"] == "p2"

    def test_highest_pillar_key_is_correct(self):
        responses = uniform_responses({"p1": 5, "p2": 2, "p3": 3, "p4": 3})
        summary = compute_score_summary(responses)
        assert summary["highest_pillar_key"] == "p1"

    def test_spread_calculation(self):
        responses = uniform_responses({"p1": 5, "p2": 1, "p3": 3, "p4": 3})
        summary = compute_score_summary(responses)
        # p1=100, p2=20 → spread = 80
        assert summary["spread"] == pytest.approx(80.0)

    def test_spread_zero_when_uniform(self):
        summary = compute_score_summary(all_scores(3))
        assert summary["spread"] == pytest.approx(0.0)

    def test_lowest_item_belongs_to_lowest_pillar(self):
        responses = uniform_responses({"p1": 4, "p2": 1, "p3": 3, "p4": 3})
        summary = compute_score_summary(responses)
        assert summary["lowest_pillar_key"] == "p2"
        li = summary["lowest_item_in_lowest_pillar"]
        assert li["id"].startswith("2.")

    def test_lowest_item_score_is_minimum_in_pillar(self):
        # Make p2 items have mixed scores — lowest should be the item with score 1
        responses = {}
        for pillar in PILLARS:
            pid = pillar["id"]
            for i, item in enumerate(pillar["items"]):
                if pid == "p2":
                    responses[item["id"]] = 1 if i == 0 else 3
                else:
                    responses[item["id"]] = 4
        summary = compute_score_summary(responses)
        assert summary["lowest_pillar_key"] == "p2"
        li = summary["lowest_item_in_lowest_pillar"]
        assert li["score"] == 1
