"""Tests for core.judgment — Kernel Judgment Interface."""

from unittest.mock import MagicMock, patch

import pytest

from core.judgment import (
    CognitionResult,
    EmpathyResult,
    VerdictResult,
    _calculate_vitality_index,
    _calculate_quad_witness,
    _check_paradox_conductance,
)


class TestCognitionResult:
    """AGI cognition judgment result dataclass."""

    def test_default_construction(self):
        result = CognitionResult(
            verdict="SEAL",
            truth_score=0.9,
            genius_score=0.85,
            grounded=True,
            floor_scores={"F2": 0.9},
            module_results={},
        )
        assert result.verdict == "SEAL"
        assert result.truth_score == 0.9
        assert result.grounded is True
        assert result.clarity_delta == 0.0
        assert result.humility_omega == 0.04

    def test_optional_fields(self):
        result = CognitionResult(
            verdict="VOID",
            truth_score=0.3,
            genius_score=0.4,
            grounded=False,
            floor_scores={},
            module_results={},
            motto="Test motto",
            error="Test error",
        )
        assert result.motto == "Test motto"
        assert result.error == "Test error"


class TestEmpathyResult:
    """ASI empathy judgment result dataclass."""

    def test_default_construction(self):
        result = EmpathyResult(
            verdict="SEAL",
            reversibility_score=0.95,
            peace_squared=1.0,
            empathy_score=0.9,
            floor_scores={"F6": 0.95},
        )
        assert result.verdict == "SEAL"
        assert result.reversibility_score == 0.95
        assert result.peace_squared == 1.0
        assert result.empathy_score == 0.9

    def test_stakeholder_impact_default(self):
        result = EmpathyResult(
            verdict="SEAL",
            reversibility_score=0.9,
            peace_squared=1.0,
            empathy_score=0.9,
            floor_scores={},
        )
        assert result.stakeholder_impact == {}


class TestVerdictResult:
    """APEX final judgment result dataclass."""

    def test_default_construction(self):
        result = VerdictResult(
            verdict="SEAL",
            confidence=0.95,
            floor_scores={"F3": 0.98},
        )
        assert result.verdict == "SEAL"
        assert result.confidence == 0.95
        assert result.requires_human_approval is False
        assert result.vitality_index is None

    def test_full_fields(self):
        result = VerdictResult(
            verdict="888_HOLD",
            confidence=0.6,
            floor_scores={"F1": 0.75},
            motto="Hold for human review",
            reasoning="Irreversibility threshold exceeded",
            requires_human_approval=True,
            vitality_index=0.8,
            tri_witness=0.96,
            paradox_conductance=0.5,
        )
        assert result.requires_human_approval is True
        assert result.vitality_index == 0.8
        assert result.tri_witness == 0.96


class TestVitalityIndex:
    """Ψ (Vitality Index) Master Equation."""

    def test_vitality_index_basic(self):
        """Ψ = (|ΔS| · Peace² · κᵣ · RASA · Amanah) / (Entropy + Shadow + ε)"""
        result = _calculate_vitality_index(
            delta_s=-0.5,
            peace2=1.0,
            kappa_r=0.95,
            rasa=0.9,
            amanah=0.9,
            entropy=0.1,
            shadow=0.05,
        )
        # Ψ should be positive
        assert result > 0
        assert isinstance(result, float)

    def test_vitality_index_equilibrium(self):
        """Ψ >= 1.0 required for homeostatic equilibrium."""
        result = _calculate_vitality_index(
            delta_s=-1.0,  # Strong clarity
            peace2=1.0,
            kappa_r=0.95,
            rasa=0.95,
            amanah=0.95,
            entropy=0.1,
            shadow=0.01,
        )
        assert result >= 1.0

    def test_vitality_index_with_zero_entropy(self):
        """Test with minimal entropy (epsilon protection)."""
        result = _calculate_vitality_index(
            delta_s=-0.3,
            peace2=0.8,
            kappa_r=0.9,
            rasa=0.85,
            amanah=0.9,
            entropy=0.0,
            shadow=0.0,
        )
        assert result > 0  # Epsilon prevents division by zero


class TestQuadWitness:
    """W₄ (Quad-Witness) geometric mean consensus."""

    def test_quad_witness_basic(self):
        """W₄ = ⁴√(Human × AI × System × Temporal)"""
        result = _calculate_quad_witness(
            human_w=0.9,
            ai_w=0.85,
            system_w=0.95,
            temporal_w=0.88,
        )
        # Geometric mean should be between min and max
        assert 0 < result <= 0.95
        assert isinstance(result, float)

    def test_quad_witness_high_consensus(self):
        """All witnesses high → W₄ > 0.95."""
        result = _calculate_quad_witness(
            human_w=0.98,
            ai_w=0.97,
            system_w=0.99,
            temporal_w=0.96,
        )
        assert result >= 0.95

    def test_quad_witness_one_low(self):
        """One low witness drags down geometric mean."""
        result = _calculate_quad_witness(
            human_w=0.9,
            ai_w=0.9,
            system_w=0.9,
            temporal_w=0.1,  # One low witness
        )
        assert result < 0.6  # Geometric mean penalized: ⁴√(0.9³×0.1) ≈ 0.52


class TestParadoxConductance:
    """Φₚ (Paradox Conductance) resolution check."""

    def test_no_paradox(self):
        """No paradox flags → high conductance."""
        result = _check_paradox_conductance(
            paradox_flags=[],
            resolved_count=0,
            total_count=0,
        )
        assert result == 1.0

    def test_all_paradoxes_resolved(self):
        """All paradoxes resolved → high conductance."""
        result = _check_paradox_conductance(
            paradox_flags=["p1", "p2"],
            resolved_count=2,
            total_count=2,
        )
        assert result == 1.0

    def test_partial_resolution(self):
        """Partial resolution → reduced conductance."""
        result = _check_paradox_conductance(
            paradox_flags=["p1", "p2", "p3", "p4"],
            resolved_count=2,
            total_count=4,
        )
        assert 0 < result < 1.0

    def test_no_resolution(self):
        """Unresolved paradoxes → zero conductance."""
        result = _check_paradox_conductance(
            paradox_flags=["p1", "p2", "p3"],
            resolved_count=0,
            total_count=3,
        )
        assert result == 0.0
