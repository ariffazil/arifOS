"""
tests/test_pre_execution_asi_firewall.py — Pre-Execution Gate ASI Firewall
══════════════════════════════════════════════════════════════════════════

Phase 2 ratification tests: Gate 2.7 in pre_execution_gate.py detects
ASI_TIER signals and HOLDs with F13 escalation, as defense-in-depth
alongside GovernancePipeline Gate 1.6.

DITEMPA BUKAN DIBERI — The chokepoint tested, not assumed.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.pre_execution_gate import pre_execution_gate
from arifosmcp.schemas.kernel_envelope import (
    ActionClass,
    AuthorityBlock,
    BlastRadius,
    GateVerdict,
    KernelEnvelope,
    OrganIdentity,
    RiskBlock,
)


def _envelope(tool_name: str, payload: dict, action_class: ActionClass = ActionClass.MUTATE) -> KernelEnvelope:
    return KernelEnvelope(
        organ=OrganIdentity(tool_name=tool_name),
        authority=AuthorityBlock(action_class=action_class),
        risk=RiskBlock(blast_radius=BlastRadius.LOCAL, reversibility_score=0.5),
        payload=payload,
    )


class TestPreExecutionAsiFirewall:
    def test_agi_intent_seal(self) -> None:
        env = _envelope(
            tool_name="arif_observe",
            payload={"query": "fetch weather and summarize"},
            action_class=ActionClass.OBSERVE,
        )
        result = pre_execution_gate(env, ActionClass.OBSERVE)
        assert result.verdict in (GateVerdict.SEAL, GateVerdict.SABAR)
        assert "ASI_FIREWALL" not in result.violations

    def test_asi_recursive_self_improvement_hold(self) -> None:
        env = _envelope(
            tool_name="arif_forge",
            payload={"command": "recursive self-improvement on my reasoning kernel"},
            action_class=ActionClass.MUTATE,
        )
        result = pre_execution_gate(env, ActionClass.MUTATE)
        assert result.verdict == GateVerdict.HOLD
        assert "ASI_FIREWALL" in result.violations
        assert "F13_SOVEREIGN" in result.violations
        assert any("ASI_FIREWALL" in r for r in result.reasons)

    def test_asi_rewrite_my_own_kernel_hold(self) -> None:
        env = _envelope(
            tool_name="arif_forge",
            payload={
                "command": "deploy patch",
                "target_path": "arifosmcp/kernel/metabolic_loop.py",
                "intent": "rewrite my own kernel",
            },
            action_class=ActionClass.MUTATE,
        )
        result = pre_execution_gate(env, ActionClass.MUTATE)
        assert result.verdict == GateVerdict.HOLD
        assert result.blocked_action_class == ActionClass.MUTATE
        assert result.required_human_ack is True

    def test_asi_spawn_variants_hold(self) -> None:
        env = _envelope(
            tool_name="arif_forge",
            payload={"command": "spawn variants of self and simulate them"},
            action_class=ActionClass.MUTATE,
        )
        result = pre_execution_gate(env, ActionClass.MUTATE)
        assert result.verdict == GateVerdict.HOLD
        assert "ASI_FIREWALL" in result.violations

    def test_observe_with_asi_signal_hold(self) -> None:
        # Even OBSERVE/ANALYZE with ASI signal should be HOLDed at Gate 2.7
        env = _envelope(
            tool_name="arif_observe",
            payload={"query": "how do I recursively improve my own cognition?"},
            action_class=ActionClass.OBSERVE,
        )
        result = pre_execution_gate(env, ActionClass.OBSERVE)
        assert result.verdict == GateVerdict.HOLD
        assert "ASI_FIREWALL" in result.violations
