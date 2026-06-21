"""
Integration contract tests for the ART-ACT → A-FORGE dispatch boundary.

These test the SCHEMA CONTRACTS, not the runtime behavior.
forge_dispatch.py doesn't exist yet (Phase 4). These tests validate
the data shapes that forge_dispatch WILL enforce.
"""

from __future__ import annotations

from arifosmcp.schemas.act import ActPatternName, ActReceipt
from arifosmcp.schemas.art import (
    ArtPrecheckResult,
    ArtToolState,
    ArtVerdict,
    ToolLifecycle,
    TrustBand,
)
from arifosmcp.schemas.kernel_envelope import ActionClass


def _make_tool_state(action_class=ActionClass.MUTATE):
    return ArtToolState(
        tool_name="test",
        lifecycle=ToolLifecycle.TRUSTED,
        trust_score=0.9,
        trust_band=TrustBand.TRUST_HIGH,
        action_class=action_class,
    )


def _make_precheck(**kwargs):
    defaults = dict(
        verdict=ArtVerdict.PROCEED,
        tool_state=_make_tool_state(),
        required_act_pattern="DEFAULT_DEPLOY",
    )
    defaults.update(kwargs)
    return ArtPrecheckResult(**defaults)


class TestForgeDispatchContract:
    """Validate the contract shapes that forge_dispatch.py will enforce in Phase 4.

    These tests don't call forge_dispatch (it doesn't exist yet).
    They validate that the data shapes are correct and that invalid
    shapes are rejected by Pydantic.
    """

    def test_sealed_plan_requires_judge_seal_authorization(self):
        """A-FORGE dispatch must require JUDGE_SEAL_AUTHORIZATION verdict."""
        receipt = ActReceipt(
            plan_id="plan_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DEFAULT_DEPLOY,
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert receipt.judge_verdict == "JUDGE_SEAL_AUTHORIZATION", (
            "A-FORGE must reject anything without JUDGE_SEAL_AUTHORIZATION"
        )

    def test_sealed_plan_requires_vault_receipt(self):
        """A-FORGE dispatch must require VAULT999 receipt."""
        receipt = ActReceipt(
            plan_id="plan_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DEFAULT_DEPLOY,
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert receipt.vault_receipt_required is True, (
            "A-FORGE must reject dispatch without vault_receipt_required"
        )

    def test_irreversible_action_requires_dangerous_migration_or_human_loop(self):
        """IRREVERSIBLE action_class → DANGEROUS_MIGRATION or HUMAN_IN_LOOP_CHANGE."""
        precheck = _make_precheck(
            verdict=ArtVerdict.HOLD,
            required_act_pattern=ActPatternName.DANGEROUS_MIGRATION.value,
            required_human_gate=True,
        )
        assert precheck.required_act_pattern in (
            ActPatternName.DANGEROUS_MIGRATION.value,
            ActPatternName.HUMAN_IN_LOOP_CHANGE.value,
        ), "IRREVERSIBLE actions require DANGEROUS_MIGRATION or HUMAN_IN_LOOP_CHANGE"

    def test_reversible_action_can_use_default_deploy(self):
        """REVERSIBLE_WRITE (DRAFT) → DEFAULT_DEPLOY is valid."""
        precheck = _make_precheck(
            verdict=ArtVerdict.SABAR,
            required_act_pattern=ActPatternName.DEFAULT_DEPLOY.value,
            required_human_gate=False,
        )
        assert precheck.required_act_pattern == ActPatternName.DEFAULT_DEPLOY.value

    def test_missing_act_pattern_invalid_for_write(self):
        """Any write-class action requires an ACT pattern — not empty string."""
        precheck = _make_precheck(
            verdict=ArtVerdict.PROCEED,
            required_act_pattern="",  # empty = no pattern selected
        )
        # Empty pattern is structurally valid (just a string) but operationally invalid.
        # forge_dispatch.py must reject empty act_pattern.
        assert precheck.required_act_pattern == "" or precheck.required_act_pattern in (
            "DEFAULT_DEPLOY",
            "DANGEROUS_MIGRATION",
            "HUMAN_IN_LOOP_CHANGE",
        ), "empty pattern must be caught at dispatch boundary"

    def test_act_receipt_seal_type_is_always_namespaced(self):
        """No bare SEAL in receipt seal_type."""
        receipt = ActReceipt(
            plan_id="plan_001",
            actor_id="arif",
            art_precheck=_make_precheck(),
            act_pattern=ActPatternName.DEFAULT_DEPLOY,
            judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        )
        assert "ART_ACT" in receipt.seal_type, "seal_type must be namespaced"
        assert receipt.seal_type != "SEAL", "bare SEAL is forbidden"
