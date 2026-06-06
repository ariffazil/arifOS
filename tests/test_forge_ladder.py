"""
tests/test_forge_ladder.py — v3.1 Forge Classification Ladder Tests
════════════════════════════════════════════════════════════════════

Tests:
  1. forge_query is OBSERVE class — always allowed, no side effects
  2. forge_plan classifies actions correctly (OBSERVE/REASON/MUTATE/ATOMIC)
  3. forge_dry_run produces diff preview and rollback plan
  4. arif_forge_execute rejects non-MUTATE/ATOMIC modes
  5. arif_forge_execute requires judge_state_hash for MUTATE/ATOMIC
  6. arif_forge_execute requires plan_id for engineer/write/generate
  7. Error codes are exact, not vague strings
  8. Tool manifests are inspectable

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.forge import ForgeErrorCode
from arifosmcp.tools.forge import arif_forge_execute
from arifosmcp.tools.forge_ladder import (
    ARIF_FORGE_EXECUTE_MANIFEST,
    FORGE_DRY_RUN_MANIFEST,
    FORGE_PLAN_MANIFEST,
    FORGE_QUERY_MANIFEST,
    forge_dry_run,
    forge_plan,
    forge_query,
)


# ═══════════════════════════════════════════════════════════════════════════════
# forge_query — OBSERVE class
# ═══════════════════════════════════════════════════════════════════════════════


class TestForgeQuery:
    def test_query_always_allowed(self):
        result = forge_query(query="list files", actor_id="test_actor")
        assert result.verdict == "SEAL"
        assert result.error_code is None
        assert len(result.workspace_tree) > 0

    def test_query_no_side_effects(self):
        result = forge_query(query="anything", actor_id="test_actor")
        assert result.result["query_mode"] is True
        assert result.result["manifest_received"] == ""

    def test_query_rejects_workspace_escape(self):
        result = forge_query(query="test", cwd="../../../etc", actor_id="test_actor")
        assert result.verdict == "HOLD"
        assert result.error_code == ForgeErrorCode.E_WORKSPACE_ESCAPE


# ═══════════════════════════════════════════════════════════════════════════════
# forge_plan — REASON class
# ═══════════════════════════════════════════════════════════════════════════════


class TestForgePlan:
    def test_classifies_observe(self):
        result = forge_plan(goal="check git status", actor_id="test_actor")
        assert result.verdict == "SEAL"
        assert result.action_class == "OBSERVE"
        assert result.risk_tier == "low"
        assert result.required_approval is False

    def test_classifies_mutate(self):
        result = forge_plan(goal="write a new file", actor_id="test_actor")
        assert result.verdict == "SEAL"
        assert result.action_class == "MUTATE"
        assert result.risk_tier == "medium"
        assert result.required_approval is True

    def test_classifies_atomic(self):
        result = forge_plan(goal="deploy to production", actor_id="test_actor")
        assert result.verdict == "SEAL"
        assert result.action_class == "ATOMIC"
        assert result.risk_tier == "critical"
        assert result.required_approval is True
        assert "arif_judge_deliberate" in result.required_tools

    def test_generates_plan_id(self):
        result = forge_plan(goal="test goal", actor_id="test_actor")
        assert result.plan_id.startswith("plan_")
        assert len(result.plan_id) == 21  # "plan_" + 16 hex chars

    def test_rejects_empty_goal(self):
        result = forge_plan(goal="", actor_id="test_actor")
        assert result.verdict == "HOLD"
        assert result.error_code == ForgeErrorCode.E_SYNTHESIS_EMPTY


# ═══════════════════════════════════════════════════════════════════════════════
# forge_dry_run — REASON class
# ═══════════════════════════════════════════════════════════════════════════════


class TestForgeDryRun:
    def test_dry_run_always_allowed(self):
        result = forge_dry_run(plan_id="plan_test", manifest="write file", actor_id="test_actor")
        assert result.verdict == "SEAL"
        assert result.dry_run is True
        assert result.error_code is None

    def test_produces_rollback_plan(self):
        result = forge_dry_run(plan_id="plan_test", manifest="write file", actor_id="test_actor")
        assert len(result.rollback_plan) > 0
        assert "git checkout" in result.rollback_plan[1]

    def test_rejects_workspace_escape(self):
        result = forge_dry_run(plan_id="plan_test", manifest="test", cwd="../../../etc")
        assert result.verdict == "HOLD"
        assert result.error_code == ForgeErrorCode.E_WORKSPACE_ESCAPE


# ═══════════════════════════════════════════════════════════════════════════════
# arif_forge_execute v2 — MUTATE/ATOMIC only
# ═══════════════════════════════════════════════════════════════════════════════


class TestArifForgeExecuteV2:
    def test_rejects_query_mode(self):
        result = arif_forge_execute(mode="query", actor_id="test_actor")
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_FORGE_MODE_NOT_ALLOWED

    def test_rejects_recall_mode(self):
        result = arif_forge_execute(mode="recall", actor_id="test_actor")
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_FORGE_MODE_NOT_ALLOWED

    def test_rejects_dry_run_mode(self):
        result = arif_forge_execute(mode="dry_run", actor_id="test_actor")
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_FORGE_MODE_NOT_ALLOWED

    def test_allows_engineer_mode(self):
        # engineer requires plan_id, so this should fail for that reason
        result = arif_forge_execute(
            mode="engineer", manifest="test", actor_id="test_actor", judge_state_hash="abc123"
        )
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_SYNTHESIS_EMPTY

    def test_requires_judge_state_hash_for_write(self):
        result = arif_forge_execute(mode="write", manifest="test", actor_id="test_actor")
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED

    def test_requires_plan_id_for_engineer(self):
        result = arif_forge_execute(
            mode="engineer", manifest="test", actor_id="test_actor", judge_state_hash="abc123"
        )
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_SYNTHESIS_EMPTY

    def test_requires_plan_id_for_write(self):
        result = arif_forge_execute(
            mode="write", manifest="test", actor_id="test_actor", judge_state_hash="abc123"
        )
        assert result.status == "HOLD"
        assert result.meta["error_code"] == ForgeErrorCode.E_SYNTHESIS_EMPTY

    def test_exact_error_codes_not_vague_strings(self):
        result = arif_forge_execute(mode="query", actor_id="test_actor")
        assert "error_code" in result.meta
        assert result.meta["error_code"].startswith("E_")
        assert result.meta["error_code"] != "HOLD"  # not a vague string


# ═══════════════════════════════════════════════════════════════════════════════
# Tool Manifests
# ═══════════════════════════════════════════════════════════════════════════════


class TestToolManifests:
    def test_query_manifest_is_safe(self):
        assert FORGE_QUERY_MANIFEST.name == "forge_query"
        assert FORGE_QUERY_MANIFEST.dangerous_modes == []
        assert FORGE_QUERY_MANIFEST.max_blast_radius == "none"

    def test_execute_manifest_has_dangerous_modes(self):
        assert ARIF_FORGE_EXECUTE_MANIFEST.name == "arif_forge_execute"
        assert "write" in ARIF_FORGE_EXECUTE_MANIFEST.dangerous_modes
        assert "commit" in ARIF_FORGE_EXECUTE_MANIFEST.dangerous_modes
        assert ARIF_FORGE_EXECUTE_MANIFEST.requires_identity is True
        assert ARIF_FORGE_EXECUTE_MANIFEST.requires_state_hash is True

    def test_all_manifests_are_dumpable(self):
        for manifest in [
            FORGE_QUERY_MANIFEST,
            FORGE_PLAN_MANIFEST,
            FORGE_DRY_RUN_MANIFEST,
            ARIF_FORGE_EXECUTE_MANIFEST,
        ]:
            dumped = manifest.model_dump()
            assert "name" in dumped
            assert "stage" in dumped
            assert "safe_modes" in dumped
            assert "dangerous_modes" in dumped
