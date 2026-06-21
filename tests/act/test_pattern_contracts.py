"""
Schema contract tests for arifosmcp.schemas.act

Validates:
  - ActPatternName enum integrity
  - ActStage strict-mode enforcement
  - ActPattern construction (min stages, allowed_action_classes)
  - ActReceipt namespaced seal type
  - Pattern-specific invariants (dangerous migration has human gate, etc.)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arifosmcp.schemas.act import (
    ActPattern,
    ActPatternName,
    ActReceipt,
    ActStage,
)
from arifosmcp.schemas.art import (
    ArtPrecheckResult,
    ArtToolState,
    ArtVerdict,
    ToolLifecycle,
    TrustBand,
)
from arifosmcp.schemas.kernel_envelope import ActionClass


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════


def _make_tool_state(**kwargs):
    return ArtToolState(
        tool_name="test",
        lifecycle=ToolLifecycle.TRUSTED,
        trust_score=0.9,
        trust_band=TrustBand.TRUST_HIGH,
        action_class=ActionClass.MUTATE,
        **kwargs,
    )


def _make_precheck(**kwargs):
    return ArtPrecheckResult(
        verdict=ArtVerdict.PROCEED,
        tool_state=_make_tool_state(),
        required_act_pattern="DEFAULT_DEPLOY",
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════
# ENUM INTEGRITY
# ═══════════════════════════════════════════════════════════════════════


class TestActPatternName:
    def test_three_patterns(self):
        values = {e.value for e in ActPatternName}
        assert values == {
            "DEFAULT_DEPLOY",
            "DANGEROUS_MIGRATION",
            "HUMAN_IN_LOOP_CHANGE",
        }


# ═══════════════════════════════════════════════════════════════════════
# ActStage — single stage contract
# ═══════════════════════════════════════════════════════════════════════


class TestActStage:
    def test_valid_minimal_stage(self):
        s = ActStage(name="dry_run", mode="dry_run")
        assert s.name == "dry_run"
        assert s.mode == "dry_run"
        assert s.required is True
        assert s.requires_human is False

    def test_human_gate_stage(self):
        s = ActStage(
            name="approval",
            mode="human_gate",
            requires_human=True,
            failure_policy="hold",
        )
        assert s.requires_human is True
        assert s.failure_policy == "hold"

    def test_timeout_must_be_positive(self):
        with pytest.raises(ValidationError):
            ActStage(name="t", mode="canary", timeout_seconds=0)

    def test_timeout_negative_rejected(self):
        with pytest.raises(ValidationError):
            ActStage(name="t", mode="canary", timeout_seconds=-1)

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            ActStage(name="t", mode="canary", not_a_field="nope")

    def test_invalid_failure_policy_rejected(self):
        with pytest.raises(ValidationError):
            ActStage(name="t", mode="canary", failure_policy="explode")  # type: ignore[arg-type]


# ═══════════════════════════════════════════════════════════════════════
# ActPattern — full execution ritual
# ═══════════════════════════════════════════════════════════════════════


class TestActPattern:
    def test_valid_pattern(self):
        p = ActPattern(
            name=ActPatternName.DEFAULT_DEPLOY,
            description="Routine deploy",
            allowed_action_classes=[ActionClass.MUTATE, ActionClass.DRAFT],
            stages=[
                ActStage(name="precheck", mode="precheck"),
                ActStage(name="dry_run", mode="dry_run"),
                ActStage(name="deploy", mode="rollout"),
            ],
        )
        assert len(p.stages) == 3
        assert ActionClass.MUTATE in p.allowed_action_classes

    def test_empty_stages_rejected(self):
        with pytest.raises(ValidationError):
            ActPattern(
                name=ActPatternName.DEFAULT_DEPLOY,
                description="bad",
                allowed_action_classes=[ActionClass.MUTATE],
                stages=[],
            )

    def test_allowed_action_classes_uses_action_class_not_blast_radius(self):
        """allowed_action_classes uses canonical ActionClass, not BlastRadius."""
        p = ActPattern(
            name=ActPatternName.DEFAULT_DEPLOY,
            description="test",
            allowed_action_classes=[ActionClass.OBSERVE, ActionClass.MUTATE],
            stages=[ActStage(name="s", mode="precheck")],
        )
        assert ActionClass.OBSERVE in p.allowed_action_classes

    def test_dangerous_migration_has_human_gate(self):
        """DANGEROUS_MIGRATION must include at least one human_gate stage."""
        p = ActPattern(
            name=ActPatternName.DANGEROUS_MIGRATION,
            description="Irreversible migration",
            allowed_action_classes=[ActionClass.IRREVERSIBLE],
            stages=[
                ActStage(name="precheck", mode="precheck"),
                ActStage(name="snapshot", mode="snapshot"),
                ActStage(name="shadow_dry_run", mode="dry_run"),
                ActStage(
                    name="888_HOLD",
                    mode="human_gate",
                    requires_human=True,
                    failure_policy="hold",
                ),
                ActStage(name="canary", mode="canary", failure_policy="rollback"),
                ActStage(name="live", mode="rollout", failure_policy="hold"),
                ActStage(name="verify", mode="verify"),
                ActStage(name="compensate", mode="compensate"),
                ActStage(name="seal", mode="seal"),
            ],
        )
        human_gates = [s for s in p.stages if s.mode == "human_gate"]
        assert len(human_gates) >= 1, "DANGEROUS_MIGRATION requires at least one human_gate"

    def test_human_in_loop_has_human_gate(self):
        """HUMAN_IN_LOOP_CHANGE must center on human gate stages."""
        p = ActPattern(
            name=ActPatternName.HUMAN_IN_LOOP_CHANGE,
            description="Human review ritual",
            allowed_action_classes=[
                ActionClass.EXTERNAL_SIDE_EFFECT,
                ActionClass.IRREVERSIBLE,
            ],
            stages=[
                ActStage(name="capture_hold", mode="human_gate", requires_human=True),
                ActStage(name="create_ticket", mode="human_gate", requires_human=True),
                ActStage(name="human_decision", mode="human_gate", requires_human=True),
                ActStage(name="resolve", mode="verify"),
                ActStage(name="seal", mode="seal"),
            ],
        )
        human_gates = [s for s in p.stages if s.mode == "human_gate"]
        assert len(human_gates) >= 1, "HUMAN_IN_LOOP_CHANGE requires at least one human_gate"


# ═══════════════════════════════════════════════════════════════════════
# ActReceipt — VAULT999 receipt contract
# ═══════════════════════════════════════════════════════════════════════


class TestActReceipt:
    def test_namespaced_seal_type(self):
        r = ActReceipt(
            plan_id="plan_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DEFAULT_DEPLOY,
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert r.seal_type == "ART_ACT_EXECUTION_RECEIPT", (
            "ActReceipt must use namespaced seal type — no bare SEAL"
        )

    def test_vault_receipt_required_by_default(self):
        r = ActReceipt(
            plan_id="plan_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DEFAULT_DEPLOY,
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert r.vault_receipt_required is True

    def test_stages_completed_tracked(self):
        r = ActReceipt(
            plan_id="plan_001",
            task_id="task_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DANGEROUS_MIGRATION,
            stages_completed=["precheck", "snapshot", "shadow_dry_run", "human_gate"],
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert len(r.stages_completed) == 4
        assert "human_gate" in r.stages_completed

    def test_extra_field_rejected(self):
        with pytest.raises(ValidationError):
            ActReceipt(
                plan_id="plan_001",
                actor_id="arif",
                art_precheck=_make_precheck(),
                act_pattern=ActPatternName.DEFAULT_DEPLOY,
                judge_verdict="JUDGE_SEAL_AUTHORIZATION",
                not_a_field=123,
            )
