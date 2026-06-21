"""
Schema contract tests for arifosmcp.schemas.art

Validates:
  - TrustBand, ToolLifecycle, ArtVerdict enum integrity
  - ArtToolState Pydantic strict-mode enforcement
  - ArtPrecheckResult construction and constraints
  - Extra field rejection
  - Trust score bounds
  - DEGRADED not yet in runtime/art.py ToolState
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arifosmcp.schemas.art import (
    ArtPrecheckResult,
    ArtToolState,
    ArtVerdict,
    ToolLifecycle,
    TrustBand,
)
from arifosmcp.schemas.kernel_envelope import ActionClass


# ═══════════════════════════════════════════════════════════════════════
# ENUM INTEGRITY
# ═══════════════════════════════════════════════════════════════════════


class TestTrustBand:
    def test_all_values_present(self):
        assert TrustBand.TRUST_HIGH.value == "TRUST_HIGH"
        assert TrustBand.TRUST_MEDIUM.value == "TRUST_MEDIUM"
        assert TrustBand.TRUST_LOW.value == "TRUST_LOW"
        assert TrustBand.TRUST_CRITICAL.value == "TRUST_CRITICAL"

    def test_four_bands(self):
        assert len(TrustBand) == 4


class TestToolLifecycle:
    def test_six_values_in_target(self):
        """Target schema has 6 values (includes DEGRADED)."""
        values = {e.value for e in ToolLifecycle}
        assert values == {
            "UNTRUSTED",
            "OBSERVED",
            "TRUSTED",
            "DEGRADED",
            "FALLBACK",
            "ABANDONED",
        }

    def test_degraded_not_in_runtime_toolstate(self):
        """DEGRADED is aspirational — runtime/art.py ToolState has only 5 values."""
        from arifosmcp.runtime.art import ToolState

        runtime_values = {e.value for e in ToolState}
        assert "DEGRADED" not in runtime_values, (
            "DEGRADED must NOT be in runtime/art.py ToolState until 888_HOLD ratified"
        )
        assert len(runtime_values) == 5


class TestArtVerdict:
    def test_four_verdicts(self):
        values = {e.value for e in ArtVerdict}
        assert values == {"PROCEED", "SABAR", "HOLD", "REJECT"}


# ═══════════════════════════════════════════════════════════════════════
# ArtToolState — strict model enforcement
# ═══════════════════════════════════════════════════════════════════════


class TestArtToolState:
    def test_valid_construction(self):
        s = ArtToolState(
            tool_name="test_tool",
            lifecycle=ToolLifecycle.OBSERVED,
            trust_score=0.75,
            trust_band=TrustBand.TRUST_MEDIUM,
            action_class=ActionClass.MUTATE,
        )
        assert s.tool_name == "test_tool"
        assert s.lifecycle == ToolLifecycle.OBSERVED
        assert s.trust_score == 0.75

    def test_action_class_not_blast_radius(self):
        """action_class uses ActionClass, not BlastRadius. Two axes."""
        s = ArtToolState(
            tool_name="t",
            lifecycle=ToolLifecycle.UNTRUSTED,
            trust_score=0.5,
            trust_band=TrustBand.TRUST_LOW,
            action_class=ActionClass.OBSERVE,
        )
        assert s.action_class == ActionClass.OBSERVE

    def test_defaults(self):
        s = ArtToolState(
            tool_name="t",
            lifecycle=ToolLifecycle.UNTRUSTED,
            trust_score=0.5,
            trust_band=TrustBand.TRUST_LOW,
            action_class=ActionClass.OBSERVE,
        )
        assert s.success_90d == 0
        assert s.failure_90d == 0
        assert s.hold_90d == 0
        assert s.rollback_90d == 0
        assert s.last_failure_code is None
        assert s.last_verified_at is None
        assert s.metadata == {}

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            ArtToolState(
                tool_name="t",
                lifecycle=ToolLifecycle.UNTRUSTED,
                trust_score=0.5,
                trust_band=TrustBand.TRUST_LOW,
                action_class=ActionClass.OBSERVE,
                not_a_field=999,
            )

    def test_trust_score_above_one_rejected(self):
        with pytest.raises(ValidationError):
            ArtToolState(
                tool_name="t",
                lifecycle=ToolLifecycle.UNTRUSTED,
                trust_score=1.5,
                trust_band=TrustBand.TRUST_HIGH,
                action_class=ActionClass.OBSERVE,
            )

    def test_trust_score_below_zero_rejected(self):
        with pytest.raises(ValidationError):
            ArtToolState(
                tool_name="t",
                lifecycle=ToolLifecycle.UNTRUSTED,
                trust_score=-0.1,
                trust_band=TrustBand.TRUST_CRITICAL,
                action_class=ActionClass.OBSERVE,
            )

    def test_negative_counts_rejected(self):
        with pytest.raises(ValidationError):
            ArtToolState(
                tool_name="t",
                lifecycle=ToolLifecycle.UNTRUSTED,
                trust_score=0.5,
                trust_band=TrustBand.TRUST_LOW,
                action_class=ActionClass.OBSERVE,
                success_90d=-1,
            )

    def test_all_seven_action_classes_accepted(self):
        for ac in ActionClass:
            s = ArtToolState(
                tool_name="t",
                lifecycle=ToolLifecycle.UNTRUSTED,
                trust_score=0.5,
                trust_band=TrustBand.TRUST_LOW,
                action_class=ac,
            )
            assert s.action_class == ac


# ═══════════════════════════════════════════════════════════════════════
# ArtPrecheckResult — reflex output contract
# ═══════════════════════════════════════════════════════════════════════


class TestArtPrecheckResult:
    @pytest.fixture
    def tool_state(self):
        return ArtToolState(
            tool_name="test",
            lifecycle=ToolLifecycle.TRUSTED,
            trust_score=0.9,
            trust_band=TrustBand.TRUST_HIGH,
            action_class=ActionClass.MUTATE,
        )

    def test_valid_construction(self, tool_state):
        r = ArtPrecheckResult(
            verdict=ArtVerdict.PROCEED,
            tool_state=tool_state,
            required_act_pattern="DEFAULT_DEPLOY",
        )
        assert r.verdict == ArtVerdict.PROCEED
        assert r.required_act_pattern == "DEFAULT_DEPLOY"
        assert r.required_dry_run is True
        assert r.required_human_gate is False
        assert r.required_canary is False

    def test_hold_with_human_gate(self, tool_state):
        r = ArtPrecheckResult(
            verdict=ArtVerdict.HOLD,
            tool_state=tool_state,
            required_act_pattern="HUMAN_IN_LOOP_CHANGE",
            reasons=["low trust"],
            required_human_gate=True,
            required_dry_run=True,
            required_canary=True,
        )
        assert r.required_human_gate is True
        assert r.required_canary is True

    def test_extra_field_rejected(self, tool_state):
        with pytest.raises(ValidationError):
            ArtPrecheckResult(
                verdict=ArtVerdict.PROCEED,
                tool_state=tool_state,
                required_act_pattern="DEFAULT_DEPLOY",
                not_real="nope",
            )
