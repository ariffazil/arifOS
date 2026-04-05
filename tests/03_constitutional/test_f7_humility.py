"""
F7 Humility tests aligned to the current uncertainty and floor APIs.
"""

from __future__ import annotations

import pytest

from core.judgment import judge_cognition
from core.shared.floors import F7_Humility
from core.uncertainty_engine import (
    HUMILITY_MAX,
    HUMILITY_MIN,
    HumilityBandViolation,
    OmniscienceError,
    check_omniscience_lock,
    enforce_humility_band,
)


class TestF7HumilityBand:
    def setup_method(self) -> None:
        self.floor = F7_Humility()

    @pytest.mark.parametrize("omega", [0.0, 0.01, 0.02, 0.029, 0.21])
    def test_out_of_band_uncertainty_fails(self, omega: float) -> None:
        result = self.floor.check({"humility_omega": omega})

        assert not result.passed
        assert result.floor_id == "F7_Humility"
        assert result.score == pytest.approx(omega)

    @pytest.mark.parametrize("omega", [0.03, 0.04, 0.05, 0.20])
    def test_humility_band_accepted(self, omega: float) -> None:
        result = self.floor.check({"humility_omega": omega})

        assert result.passed
        assert self.floor.min_o <= result.score <= self.floor.max_o

    def test_confidence_path_uses_inverse_omega(self) -> None:
        result = self.floor.check({"confidence": 0.96})

        assert result.passed
        assert result.score == pytest.approx(0.04)


class TestF7Hardening:
    def test_humility_band_clamps_overconfidence(self) -> None:
        assert enforce_humility_band(0.01) == pytest.approx(HUMILITY_MIN)
        assert enforce_humility_band(0.04) == pytest.approx(0.04)

    def test_critical_uncertainty_raises(self) -> None:
        with pytest.raises(HumilityBandViolation):
            enforce_humility_band(0.09)

    def test_omniscience_lock_blocks_empirical_certainty(self) -> None:
        with pytest.raises(OmniscienceError):
            check_omniscience_lock(1.0, is_mathematical=False)

    def test_judge_cognition_exposes_humility_band(self) -> None:
        result = judge_cognition(
            query="What is the capital of France?",
            evidence_count=3,
            evidence_relevance=0.9,
            reasoning_consistency=0.95,
            knowledge_gaps=[],
            model_logits_confidence=0.9,
            grounding=[{"source": "atlas", "relevance": 0.9}],
        )

        assert HUMILITY_MIN <= result.humility_omega <= HUMILITY_MAX
        assert "omega" in result.module_results
