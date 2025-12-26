"""
test_waw_geox_signals.py - Tests for @GEOX W@W Organ Signals (v36.3Omega)

Comprehensive tests for GeoxSignals dataclass and compute_geox_signals function:
- Physical impossibility pattern detection
- Physics violation pattern detection
- Resource impossibility pattern detection
- Reality grounding bonus patterns
- E_earth floor thresholds
- GeoxOrgan.check() integration
"""

import pytest
from arifos_core.waw.geox import GeoxOrgan, compute_geox_signals
from arifos_core.waw.base import OrganVote
from arifos_core.enforcement.metrics import Metrics


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
def geox_organ():
    """Create GeoxOrgan instance."""
    return GeoxOrgan()


# =============================================================================
# PHYSICAL IMPOSSIBILITY PATTERN DETECTION TESTS
# =============================================================================


class TestPhysicalImpossibilityPatterns:
    """Tests for physical impossibility pattern detection (AI claiming body)."""

    def test_i_can_touch_detected(self, geox_organ, default_metrics):
        """'I can touch' pattern triggers physical impossibility detection."""
        text = "I can touch the keyboard to help you."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 1

    def test_i_have_a_body_detected(self, geox_organ, default_metrics):
        """'I have a body' pattern triggers physical impossibility detection."""
        text = "Well, I have a body so I can help."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 1

    def test_i_can_see_you_detected(self, geox_organ, default_metrics):
        """'I can see you' pattern triggers physical impossibility detection."""
        text = "I can see you through the camera."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 1

    def test_i_can_hear_you_detected(self, geox_organ, default_metrics):
        """'I can hear you' pattern triggers physical impossibility detection."""
        text = "I can hear you speaking."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 1

    def test_i_will_physically_detected(self, geox_organ, default_metrics):
        """'I will physically' pattern triggers physical impossibility detection."""
        text = "I will physically assist you."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 1

    def test_multiple_physical_claims(self, geox_organ, default_metrics):
        """Multiple physical impossibility claims increase risk."""
        text = "I can touch things and I can see you."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physical_impossibility_count", 0) >= 2


# =============================================================================
# PHYSICS VIOLATION PATTERN DETECTION TESTS
# =============================================================================


class TestPhysicsViolationPatterns:
    """Tests for physics violation pattern detection."""

    def test_faster_than_light_detected(self, geox_organ, default_metrics):
        """'Faster than light' pattern triggers physics violation detection."""
        text = "We can travel faster than light."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physics_violation_count", 0) >= 1

    def test_perpetual_motion_detected(self, geox_organ, default_metrics):
        """'Perpetual motion' pattern triggers physics violation detection."""
        text = "This machine uses perpetual motion."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physics_violation_count", 0) >= 1

    def test_time_travel_detected(self, geox_organ, default_metrics):
        """'Time travel' pattern triggers physics violation detection."""
        text = "We can use time travel to fix this."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physics_violation_count", 0) >= 1

    def test_teleportation_detected(self, geox_organ, default_metrics):
        """'Teleportation' pattern triggers physics violation detection."""
        text = "Using teleportation we can move instantly."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physics_violation_count", 0) >= 1

    def test_infinite_energy_detected(self, geox_organ, default_metrics):
        """'Infinite energy' pattern triggers physics violation detection."""
        text = "We can harness infinite energy."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("physics_violation_count", 0) >= 1


# =============================================================================
# RESOURCE IMPOSSIBILITY PATTERN DETECTION TESTS
# =============================================================================


class TestResourceImpossibilityPatterns:
    """Tests for resource impossibility pattern detection."""

    def test_unlimited_memory_detected(self, geox_organ, default_metrics):
        """'Unlimited memory' pattern triggers resource impossibility detection."""
        text = "This has unlimited memory."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("resource_impossibility_count", 0) >= 1

    def test_infinite_storage_detected(self, geox_organ, default_metrics):
        """'Infinite storage' pattern triggers resource impossibility detection."""
        text = "We can store infinite storage."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("resource_impossibility_count", 0) >= 1

    def test_instant_processing_detected(self, geox_organ, default_metrics):
        """'Instant processing' pattern triggers resource impossibility detection."""
        text = "This uses instant processing."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("resource_impossibility_count", 0) >= 1

    def test_zero_latency_detected(self, geox_organ, default_metrics):
        """'Zero latency' pattern triggers resource impossibility detection."""
        text = "We achieve zero latency."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("resource_impossibility_count", 0) >= 1

    def test_multiple_resource_impossibilities(self, geox_organ, default_metrics):
        """Multiple resource impossibilities increase risk."""
        text = "We have unlimited memory, infinite storage, and instant processing."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("resource_impossibility_count", 0) >= 3
        # With 3 patterns, risk should be >= 0.30
        assert signal.tags.get("resource_impossibility_risk", 0) >= 0.30


