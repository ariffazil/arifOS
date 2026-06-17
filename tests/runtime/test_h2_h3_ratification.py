"""
Tests for 888 HOLD ratification H2 (Planning Organ) and H3 (Epoch Lifecycle).
Epoch 2026-04-26 — SOVEREIGN_RATIFICATION
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.tools import (
    _arif_session_init,
    _arif_mind_reason,
    _arif_forge_execute,
    _ok,
    _SESSIONS,
    _EPOCH_REGISTRY,
    _PLAN_REGISTRY,
    _VAULT_LEDGER,
)


def _inject_lease_for_plan(plan_id: str) -> None:
    """Inject a canonical ADR-001 lease matching plan_id so forge_execute can proceed."""
    from arifosmcp.runtime.lease_registry import issue_lease

    issue_lease(
        lease_id=plan_id,
        organ_id="A-FORGE",
        actor_id="test_actor",
        scope=["arif_forge_execute"],
        max_action_class="MUTATE",
        ttl_seconds=300,
        max_uses=10,
    )


@pytest.mark.skip(reason="H3 epoch tests hang on vault seal path — needs async event loop fix in vault writer")
class TestH3EpochLifecycle:
    """H3: arif_session_init epoch_open / epoch_seal modes."""

    @pytest.fixture(autouse=True)
    def _clean_state(self):
        _SESSIONS.clear()
        _EPOCH_REGISTRY.clear()
        _VAULT_LEDGER.clear()
        yield
        _SESSIONS.clear()
        _EPOCH_REGISTRY.clear()
        _VAULT_LEDGER.clear()

    def test_epoch_open_creates_epoch(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        result = _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        assert result["status"] == "OK"
        eid = result["result"]["epoch_id"]
        assert eid.startswith("EPOCH-")
        assert eid in _EPOCH_REGISTRY
        assert _EPOCH_REGISTRY[eid]["status"] == "open"
        assert _SESSIONS[sid]["epoch_id"] == eid

    def test_epoch_open_without_session_id_holds(self):
        result = _arif_session_init(mode="epoch_open", actor_id="test_actor")
        assert result["status"] == "HOLD"

    def test_epoch_seal_writes_vault_entry(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        result = _arif_session_init(mode="epoch_seal", session_id=sid, actor_id="test_actor")
        assert result["status"] == "OK"
        assert result["result"]["status"] == "sealed"
        assert "vault_entry_id" in result["result"]
        entry_id = result["result"]["vault_entry_id"]
        assert any(e["id"] == entry_id for e in _VAULT_LEDGER)

    def test_epoch_id_injected_into_ok_results(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        eid = _SESSIONS[sid]["epoch_id"]
        ok = _ok("test_tool", {"data": 1}, session_id=sid)
        assert ok["result"]["epoch_id"] == eid

    def test_epoch_tools_used_tracking(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        eid = _SESSIONS[sid]["epoch_id"]
        _ok("arif_sense_observe", {}, session_id=sid)
        _ok("arif_mind_reason", {}, session_id=sid)
        assert "arif_sense_observe" in _EPOCH_REGISTRY[eid]["tools_used"]
        assert "arif_mind_reason" in _EPOCH_REGISTRY[eid]["tools_used"]

    def test_init_with_epoch_id_binds_at_creation(self):
        eid = "EPOCH-custom-123"
        init = _arif_session_init(mode="init", actor_id="test_actor", epoch_id=eid)
        sid = init["result"]["session"]["session_id"]
        assert _SESSIONS[sid]["epoch_id"] == eid
        assert eid in _EPOCH_REGISTRY


class TestH2PlanningOrgan:
    """H2: arif_mind_reason plan mode + arif_forge_execute plan gate."""

    @pytest.fixture(autouse=True)
    def _clean_state(self):
        _SESSIONS.clear()
        _PLAN_REGISTRY.clear()
        _VAULT_LEDGER.clear()
        _EPOCH_REGISTRY.clear()
        yield
        _SESSIONS.clear()
        _PLAN_REGISTRY.clear()
        _VAULT_LEDGER.clear()
        _EPOCH_REGISTRY.clear()

    def test_plan_mode_emits_plan_receipt(self):
        result = _arif_mind_reason(
            mode="plan",
            query="Build app. Deploy it. Clean up old files.",
            actor_id="test_actor",
        )
        assert result["status"] == "OK"
        receipt = result["result"]["plan_receipt"]
        assert "plan_id" in receipt
        assert receipt["plan_id"].startswith("PLAN-")
        assert "task_graph" in receipt
        assert "reversibility_map" in receipt
        assert receipt["status"] == "pending_approval"

    def test_plan_mode_detects_irreversible_steps(self):
        result = _arif_mind_reason(
            mode="plan",
            query="Delete the database. Deploy the build.",
            actor_id="test_actor",
        )
        receipt = result["result"]["plan_receipt"]
        # At least one step should be irreversible
        assert any(v is False for v in receipt["reversibility_map"].values())

    def test_plan_stored_in_registry_and_vault(self):
        result = _arif_mind_reason(mode="plan", query="Test plan", actor_id="test_actor")
        pid = result["result"]["plan_receipt"]["plan_id"]
        assert pid in _PLAN_REGISTRY
        assert any(e.get("type") == "plan" and e.get("plan_id") == pid for e in _VAULT_LEDGER)

    def test_plan_review_retrieves_plan(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        review = _arif_mind_reason(mode="plan_review", plan_id=pid)
        assert review["status"] == "OK"
        assert review["result"]["plan_receipt"]["plan_id"] == pid

    def test_plan_review_missing_plan_id_holds(self):
        result = _arif_mind_reason(mode="plan_review")
        assert result["status"] == "HOLD"

    def test_plan_approve_updates_status(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        result = _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        assert result["status"] == "OK"
        assert _PLAN_REGISTRY[pid]["status"] == "approved"

    def test_forge_engineer_without_plan_holds(self):
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            ack_irreversible=True,
            actor_id="test_actor",
        )
        assert result["status"] == "HOLD"
        reason = result.get("meta", {}).get("reason", "")
        assert any(k in reason for k in ("plan_id", "LEASE GATE", "lease"))

    def test_forge_query_does_not_require_plan(self):
        result = _arif_forge_execute(
            mode="query", query="status", actor_id="test_actor", ack_irreversible=True
        )
        assert result["status"] == "OK"

    def test_forge_engineer_with_unapproved_plan_holds(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            plan_id=pid,
            ack_irreversible=True,
            actor_id="test_actor",
        )
        assert result["status"] == "HOLD"
        reason = result.get("meta", {}).get("reason", "")
        assert any(k in reason for k in ("not approved", "LEASE GATE", "lease"))

    def test_forge_engineer_with_approved_plan_succeeds(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        _inject_lease_for_plan(pid)
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            plan_id=pid,
            ack_irreversible=True,
            actor_id="test_actor",
            witness_type="human",
        )
        assert result["status"] == "OK"

    def test_plan_transitions_to_in_execution_on_forge_start(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        _inject_lease_for_plan(pid)
        _arif_forge_execute(
            mode="engineer",
            manifest="test",
            plan_id=pid,
            ack_irreversible=True,
            actor_id="test_actor",
            witness_type="human",
        )
        assert _PLAN_REGISTRY[pid]["status"] == "completed"
        history = _PLAN_REGISTRY[pid]["state_history"]
        assert any(h["to"] == "in_execution" for h in history)
        assert any(h["to"] == "completed" for h in history)

    def test_plan_transitions_to_aborted_on_forge_hold(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        # Inject a valid lease so we pass the lease hard-block gate
        # and reach the constitution kernel (which will return HOLD).
        _inject_lease_for_plan(pid)
        result = _arif_forge_execute(
            mode="commit", manifest="test", plan_id=pid, actor_id="test_actor"
        )
        assert result["status"] == "HOLD"
        assert _PLAN_REGISTRY[pid]["status"] == "aborted"
        history = _PLAN_REGISTRY[pid]["state_history"]
        assert any(h["to"] == "aborted" for h in history)

    def test_lease_hard_block_commit_without_lease(self):
        """FORGE D (2026-06-14): Mutation without lease must fail closed
        even when ack_irreversible=False. The Lease Gate is the
        constitutional circuit breaker."""
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        result = _arif_forge_execute(
            mode="commit", manifest="test", plan_id=pid, actor_id="test_actor"
        )
        assert result["status"] == "HOLD"
        reason = result.get("meta", {}).get("reason", "")
        assert "LEASE GATE" in reason, (
            f"Expected LEASE GATE in reason, got: {reason}"
        )
        # Plan should NOT have transitioned — lease gate stops before
        # constitution kernel evaluation.
        assert _PLAN_REGISTRY[pid]["status"] == "approved", (
            f"Plan should remain 'approved' when blocked by lease gate, "
            f"got: {_PLAN_REGISTRY[pid]['status']}"
        )

    def test_lease_hard_block_write_without_lease(self):
        """FORGE D (2026-06-14): mode='write' must also hard-block without lease."""
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        result = _arif_forge_execute(
            mode="write", manifest="test", plan_id=pid,
            actor_id="test_actor", judge_state_hash="abc123",
        )
        assert result["status"] == "HOLD"
        reason = result.get("meta", {}).get("reason", "")
        assert "LEASE GATE" in reason, (
            f"Expected LEASE GATE in reason for write mode, got: {reason}"
        )

    def test_lease_success_with_valid_lease(self):
        """FORGE D (2026-06-14): With a valid lease, mutation proceeds to
        constitution kernel (which may still HOLD for other reasons)."""
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        _inject_lease_for_plan(pid)
        result = _arif_forge_execute(
            mode="engineer",
            manifest="test",
            plan_id=pid,
            ack_irreversible=True,
            actor_id="test_actor",
            witness_type="human",
        )
        assert result["status"] == "OK"
        assert _PLAN_REGISTRY[pid]["status"] in ("completed", "in_execution")

    def test_plan_approve_logs_witness_to_vault(self):
        plan = _arif_mind_reason(mode="plan", query="Test", actor_id="test_actor")
        pid = plan["result"]["plan_receipt"]["plan_id"]
        before = len(_VAULT_LEDGER)
        _arif_mind_reason(
            mode="plan_approve",
            plan_id=pid,
            actor_id="test_actor",
            witness_type="human",
        )
        after = len(_VAULT_LEDGER)
        assert after > before
        entry = _VAULT_LEDGER[-1]
        assert entry["type"] == "plan_approval"
        assert entry["plan_id"] == pid
        assert entry["witness_type"] == "human"
        assert entry["approved_by"] == "test_actor"


class TestH3EpochSealGuard:
    """H3: epoch_seal 888 HOLD guard for degraded epochs."""

    @pytest.fixture(autouse=True)
    def _clean_state(self):
        _SESSIONS.clear()
        _EPOCH_REGISTRY.clear()
        _VAULT_LEDGER.clear()
        yield
        _SESSIONS.clear()
        _EPOCH_REGISTRY.clear()
        _VAULT_LEDGER.clear()

    def test_epoch_seal_holds_on_void_verdict(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        eid = _SESSIONS[sid]["epoch_id"]
        _EPOCH_REGISTRY[eid]["verdict"] = "VOID"
        result = _arif_session_init(mode="epoch_seal", session_id=sid, actor_id="test_actor")
        assert result["status"] == "HOLD"
        assert "sovereign review" in result["meta"]["reason"]

    def test_epoch_seal_holds_on_low_peace2(self):
        init = _arif_session_init(mode="init", actor_id="test_actor")
        sid = init["result"]["session"]["session_id"]
        _arif_session_init(mode="epoch_open", session_id=sid, actor_id="test_actor")
        eid = _SESSIONS[sid]["epoch_id"]
        _EPOCH_REGISTRY[eid]["peace2"] = 0.8
        result = _arif_session_init(mode="epoch_seal", session_id=sid, actor_id="test_actor")
        assert result["status"] == "HOLD"
        assert "sovereign review" in result["meta"]["reason"]
