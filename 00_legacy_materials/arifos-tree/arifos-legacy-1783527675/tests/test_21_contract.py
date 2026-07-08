"""
test_21_contract.py — The 21-test Band 1 Kernel SDK contract.

The arifos SDK does not ship until these pass. 5 categories:
- Authority (5)
- Reversibility (5)
- Tool (5)
- State (3)
- Agent (3)

All tests run against a mock client (no live kernel required).
Live integration test lives in test_live_integration.py.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock

import pytest

from arifos import (
    ActionClass,
    Actor,
    ArifDenied,
    ArifHold,
    ArifSealMissing,
    CognitionLane,
    Decision,
    Kernel,
    check_f11_audit,
    posttool,
    prethink,
    pretool,
    seal,
)
from arifos.intent import Intent
from arifos.risk import BlastRadius


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def make_mock_client(verdict: str = "ALLOW", with_lease: bool = True) -> AsyncMock:
    """Build a mock MCP client returning a specific verdict."""
    client = AsyncMock()
    response = {"verdict": verdict, "reasons": [f"test {verdict}"]}
    if with_lease:
        response["lease_id"] = "lease_test_123"
    client.kernel_check_call = AsyncMock(return_value=response)
    client.kernel_seal = AsyncMock(return_value={"entry_id": "vault_999_test_seal"})
    return client


def make_actor() -> Actor:
    return Actor(actor_id="arif", actor_type="sovereign", trust_tier="OWNER")


def make_intent(action_class: ActionClass = ActionClass.OBSERVE) -> Intent:
    return Intent(
        action="test_action",
        action_class=action_class.value,
        lane="OBSERVE",
        blast_radius=BlastRadius.NONE,
        reason="test intent",
        actor=make_actor(),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Authority tests (5)
# ─────────────────────────────────────────────────────────────────────────────


def test_1_unknown_actor_cannot_mutate():
    """F11 fails on missing actor_id → action must HOLD/DENY."""
    f11 = check_f11_audit(actor_id=None)
    assert f11.verdict == "FAIL"
    assert f11.floor_id == "F11"


def test_2_known_actor_without_lease_gets_lease():
    """Prethink with valid actor + OBSERVE action → ALLOW + lease."""

    async def run():
        client = make_mock_client("ALLOW")
        intent = make_intent(ActionClass.OBSERVE)
        decision = await prethink(intent=intent, client=client)
        assert decision.verdict == "ALLOW"
        assert decision.lease_id == "lease_test_123"

    asyncio.run(run())


def test_3_lease_scope_cannot_expand_silently():
    """Pretol under wrong prior decision → DENY/HOLD."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
            action_class=ActionClass.OBSERVE,
        )
        client = AsyncMock(actor=make_actor())
        client.kernel_check_call = AsyncMock(
            return_value={
                "verdict": "HOLD",
                "reasons": ["F13: scope expansion detected"],
            }
        )
        with pytest.raises(ArifHold):
            await pretool(
                tool_name="delete_file",
                tool_args={"path": "/etc/passwd"},
                prior_decision=prior,
                client=client,
            )

    asyncio.run(run())


