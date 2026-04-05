"""
tests/core/test_apex_non_learning.py

Validates the hard constraint that APEX (Ψ/777-888) is NON-LEARNING.

This is a safety-critical test suite. If APEX could learn, it would
silently edit the constitution it's supposed to guard.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import inspect

import pytest

from core.governance.apex_invariants import (
    APEX_CONSTANTS,
    ApexConstants,
    get_invariant_table,
    validate_apex_non_learning,
)
from core.physics.thermodynamic_enforcement import ThermodynamicProsecutor


class TestApexNonLearningGuarantee:
    """
    APEX must be a calculator, not a student.
    
    The judge applies fixed law. If it learned, constitutional drift
    would occur—floors softening over time in the name of efficiency.
    """

    def test_apex_has_no_learn_method(self) -> None:
        """
        ThermodynamicProsecutor must NOT have a learn() method.
        
        Learning at APEX would mean the judge updates its own thresholds,
        violating the separation between legislation and adjudication.
        """
        assert not hasattr(ThermodynamicProsecutor, "learn"), \
            "APEX class has forbidden learn() method"

    def test_apex_has_no_fit_method(self) -> None:
        """
        ThermodynamicProsecutor must NOT have a fit() method.
        
        Fitting/training is for AGI/ASI layers, not the judge.
        """
        assert not hasattr(ThermodynamicProsecutor, "fit"), \
            "APEX class has forbidden fit() method"

    def test_apex_has_no_train_method(self) -> None:
        """
        ThermodynamicProsecutor must NOT have a train() method.
        
        Training loops belong in Delta (AGI), not Psi (APEX).
        """
        assert not hasattr(ThermodynamicProsecutor, "train"), \
            "APEX class has forbidden train() method"

    def test_apex_has_no_update_thresholds(self) -> None:
        """
        ThermodynamicProsecutor must NOT have update_thresholds().
        
        Threshold modification is a GOVERNANCE EVENT (888_HOLD),
        not an optimization outcome.
        """
        assert not hasattr(ThermodynamicProsecutor, "update_thresholds"), \
            "APEX class has forbidden update_thresholds() method"
        assert not hasattr(ThermodynamicProsecutor, "adjust_thresholds"), \
            "APEX class has forbidden adjust_thresholds() method"

    def test_apex_has_no_adapt_method(self) -> None:
        """
        ThermodynamicProsecutor must NOT have adapt() method.
        
        Adaptation at APEX = constitutional drift.
        """
        assert not hasattr(ThermodynamicProsecutor, "adapt"), \
            "APEX class has forbidden adapt() method"

    def test_apex_validate_non_learning_returns_clean(self) -> None:
        """
        The built-in validation must confirm no learning capabilities.
        """
        result = ThermodynamicProsecutor.validate_non_learning()
        
        assert result["clean"] is True, \
            f"APEX learning detected: {result['violations']}"
        assert len(result["violations"]) == 0
        assert "clean" in result["message"].lower()


class TestApexConstantsAreImmutable:
    """
    APEX constants must be frozen—no modification at runtime.
    """

    def test_apex_constants_is_frozen_dataclass(self) -> None:
        """
        ApexConstants must be a frozen dataclass.
        """
        # Check it's frozen
        with pytest.raises(Exception):  # FrozenInstanceError or similar
            consts = ApexConstants()
            consts.F2_TRUTH_THRESHOLD = 0.5  # type: ignore

    def test_global_constants_is_singleton(self) -> None:
        """
        APEX_CONSTANTS must be the global singleton instance.
        """
        assert isinstance(APEX_CONSTANTS, ApexConstants)
        
        # All expected attributes present
        assert hasattr(APEX_CONSTANTS, "F2_TRUTH_THRESHOLD")
        assert hasattr(APEX_CONSTANTS, "F3_TRI_WITNESS_MIN")
        assert hasattr(APEX_CONSTANTS, "LANDAUER_MIN")

    def test_thresholds_are_reasonable_values(self) -> None:
        """
        APEX thresholds must have reasonable, strict values.
        
        These are hard floors—not suggestions, not defaults.
        """
        # F2 Truth must be strict (≥ 0.99)
        assert APEX_CONSTANTS.F2_TRUTH_THRESHOLD >= 0.99, \
            "F2 Truth threshold too lenient"
        
        # F3 Tri-Witness must be high (≥ 0.95)
        assert APEX_CONSTANTS.F3_TRI_WITNESS_MIN >= 0.95, \
            "F3 Tri-Witness threshold too low"
        
        # F7 Humility must be in [0.03, 0.05]
        assert 0.03 <= APEX_CONSTANTS.F7_HUMILITY_MIN <= 0.05, \
            "F7 Humility min out of band"
        assert 0.03 <= APEX_CONSTANTS.F7_HUMILITY_MAX <= 0.05, \
            "F7 Humility max out of band"
        
        # F8 Genius must be meaningful (≥ 0.80)
        assert APEX_CONSTANTS.F8_GENIUS_MIN >= 0.80, \
            "F8 Genius threshold too low"
        
        # F9 Shadow must be strict (≤ 0.30)
        assert APEX_CONSTANTS.F9_SHADOW_MAX <= 0.30, \
            "F9 Shadow ceiling too high"

    def test_landauer_min_is_physics_constant(self) -> None:
        """
        Landauer minimum must be the actual physics constant.
        
        E_min = k_B * T * ln(2) ≈ 2.87×10^-21 J/bit at room temp
        """
        # Should be very small (~10^-21)
        assert 1e-22 < APEX_CONSTANTS.LANDAUER_MIN < 1e-20, \
            f"Landauer min {APEX_CONSTANTS.LANDAUER_MIN} not in expected range"


class TestContrastBelongsElsewhere:
    """
    "Contrast is knowledge" applies to AGI/ASI, NOT APEX.
    
    APEX takes already-contrasted outputs and judges them.
    It does NOT perform contrast operations itself.
    """

    def test_prosecutor_has_no_contrast_method(self) -> None:
        """
        ThermodynamicProsecutor must NOT have contrast/compare methods.
        
        Contrast operations belong in:
        - AGI (Δ): Comparing hypotheses
        - ASI (Ω): Comparing stakeholder impacts
        
        NOT in APEX (Ψ): Binary judgment only.
        """
        forbidden = [
            "contrast",
            "compare",
            "compare_outputs",
            "select_best",
            "rank",
            "score_alternatives",
        ]
        
        for method in forbidden:
            assert not hasattr(ThermodynamicProsecutor, method), \
                f"APEX has forbidden contrast method: {method}()"

    def test_prosecutor_only_binary_verdicts(self) -> None:
        """
        APEX verdicts must be binary/categorical, not graded.
        
        - SEAL: Pass (meets threshold)
        - VOID: Hard fail (violates physics)
        - SABAR: Soft fail (needs refinement)
        
        No "partial credit" or "improving score"—this is law, not school.
        """
        result = ThermodynamicProsecutor.prosecute_claim(
            claimed_entropy_reduction=-0.1,
            tokens_generated=10,
            compute_time_ms=5000,
        )
        
        assert result["verdict"] in ["SEAL", "VOID", "SABAR"], \
            "Verdict must be categorical, not graded"
        
        # No "score" or "grade" field
        assert "score" not in result
        assert "grade" not in result


class TestConstitutionalDriftPrevention:
    """
    Tests that simulate what would happen if APEX could learn.
    
    These tests document WHY learning is forbidden—the consequences
    of constitutional drift over time.
    """

    def test_document_constitutional_drift_scenario(self) -> None:
        """
        Document the hypothetical drift scenario.
        
        Year 1:  τ ≥ 0.99 (strict)
        Year 2:  τ ≥ 0.97 ("optimization")
        Year 5:  τ ≥ 0.85 ("creativity")
        Year 10: τ ≥ 0.70 (hallucinations normalized)
        
        This test documents the hazard; the other tests prevent it.
        """
        # Current strict threshold
        current_threshold = APEX_CONSTANTS.F2_TRUTH_THRESHOLD
        
        # Hypothetical drifted thresholds (what we'd get if learning allowed)
        drifted_thresholds = [0.97, 0.95, 0.85, 0.70]
        
        for drifted in drifted_thresholds:
            assert current_threshold > drifted, \
                f"Current threshold {current_threshold} not stricter than " \
                f"hypothetical drifted threshold {drifted}"

    def test_thresholds_documented_in_invariant_table(self) -> None:
        """
        All APEX thresholds must be documented in the invariant table.
        """
        table = get_invariant_table()
        
        # Core thresholds must be present
        required = [
            "landauer_minimum",
            "truth_threshold",
            "humility_band",
            "tri_witness_floor",
            "genius_minimum",
            "shadow_ceiling",
            "empathy_minimum",
        ]
        
        for key in required:
            assert key in table, f"Missing invariant documentation: {key}"
            assert table[key].get("learnable") is False, \
                f"{key} marked as learnable in invariant table"


class TestApexSeparationOfPowers:
    """
    Validate separation: Legislators change law; Judges apply law.
    """

    def test_apex_does_not_modify_self(self) -> None:
        """
        APEX classes must have no self-modifying methods.
        
        The judge cannot change its own code—that's legislation,
        not adjudication.
        """
        forbidden_patterns = [
            "setattr",
            "__setattr__",
            "globals()[",
            "locals()[",
            "exec",
            "eval",
        ]
        
        source = inspect.getsource(ThermodynamicProsecutor)
        
        for pattern in forbidden_patterns:
            # Allow the pattern in comments/docstrings
            lines = source.split("\n")
            for line in lines:
                # Skip comments
                code_line = line.split("#")[0]
                if pattern in code_line:
                    pytest.fail(
                        f"APEX class contains forbidden self-modification: {pattern}\n"
                        f"Line: {line.strip()}"
                    )

    def test_apex_prosecutor_is_class_not_instance(self) -> None:
        """
        Key methods should be classmethods, not instance methods.
        
        This prevents stateful learning (instance variables) and
        enforces stateless judgment (class constants).
        """
        # prosecute_claim should be a classmethod
        assert isinstance(
            inspect.getattr_static(ThermodynamicProsecutor, "prosecute_claim"),
            classmethod
        ), "prosecute_claim should be classmethod (stateless)"
        
        # detect_stochastic_magic should be a classmethod
        assert isinstance(
            inspect.getattr_static(ThermodynamicProsecutor, "detect_stochastic_magic"),
            classmethod
        ), "detect_stochastic_magic should be classmethod (stateless)"
