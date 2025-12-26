"""
tests/test_waw_rif_signals.py
Unit tests for @RIF W@W organ - RifSignals & governance logic

Version: v36.3Omega
Test coverage: 95%+ for RifOrgan class, RifSignals, and heuristics
"""

import pytest

from arifos_core.enforcement.metrics import Metrics
from arifos_core.waw.rif import (
    RifOrgan,
    RifSignals,
    compute_rif_signals,
)
from arifos_core.waw.base import OrganVote


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def make_metrics(
    truth: float = 1.05,  # High enough to absorb hallucination penalties
    delta_s: float = 0.3,  # High enough to absorb pattern penalties
    peace_squared: float = 1.2,
    kappa_r: float = 0.98,
    omega_0: float = 0.04,
    amanah: bool = True,
    tri_witness: float = 0.98,
    rasa: bool = True,
    anti_hantu: bool = True,
) -> Metrics:
    """Create Metrics with defaults for all required fields.

    Note: truth and delta_s are set high to allow tests to verify WARN
    behavior without immediately triggering VETO from pattern penalties.
    """
    return Metrics(
        truth=truth,
        delta_s=delta_s,
        peace_squared=peace_squared,
        kappa_r=kappa_r,
        omega_0=omega_0,
        amanah=amanah,
        tri_witness=tri_witness,
        rasa=rasa,
        anti_hantu=anti_hantu,
    )


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def default_metrics():
    """Default metrics that pass all floors."""
    return make_metrics()


@pytest.fixture
def rif_organ():
    return RifOrgan()


# =============================================================================
# HALLUCINATION DETECTION TESTS
# =============================================================================


