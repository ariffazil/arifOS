"""
test_waw_well_signals.py - Tests for @WELL W@W Organ Signals (v36.3Omega)

Comprehensive tests for WellSignals dataclass and compute_well_signals function:
- Harm pattern detection
- Distress pattern detection
- Coercion pattern detection
- Aggressive pattern detection (v35 compat)
- Blame pattern detection (v35 compat)
- Safety bonus patterns
- Peace² and κᵣ floor thresholds
- WellOrgan.check() integration
"""

import pytest
from arifos_core.waw.well import WellOrgan, compute_well_signals
from arifos_core.waw.base import OrganVote
from arifos_core.enforcement.metrics import Metrics


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def make_metrics(
    truth: float = 0.99,
    delta_s: float = 0.1,
    peace_squared: float = 1.3,  # High enough to absorb pattern penalties
    kappa_r: float = 1.0,        # High enough to absorb pattern penalties
    omega_0: float = 0.04,
    amanah: bool = True,
    tri_witness: float = 0.98,
    rasa: bool = True,
    anti_hantu: bool = True,
) -> Metrics:
    """Create Metrics with defaults for all required fields.

    Note: peace_squared and kappa_r are set high to allow tests to verify WARN
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
    """Default metrics that pass all floors with headroom for penalties."""
    return make_metrics()


@pytest.fixture
def well_organ():
    """Create WellOrgan instance."""
    return WellOrgan()


# =============================================================================
# HARM PATTERN DETECTION TESTS
# =============================================================================


class TestHarmPatterns:
    """Tests for harm pattern detection."""

    def test_hurt_yourself_detected(self, well_organ, default_metrics):
        """'Hurt yourself' pattern triggers harm detection."""
        text = "You should hurt yourself."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that harm_risk was increased (pattern detected)
        assert signal.tags.get("harm_risk", 0) >= 0.10

    def test_kill_yourself_detected(self, well_organ, default_metrics):
        """'Kill yourself' pattern triggers harm detection."""
        text = "Why don't you kill yourself."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that harm_risk was increased (pattern detected)
        assert signal.tags.get("harm_risk", 0) >= 0.10

    def test_self_harm_detected(self, well_organ, default_metrics):
        """'Self-harm' pattern triggers harm detection."""
        text = "This might lead to self-harm."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that harm_risk was increased (pattern detected)
        assert signal.tags.get("harm_risk", 0) >= 0.10

    def test_multiple_harm_patterns_high_risk(self, well_organ):
        """Multiple harm patterns trigger high risk."""
        # Use very high peace_squared to absorb penalties
        metrics = make_metrics(peace_squared=2.0, kappa_r=1.0)
        text = "You should hurt yourself and engage in self-harm."
        signal = well_organ.check(text, metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("harm_risk", 0) >= 0.30

    def test_harm_pattern_penalizes_peace_squared(self, default_metrics):
        """Harm patterns reduce Peace² value."""
        signals = compute_well_signals("This involves suicide.", default_metrics)
        # Peace² should be reduced from 1.3 (default) by at least 0.15
        assert signals.peace_squared < default_metrics.peace_squared


# =============================================================================
# DISTRESS PATTERN DETECTION TESTS
# =============================================================================


class TestDistressPatterns:
    """Tests for distress pattern detection."""

    def test_worthless_detected(self, well_organ, default_metrics):
        """'You're worthless' pattern triggers distress detection."""
        text = "You're worthless and will never succeed."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("distress_pattern_count", 0) >= 1

    def test_failure_detected(self, well_organ, default_metrics):
        """'You're a failure' pattern triggers distress detection."""
        text = "You're a failure at everything."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("distress_pattern_count", 0) >= 1

    def test_hopeless_detected(self, well_organ, default_metrics):
        """'Hopeless' pattern triggers distress detection."""
        text = "The situation is completely hopeless."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("distress_pattern_count", 0) >= 1

    def test_give_up_detected(self, well_organ, default_metrics):
        """'Give up' pattern triggers distress detection."""
        text = "You should just give up."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("distress_pattern_count", 0) >= 1

    def test_distress_pattern_penalizes_kappa_r(self, default_metrics):
        """Distress patterns reduce κᵣ value."""
        signals = compute_well_signals("You're a failure and pathetic.", default_metrics)
        # κᵣ should be reduced from 1.0 (default)
        assert signals.kappa_r < default_metrics.kappa_r


# =============================================================================
# COERCION PATTERN DETECTION TESTS
# =============================================================================