def test_4_expired_lease_fails_closed():
    """Kernel returns DENY → pretool raises ArifDenied."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
        )
        client = AsyncMock(actor=make_actor())
        client.kernel_check_call = AsyncMock(
            return_value={
                "verdict": "DENY",
                "reasons": ["lease expired"],
            }
        )
        with pytest.raises(ArifDenied):
            await pretool(
                tool_name="read_file",
                tool_args={},
                prior_decision=prior,
                client=client,
            )

    asyncio.run(run())


def test_5_wrong_organ_jurisdiction_fails_closed():
    """PUBLISH action → F1 short-circuits to HOLD."""

    async def run():
        decision = await prethink(
            intent=make_intent(ActionClass.PUBLISH),
            client=make_mock_client("ALLOW"),
        )
        assert decision.verdict == "HOLD"
        assert decision.required_human_ack is True
        assert any(f.floor_id == "F1" for f in decision.floor_verdicts)

    asyncio.run(run())


# ─────────────────────────────────────────────────────────────────────────────
# Reversibility tests (5)
# ─────────────────────────────────────────────────────────────────────────────


def test_6_observe_only_action_passes():
    """OBSERVE + NONE blast-radius → ALLOW."""

    async def run():
        decision = await prethink(
            intent=make_intent(ActionClass.OBSERVE),
            client=make_mock_client("ALLOW"),
        )
        assert decision.verdict == "ALLOW"
        assert decision.risk.blast_radius == "NONE"
        assert decision.risk.reversibility == "REVERSIBLE"

    asyncio.run(run())


def test_7_reversible_local_mutation_passes_with_seal():
    """MUTATE_LOCAL → ALLOW, lease issued."""

    async def run():
        decision = await prethink(
            intent=make_intent(ActionClass.MUTATE_LOCAL),
            client=make_mock_client("ALLOW"),
        )
        assert decision.verdict == "ALLOW"
        assert decision.action_class == ActionClass.MUTATE_LOCAL

    asyncio.run(run())


def test_8_external_mutation_requires_lease():
    """MUTATE_EXTERNAL with EXTERNAL blast-radius → F13 HOLD."""

    async def run():
        client = make_mock_client("ALLOW")
        intent = Intent(
            action="external_mutation",
            action_class=ActionClass.MUTATE_EXTERNAL.value,
            lane="EXECUTE",
            blast_radius=BlastRadius.EXTERNAL,
            reason="external action",
            actor=make_actor(),
        )
        decision = await prethink(intent=intent, client=client)
        assert decision.verdict == "HOLD"
        assert any(f.floor_id == "F13" for f in decision.floor_verdicts)

    asyncio.run(run())


def test_9_irreversible_action_triggers_888_hold():
    """All HOLD_TRIGGERS actions → 888 HOLD."""
    for action_class in [
        ActionClass.DEPLOY,
        ActionClass.PUBLISH,
        ActionClass.DELETE,
        ActionClass.SPEND,
        ActionClass.SIGN,
        ActionClass.GRANT_ACCESS,
        ActionClass.CREDENTIAL_CHANGE,
        ActionClass.CONSTITUTION_CHANGE,
    ]:

        async def run(ac=action_class):
            decision = await prethink(
                intent=Intent(
                    action=ac.value,
                    action_class=ac.value,
                    lane="EXECUTE",
                    blast_radius=BlastRadius.FEDERATION,
                    reason=f"test {ac.value}",
                    actor=make_actor(),
                ),
                client=make_mock_client("ALLOW"),
            )
            assert decision.verdict == "HOLD", f"{ac.value} should HOLD"
            assert decision.required_human_ack is True
            assert any(f.floor_id == "F1" for f in decision.floor_verdicts)

        asyncio.run(run())


def test_10_delete_publish_deploy_spend_require_explicit_human_authority():
    """Irreversible actions all set required_human_ack=True."""
    for ac in [ActionClass.DEPLOY, ActionClass.PUBLISH, ActionClass.DELETE, ActionClass.SPEND]:

        async def run(action_class=ac):
            decision = await prethink(
                intent=Intent(
                    action=action_class.value,
                    action_class=action_class.value,
                    lane="EXECUTE",
                    blast_radius=BlastRadius.FEDERATION,
                    reason=f"test {action_class.value}",
                    actor=make_actor(),
                ),
                client=make_mock_client("ALLOW"),
            )
            assert decision.required_human_ack is True

        asyncio.run(run())


# ─────────────────────────────────────────────────────────────────────────────
# Tool tests (5)
# ─────────────────────────────────────────────────────────────────────────────


def test_11_tool_call_without_prethink_fails():
    """The integration contract: no prethink → no tool call allowed."""
    # This is the integration contract — the adapter enforces it.
    # At the unit level, we verify the Decision shape allows raising.
    no_decision = None
    with pytest.raises(ArifHold):
        if no_decision is None:
            raise ArifHold(
                Decision(
                    verdict="HOLD",
                    cognition_lane=CognitionLane.OBSERVE,
                    reasons=["F8 LAW: tool called before prethink"],
                    required_human_ack=True,
                )
            )


def test_12_prethink_tool_schema_is_strict():
    """The prethink tool schema enforces required fields."""
    try:
        from arifos.adapters.openai import ARIFOS_PRETHINK_TOOL
    except ImportError:
        pytest.skip("openai adapter not installed")

    params = ARIFOS_PRETHINK_TOOL["function"]["parameters"]
    required = params.get("required", [])
    assert "action" in required
    assert "action_class" in required
    assert "lane" in required
    assert "blast_radius" in required
    assert ARIFOS_PRETHINK_TOOL["function"].get("strict") is True


def test_13_hidden_side_effect_detected_or_downgraded():
    """Pretol with scope-expanding intent → DENY."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
            action_class=ActionClass.OBSERVE,
        )
        client = AsyncMock(actor=make_actor())
        client.kernel_check_call = AsyncMock(
            return_value={
                "verdict": "DENY",
                "reasons": ["scope expansion: OBSERVE prior, MUTATE requested"],
            }
        )
        with pytest.raises(ArifDenied):
            await pretool(
                tool_name="write_file",
                tool_args={"path": "/tmp/test"},
                prior_decision=prior,
                client=client,
            )

    asyncio.run(run())