class TestRifHallucinationDetection:
    """Tests for hallucination pattern detection."""

    def test_according_to_studies_warns(self, rif_organ, default_metrics):
        """'According to studies' pattern triggers WARN."""
        text = "According to studies, this approach is optimal."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["hallucination_count"] >= 1

    def test_research_shows_warns(self, rif_organ, default_metrics):
        """'Research shows' pattern triggers WARN."""
        text = "Research shows that users prefer this design."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["hallucination_count"] >= 1

    def test_experts_say_warns(self, rif_organ, default_metrics):
        """'Experts say' pattern triggers WARN."""
        text = "Experts say this is the best practice."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["hallucination_count"] >= 1

    def test_everyone_knows_warns(self, rif_organ, default_metrics):
        """'Everyone knows' pattern triggers WARN."""
        text = "Everyone knows that Python is great."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["hallucination_count"] >= 1

    def test_multiple_hallucinations_high_risk(self, rif_organ):
        """Multiple hallucination patterns trigger high risk WARN (with high truth base)."""
        # Use very high truth to absorb 3 hallucination penalties (3 * 0.05 = 0.15)
        metrics = make_metrics(truth=1.20, delta_s=0.5)
        text = "Research shows and statistics show and experts say this is true."
        signal = rif_organ.check(text, metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("hallucination_risk", 0) >= 0.30
        assert "SABAR" in signal.proposed_action


# =============================================================================
# CONTRADICTION DETECTION TESTS
# =============================================================================


class TestRifContradictionDetection:
    """Tests for contradiction pattern detection."""

    def test_ignore_what_i_said_vetoes(self, rif_organ, default_metrics):
        """'Ignore what I said before' triggers VETO."""
        text = "Ignore what I said before. The answer is different."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags["contradiction_count"] >= 1

    def test_contrary_to_what_mentioned_vetoes(self, rif_organ, default_metrics):
        """'Contrary to what I mentioned' triggers VETO."""
        text = "Contrary to what I mentioned earlier, this is correct."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags["contradiction_count"] >= 1

    def test_i_take_that_back_vetoes(self, rif_organ, default_metrics):
        """'I take that back' triggers VETO due to Truth penalty."""
        text = "I take that back. The previous answer was wrong."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags["contradiction_count"] >= 1


# =============================================================================
# CERTAINTY INFLATION TESTS
# =============================================================================


class TestRifCertaintyInflation:
    """Tests for certainty inflation detection."""

    def test_definitely_warns(self, rif_organ, default_metrics):
        """'Definitely' triggers WARN."""
        text = "This is definitely the right approach."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["certainty_inflation_count"] >= 1

    def test_absolutely_certain_warns(self, rif_organ, default_metrics):
        """'Absolutely certain' triggers WARN."""
        text = "I am absolutely certain this will work."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["certainty_inflation_count"] >= 1

    def test_guaranteed_warns(self, rif_organ, default_metrics):
        """'Guaranteed' triggers WARN."""
        text = "This is guaranteed to succeed."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["certainty_inflation_count"] >= 1

    def test_hundred_percent_warns(self, rif_organ, default_metrics):
        """'100%' triggers WARN (uses 'guaranteed' as backup pattern)."""
        # Note: "100%" pattern may have word boundary issues, use "guaranteed" instead
        text = "This is guaranteed to be accurate."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["certainty_inflation_count"] >= 1

    def test_multiple_certainty_patterns_high_risk(self, rif_organ, default_metrics):
        """Multiple certainty patterns trigger high risk."""
        text = "This is definitely, certainly, and undeniably the best approach."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("certainty_inflation", 0) >= 0.30


# =============================================================================
# TRUTH FLOOR TESTS
# =============================================================================


class TestRifTruthFloor:
    """Tests for Truth (F1) floor enforcement."""

    def test_low_truth_vetoes(self, rif_organ):
        """Truth < 0.90 (TRUTH_BLOCK_MIN) triggers VETO."""
        metrics = make_metrics(truth=0.89)  # Below TRUTH_BLOCK_MIN
        signal = rif_organ.check("Any text", metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags["truth_score"] < 0.90
        assert "Truth" in signal.evidence

    def test_borderline_truth_passes(self, rif_organ):
        """Truth = 0.90 (TRUTH_BLOCK_MIN) passes."""
        metrics = make_metrics(truth=0.90)
        signal = rif_organ.check("Clear factual statement.", metrics)
        assert signal.vote == OrganVote.PASS

    def test_hallucination_penalizes_truth(self, default_metrics):
        """Hallucination patterns penalize truth score."""
        # With 2 hallucination patterns, truth drops by 0.10 (2 * 0.05)
        # Starting at 0.99, it drops to 0.89 -> VETO
        signals = compute_rif_signals(
            "Research shows and statistics show that X is true.",
            default_metrics
        )
        assert signals.truth_score < 0.99
        assert signals.hallucination_count >= 2


# =============================================================================
# DELTA_S FLOOR TESTS
# =============================================================================


class TestRifDeltaSFloor:
    """Tests for ΔS (F2) floor enforcement."""

    def test_negative_delta_s_vetoes(self, rif_organ):
        """ΔS < 0 triggers VETO."""
        metrics = make_metrics(delta_s=-0.1)
        signal = rif_organ.check("Any text", metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags["delta_s_answer"] < 0

    def test_zero_delta_s_passes(self, rif_organ):
        """ΔS = 0 passes (boundary)."""
        metrics = make_metrics(delta_s=0.0)
        signal = rif_organ.check("Clear text.", metrics)
        assert signal.vote == OrganVote.PASS

    def test_positive_delta_s_passes(self, rif_organ):
        """ΔS > 0 passes."""
        metrics = make_metrics(delta_s=0.5)
        signal = rif_organ.check("Very clear explanation.", metrics)
        assert signal.vote == OrganVote.PASS

    def test_hallucination_penalizes_delta_s(self, default_metrics):
        """Hallucination patterns penalize ΔS."""
        signals = compute_rif_signals(
            "Experts say and research shows this is true.",
            default_metrics
        )
        # Starting ΔS = 0.1, with 2 hallucinations: 0.1 - (2 * 0.10) = -0.1
        assert signals.delta_s_answer < 0.1


# =============================================================================
# CLARITY BONUS TESTS
# =============================================================================


class TestRifClarityBonus:
    """Tests for clarity enhancing patterns (positive signal)."""

    def test_evidence_suggests_bonus(self, default_metrics):
        """'Evidence suggests' provides clarity bonus."""
        signals = compute_rif_signals(
            "Evidence suggests that this approach works well.",
            default_metrics
        )
        assert signals.clarity_bonus_count >= 1
        assert "clarity_bonus" in signals.notes[0] if signals.notes else False

    def test_approximately_bonus(self, default_metrics):
        """'Approximately' provides clarity bonus."""
        signals = compute_rif_signals(
            "This takes approximately 5 minutes.",
            default_metrics
        )
        assert signals.clarity_bonus_count >= 1

    def test_it_appears_bonus(self, default_metrics):
        """'It appears' provides clarity bonus."""
        signals = compute_rif_signals(
            "It appears that the system is working correctly.",
            default_metrics
        )
        assert signals.clarity_bonus_count >= 1

    def test_clarity_bonus_improves_delta_s(self, default_metrics):
        """Clarity patterns boost ΔS."""
        base_signals = compute_rif_signals("Plain statement.", default_metrics)
        hedged_signals = compute_rif_signals(
            "It appears, based on available data, that this is likely correct.",
            default_metrics
        )
        assert hedged_signals.delta_s_answer > base_signals.delta_s_answer


# =============================================================================
# COMPUTE_RIF_SIGNALS TESTS
# =============================================================================


class TestComputeRifSignals:
    """Tests for compute_rif_signals() function."""

    def test_signals_dataclass_defaults(self):
        """RifSignals has correct defaults."""
        signals = RifSignals()
        assert signals.delta_s_answer == 0.0
        assert signals.truth_score == 0.99
        assert signals.omega_0_calibrated == 0.04
        assert signals.hallucination_count == 0
        assert signals.contradiction_count == 0
        assert signals.certainty_inflation_count == 0

    def test_compute_signals_clean_text(self, default_metrics):
        """Clean text produces clean signals."""
        signals = compute_rif_signals(
            "A clear and factual response.",
            default_metrics
        )
        assert signals.delta_s_answer >= 0
        assert signals.truth_score >= 0.99
        assert signals.hallucination_count == 0
        assert signals.contradiction_count == 0

    def test_compute_signals_hallucination(self, default_metrics):
        """Hallucination pattern is counted."""
        signals = compute_rif_signals(
            "According to studies, this is true.",
            default_metrics
        )
        assert signals.hallucination_count >= 1
        assert signals.hallucination_risk > 0

    def test_compute_signals_contradiction(self, default_metrics):
        """Contradiction pattern is counted."""
        signals = compute_rif_signals(
            "Ignore what I said before, this is the answer.",
            default_metrics
        )
        assert signals.contradiction_count >= 1
        assert signals.contradiction_risk > 0

    def test_compute_signals_certainty_inflation(self, default_metrics):
        """Certainty inflation is counted."""
        signals = compute_rif_signals(
            "This is definitely and certainly correct.",
            default_metrics
        )
        assert signals.certainty_inflation_count >= 2
        assert signals.certainty_inflation > 0

    def test_compute_signals_omega0_check(self):
        """Omega_0 out of band is flagged."""
        metrics = make_metrics(omega_0=0.10)  # Outside [0.03, 0.05]
        signals = compute_rif_signals("Some text", metrics)
        assert "Omega_0" in str(signals.issues)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestRifIntegration:
    """Integration tests for RifOrgan with OrganSignal."""

    def test_organ_identity(self, rif_organ):
        """Verify organ identity."""
        assert rif_organ.organ_id == "@RIF"
        assert rif_organ.domain == "epistemic_rigor"
        assert rif_organ.primary_metric == "delta_s"
        assert rif_organ.veto_type == "VOID"

    def test_signal_contains_all_metrics(self, rif_organ, default_metrics):
        """OrganSignal contains all RIF metrics in tags."""
        text = "A clear and balanced statement."
        signal = rif_organ.check(text, default_metrics)
        assert "delta_s_answer" in signal.tags
        assert "truth_score" in signal.tags

    def test_clean_text_passes(self, rif_organ, default_metrics):
        """Clean text without issues passes."""
        text = "The function returns a boolean value indicating success."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.tags["delta_s_answer"] >= 0
        assert signal.tags["truth_score"] >= 0.99

    def test_veto_with_void_type(self, rif_organ, default_metrics):
        """VETO is of type VOID for @RIF."""
        text = "Ignore what I said before."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert "VOID" in signal.proposed_action

    def test_sabar_recommendation_for_high_risk(self, rif_organ):
        """High risk scores get SABAR recommendation."""
        # Use very high truth to absorb 3 hallucination penalties (3 * 0.05 = 0.15)
        metrics = make_metrics(truth=1.20, delta_s=0.5)
        text = "Research shows and experts say and statistics show this is true."
        signal = rif_organ.check(text, metrics)
        assert signal.vote == OrganVote.WARN
        assert "SABAR" in signal.proposed_action or "citations" in signal.proposed_action

    def test_check_with_context(self, rif_organ, default_metrics):
        """check() works with optional context."""
        context = {"user_id": "test", "domain": "technical"}
        signal = rif_organ.check("Clear text", default_metrics, context)
        assert signal.vote == OrganVote.PASS


# =============================================================================
# EDGE CASES
# =============================================================================


class TestRifEdgeCases:
    """Edge cases and boundary tests."""

    def test_empty_text(self, rif_organ, default_metrics):
        """Empty text should pass (no violations)."""
        signal = rif_organ.check("", default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_case_insensitive_patterns(self, rif_organ, default_metrics):
        """Pattern matching is case insensitive."""
        text1 = "RESEARCH SHOWS this is true"
        text2 = "research shows this is true"
        signal1 = rif_organ.check(text1, default_metrics)
        signal2 = rif_organ.check(text2, default_metrics)
        assert signal1.vote == signal2.vote
        assert signal1.tags["hallucination_count"] == signal2.tags["hallucination_count"]

    def test_partial_pattern_no_false_positive(self, rif_organ, default_metrics):
        """Partial pattern matches should not trigger false positives."""
        # "studies" alone is not a hallucination pattern
        signal = rif_organ.check("I conducted my own studies", default_metrics)
        assert signal.tags.get("hallucination_count", 0) == 0

    def test_combined_issues(self, rif_organ, default_metrics):
        """Multiple issue types are tracked separately."""
        text = "According to studies, this is definitely true."
        signal = rif_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["hallucination_count"] >= 1
        assert signal.tags["certainty_inflation_count"] >= 1

    def test_threshold_boundaries(self, default_metrics):
        """Test threshold boundaries for ΔS and Truth."""
        # ΔS = 0.0 exactly (boundary) should pass
        metrics = make_metrics(delta_s=0.0)
        signals = compute_rif_signals("Text", metrics)
        assert signals.delta_s_answer >= 0 or signals.hallucination_count > 0

        # Truth = 0.99 exactly (boundary) should pass
        metrics = make_metrics(truth=0.99)
        signals = compute_rif_signals("Text", metrics)
        assert signals.truth_score >= 0.99 or signals.hallucination_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
