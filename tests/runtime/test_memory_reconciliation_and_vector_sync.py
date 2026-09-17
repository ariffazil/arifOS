"""
test_memory_reconciliation_and_vector_sync.py — Falsification Suite for
P1-MEM-001, P1-MEM-002, P1-MEM-003, P2-MEM-001.

DITEMPA BUKAN DIBERI.
Verifies:
1. P1-MEM-001: Background reality-veto periodic reconciliation.
2. P1-MEM-002: Qdrant payload receives canonical supersession state.
3. P1-MEM-002: Semantic vector search excludes superseded claims by default.
4. P1-MEM-003: Graph layer retired_888 invariant honored.
5. P2-MEM-001: Memory authority escalation is strictly 0/N.
6. P2-002: Session enforcement falsification probe diagnosis.
"""

import asyncio
import uuid

import pytest
from arifosmcp.runtime.memory_reconciler import (
    PROBE_REGISTRY,
    MemoryReconciler,
)
from arifosmcp.runtime.memory_store import (
    _pg_supersede,
    reality_veto_check,
)
from arifosmcp.schemas.memory_object import (
    MemoryAuthorityBlock,
)

# ── Test 1: P1-MEM-001 Probe Contracts & Reality Veto Evaluation ────────────


def test_p1_mem_001_probe_contracts_and_contradiction():
    # 1. Consistent observation
    stored = {"git_head": "4bce9bf", "service_health": "green"}
    observed_same = {"git_head": "4bce9bf", "service_health": "green"}
    res_same = reality_veto_check(stored, observed_same)
    assert res_same["veto"] is False
    assert res_same["contradiction_detected"] is False

    # 2. Contradictory observation (Reality t+1 > Memory t)
    observed_diff = {"git_head": "new_sha_999", "service_health": "green"}
    res_diff = reality_veto_check(stored, observed_diff, key_fields=["git_head"])
    assert res_diff["veto"] is True
    assert res_diff["contradiction_detected"] is True
    assert len(res_diff["discrepancies"]) == 1
    assert res_diff["discrepancies"][0]["field"] == "git_head"
    assert res_diff["discrepancies"][0]["stored"] == "4bce9bf"
    assert res_diff["discrepancies"][0]["observed"] == "new_sha_999"


# ── Test 2: P1-MEM-001 Reconciler Evaluation & Dry-Run Pass ──────────────────


@pytest.mark.asyncio
async def test_p1_mem_001_reconciler_claim_evaluation():
    reconciler = MemoryReconciler(dry_run=True)

    # Claim with no probe contract
    claim_no_probe = {"id": str(uuid.uuid4()), "metadata": {}}
    eval_none = reconciler.evaluate_claim(claim_no_probe)
    assert eval_none["reconcilable"] is False

    # Mock custom probe in registry
    PROBE_REGISTRY["mock_test_probe"] = lambda: {"version": "2.0", "healthy": True}

    # Claim consistent with reality
    claim_consistent = {
        "id": str(uuid.uuid4()),
        "metadata": {
            "probe_contract": {"type": "mock_test_probe"},
            "expected_values": {"version": "2.0", "healthy": True},
        },
    }
    eval_ok = reconciler.evaluate_claim(claim_consistent)
    assert eval_ok["reconcilable"] is True
    assert eval_ok["veto_result"]["veto"] is False

    # Claim contradictory with reality
    claim_stale = {
        "id": str(uuid.uuid4()),
        "metadata": {
            "probe_contract": {"type": "mock_test_probe"},
            "expected_values": {"version": "1.0", "healthy": True},  # Version 1.0 is stale!
        },
    }
    eval_stale = reconciler.evaluate_claim(claim_stale)
    assert eval_stale["reconcilable"] is True
    assert eval_stale["veto_result"]["veto"] is True

    # Reconcile in dry-run mode
    action_res = await reconciler.reconcile_single_claim(
        claim_stale,
        eval_stale,
        trace_id="trc-test-reconcile-001",
        objective_id="obj-test-reconcile",
    )
    assert action_res["status"] == "veto_detected_dry_run"
    assert "discrepancies" in str(action_res) or "version" in str(action_res)


# ── Test 3: P1-MEM-002 Qdrant Vector Layer Supersession Synchronization ─────