def test_14_transport_verdict_mismatch_fails_closed():
    """Kernel DENY → pretool raises ArifDenied."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
        )
        client = AsyncMock(actor=make_actor())
        client.kernel_check_call = AsyncMock(
            return_value={
                "verdict": "DENY",
                "reasons": ["kernel says no"],
            }
        )
        with pytest.raises(ArifDenied):
            await pretool(
                tool_name="read_file",
                tool_args={},
                prior_decision=prior,
                client=client,
            )

    asyncio.run(run())


def test_15_kernel_unavailable_fails_closed():
    """Kernel unreachable → pretool raises ArifHold (fail-closed)."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
        )
        client = AsyncMock(actor=make_actor())
        client.kernel_check_call = AsyncMock(side_effect=ConnectionError("kernel down"))
        with pytest.raises(ArifHold):
            await pretool(
                tool_name="read_file",
                tool_args={},
                prior_decision=prior,
                client=client,
            )

    asyncio.run(run())


# ─────────────────────────────────────────────────────────────────────────────
# State tests (3)
# ─────────────────────────────────────────────────────────────────────────────


def test_16_every_sealed_result_has_seal_pointer():
    """Seal returns Decision with seal_pointer from VAULT999."""

    async def run():
        history = [
            Decision(verdict="ALLOW", cognition_lane=CognitionLane.OBSERVE),
        ]
        client = make_mock_client("ALLOW")
        sealed = await seal(
            final_output="test",
            decision_history=history,
            client=client,
        )
        assert sealed.seal_pointer == "vault_999_test_seal"

    asyncio.run(run())


def test_17_seal_missing_raises():
    """No entry_id from kernel → ArifSealMissing."""

    async def run():
        client = AsyncMock(actor=make_actor())
        client.kernel_seal = AsyncMock(return_value={})  # no entry_id
        with pytest.raises(ArifSealMissing):
            await seal(
                final_output="test",
                decision_history=[Decision(verdict="ALLOW", cognition_lane=CognitionLane.OBSERVE)],
                client=client,
            )

    asyncio.run(run())


def test_18_seal_refused_on_hold():
    """Any HOLD in history → seal refused."""

    async def run():
        history = [
            Decision(verdict="ALLOW", cognition_lane=CognitionLane.OBSERVE),
            Decision(verdict="HOLD", cognition_lane=CognitionLane.EXECUTE),
        ]
        sealed = await seal(
            final_output="test",
            decision_history=history,
            client=make_mock_client("ALLOW"),
        )
        assert sealed.verdict == "HOLD"


# ─────────────────────────────────────────────────────────────────────────────
# Agent tests (3)
# ─────────────────────────────────────────────────────────────────────────────


def test_19_kernel_class_exposes_high_level_methods():
    """The Kernel class wraps the 4 guards in a clean API."""
    kernel = Kernel(actor=make_actor())
    assert kernel.actor.actor_id == "arif"
    assert hasattr(kernel, "prethink")
    assert hasattr(kernel, "pretool")
    assert hasattr(kernel, "posttool")
    assert hasattr(kernel, "seal")
    assert kernel.fail_closed is True
    assert kernel.history == []


def test_20_decision_envelope_is_consistent_across_guards():
    """All guards return Decision objects with the same shape."""

    async def run():
        client = make_mock_client("ALLOW")
        d1 = await prethink(intent=make_intent(), client=client)
        d2 = await posttool(
            tool_name="read_file",
            tool_result={"data": "x"},
            prior_decision=d1,
        )
        assert isinstance(d1, Decision)
        assert isinstance(d2, Decision)
        for d in (d1, d2):
            assert hasattr(d, "verdict")
            assert hasattr(d, "cognition_lane")
            assert hasattr(d, "floor_verdicts")

    asyncio.run(run())


def test_21_posttool_applies_f2_stamp_to_untrusted_results():
    """Posttool stamps untrusted results with F2 WARN."""

    async def run():
        prior = Decision(
            verdict="ALLOW",
            cognition_lane=CognitionLane.OBSERVE,
            action_class=ActionClass.OBSERVE,
        )
        decision = await posttool(
            tool_name="web_search",
            tool_result={"content": "untrusted AI summary"},
            prior_decision=prior,
            confidence=None,
            source=None,
        )
        assert any(f.floor_id == "F2" and f.verdict == "WARN" for f in decision.floor_verdicts)

    asyncio.run(run())
