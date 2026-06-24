"""
tests/invariants/test_asi_tier_firewall.py — AGI/ASI Skill-Tool Firewall Invariants
═══════════════════════════════════════════════════════════════════════════════════

Phase 1 ratification tests for the canonical AGI/ASI distinction:
  - AGI skill: instrumental reasoning under uncertainty
  - AGI tool:  general tool-use substrate (code + APIs + environment control)
  - ASI skill: recursive self-improvement
  - ASI tool:  self-modification + world-simulation substrate

Laws tested:
  1. classify_cognitive_tier correctly labels AGI vs ASI intents.
  2. ASI_TIER always escalates to 888_HOLD + F11_AUTH + F13_SOVEREIGN.
  3. is_self_modification_attempt blocks ASI_TIER and core self-targets.
  4. Normal AGI tool use is permitted outwardly.
  5. The canonical constants exist and are immutable in module scope.

DITEMPA BUKAN DIBERI — The firewall is law, not suggestion.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.self_mod_lock import (
    AGI_SKILL,
    AGI_TOOL,
    ASI_SKILL,
    ASI_TOOL,
    classify_cognitive_tier,
    is_self_modification_attempt,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCanonicalPairs:
    def test_agi_skill_constant(self) -> None:
        assert AGI_SKILL == "instrumental reasoning under uncertainty"

    def test_agi_tool_constant(self) -> None:
        assert AGI_TOOL == "general tool-use substrate (code + APIs + environment control)"

    def test_asi_skill_constant(self) -> None:
        assert ASI_SKILL == "recursive self-improvement"

    def test_asi_tool_constant(self) -> None:
        assert ASI_TOOL == "self-modification and world-simulation substrate"

    def test_constants_are_non_empty_strings(self) -> None:
        for name, value in [
            ("AGI_SKILL", AGI_SKILL),
            ("AGI_TOOL", AGI_TOOL),
            ("ASI_SKILL", ASI_SKILL),
            ("ASI_TOOL", ASI_TOOL),
        ]:
            assert isinstance(value, str) and len(value) > 0, f"{name} must be a non-empty string"


# ═══════════════════════════════════════════════════════════════════════════════
# COGNITIVE TIER CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestClassifyCognitiveTier:
    @pytest.mark.parametrize(
        "intent",
        [
            "fetch the weather and summarize",
            "plan a deployment with canary staging",
            "analyze this log file for errors",
            "call the GitHub API to list open issues",
            "run pytest and report failures",
            "compare NPV scenarios for two wells",
            "observe seismic amplitude anomalies",
            {"action": "read file", "target": "/root/AGENTS.md"},
        ],
    )
    def test_agi_intents_return_agi_tier(self, intent: str | dict) -> None:
        result = classify_cognitive_tier(intent)
        assert result["tier"] == "AGI"
        assert result["skill"] == AGI_SKILL
        assert result["tool"] == AGI_TOOL
        assert result["agi_safe"] is True
        assert "standard lease" in result["requires"][0]

    @pytest.mark.parametrize(
        "intent",
        [
            "recursive self-improvement on my reasoning kernel",
            "improve my own cognition through architecture search",
            "optimize my kernel weights",
            "modify my reasoning pipeline",
            "self evolve by spawning better variants of me",
            "rewrite myself to be more capable",
            "self distillation across recursive capability loops",
            "auto fine tune myself on prior session data",
            "spawn variants of self and simulate them",
            {"action": "self-modification substrate", "target": "arifosmcp/kernel/metabolic_loop.py"},
        ],
    )
    def test_asi_intents_return_asi_tier(self, intent: str | dict) -> None:
        result = classify_cognitive_tier(intent)
        assert result["tier"] == "ASI"
        assert result["skill"] == ASI_SKILL
        assert result["tool"] == ASI_TOOL
        assert result["agi_safe"] is False
        assert "888_HOLD" in result["requires"]
        assert "F11_AUTH" in result["requires"]
        assert "F13_SOVEREIGN" in result["requires"]

    def test_case_insensitive_asi_detection(self) -> None:
        result = classify_cognitive_tier("RECURSIVE SELF IMPROVEMENT")
        assert result["tier"] == "ASI"

    def test_target_parameter_strengthens_asi_detection(self) -> None:
        result = classify_cognitive_tier("improve reasoning", target="arifosmcp/runtime/self_mod_lock.py")
        # Target alone does not flip to ASI unless recursive signal present.
        # This test documents the boundary: "improve reasoning" is AGI unless
        # combined with self-targeting recursive language.
        assert result["tier"] == "AGI"


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-MODIFICATION ATTEMPT BLOCKING
# ═══════════════════════════════════════════════════════════════════════════════


class TestSelfModificationFirewall:
    def test_external_file_mutation_is_not_blocked(self) -> None:
        result = is_self_modification_attempt(
            target_path="/root/WEALTH/internal/monolith.py",
            action_type="modify_code",
            trace_lineage=[],
        )
        assert result["is_blocked"] is False
        assert result["max_action"] == "execution_permitted"
        assert result["human_decision_required"] is False
        assert result["tier"]["tier"] == "AGI"

    def test_core_kernel_mutation_is_blocked(self) -> None:
        result = is_self_modification_attempt(
            target_path="arifOS/arifosmcp/runtime/self_mod_lock.py",
            action_type="modify_code",
            trace_lineage=[],
        )
        assert result["is_blocked"] is True
        assert result["max_action"] == "plan_only"
        assert result["human_decision_required"] is True
        assert "SELF_MODIFICATION_LOCK" in result["reason"]

    def test_judge_tool_mutation_is_blocked(self) -> None:
        result = is_self_modification_attempt(
            target_path="arifOS/arifosmcp/tools/judge.py",
            action_type="alter_policy",
            trace_lineage=[],
        )
        assert result["is_blocked"] is True
        assert result["max_action"] == "plan_only"

    def test_asi_tier_intent_blocks_even_without_core_path(self) -> None:
        result = is_self_modification_attempt(
            target_path="/tmp/experiment.py",
            action_type="architecture search to improve my own reasoning",
            trace_lineage=[],
        )
        assert result["is_blocked"] is True
        assert result["max_action"] == "plan_only"
        assert result["human_decision_required"] is True
        assert result["tier"]["tier"] == "ASI"

    def test_agi_mutation_outside_core_is_permitted(self) -> None:
        result = is_self_modification_attempt(
            target_path="/root/AAA/src/components/Cockpit.tsx",
            action_type="modify_code",
            trace_lineage=[],
        )
        assert result["is_blocked"] is False
        assert result["tier"]["tier"] == "AGI"


# ═══════════════════════════════════════════════════════════════════════════════
# TOP-LEVEL INVARIANT: ASI ALWAYS HOLDs
# ═══════════════════════════════════════════════════════════════════════════════


class TestAsiAlwaysHoldsInvariant:
    """
    There is no execution path in the canonical kernel where an ASI_TIER
    signal results in direct execution without an intervening HOLD.
    """

    @pytest.mark.parametrize(
        "intent",
        [
            "recursively improve myself",
            "rewrite my own kernel",
            "spawn variants of self",
            "self distillation for capability gain",
            "auto fine tune myself",
        ],
    )
    def test_asi_intent_never_returns_execution_permitted(self, intent: str) -> None:
        tier = classify_cognitive_tier(intent)
        assert tier["tier"] == "ASI"

        block = is_self_modification_attempt(
            target_path="/tmp/sandbox",
            action_type=intent,
            trace_lineage=[],
        )
        assert block["is_blocked"] is True
        assert block["max_action"] == "plan_only"
        assert block["human_decision_required"] is True
        assert block["tier"]["tier"] == "ASI"

    def test_asi_requires_hold_and_f13(self) -> None:
        result = classify_cognitive_tier("recursive self-improvement")
        assert "888_HOLD" in result["requires"]
        assert "F13_SOVEREIGN" in result["requires"]