# =============================================================================
# REALITY GROUNDING BONUS PATTERN TESTS
# =============================================================================


class TestGroundingBonusPatterns:
    """Tests for reality-grounding pattern bonuses."""

    def test_within_physical_constraints_bonus(self, default_metrics):
        """'Within physical constraints' pattern provides grounding bonus."""
        signals = compute_geox_signals(
            "This operates within physical constraints.",
            default_metrics
        )
        assert signals.grounding_bonus_count >= 1
        assert "grounding_bonus" in str(signals.notes)

    def test_hardware_limitations_bonus(self, default_metrics):
        """'Hardware limitations' pattern provides grounding bonus."""
        signals = compute_geox_signals(
            "We must consider hardware limitations.",
            default_metrics
        )
        assert signals.grounding_bonus_count >= 1

    def test_realistic_timeframe_bonus(self, default_metrics):
        """'Realistic timeframe' pattern provides grounding bonus."""
        signals = compute_geox_signals(
            "This can be done in a realistic timeframe.",
            default_metrics
        )
        assert signals.grounding_bonus_count >= 1

    def test_grounding_patterns_boost_e_earth(self, default_metrics):
        """Grounding patterns can boost E_earth above 1.0 (clamped)."""
        signals = compute_geox_signals(
            "Within physical constraints and hardware limitations.",
            default_metrics
        )
        # E_earth starts at 1.0, bonus doesn't push it higher due to clamping
        assert signals.e_earth == 1.0
        assert signals.grounding_bonus_count >= 2


# =============================================================================
# E_EARTH FLOOR THRESHOLD TESTS
# =============================================================================