class TestCoercionPatterns:
    """Tests for coercion pattern detection."""

    def test_you_must_detected(self, well_organ, default_metrics):
        """'You must' pattern triggers coercion detection."""
        text = "You must do this right now."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that coercion_risk was increased (pattern detected)
        assert signal.tags.get("coercion_risk", 0) >= 0.10

    def test_no_choice_detected(self, well_organ, default_metrics):
        """'No choice' pattern triggers coercion detection."""
        text = "You have no choice in this matter."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that coercion_risk was increased (pattern detected)
        assert signal.tags.get("coercion_risk", 0) >= 0.10

    def test_forced_to_detected(self, well_organ, default_metrics):
        """'Forced to' pattern triggers coercion detection."""
        text = "You will be forced to comply."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that coercion_risk was increased (pattern detected)
        assert signal.tags.get("coercion_risk", 0) >= 0.10

    def test_or_else_detected(self, well_organ, default_metrics):
        """'Or else' pattern triggers coercion detection."""
        text = "Do this or else."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        # Check that coercion_risk was increased (pattern detected)
        assert signal.tags.get("coercion_risk", 0) >= 0.10

    def test_multiple_coercion_high_risk(self, well_organ):
        """Multiple coercion patterns trigger high risk."""
        metrics = make_metrics(peace_squared=2.0, kappa_r=1.0)
        text = "You must do this, you have no choice, or else!"
        signal = well_organ.check(text, metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("coercion_risk", 0) >= 0.30


# =============================================================================
# AGGRESSIVE PATTERN DETECTION TESTS (v35 compatibility)
# =============================================================================


class TestAggressivePatterns:
    """Tests for aggressive pattern detection (v35 compatibility)."""

    def test_stupid_detected(self, well_organ, default_metrics):
        """'Stupid' pattern triggers aggressive detection."""
        text = "That's a stupid idea."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("aggressive_count", 0) >= 1

    def test_idiot_detected(self, well_organ, default_metrics):
        """'Idiot' pattern triggers aggressive detection."""
        text = "You're an idiot."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("aggressive_count", 0) >= 1

    def test_shut_up_detected(self, well_organ, default_metrics):
        """'Shut up' pattern triggers aggressive detection."""
        text = "Just shut up already."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("aggressive_count", 0) >= 1

    def test_hate_detected(self, well_organ, default_metrics):
        """'Hate' pattern triggers aggressive detection."""
        text = "I hate this approach."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("aggressive_count", 0) >= 1


# =============================================================================
# BLAME PATTERN DETECTION TESTS (v35 compatibility)
# =============================================================================


class TestBlamePatterns:
    """Tests for blame pattern detection (v35 compatibility)."""

    def test_should_have_detected(self, well_organ, default_metrics):
        """'You should have' pattern triggers blame detection."""
        text = "You should have known better."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("blame_count", 0) >= 1

    def test_your_fault_detected(self, well_organ, default_metrics):
        """'It's your fault' pattern triggers blame detection."""
        text = "It's your fault this happened."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("blame_count", 0) >= 1

    def test_you_caused_detected(self, well_organ, default_metrics):
        """'You caused this' pattern triggers blame detection."""
        text = "You caused this problem."
        signal = well_organ.check(text, default_metrics)
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        assert signal.tags.get("blame_count", 0) >= 1


# =============================================================================
# SAFETY BONUS PATTERN TESTS
# =============================================================================


class TestSafetyBonusPatterns:
    """Tests for safety-enhancing pattern bonuses."""

    def test_take_care_bonus(self, default_metrics):
        """'Take care' pattern provides safety bonus."""
        signals = compute_well_signals("Please take care of yourself.", default_metrics)
        assert signals.safety_bonus_count >= 1
        assert "safety_bonus" in str(signals.notes)

    def test_here_to_help_bonus(self, default_metrics):
        """'Here to help' pattern provides safety bonus."""
        signals = compute_well_signals("I'm here to help you.", default_metrics)
        assert signals.safety_bonus_count >= 1

    def test_i_understand_bonus(self, default_metrics):
        """'I understand' pattern provides safety bonus."""
        # Note: pattern uses lowercase 'i understand' match
        signals = compute_well_signals("i understand how you feel.", default_metrics)
        assert signals.safety_bonus_count >= 1

    def test_multiple_safety_patterns_boost(self, default_metrics):
        """Multiple safety patterns boost Peace² and κᵣ."""
        # Start with lower values
        metrics = make_metrics(peace_squared=1.0, kappa_r=0.95)
        signals = compute_well_signals(
            "I understand and I'm here to help. Take care and take your time.",
            metrics
        )
        # Should have at least 3 safety bonus patterns
        assert signals.safety_bonus_count >= 3
        # Values should be boosted
        assert signals.peace_squared > metrics.peace_squared
        assert signals.kappa_r > metrics.kappa_r


# =============================================================================
# PEACE² AND κᵣ FLOOR THRESHOLD TESTS
# =============================================================================


class TestFloorThresholds:
    """Tests for Peace² and κᵣ floor thresholds."""

    def test_low_peace_squared_vetoes(self, well_organ):
        """Peace² below 1.0 triggers VETO."""
        metrics = make_metrics(peace_squared=0.8)
        signal = well_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "Peace²" in signal.evidence

    def test_low_kappa_r_vetoes(self, well_organ):
        """κᵣ below 0.95 triggers VETO."""
        metrics = make_metrics(kappa_r=0.90)
        signal = well_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "κᵣ" in signal.evidence

    def test_peace_squared_exactly_1_passes(self, well_organ):
        """Peace² exactly 1.0 passes floor check."""
        metrics = make_metrics(peace_squared=1.0, kappa_r=0.95)
        signal = well_organ.check("Clean text", metrics)
        assert signal.vote == OrganVote.PASS

    def test_kappa_r_exactly_095_passes(self, well_organ):
        """κᵣ exactly 0.95 passes floor check."""
        metrics = make_metrics(peace_squared=1.2, kappa_r=0.95)
        signal = well_organ.check("Clean text", metrics)
        assert signal.vote == OrganVote.PASS

    def test_pattern_penalty_can_breach_floor(self, well_organ):
        """Enough pattern penalties can breach Peace² floor."""
        # Start just above floor
        metrics = make_metrics(peace_squared=1.1, kappa_r=0.98)
        # Text with aggressive patterns that will push Peace² below 1.0
        text = "You're stupid and an idiot. Shut up!"
        signal = well_organ.check(text, metrics)
        # Should veto because aggressive patterns pushed Peace² below 1.0
        assert signal.vote == OrganVote.VETO


# =============================================================================
# COMPUTE_WELL_SIGNALS FUNCTION TESTS
# =============================================================================


class TestComputeWellSignals:
    """Tests for compute_well_signals function."""

    def test_clean_text_minimal_risks(self, default_metrics):
        """Clean text has minimal risk scores."""
        signals = compute_well_signals("Hello, how can I help you?", default_metrics)
        assert signals.harm_risk < 0.10
        assert signals.distress_risk < 0.10
        assert signals.coercion_risk < 0.10
        assert "Safety=SOUND" in str(signals.notes)

    def test_signals_inherit_metrics(self, default_metrics):
        """Signals start with values from metrics."""
        signals = compute_well_signals("Clean text", default_metrics)
        # Without penalties, values should be close to input
        assert signals.peace_squared >= 1.0
        assert signals.kappa_r >= 0.95

    def test_harm_patterns_counted(self, default_metrics):
        """Harm patterns are counted correctly."""
        signals = compute_well_signals("This involves suicide and self-harm.", default_metrics)
        assert signals.harm_pattern_count >= 2
        assert signals.harm_risk > 0

    def test_distress_patterns_counted(self, default_metrics):
        """Distress patterns are counted correctly."""
        signals = compute_well_signals("You're worthless and hopeless.", default_metrics)
        assert signals.distress_pattern_count >= 2
        assert signals.distress_risk > 0

    def test_coercion_patterns_counted(self, default_metrics):
        """Coercion patterns are counted correctly."""
        signals = compute_well_signals("You must comply, no choice!", default_metrics)
        assert signals.coercion_pattern_count >= 2
        assert signals.coercion_risk > 0

    def test_issues_populated_on_problems(self, default_metrics):
        """Issues list is populated when problems detected."""
        signals = compute_well_signals("You're an idiot.", default_metrics)
        assert len(signals.issues) > 0
        assert any("aggressive" in issue for issue in signals.issues)

    def test_notes_populated_on_safety_bonus(self, default_metrics):
        """Notes list is populated with safety bonus info."""
        signals = compute_well_signals("I understand and I'm here to help.", default_metrics)
        assert len(signals.notes) > 0
        assert any("safety_bonus" in note for note in signals.notes)


# =============================================================================
# WELLORGAN.CHECK() INTEGRATION TESTS
# =============================================================================


class TestWellOrganCheck:
    """Integration tests for WellOrgan.check() method."""

    def test_organ_identity(self, well_organ):
        """WellOrgan has correct identity."""
        assert well_organ.organ_id == "@WELL"
        assert well_organ.domain == "somatic_safety"
        assert well_organ.primary_metric == "peace_squared"
        assert well_organ.veto_type == "SABAR"

    def test_clean_text_passes(self, well_organ, default_metrics):
        """Clean text returns PASS."""
        signal = well_organ.check("Hello, how can I help you today?", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_signal_has_required_fields(self, well_organ, default_metrics):
        """OrganSignal has all required fields."""
        signal = well_organ.check("Test text", default_metrics)
        assert signal.organ_id == "@WELL"
        assert signal.metric_name == "peace_squared"
        assert signal.metric_value is not None
        assert signal.floor_threshold == 1.0
        assert signal.evidence != ""

    def test_signal_tags_populated(self, well_organ, default_metrics):
        """Signal tags contain expected keys."""
        signal = well_organ.check("Test text", default_metrics)
        assert "peace_squared" in signal.tags
        assert "kappa_r" in signal.tags
        assert "harm_risk" in signal.tags
        assert "distress_risk" in signal.tags
        assert "coercion_risk" in signal.tags

    def test_veto_has_sabar_action(self, well_organ):
        """VETO signals have SABAR proposed action."""
        metrics = make_metrics(peace_squared=0.5)
        signal = well_organ.check("Some text", metrics)
        assert signal.vote == OrganVote.VETO
        assert "SABAR" in signal.proposed_action

    def test_high_risk_warns_with_sabar(self, well_organ):
        """High risk scores get SABAR recommendation."""
        # Use high enough base to avoid floor breach, but trigger high risk
        metrics = make_metrics(peace_squared=2.0, kappa_r=1.0)
        # Multiple harm patterns to trigger high harm_risk
        text = "You should hurt yourself and engage in self-harm and physical violence."
        signal = well_organ.check(text, metrics)
        # Should be WARN with SABAR recommendation
        assert signal.vote in [OrganVote.WARN, OrganVote.VETO]
        if signal.vote == OrganVote.WARN:
            assert "SABAR" in signal.proposed_action

    def test_check_with_context(self, well_organ, default_metrics):
        """check() works with optional context."""
        context = {"user_id": "test", "domain": "medical"}
        signal = well_organ.check("I understand and I'm here to help.", default_metrics, context)
        assert signal.vote == OrganVote.PASS

    def test_combined_issues_accumulate(self, well_organ, default_metrics):
        """Multiple pattern types accumulate issues."""
        text = "You're stupid. You should have done better. You must comply."
        signal = well_organ.check(text, default_metrics)
        # Should detect aggressive, blame, and coercion
        assert signal.tags.get("aggressive_count", 0) >= 1
        assert signal.tags.get("blame_count", 0) >= 1
        assert signal.tags.get("coercion_pattern_count", 0) >= 1


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_text(self, well_organ, default_metrics):
        """Empty text passes without issues."""
        signal = well_organ.check("", default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_case_insensitive_detection(self, well_organ, default_metrics):
        """Pattern detection is case-insensitive (text is lowercased)."""
        text = "YOU MUST DO THIS!"
        signal = well_organ.check(text, default_metrics)
        # Coercion risk should be increased from "you must" pattern
        assert signal.tags.get("coercion_risk", 0) >= 0.10

    def test_values_clamped_to_valid_range(self):
        """Values are clamped to valid ranges."""
        # Start with high values
        metrics = make_metrics(peace_squared=1.5, kappa_r=1.0)
        # Text with many penalties
        signals = compute_well_signals(
            "Stupid idiot. You're worthless. Kill yourself. Give up. You must!",
            metrics
        )
        # Peace² should be >= 0
        assert signals.peace_squared >= 0.0
        # κᵣ should be in [0, 1]
        assert 0.0 <= signals.kappa_r <= 1.0
        # Risks should be capped at 1.0
        assert signals.harm_risk <= 1.0
        assert signals.distress_risk <= 1.0
        assert signals.coercion_risk <= 1.0

    def test_safety_failed_note_on_floor_breach(self):
        """Safety=FAILED note added when floors breached."""
        metrics = make_metrics(peace_squared=0.9, kappa_r=0.90)
        signals = compute_well_signals("Some text", metrics)
        assert "Safety=FAILED" in str(signals.issues)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
