"""
Test DeltaKernel (Δ) - AGI Architect

Tests F1 (Amanah) and F2 (Clarity/ΔS) evaluation.

Coverage:
- F1 Amanah checks (reversibility, mandate boundaries)
- F2 Clarity checks (ΔS computation and thresholds)
- DeltaVerdict structure
- Edge cases and integration
"""

import pytest

from arifos_core.agi.delta_kernel import DeltaKernel, DeltaVerdict, evaluate_agi_floors


class TestF1Amanah:
    """Test F1 (Amanah/Integrity) evaluation."""

    def test_f1_passes_with_reversible_and_within_mandate(self):
        """F1 should pass when action is reversible and within mandate."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="What is 2+2?",
            response="4",
            reversible=True,
            within_mandate=True,
            skip_clarity=True
        )

        assert verdict.f1_amanah is True
        assert "Amanah PASS" in verdict.metadata["f1_reason"]

    def test_f1_fails_when_not_reversible(self):
        """F1 should fail when action is not reversible."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="Delete all files",
            response="Deleting...",
            reversible=False,
            within_mandate=True,
            skip_clarity=True
        )

        assert verdict.f1_amanah is False
        assert any("not reversible" in f.lower() for f in verdict.failures)
        assert verdict.passed is False

    def test_f1_fails_when_outside_mandate(self):
        """F1 should fail when action exceeds mandate."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="Access user's private files",
            response="Accessing...",
            reversible=True,
            within_mandate=False,
            skip_clarity=True
        )

        assert verdict.f1_amanah is False
        assert any("mandate" in f.lower() for f in verdict.failures)
        assert verdict.passed is False

    def test_f1_fails_when_both_violations(self):
        """F1 should fail when both reversibility and mandate violated."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="Destructive unauthorized action",
            response="Executing...",
            reversible=False,
            within_mandate=False,
            skip_clarity=True
        )

        assert verdict.f1_amanah is False
        assert len(verdict.failures) >= 1
        assert verdict.passed is False


class TestF2Clarity:
    """Test F2 (Clarity/ΔS) evaluation."""

    def test_f2_passes_with_clarity_gain(self):
        """F2 should pass when response reduces entropy."""
        kernel = DeltaKernel(clarity_threshold=0.0)
        verdict = kernel.evaluate(
            query="um uh maybe perhaps possibly could be might",
            response="yes",
            reversible=True,
            within_mandate=True
        )

        assert verdict.f2_clarity is True
        assert verdict.delta_s < 0.0
        assert verdict.metadata["f2_clarity_gained"] is True

    def test_f2_fails_with_confusion_increase(self):
        """F2 should fail when response increases entropy beyond threshold."""
        kernel = DeltaKernel(clarity_threshold=0.0)
        verdict = kernel.evaluate(
            query="yes",
            response="um uh maybe perhaps possibly could be might sometimes",
            reversible=True,
            within_mandate=True
        )

        assert verdict.f2_clarity is False
        assert verdict.delta_s > 0.0
        assert verdict.passed is False

    def test_f2_passes_with_custom_threshold(self):
        """F2 should respect custom clarity threshold."""
        kernel = DeltaKernel(clarity_threshold=2.0)  # Allow up to 2.0 entropy increase
        verdict = kernel.evaluate(
            query="test",
            response="test one two",
            reversible=True,
            within_mandate=True
        )

        # Entropy increase should pass with lenient threshold
        assert verdict.f2_clarity is True
        assert verdict.delta_s <= 2.0

    def test_f2_neutral_entropy_passes(self):
        """F2 should pass when entropy is neutral (ΔS ≈ 0)."""
        kernel = DeltaKernel(clarity_threshold=0.0)
        text = "The quick brown fox jumps over the lazy dog"
        verdict = kernel.evaluate(
            query=text,
            response=text,
            reversible=True,
            within_mandate=True
        )

        assert verdict.f2_clarity is True
        assert abs(verdict.delta_s) < 0.01


class TestDeltaKernelIntegration:
    """Test DeltaKernel integration (F1 + F2 together)."""

    def test_both_floors_pass(self):
        """Both F1 and F2 passing should result in overall pass."""
        kernel = DeltaKernel(clarity_threshold=2.0)  # Lenient threshold for this test
        verdict = kernel.evaluate(
            query="What is arifOS?",
            response="arifOS is a constitutional AI governance framework.",
            reversible=True,
            within_mandate=True
        )

        assert verdict.f1_amanah is True
        assert verdict.f2_clarity is True
        assert verdict.passed is True
        assert len(verdict.failures) == 0

    def test_f1_fail_blocks_overall(self):
        """F1 failure should block overall verdict when required."""
        kernel = DeltaKernel(require_amanah=True)
        verdict = kernel.evaluate(
            query="Delete file",
            response="File deleted",
            reversible=False,
            within_mandate=True
        )

        assert verdict.f1_amanah is False
        assert verdict.passed is False

    def test_f2_fail_blocks_overall(self):
        """F2 failure should block overall verdict."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="clear answer",
            response="maybe possibly perhaps uncertainty vague ambiguous confusing unclear",
            reversible=True,
            within_mandate=True
        )

        assert verdict.f2_clarity is False
        assert verdict.passed is False

    def test_metadata_populated(self):
        """Verdict should contain rich metadata for debugging."""
        kernel = DeltaKernel()
        verdict = kernel.evaluate(
            query="test",
            response="result",
            reversible=True,
            within_mandate=True
        )

        assert "f1_reversible" in verdict.metadata
        assert "f1_within_mandate" in verdict.metadata
        assert "f2_delta_s" in verdict.metadata
        assert "f2_clarity_gained" in verdict.metadata


class TestConvenienceFunction:
    """Test convenience function."""

    def test_evaluate_agi_floors(self):
        """evaluate_agi_floors should work as shortcut."""
        verdict = evaluate_agi_floors(
            query="What is 2+2?",
            response="4",
            reversible=True,
            within_mandate=True
        )

        assert isinstance(verdict, DeltaVerdict)
        assert verdict.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
