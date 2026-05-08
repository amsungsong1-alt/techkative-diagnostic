"""Unit tests for the observation rule engine in scoring.py."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from framework import PILLARS
from scoring import compute_score_summary, generate_observations


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def uniform_responses(score_map: dict) -> dict:
    responses = {}
    for pillar in PILLARS:
        pid = pillar["id"]
        score = score_map.get(pid, 3)
        for item in pillar["items"]:
            responses[item["id"]] = score
    return responses


def all_scores(score: int) -> dict:
    return uniform_responses({"p1": score, "p2": score, "p3": score, "p4": score})


def observations_for(score_map: dict) -> list:
    responses = uniform_responses(score_map)
    scores = compute_score_summary(responses)
    return generate_observations(scores)


# ---------------------------------------------------------------------------
# R1 — always fires
# ---------------------------------------------------------------------------

class TestR1AlwaysFires:
    def test_r1_fires_for_all_ones(self):
        obs = observations_for({"p1": 1, "p2": 1, "p3": 1, "p4": 1})
        assert len(obs) >= 1
        # R1 mentions the lowest pillar name
        first = obs[0]
        assert "most acute development need" in first

    def test_r1_fires_for_all_fives(self):
        obs = observations_for({"p1": 5, "p2": 5, "p3": 5, "p4": 5})
        assert len(obs) >= 1
        assert "most acute development need" in obs[0]

    def test_r1_fires_for_mixed_scores(self):
        obs = observations_for({"p1": 4, "p2": 2, "p3": 3, "p4": 3})
        assert len(obs) >= 1
        assert "most acute development need" in obs[0]

    def test_r1_names_lowest_pillar(self):
        # p3 is lowest (score 1), others are 4 → R1 should mention Organisational Capacity
        obs = observations_for({"p1": 4, "p2": 4, "p3": 1, "p4": 4})
        assert "Organisational Capacity" in obs[0]

    def test_r1_names_data_foundations_when_lowest(self):
        obs = observations_for({"p1": 4, "p2": 1, "p3": 3, "p4": 3})
        assert "Data Foundations" in obs[0]

    def test_r1_includes_item_id(self):
        obs = observations_for({"p1": 4, "p2": 1, "p3": 3, "p4": 3})
        # Item IDs for p2 are 2.1–2.6
        assert any(f"2." in obs[0].split("Item ")[-1][:4] for _ in [1])

    def test_r1_includes_score_out_of_five(self):
        obs = observations_for({"p1": 4, "p2": 1, "p3": 3, "p4": 3})
        assert "/5" in obs[0]


# ---------------------------------------------------------------------------
# R2 — policy strong, data weak
# ---------------------------------------------------------------------------

class TestR2PolicyDataDivergence:
    def _r2_score_map(self):
        # p1=3 (60), p2=2 (40) → R2 fires; p3=3, p4=3
        return {"p1": 3, "p2": 2, "p3": 3, "p4": 3}

    def test_r2_fires_when_conditions_met(self):
        obs = observations_for(self._r2_score_map())
        assert any("divergence between Governance" in o for o in obs)

    def test_r2_mentions_governance_score(self):
        obs = observations_for(self._r2_score_map())
        r2 = next(o for o in obs if "divergence between Governance" in o)
        assert "60" in r2  # p1 score

    def test_r2_mentions_data_score(self):
        obs = observations_for(self._r2_score_map())
        r2 = next(o for o in obs if "divergence between Governance" in o)
        assert "40" in r2  # p2 score

    def test_r2_does_not_fire_when_p1_below_60(self):
        # p1=2 (40), p2=1 (20) → p1 < 60, R2 should NOT fire
        obs = observations_for({"p1": 2, "p2": 1, "p3": 3, "p4": 3})
        assert not any("divergence between Governance" in o for o in obs)

    def test_r2_does_not_fire_when_p2_above_50(self):
        # p1=4 (80), p2=3 (60) → p2 >= 50, R2 should NOT fire
        obs = observations_for({"p1": 4, "p2": 3, "p3": 3, "p4": 3})
        assert not any("divergence between Governance" in o for o in obs)

    def test_r2_includes_gap_calculation(self):
        # p1=4 (80), p2=2 (40) → gap = 40
        obs = observations_for({"p1": 4, "p2": 2, "p3": 3, "p4": 3})
        r2 = next((o for o in obs if "divergence between Governance" in o), None)
        assert r2 is not None
        assert "40" in r2  # the gap value


# ---------------------------------------------------------------------------
# R3 — ethics below governance
# ---------------------------------------------------------------------------

class TestR3EthicsBelowGovernance:
    def _r3_score_map(self):
        # p1=4 (80), p4=2 (40) → gap = 40 >= 20 → R3 fires
        return {"p1": 4, "p2": 3, "p3": 3, "p4": 2}

    def test_r3_fires_when_conditions_met(self):
        obs = observations_for(self._r3_score_map())
        assert any("Ethical Infrastructure" in o and "Governance & Policy" in o for o in obs)

    def test_r3_fires_with_minimal_gap(self):
        # Exact boundary: p1=4 (80), p4=3 (60) → gap=20, should fire
        obs = observations_for({"p1": 4, "p2": 3, "p3": 3, "p4": 3})
        # gap = 80-60 = 20, should fire
        assert any("Ethical Infrastructure" in o and "Governance & Policy" in o for o in obs)

    def test_r3_does_not_fire_when_gap_below_20(self):
        # p1=3 (60), p4=3 (60) → gap = 0 < 20
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        # No R3; R5 should fire instead (balanced)
        assert not any("Ethical Infrastructure" in o and "Governance & Policy" in o for o in obs)

    def test_r3_mentions_operationalisation(self):
        obs = observations_for(self._r3_score_map())
        r3 = next(o for o in obs if "Ethical Infrastructure" in o and "Governance & Policy" in o)
        assert "operationalised" in r3


# ---------------------------------------------------------------------------
# R4 — organisational capacity drag
# ---------------------------------------------------------------------------

class TestR4CapacityDrag:
    def _r4_score_map(self):
        # p1=4(80), p2=4(80), p3=2(40), p4=4(80) → composite=70, composite-p3=30 >= 15, p3 is lowest
        return {"p1": 4, "p2": 4, "p3": 2, "p4": 4}

    def test_r4_fires_when_conditions_met(self):
        obs = observations_for(self._r4_score_map())
        assert any("Organisational Capacity" in o and "composite" in o.lower() for o in obs)

    def test_r4_does_not_fire_when_p3_not_lowest(self):
        # p2 lowest, p3 not lowest
        obs = observations_for({"p1": 4, "p2": 1, "p3": 3, "p4": 4})
        assert not any("Organisational Capacity" in o and "composite" in o.lower() for o in obs)

    def test_r4_does_not_fire_when_composite_below_50(self):
        # p1=2(40), p2=2(40), p3=1(20), p4=2(40) → composite=35, below 50
        obs = observations_for({"p1": 2, "p2": 2, "p3": 1, "p4": 2})
        assert not any("Organisational Capacity" in o and "composite" in o.lower() for o in obs)

    def test_r4_does_not_fire_when_drag_below_15(self):
        # p1=3(60), p2=3(60), p3=3(60), p4=3(60) → drag=0, below 15
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        assert not any("Organisational Capacity" in o and "composite" in o.lower() for o in obs)

    def test_r4_mentions_tier(self):
        obs = observations_for(self._r4_score_map())
        r4 = next(o for o in obs if "Organisational Capacity" in o and "composite" in o.lower())
        assert any(tier in r4 for tier in ["Pre-foundational", "Foundational", "Developing", "Mature"])


# ---------------------------------------------------------------------------
# R5 — balanced profile / fallback
# ---------------------------------------------------------------------------

class TestR5BalancedProfile:
    def test_r5_fires_as_fallback_when_no_divergence(self):
        # All 3s: perfectly balanced, no R2/R3/R4 trigger
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        assert len(obs) >= 2
        # R5 uses "balanced" or "spread" language
        assert any("balanced" in o.lower() or "spread" in o.lower() for o in obs)

    def test_r5_variant_a_when_composite_at_least_60(self):
        # All 3s → composite = 60 → Variant A ("notably balanced")
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        r5 = next(o for o in obs if "balanced" in o.lower() or "spread" in o.lower())
        assert "notably balanced" in r5

    def test_r5_variant_b_when_composite_below_60(self):
        # All 2s → composite = 40 < 60 → Variant B
        obs = observations_for({"p1": 2, "p2": 2, "p3": 2, "p4": 2})
        r5 = next(o for o in obs if "balanced" in o.lower() or "spread" in o.lower())
        assert "notably balanced" not in r5
        assert "balanced" in r5.lower()

    def test_r5_includes_spread_value(self):
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        r5 = next(o for o in obs if "balanced" in o.lower() or "spread" in o.lower())
        # Spread of 0 when all equal
        assert "0" in r5


# ---------------------------------------------------------------------------
# Output contract — always 2–4 observations, capped at 4
# ---------------------------------------------------------------------------

class TestObservationOutputContract:
    def test_minimum_two_observations_all_patterns(self):
        test_cases = [
            {"p1": 1, "p2": 1, "p3": 1, "p4": 1},  # all low
            {"p1": 5, "p2": 5, "p3": 5, "p4": 5},  # all high
            {"p1": 3, "p2": 3, "p3": 3, "p4": 3},  # balanced mid
            {"p1": 4, "p2": 2, "p3": 3, "p4": 3},  # R2 pattern
            {"p1": 4, "p2": 3, "p3": 3, "p4": 2},  # R3 pattern
            {"p1": 4, "p2": 4, "p3": 2, "p4": 4},  # R4 pattern
            {"p1": 4, "p2": 2, "p3": 3, "p4": 2},  # R2+R3 pattern
        ]
        for score_map in test_cases:
            obs = observations_for(score_map)
            assert len(obs) >= 2, f"Expected >= 2 observations for {score_map}, got {len(obs)}"

    def test_maximum_four_observations(self):
        # R1 always + up to 3 conditionals: R2, R3, R4 could all fire
        # p1=4(80), p2=2(40), p3=2(40), p4=2(40)
        # R2: p1>=60, p2<50 ✓
        # R3: p1-p4=40>=20 ✓
        # R4: p3 is tied lowest, not definitively lowest — may or may not fire
        obs = observations_for({"p1": 4, "p2": 2, "p3": 2, "p4": 2})
        assert len(obs) <= 4

    def test_all_observations_are_non_empty_strings(self):
        obs = observations_for({"p1": 3, "p2": 3, "p3": 3, "p4": 3})
        for o in obs:
            assert isinstance(o, str)
            assert len(o.strip()) > 0

    def test_r1_always_first(self):
        for score_map in [
            {"p1": 1, "p2": 1, "p3": 1, "p4": 1},
            {"p1": 4, "p2": 2, "p3": 3, "p4": 3},
            {"p1": 3, "p2": 3, "p3": 3, "p4": 3},
        ]:
            obs = observations_for(score_map)
            assert "most acute development need" in obs[0], (
                f"R1 should always be first observation; score_map={score_map}"
            )