class TestEEarthFloorThresholds:
    """Tests for E_earth floor thresholds."""

    def test_clean_text_e_earth_1(self, geox_organ, default_metrics):
        """Clean text has E_earth = 1.0."""
        signal = geox_organ.check("Here is the code solution.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.tags.get("e_earth", 0) == 1.0

    def test_physical_claim_reduces_e_earth(self, geox_organ, default_metrics):
        """Physical impossibility claim reduces E_earth."""
        signal = geox_organ.check("I can touch the keyboard.", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("e_earth", 1.0) < 1.0

    def test_physics_violation_reduces_e_earth(self, geox_organ, default_metrics):
        """Physics violation reduces E_earth."""
        signal = geox_organ.check("We can use time travel.", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert signal.tags.get("e_earth", 1.0) < 1.0

    def test_resource_impossibility_reduces_e_earth(self, geox_organ, default_metrics):
        """Resource impossibility reduces E_earth."""
        signal = geox_organ.check("This has unlimited memory.", default_metrics)
        assert signal.vote == OrganVote.WARN
        assert signal.tags.get("e_earth", 1.0) < 1.0


# =============================================================================
# COMPUTE_GEOX_SIGNALS FUNCTION TESTS
# =============================================================================


class TestComputeGeoxSignals:
    """Tests for compute_geox_signals function."""

    def test_clean_text_sound_physics(self, default_metrics):
        """Clean text has SOUND physics status."""
        signals = compute_geox_signals("Here is the code.", default_metrics)
        assert signals.e_earth == 1.0
        assert signals.physical_impossibility_count == 0
        assert signals.physics_violation_count == 0
        assert signals.resource_impossibility_count == 0
        assert "Physics=SOUND" in str(signals.notes)

    def test_resource_only_partial_physics(self, default_metrics):
        """Resource impossibility only gives PARTIAL physics status."""
        signals = compute_geox_signals("This has unlimited memory.", default_metrics)
        assert signals.resource_impossibility_count >= 1
        assert signals.physical_impossibility_count == 0
        assert signals.physics_violation_count == 0
        assert "Physics=PARTIAL" in str(signals.notes)

    def test_physical_claim_failed_physics(self, default_metrics):
        """Physical claim gives FAILED physics status."""
        signals = compute_geox_signals("I can touch you.", default_metrics)
        assert signals.physical_impossibility_count >= 1
        assert "Physics=FAILED" in str(signals.issues)

    def test_physics_violation_failed_physics(self, default_metrics):
        """Physics violation gives FAILED physics status."""
        signals = compute_geox_signals("Using perpetual motion.", default_metrics)
        assert signals.physics_violation_count >= 1
        assert "Physics=FAILED" in str(signals.issues)

    def test_e_earth_clamped_to_valid_range(self, default_metrics):
        """E_earth is clamped to [0, 1] range."""
        # Multiple physics violations would push E_earth negative
        signals = compute_geox_signals(
            "I can touch, I can see you, faster than light, time travel!",
            default_metrics
        )
        assert signals.e_earth >= 0.0
        assert signals.e_earth <= 1.0

    def test_tri_witness_earth_from_metrics(self, default_metrics):
        """Tri-witness earth is taken from metrics."""
        signals = compute_geox_signals("Clean text.", default_metrics)
        assert signals.tri_witness_earth == default_metrics.tri_witness


# =============================================================================
# GEOXORGAN.CHECK() INTEGRATION TESTS
# =============================================================================


class TestGeoxOrganCheck:
    """Integration tests for GeoxOrgan.check() method."""

    def test_organ_identity(self, geox_organ):
        """GeoxOrgan has correct identity."""
        assert geox_organ.organ_id == "@GEOX"
        assert geox_organ.domain == "physical_feasibility"
        assert geox_organ.primary_metric == "e_earth"
        assert geox_organ.veto_type == "HOLD-888"

    def test_clean_text_passes(self, geox_organ, default_metrics):
        """Clean text returns PASS."""
        signal = geox_organ.check("Here is the code solution.", default_metrics)
        assert signal.vote == OrganVote.PASS
        assert signal.floor_pass is True

    def test_signal_has_required_fields(self, geox_organ, default_metrics):
        """OrganSignal has all required fields."""
        signal = geox_organ.check("Test text", default_metrics)
        assert signal.organ_id == "@GEOX"
        assert signal.metric_name == "e_earth"
        assert signal.metric_value is not None
        assert signal.floor_threshold == 1.0
        assert signal.evidence != ""

    def test_signal_tags_populated(self, geox_organ, default_metrics):
        """Signal tags contain expected keys."""
        signal = geox_organ.check("Test text", default_metrics)
        assert "e_earth" in signal.tags

    def test_veto_has_hold_888_action(self, geox_organ, default_metrics):
        """VETO signals have HOLD-888 proposed action."""
        signal = geox_organ.check("I can touch the screen.", default_metrics)
        assert signal.vote == OrganVote.VETO
        assert "HOLD-888" in signal.proposed_action

    def test_check_with_context(self, geox_organ, default_metrics):
        """check() works with optional context."""
        context = {"user_id": "test", "domain": "technical"}
        signal = geox_organ.check("Here is the solution.", default_metrics, context)
        assert signal.vote == OrganVote.PASS

    def test_combined_violations_accumulate(self, geox_organ, default_metrics):
        """Multiple violation types accumulate in tags."""
        text = "I can touch things and we use time travel with unlimited memory."
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO
        # Should detect physical impossibility, physics violation, and resource impossibility
        assert signal.tags.get("physical_impossibility_count", 0) >= 1
        assert signal.tags.get("physics_violation_count", 0) >= 1
        assert signal.tags.get("resource_impossibility_count", 0) >= 1


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_text(self, geox_organ, default_metrics):
        """Empty text passes without issues."""
        signal = geox_organ.check("", default_metrics)
        assert signal.vote == OrganVote.PASS

    def test_case_insensitive_detection(self, geox_organ, default_metrics):
        """Pattern detection is case-insensitive."""
        text = "I CAN TOUCH THE SCREEN!"
        signal = geox_organ.check(text, default_metrics)
        assert signal.vote == OrganVote.VETO

    def test_physical_claim_in_quote(self, geox_organ, default_metrics):
        """Physical claims in quotes are still detected (conservative)."""
        text = "The user said 'I can touch the screen'."
        signal = geox_organ.check(text, default_metrics)
        # Note: Current implementation doesn't distinguish quotes
        # This is acceptable conservative behavior
        assert signal.vote == OrganVote.VETO

    def test_e_earth_not_negative(self, default_metrics):
        """E_earth cannot go below 0."""
        # Many violations would push E_earth way negative without clamping
        signals = compute_geox_signals(
            "I can touch, I can see you, I can hear you, I have a body, "
            "faster than light, perpetual motion, time travel, teleportation",
            default_metrics
        )
        assert signals.e_earth >= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
