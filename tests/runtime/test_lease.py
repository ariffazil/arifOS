"""
tests/runtime/test_lease.py — Unit tests for the canonical lease registry.

ADR-001 (2026-06-16): runtime/lease.py is deprecated. This file now tests
arifosmcp.runtime.lease_registry, the single source of lease truth.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time

import pytest

from arifosmcp.runtime.lease_registry import (
    _reset_registry,
    arif_lease_inspect,
    arif_lease_issue,
    arif_lease_revoke,
    issue_lease,
    present_lease,
    validate_lease_for_tool,
)


@pytest.fixture(autouse=True)
def _clear_registry():
    _reset_registry()
    yield
    _reset_registry()


# ──────────────────────────────────────────────────────────────────────
# Issue and basic lease state
# ──────────────────────────────────────────────────────────────────────


class TestIssue:
    def test_issue_returns_lease(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="did:web:arif-fazil.com:000",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            ttl_seconds=60,
        )
        assert rec.lease_id.startswith("LEASE-")
        assert rec.organ_id == "A-FORGE"
        assert rec.actor_id == "did:web:arif-fazil.com:000"
        assert rec.scope == ["arif_forge_execute"]
        assert rec.uses_consumed == 0
        assert rec.revoked is False
        assert rec.is_expired() is False

    def test_issue_rejects_unknown_action_class(self) -> None:
        with pytest.raises(ValueError):
            issue_lease(
                organ_id="A-FORGE",
                actor_id="x",
                scope=["x"],
                max_action_class="INVALID",
            )

    def test_issue_rejects_irreversible(self) -> None:
        result = arif_lease_issue(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["x"],
            max_action_class="IRREVERSIBLE",
        )
        assert result["verdict"] == "HOLD"
        assert "F13" in result["reason"]

    def test_issue_rejects_disallowed_organ(self) -> None:
        with pytest.raises(ValueError):
            issue_lease(
                organ_id="unknown-organ",
                actor_id="x",
                scope=["x"],
            )

    def test_issue_rejects_non_positive_max_uses(self) -> None:
        with pytest.raises(ValueError):
            issue_lease(
                organ_id="A-FORGE",
                actor_id="x",
                scope=["x"],
                max_uses=0,
            )


# ──────────────────────────────────────────────────────────────────────
# Validation (does not consume)
# ──────────────────────────────────────────────────────────────────────


class TestValidate:
    def test_unknown_lease_rejected(self) -> None:
        r = validate_lease_for_tool("LEASE-DEADBEEF", "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "HOLD"

    def test_valid_lease_accepted(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert r["valid"]
        assert r["verdict"] == "SEAL"

    def test_tool_outside_scope_rejected(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_sense_observe"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "DENY"

    def test_action_class_exceeds_lease_max(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="OBSERVE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "HOLD"

    def test_revoked_lease_rejected(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        arif_lease_revoke(rec.lease_id, "test", actor_id="x")
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "HOLD"

    def test_expired_lease_rejected(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            ttl_seconds=1,
        )
        time.sleep(1.1)
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "HOLD"

    def test_forbidden_tool_rejected(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["*"],
            forbidden=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "DENY"


# ──────────────────────────────────────────────────────────────────────
# Presentation (validates + consumes atomically)
# ──────────────────────────────────────────────────────────────────────


class TestPresent:
    def test_present_consumes_use(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            max_uses=2,
        )
        r = present_lease(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert r["valid"]
        assert r["uses_consumed"] == 1
        refreshed = arif_lease_inspect(rec.lease_id)["result"]["lease"]
        assert refreshed["uses_consumed"] == 1

    def test_present_exhausts_lease(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            max_uses=1,
        )
        r1 = present_lease(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert r1["valid"]
        r2 = present_lease(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r2["valid"]
        assert "exhausted" in r2["reason"].lower()

    def test_present_rejects_scope_mismatch(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_sense_observe"],
            max_action_class="MUTATE",
        )
        r = present_lease(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "DENY"

    def test_present_rejects_class_exceeded(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="OBSERVE",
        )
        r = present_lease(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert not r["valid"]
        assert r["verdict"] == "HOLD"


# ──────────────────────────────────────────────────────────────────────
# MCP tool handlers
# ──────────────────────────────────────────────────────────────────────


class TestMcpHandlers:
    def test_arif_lease_issue_roundtrip(self) -> None:
        result = arif_lease_issue(
            organ_id="A-FORGE",
            actor_id="test-agent",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            ttl_seconds=120,
            max_uses=3,
        )
        assert result["status"] == "OK"
        lease = result["result"]["lease"]
        assert lease["organ_id"] == "A-FORGE"
        assert lease["max_action_class"] == "MUTATE"
        assert lease["max_uses"] == 3

    def test_arif_lease_revoke(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        result = arif_lease_revoke(rec.lease_id, "test", actor_id="x")
        assert result["status"] == "OK"
        assert result["result"]["lease"]["revoked"] is True

    def test_arif_lease_inspect_lists_active(self) -> None:
        issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        result = arif_lease_inspect(organ_id="A-FORGE")
        assert result["status"] == "OK"
        assert result["result"]["total_active"] == 1


# ──────────────────────────────────────────────────────────────────────
# Scope wildcard and prefix matching
# ──────────────────────────────────────────────────────────────────────


class TestScopeMatching:
    def test_prefix_scope_matches(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge:*"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert r["valid"]

    def test_wildcard_scope_matches(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["*"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "any_tool", "MUTATE")
        assert r["valid"]

    def test_exact_scope_matches(self) -> None:
        rec = issue_lease(
            organ_id="A-FORGE",
            actor_id="x",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
        )
        r = validate_lease_for_tool(rec.lease_id, "arif_forge_execute", "MUTATE")
        assert r["valid"]


# ──────────────────────────────────────────────────────────────────────
# ADR-001 migration guards
# ──────────────────────────────────────────────────────────────────────


class TestAdr001Migration:
    def test_legacy_lease_module_raises_import_error(self) -> None:
        with pytest.raises(ImportError):
            import arifosmcp.runtime.lease  # noqa: F401

    def test_runtime_init_exports_canonical_registry_only(self) -> None:
        from arifosmcp import runtime

        assert hasattr(runtime, "LeaseRecord")
        assert hasattr(runtime, "present_lease")
        assert not hasattr(runtime, "LeaseStore")
        assert not hasattr(runtime, "LeaseScope")


# ──────────────────────────────────────────────────────────────────────
# _arif_forge_execute lease gate
# ──────────────────────────────────────────────────────────────────────


class TestForgeExecuteLeaseGate:
    def test_engineer_without_lease_or_plan_holds(self) -> None:
        from arifosmcp.runtime.tools import _arif_forge_execute

        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            ack_irreversible=True,
            actor_id="test_actor",
        )
        assert result["status"] == "HOLD"
        assert "LEASE GATE" in result.get("meta", {}).get("reason", "")

    def test_engineer_with_valid_lease_id_succeeds(self) -> None:
        from arifosmcp.runtime.tools import _arif_forge_execute, _arif_mind_reason

        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        lease = issue_lease(
            organ_id="A-FORGE",
            actor_id="test_actor",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            ttl_seconds=60,
        )
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            plan_id=pid,
            lease_id=lease.lease_id,
            ack_irreversible=True,
            actor_id="test_actor",
            witness_type="human",
        )
        assert result["status"] == "OK"

    def test_engineer_with_exhausted_lease_holds(self) -> None:
        from arifosmcp.runtime.tools import _arif_forge_execute

        lease = issue_lease(
            organ_id="A-FORGE",
            actor_id="test_actor",
            scope=["arif_forge_execute"],
            max_action_class="MUTATE",
            ttl_seconds=60,
            max_uses=1,
        )
        # Consume the single use
        present_lease(lease.lease_id, "arif_forge_execute", "MUTATE")
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            lease_id=lease.lease_id,
            ack_irreversible=True,
            actor_id="test_actor",
        )
        assert result["status"] == "HOLD"
        assert "exhausted" in result.get("meta", {}).get("reason", "").lower()

    def test_write_mode_requires_lease(self) -> None:
        from arifosmcp.runtime.tools import _arif_forge_execute

        result = _arif_forge_execute(
            mode="write",
            manifest="test",
            actor_id="test_actor",
            judge_state_hash="abc123",
        )
        assert result["status"] == "HOLD"
        assert "LEASE GATE" in result.get("meta", {}).get("reason", "")