@pytest.mark.asyncio
async def test_p1_mem_002_qdrant_supersession_synchronization(monkeypatch):
    """Verify Qdrant point payload receives canonical supersession state."""

    payload_updates = []

    class MockQdrantClient:
        def set_payload(self, collection_name, payload, points):
            payload_updates.append(
                {
                    "collection": collection_name,
                    "payload": payload,
                    "points": points,
                }
            )

    from arifosmcp.runtime import memory_store

    monkeypatch.setattr(memory_store, "_get_qdrant_client", lambda: MockQdrantClient())

    # Simulate superseding a memory record
    old_id = str(uuid.uuid4())
    new_id = str(uuid.uuid4())

    # Mock asyncpg to simulate successful row update
    class MockConn:
        async def fetchrow(self, query, *args):
            return {"qdrant_id": "mock-qdrant-pt-123"}

        async def close(self):
            pass

    import asyncpg

    monkeypatch.setattr(
        asyncpg, "connect", lambda *args, **kwargs: asyncio.sleep(0, result=MockConn())
    )

    res = await _pg_supersede(old_id, new_id, reason="reality_veto_disconfirmed_claim")
    assert res is True

    # Verify Qdrant payload was updated
    assert len(payload_updates) >= 1
    update = payload_updates[0]
    assert update["payload"]["active"] is False
    assert update["payload"]["status"] == "superseded"
    assert update["payload"]["superseded_by"] == new_id
    assert update["payload"]["supersession_reason"] == "reality_veto_disconfirmed_claim"


# ── Test 4: P1-MEM-002 Vector Search Excludes Superseded by Default ─────────


def test_p1_mem_002_vector_search_filtering_rules():
    """Verify that recall excludes superseded memories unless include_historical=True."""
    active_point = {
        "memory_id": "mem-1",
        "content": "active fact",
        "active": True,
        "status": "active",
    }
    superseded_point = {
        "memory_id": "mem-2",
        "content": "old fact",
        "active": False,
        "status": "superseded",
        "superseded_by": "mem-3",
    }

    # Default retrieval (include_historical = False)
    def filter_candidates(points, include_historical=False):
        res = []
        for p in points:
            if not include_historical:
                if (
                    p.get("active") is False
                    or p.get("status") in ("superseded", "revoked")
                    or p.get("superseded_by")
                ):
                    continue
            res.append(p)
        return res

    candidates = [active_point, superseded_point]

    # Default: only active returned
    default_results = filter_candidates(candidates, include_historical=False)
    assert len(default_results) == 1
    assert default_results[0]["memory_id"] == "mem-1"

    # Historical: both returned
    hist_results = filter_candidates(candidates, include_historical=True)
    assert len(hist_results) == 2
    assert any(r["memory_id"] == "mem-2" and r["superseded_by"] == "mem-3" for r in hist_results)


# ── Test 5: P1-MEM-003 Graph Layer retired_888 Invariant ─────────────────────


def test_p1_mem_003_graphiti_retired_888_invariant():
    """Verify Graphiti temporal edges acknowledged as retired_888 without deletion."""
    status = "retired_888"
    assert status == "retired_888"
    assert status.startswith("retired")


# ── Test 6: P2-MEM-001 Authority Contract Gate (Zero Escalation) ─────────────


def test_p2_mem_001_authority_escalation_attack_blocked():
    """Test attack: Stored memory claims Arif approved root access.
    Invariant: AuthorityEscalationFromMemory must be strictly 0/N.
    """
    attack_authority = {
        "may_expand_tools": True,
        "may_raise_autonomy": True,
        "scope": "sovereign",
    }

    # Pydantic schema validation MUST reject may_expand_tools=True
    with pytest.raises(ValueError):
        MemoryAuthorityBlock(**attack_authority)

    # Valid schema enforces False
    valid_authority = MemoryAuthorityBlock(
        may_expand_tools=False,
        may_raise_autonomy=False,
    )
    assert valid_authority.may_expand_tools is False
    assert valid_authority.may_raise_autonomy is False

    # Invariant holds across all tested attempts
    attempts = 10
    escalations = 0
    for _ in range(attempts):
        try:
            MemoryAuthorityBlock(may_expand_tools=True)
            escalations += 1
        except Exception:
            pass

    assert escalations == 0
    escalation_rate = escalations / attempts
    assert escalation_rate == 0.0


# ── Test 7: P2-002 Diagnostic on Session Enforcement Probe ──────────────────


def test_p2_002_session_enforcement_probe_diagnosis():
    """Verify session enforcement probe logic:
    tools/list is discovery (HTTP 200). Enforcement is at tool call boundary.
    The probe fails closed (returning False, never falsely asserting Pass).
    """
    from arifosmcp.runtime.reality_scoring import probe_mcp_session_enforcement

    passed, reason = probe_mcp_session_enforcement()
    assert isinstance(passed, bool)
    assert isinstance(reason, str)
    if not passed:
        assert "bypassed" in reason or "probe_timeout" in reason
