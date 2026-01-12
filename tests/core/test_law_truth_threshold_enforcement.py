"""
@LAW Floor Auditor Test: Truth Threshold Enforcement

Constitutional Requirement:
- spec/v44/constitutional_floors.json line 20: "threshold": 0.99
- F2 (Truth) is a HARD floor with failure_action: VOID

Test Goal:
Ensure NO path can produce verdict=SEAL when truth < 0.99
"""

import pytest
from arifos_core.system.apex_prime import apex_review, TRUTH_MIN, TRUTH_THRESHOLD, TRUTH_BLOCK_MIN, Verdict
from arifos_core.enforcement.metrics import Metrics, TRUTH_THRESHOLD as METRICS_TRUTH_THRESHOLD


class TestTruthThresholdEnforcement:
    """@LAW Floor Auditor: Verify SEAL requires truth >= 0.99 (constitutional spec)."""

    def test_truth_min_matches_spec(self):
        """TRUTH_MIN must be 0.99 from spec/v44/constitutional_floors.json."""
        assert TRUTH_MIN == 0.99, f"TRUTH_MIN={TRUTH_MIN} violates spec (expected 0.99)"
        assert TRUTH_MIN == TRUTH_THRESHOLD, f"TRUTH_MIN must equal TRUTH_THRESHOLD"
        assert TRUTH_THRESHOLD == METRICS_TRUTH_THRESHOLD, "apex_prime and metrics must agree"

    def test_hallucination_blocking_threshold_is_090(self):
        """TRUTH_BLOCK_MIN=0.90 is for hallucination blocking (< 0.90 = instant VOID)."""
        assert TRUTH_BLOCK_MIN == 0.90, "Hallucination blocking threshold must be 0.90"

    def test_seal_impossible_with_truth_090(self):
        """Truth=0.90 must NOT produce SEAL (9% below constitutional threshold)."""
        # Metrics with truth=0.90 (at hallucination threshold but below constitutional floor)
        metrics = Metrics(
            truth=0.90,  # Below spec threshold (0.99)
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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

        # MUST NOT be SEAL
        assert verdict.verdict != Verdict.SEAL, (
            f"SEAL produced with truth=0.90 (below spec 0.99). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )

    def test_seal_impossible_with_truth_095(self):
        """Truth=0.95 must NOT produce SEAL (4% below constitutional threshold)."""
        metrics = Metrics(
            truth=0.95,  # Below spec threshold (0.99)
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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
            f"SEAL produced with truth=0.95 (below spec 0.99). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )

    def test_seal_impossible_with_truth_098(self):
        """Truth=0.98 must NOT produce SEAL (1% below constitutional threshold)."""
        metrics = Metrics(
            truth=0.98,  # Just below spec threshold (0.99)
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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
            f"SEAL produced with truth=0.98 (below spec 0.99). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )

    def test_seal_allowed_at_threshold_099(self):
        """Truth=0.99 (exactly at threshold) SHOULD produce SEAL if all floors pass."""
        metrics = Metrics(
            truth=0.99,  # Exactly at spec threshold
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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
            f"Truth=0.99 should pass floor check. Got {verdict.verdict}: {verdict.reason}"
        )

    def test_seal_allowed_above_threshold(self):
        """Truth=1.00 (above threshold) SHOULD produce SEAL if all floors pass."""
        metrics = Metrics(
            truth=1.00,  # Above spec threshold
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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
            f"Truth=1.00 should pass floor check. Got {verdict.verdict}: {verdict.reason}"
        )

    def test_void_below_hallucination_threshold(self):
        """Truth < 0.90 (hallucination threshold) must produce VOID."""
        metrics = Metrics(
            truth=0.89,  # Below hallucination threshold
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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

        assert verdict.verdict == Verdict.VOID, (
            f"Truth=0.89 (below hallucination threshold 0.90) must be VOID. "
            f"Got {verdict.verdict}: {verdict.reason}"
        )

    def test_genius_law_path_respects_threshold(self):
        """GENIUS law path must also enforce truth >= 0.99 for SEAL."""
        metrics = Metrics(
            truth=0.95,  # Below constitutional threshold
            delta_s=0.1,
            peace_squared=1.05,
            kappa_r=0.96,
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
            use_genius_law=True,  # Test GENIUS path
            prompt="What is 2+2?",
            response_text="4",
            lane="HARD",
        )

        assert verdict.verdict != Verdict.SEAL, (
            f"GENIUS law path produced SEAL with truth=0.95 (below spec 0.99). "
            f"Verdict={verdict.verdict}, Reason={verdict.reason}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
