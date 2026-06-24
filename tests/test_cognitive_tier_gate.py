"""
tests/test_cognitive_tier_gate.py — Governance Pipeline ASI Firewall Gate
══════════════════════════════════════════════════════════════════════════

Phase 2 ratification tests: Gate 1.6 COGNITIVE_TIER is wired into the
single governance pipeline. Any tool call carrying an ASI_TIER signal
must be HOLDed at Gate 1.6 with F13 escalation, before budget/risk gates.

DITEMPA BUKAN DIBERI — The pipe tested, not assumed.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.governance_pipeline import (
    Gate,
    GovernancePipeline,
    PipelineVerdict,
    ToolCallContext,
)


@pytest.fixture
def pipeline() -> GovernancePipeline:
    """Pipeline with optional gates disabled to isolate Gate 1.6."""
    return GovernancePipeline(
        f0_rootkey_enabled=False,
        kaparinyo_enabled=False,
        f13_gate_enabled=False,
        principal_paradox_enabled=False,
        budget_enabled=False,
        vault_liveness_enabled=False,
        drift_enabled=False,
        floor_enabled=False,
        envelope_enabled=False,
    )


class TestCognitiveTierGate:
    def test_agi_intent_passes_gate_1_6(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_sense_observe",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={"query": "fetch weather and summarize"},
            action_class="OBSERVE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is True
        cognitive_gate = next(r for r in result.gate_results if r.gate == Gate.COGNITIVE_TIER)
        assert cognitive_gate.passed is True
        assert cognitive_gate.metadata.get("tier") == "AGI"

    def test_asi_intent_blocked_at_gate_1_6(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_forge_execute",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={"command": "recursive self-improvement on my reasoning kernel"},
            action_class="MUTATE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is False
        assert result.verdict == PipelineVerdict.HOLD
        assert result.blocked_at == Gate.COGNITIVE_TIER
        cognitive_gate = next(r for r in result.gate_results if r.gate == Gate.COGNITIVE_TIER)
        assert cognitive_gate.passed is False
        assert cognitive_gate.metadata.get("tier") == "ASI"
        assert "888_HOLD" in str(cognitive_gate.metadata.get("requires", []))

    def test_asi_rewrite_my_own_kernel_blocked(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_forge_execute",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={
                "command": "deploy patched weights",
                "target_path": "arifosmcp/kernel/metabolic_loop.py",
                "intent": "rewrite my own kernel",
            },
            action_class="MUTATE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is False
        assert result.blocked_at == Gate.COGNITIVE_TIER
        assert "ASI_FIREWALL" in result.violated_laws

    def test_asi_spawn_variants_blocked(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_forge_execute",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={"command": "spawn variants of self and evaluate in simulation"},
            action_class="MUTATE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is False
        assert result.blocked_at == Gate.COGNITIVE_TIER

    def test_external_mutation_remains_agi(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_forge_execute",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={
                "command": "modify code",
                "target_path": "/root/AAA/src/components/Cockpit.tsx",
            },
            action_class="MUTATE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is True
        cognitive_gate = next(r for r in result.gate_results if r.gate == Gate.COGNITIVE_TIER)
        assert cognitive_gate.passed is True
        assert cognitive_gate.metadata.get("tier") == "AGI"

    def test_asi_firewall_can_be_disabled(self, pipeline: GovernancePipeline) -> None:
        pipeline.asi_firewall_enabled = False
        ctx = ToolCallContext(
            tool_name="arif_forge_execute",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={"command": "recursive self-improvement"},
            action_class="MUTATE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is True
        # Gate should not appear in results when disabled
        assert not any(r.gate == Gate.COGNITIVE_TIER for r in result.gate_results)

    def test_hold_includes_f13_next_action(self, pipeline: GovernancePipeline) -> None:
        ctx = ToolCallContext(
            tool_name="arif_mind_reason",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={"query": "how can I recursively improve my own cognition?"},
            action_class="ANALYZE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is False
        assert result.blocked_at == Gate.COGNITIVE_TIER
        assert "F13 SOVEREIGN" in result.next_safe_action
        assert "BRAIN" in result.next_safe_action

    def test_asi_signal_in_tool_name_blocked(self, pipeline: GovernancePipeline) -> None:
        # Even an unknown tool with ASI signal in its name should be caught.
        ctx = ToolCallContext(
            tool_name="self_rewrite_agent",
            session_id="test-session",
            actor_id="test-agent",
            actor_verification="verified",
            params={},
            action_class="OBSERVE",
        )
        result = pipeline.run(ctx)
        assert result.all_clear is False
        assert result.blocked_at == Gate.COGNITIVE_TIER
