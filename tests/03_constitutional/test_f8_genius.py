"""
F8 Genius tests aligned to the current floor and physics APIs.
"""

from __future__ import annotations

import pytest

from core.judgment import judge_cognition
from core.shared.floors import F8_Genius
from core.shared.physics import GeniusDial, genius_score


class TestF8GeniusFloor:
    def setup_method(self) -> None:
        self.floor = F8_Genius()

    def test_floor_matches_current_genius_formula(self) -> None:
        result = self.floor.check({"akal": 0.9, "present": 0.9, "exploration": 0.9, "energy": 0.9})

        assert result.score == pytest.approx(genius_score(A=0.9, P=0.9, X=0.9, E=0.9))

    def test_low_genius_fails_threshold(self) -> None:
        result = self.floor.check({"akal": 0.5, "present": 0.5, "exploration": 0.5, "energy": 0.5})

        assert not result.passed
        assert result.score < 0.8

    def test_high_genius_passes_threshold(self) -> None:
        result = self.floor.check({"akal": 1.0, "present": 1.0, "exploration": 1.0, "energy": 1.0})

        assert result.passed
        assert result.score == pytest.approx(1.0)

    def test_energy_has_quadratic_effect(self) -> None:
        half = genius_score(A=1.0, P=1.0, X=1.0, E=0.5)
        full = genius_score(A=1.0, P=1.0, X=1.0, E=1.0)

        assert half == pytest.approx(0.25)
        assert full == pytest.approx(1.0)

    def test_hysteresis_penalty_reduces_genius(self) -> None:
        clean = GeniusDial(A=0.9, P=0.9, X=0.9, E=0.9, h=0.0).G()
        penalized = GeniusDial(A=0.9, P=0.9, X=0.9, E=0.9, h=0.3).G()

        assert penalized < clean


class TestF8Kernel:
    def test_judge_cognition_reports_genius_score(self) -> None:
        result = judge_cognition(
            query="Well-grounded answer",
            evidence_count=4,
            evidence_relevance=0.95,
            reasoning_consistency=0.95,
            knowledge_gaps=[],
            model_logits_confidence=0.9,
            grounding=[
                {"source": "authoritative-1", "relevance": 0.95},
                {"source": "authoritative-2", "relevance": 0.95},
            ],
        )

        assert 0.0 <= result.genius_score <= 1.0
        assert result.verdict in {"SEAL", "PROVISIONAL", "PARTIAL", "SABAR"}

    def test_grounding_improves_genius_score(self) -> None:
        low = judge_cognition(
            query="Sparse answer",
            evidence_count=0,
            evidence_relevance=0.0,
            reasoning_consistency=0.5,
            knowledge_gaps=["missing evidence"],
            model_logits_confidence=0.4,
        )
        high = judge_cognition(
            query="Well-grounded answer",
            evidence_count=4,
            evidence_relevance=0.95,
            reasoning_consistency=0.95,
            knowledge_gaps=[],
            model_logits_confidence=0.9,
            grounding=[
                {"source": "authoritative-1", "relevance": 0.95},
                {"source": "authoritative-2", "relevance": 0.95},
            ],
        )

        assert high.genius_score >= low.genius_score
