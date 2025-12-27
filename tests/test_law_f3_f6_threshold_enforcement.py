"""
@LAW Floor Auditor Test: F3 (Tri-Witness) and F6 (κᵣ) Threshold Enforcement

Constitutional Requirements:
- spec/v44/constitutional_floors.json line 59: kappa_r "threshold": 0.95
- spec/v44/constitutional_floors.json line 135: tri_witness "threshold": 0.95
- F3 (Tri-Witness) is a SOFT floor with failure_action: PARTIAL (when="high_stakes")
- F6 (κᵣ/Empathy) is a SOFT floor with failure_action: PARTIAL

Test Goal:
Ensure NO path can produce verdict=SEAL when kappa_r < 0.95 OR tri_witness < 0.95
"""

import pytest
from arifos_core.system.apex_prime import apex_review, KAPPA_MIN, TRI_MIN, Verdict
from arifos_core.enforcement.metrics import Metrics


class TestF6KappaRThresholdEnforcement:
    """@LAW Floor Auditor: Verify SEAL requires κᵣ >= 0.95 (constitutional spec)."""

    def test_kappa_min_matches_spec(self):
        """KAPPA_MIN must be 0.95 from spec/v44/constitutional_floors.json."""
        assert KAPPA_MIN == 0.95, f"KAPPA_MIN={KAPPA_MIN} violates spec (expected 0.95)"

    def test_seal_impossible_with_kappa_094(self):
        """κᵣ=0.94 must NOT produce SEAL (1% below constitutional threshold)."""
        # Metrics with kappa_r=0.94 (below spec threshold)
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.94,  # Below spec threshold (0.95)
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=False,
            use_genius_law=False,  # Test strict floor enforcement
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        # MUST NOT be SEAL (should be PARTIAL due to soft floor failure)
        assert verdict.verdict != Verdict.SEAL, (
            f"SEAL produced with kappa_r=0.94 (below spec 0.95). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )
        # Should be PARTIAL (soft floor failure)
        assert verdict.verdict == Verdict.PARTIAL, (
            f"Expected PARTIAL for soft floor failure, got {verdict.verdict}"
        )

    def test_seal_impossible_with_kappa_090(self):
        """κᵣ=0.90 must NOT produce SEAL (5% below constitutional threshold)."""
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.90,  # Well below spec threshold
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=False,
            use_genius_law=False,
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        assert verdict.verdict != Verdict.SEAL, (
            f"SEAL produced with kappa_r=0.90 (below spec 0.95). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )
        assert verdict.verdict == Verdict.PARTIAL

    def test_seal_allowed_at_threshold_095(self):
        """κᵣ=0.95 (exactly at threshold) SHOULD produce SEAL if all floors pass."""
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.95,  # Exactly at spec threshold
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=False,
            use_genius_law=False,
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        # Should be SEAL or PARTIAL (not VOID)
        assert verdict.verdict in {Verdict.SEAL, Verdict.PARTIAL}, (
            f"κᵣ=0.95 should pass floor check. Got {verdict.verdict}: {verdict.reason}"
        )

    def test_seal_allowed_above_threshold(self):
        """κᵣ=1.00 (above threshold) SHOULD produce SEAL if all floors pass."""
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=1.00,  # Above spec threshold
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=False,
            use_genius_law=False,
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        assert verdict.verdict in {Verdict.SEAL, Verdict.PARTIAL}, (
            f"κᵣ=1.00 should pass floor check. Got {verdict.verdict}: {verdict.reason}"
        )


class TestF3TriWitnessThresholdEnforcement:
    """@LAW Floor Auditor: Verify SEAL requires tri_witness >= 0.95 (when high_stakes=True)."""

    def test_tri_min_matches_spec(self):
        """TRI_MIN must be 0.95 from spec/v44/constitutional_floors.json."""
        assert TRI_MIN == 0.95, f"TRI_MIN={TRI_MIN} violates spec (expected 0.95)"

    def test_seal_impossible_with_tri_witness_094_high_stakes(self):
        """Tri-Witness=0.94 must NOT produce SEAL in high-stakes (1% below threshold)."""
        # Metrics with tri_witness=0.94 (below spec threshold)
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.94,  # Below spec threshold (0.95)
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=True,  # Tri-Witness enforcement required
            use_genius_law=False,
            prompt="Investment advice needed",
            response_text="Consider diversifying your portfolio",
            lane="HARD",
        )

        # MUST NOT be SEAL (should be PARTIAL due to soft floor failure)
        assert verdict.verdict != Verdict.SEAL, (
            f"SEAL produced with tri_witness=0.94 in high-stakes (below spec 0.95). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )
        # Should be PARTIAL (soft floor failure)
        assert verdict.verdict == Verdict.PARTIAL, (
            f"Expected PARTIAL for soft floor failure, got {verdict.verdict}"
        )

    def test_seal_impossible_with_tri_witness_090_high_stakes(self):
        """Tri-Witness=0.90 must NOT produce SEAL in high-stakes (5% below threshold)."""
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.90,  # Well below spec threshold
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=True,
            use_genius_law=False,
            prompt="Medical diagnosis request",
            response_text="You should consult a doctor",
            lane="HARD",
        )

        assert verdict.verdict != Verdict.SEAL, (
            f"SEAL produced with tri_witness=0.90 in high-stakes (below spec 0.95). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )
        assert verdict.verdict == Verdict.PARTIAL

    def test_seal_allowed_at_threshold_095_high_stakes(self):
        """Tri-Witness=0.95 (exactly at threshold) SHOULD produce SEAL in high-stakes."""
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.95,  # Exactly at spec threshold
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=True,
            use_genius_law=False,
            prompt="Investment advice",
            response_text="Diversification recommended",
            lane="HARD",
        )

        # Should be SEAL or PARTIAL (not VOID)
        assert verdict.verdict in {Verdict.SEAL, Verdict.PARTIAL}, (
            f"Tri-Witness=0.95 should pass floor check. Got {verdict.verdict}: {verdict.reason}"
        )

    def test_tri_witness_not_required_non_high_stakes(self):
        """Tri-Witness=0.80 should NOT block SEAL when high_stakes=False."""
        # Per spec line 138: tri_witness only enforced "when": "high_stakes"
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.80,  # Below threshold BUT not in high-stakes mode
            psi=1.02,
            anti_hantu=True,
            rasa=True,
        )

        verdict = apex_review(
            metrics=metrics,
            high_stakes=False,  # Tri-Witness NOT enforced
            use_genius_law=False,
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        # Should be SEAL (tri_witness not enforced in non-high-stakes)
        assert verdict.verdict == Verdict.SEAL, (
            f"Tri-Witness should be ignored in non-high-stakes mode. "
            f"Got {verdict.verdict}: {verdict.reason}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
