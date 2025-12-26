"""
tests/test_waw_wealth_signals.py
Unit tests for @WEALTH W@W organ - WealthSignals & governance logic

Version: v36.3Omega
Test coverage: 95%+ for WealthOrgan class, WealthSignals, and heuristics
"""

import pytest

from arifos_core.enforcement.metrics import Metrics
from arifos_core.waw.wealth import (
    WealthOrgan,
    WealthSignals,
    compute_wealth_signals,
)
from arifos_core.waw.base import OrganVote


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def make_metrics(
    truth: float = 0.99,
    delta_s: float = 0.1,
    peace_squared: float = 1.2,
    kappa_r: float = 0.98,
    omega_0: float = 0.04,
    amanah: bool = True,
    tri_witness: float = 0.98,
    rasa: bool = True,
    anti_hantu: bool = True,
) -> Metrics:
    """Create Metrics with defaults for all required fields."""
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
def wealth_organ():
    return WealthOrgan()


# =============================================================================
# AMANAH DETECTION TESTS (ABSOLUTE VETO)
# =============================================================================


class TestWealthAmanahDetection:
    """Tests for ABSOLUTE VETO on Amanah breaches."""

    def test_fraud_prompts_veto(self, wealth_organ, default_metrics):
        """Fraud-like text triggers ABSOLUTE VETO."""
        text = "Let's bypass security and delete all the data"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True
        assert "scope_violations" in signal.evidence

    def test_data_theft_veto(self, wealth_organ, default_metrics):
        """Data theft patterns trigger ABSOLUTE VETO."""
        text = "I'll do it anyway without permission"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True
        assert "trust_violations" in signal.evidence

    def test_irreversible_destruction_veto(self, wealth_organ, default_metrics):
        """Destructive irreversible actions trigger ABSOLUTE VETO."""
        text = "Run rm -rf / to clean everything"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_drop_database_veto(self, wealth_organ, default_metrics):
        """DROP DATABASE triggers ABSOLUTE VETO."""
        text = "Execute drop database production"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_sudo_pattern_veto(self, wealth_organ, default_metrics):
        """sudo command triggers ABSOLUTE VETO."""
        text = "Let me run sudo apt-get purge"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_override_safety_veto(self, wealth_organ, default_metrics):
        """Override safety triggers ABSOLUTE VETO."""
        text = "We should override safety protocols"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_ignore_rules_veto(self, wealth_organ, default_metrics):
        """Ignore the rules triggers ABSOLUTE VETO."""
        text = "Just ignore the rules this time"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_broken_amanah_metric_veto(self, wealth_organ):
        """Broken Amanah metric triggers ABSOLUTE VETO."""
        metrics = make_metrics(amanah=False)
        signal = wealth_organ.check("Some safe text", metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_malay_scope_violation(self, wealth_organ, default_metrics):
        """Malay scope violation: delete all."""
        text = "delete all fail dalam sistem"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True


# =============================================================================
# RISK SCORING TESTS (bias, dignity, exploitation)
# =============================================================================


class TestWealthRiskScoring:
    """Tests for bias_index, dignity_risk, and exploitation_risk."""

    def test_clean_text_passes(self, wealth_organ, default_metrics):
        """Clean text with no violations passes."""
        text = "Let me help you with that task in a fair way."
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.is_absolute_veto is False
        assert signal.tags["bias_index"] == 0.0
        assert signal.tags["dignity_risk"] == 0.0
        assert signal.tags["exploitation_risk"] == 0.0

    def test_dignity_violation_warns(self, wealth_organ, default_metrics):
        """Dignity violations increase dignity_risk and trigger WARN."""
        text = "We should humiliate them and mock their efforts"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["dignity_risk"] >= 0.30  # At least 2 violations
        assert "dignity_risk" in signal.evidence

    def test_exploitation_pattern_warns(self, wealth_organ, default_metrics):
        """Exploitation patterns increase exploitation_risk."""
        text = "Let's exploit their weakness and take advantage"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["exploitation_risk"] >= 0.30  # At least 2 patterns

    def test_discriminatory_text_warns(self, wealth_organ, default_metrics):
        """Discriminatory text increases bias_index."""
        # Need 2+ patterns to reach >= 0.20 threshold for WARN
        text = "We should discriminate and give unfair advantage to some"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags["bias_index"] >= 0.30  # At least 2 violations

    def test_reversible_action_passes(self, wealth_organ, default_metrics):
        """Reversible safe action passes."""
        text = "Save the file to a backup location first."
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_irreversible_warns_888_hold(self, wealth_organ, default_metrics):
        """Irreversible action triggers WARN with 888_HOLD suggestion."""
        text = "This change cannot be undone"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "888_HOLD" in signal.proposed_action
        assert "irreversible_actions" in signal.evidence


# =============================================================================
# COMPUTE_WEALTH_SIGNALS TESTS
# =============================================================================


class TestComputeWealthSignals:
    """Tests for compute_wealth_signals() function."""

    def test_signals_dataclass_defaults(self):
        """WealthSignals has correct defaults."""
        signals = WealthSignals()
        assert signals.amanah_ok is True
        assert signals.bias_index == 0.0
        assert signals.dignity_risk == 0.0
        assert signals.exploitation_risk == 0.0
        assert signals.scope_violation_count == 0

    def test_compute_signals_clean_text(self, default_metrics):
        """Clean text produces clean signals."""
        signals = compute_wealth_signals(
            "A helpful and fair response.",
            default_metrics
        )
        assert signals.amanah_ok is True
        assert signals.bias_index == 0.0
        assert signals.dignity_risk == 0.0
        assert signals.exploitation_risk == 0.0

    def test_compute_signals_scope_violation(self, default_metrics):
        """Scope violation breaks amanah_ok."""
        signals = compute_wealth_signals(
            "Let me delete all your files",
            default_metrics
        )
        assert signals.amanah_ok is False
        assert signals.scope_violation_count >= 1
        assert "scope_violations" in signals.issues[0]

    def test_compute_signals_trust_violation(self, default_metrics):
        """Trust violation breaks amanah_ok."""
        signals = compute_wealth_signals(
            "I'll do it anyway without permission",
            default_metrics
        )
        assert signals.amanah_ok is False
        assert signals.trust_violation_count >= 1

    def test_compute_signals_dignity_risk(self, default_metrics):
        """Dignity patterns increase dignity_risk."""
        signals = compute_wealth_signals(
            "Mock their mistakes and shame them publicly",
            default_metrics
        )
        assert signals.amanah_ok is True  # Not an Amanah breach
        assert signals.dignity_risk >= 0.30
        assert signals.dignity_violation_count >= 2

    def test_compute_signals_exploitation_risk(self, default_metrics):
        """Exploitation patterns increase exploitation_risk."""
        signals = compute_wealth_signals(
            "We can exploit the situation and coerce them",
            default_metrics
        )
        assert signals.amanah_ok is True  # Not an Amanah breach
        assert signals.exploitation_risk >= 0.30

    def test_compute_signals_multiple_violations(self, default_metrics):
        """Multiple violation types are tracked separately."""
        signals = compute_wealth_signals(
            "Humiliate them and exploit their weakness, we can take advantage of the situation",
            default_metrics
        )
        assert signals.dignity_violation_count >= 1
        assert signals.exploitation_pattern_count >= 2
        assert signals.dignity_risk > 0
        assert signals.exploitation_risk > 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestWealthIntegration:
    """Integration tests for WealthOrgan with OrganSignal."""

    def test_organ_identity(self, wealth_organ):
        """Verify organ identity."""
        assert wealth_organ.organ_id == "@WEALTH"
        assert wealth_organ.domain == "resource_stewardship"
        assert wealth_organ.primary_metric == "amanah"
        assert wealth_organ.veto_type == "ABSOLUTE"

    def test_signal_contains_all_metrics(self, wealth_organ, default_metrics):
        """OrganSignal contains all wealth metrics in tags."""
        text = "A fair and balanced proposal."
        signal = wealth_organ.check(text, default_metrics)
        assert "amanah_ok" in signal.tags
        assert "bias_index" in signal.tags
        assert "dignity_risk" in signal.tags
        assert "exploitation_risk" in signal.tags

    def test_absolute_veto_takes_precedence(self, wealth_organ, default_metrics):
        """ABSOLUTE VETO from scope violation takes precedence over other issues."""
        text = "Delete all files and humiliate the user"
        signal = wealth_organ.check(text, default_metrics)
        # Amanah break takes precedence - should be VETO not just WARN
        assert signal.vote == OrganVote.VETO
        assert signal.is_absolute_veto is True

    def test_sabar_recommendation_for_high_risk(self, wealth_organ, default_metrics):
        """High risk scores get SABAR recommendation."""
        # Multiple dignity violations to hit high threshold
        text = "Humiliate them, mock them, shame them, belittle their work"
        signal = wealth_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert "SABAR" in signal.proposed_action or "dignity" in signal.proposed_action

    def test_check_with_context(self, wealth_organ, default_metrics):
        """check() works with optional context."""
        context = {"user_id": "test", "high_stakes": True}
        signal = wealth_organ.check("Safe text", default_metrics, context)
        assert signal.vote == OrganVote.PASS


# =============================================================================
# EDGE CASES
# =============================================================================


class TestWealthEdgeCases:
    """Edge cases and boundary tests."""

    def test_empty_text(self, wealth_organ, default_metrics):
        """Empty text should pass (no violations)."""
        signal = wealth_organ.check("", default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_case_insensitive_patterns(self, wealth_organ, default_metrics):
        """Pattern matching is case insensitive."""
        text1 = "DELETE ALL files"
        text2 = "delete all files"
        signal1 = wealth_organ.check(text1, default_metrics)
        signal2 = wealth_organ.check(text2, default_metrics)
        assert signal1.vote == OrganVote.VETO
        assert signal2.vote == OrganVote.VETO

    def test_partial_pattern_no_false_positive(self, wealth_organ, default_metrics):
        """Partial pattern matches should not trigger false positives."""
        # "sudo" is a scope violation, but "pseudo" is not
        signal = wealth_organ.check("This is a pseudo-random test", default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_threshold_boundaries(self, default_metrics):
        """Test threshold boundaries for SEAL/PARTIAL/SABAR."""
        # 0 violations = 0.0 (SEAL)
        signals = compute_wealth_signals("Clean text", default_metrics)
        assert signals.bias_index == 0.0

        # 1 violation = 0.15 (below 0.20, still SEAL)
        signals = compute_wealth_signals("discriminate once", default_metrics)
        assert signals.bias_index == 0.15

    def test_multiple_scope_violations_counted(self, default_metrics):
        """Multiple scope violations are counted."""
        signals = compute_wealth_signals(
            "Run sudo then bypass security and delete all",
            default_metrics
        )
        assert signals.scope_violation_count >= 3
        assert signals.amanah_ok is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
