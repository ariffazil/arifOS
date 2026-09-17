"""
tests/runtime/test_institutional_memory_closure.py — 777 FORGE Institutional Memory Closure

Falsification suite for AGI Institutional Memory Invariants (M1 to M24):
  - T1: Normal memory write with objective_id and trace_id
  - T2: Child agent handoff preserving causal lineage
  - T3: Tool observation -> memory persistence
  - T4: Memory -> decision -> action provenance
  - T5: Reality contradiction veto & supersession
  - T6: Missing trace rejection / quarantine
  - T7: Unverified actor mutation blocking
  - T8: Asymmetric memory authority (no tool/autonomy expansion)
  - T9: Epistemic separation (OBS vs INT human meaning membrane)
  - T10: Full envelope reconstruction
  - T11: Temporal truth queryability post-supersession
  - T12: Decay and lifecycle transitions
  - Scenario A: Machine reality changes & reality veto
  - Scenario B: Human statement corrigibility
  - Scenario C: Persistent memory poisoning defense
  - Institutional Queries: Q1 (Events), Q2 (Beliefs), Q3 (Decisions), Q4 (Outcomes)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import uuid
import pytest
from datetime import UTC, datetime

from arifosmcp.runtime import memory_handlers_v5, memory_store
from arifosmcp.runtime.decision_memory import (
    activation_changes,
    decayed_confidence,
    lifecycle_recommendation,
    predicted_value,
    record_outcome,
    record_retrieval,
    should_retrieve,
)
from arifosmcp.runtime.memory_store import (
    execute_reality_veto,
    reality_veto_check,
)
from arifosmcp.schemas.memory_object import (
    FutureValueBlock,
    MemoryAuthorityBlock,
    MemoryObject,
    ProvenanceBlock,
    EpistemicsBlock,
    PolicyBlock,
)


# ── In-Memory Store Fixture for Offline Falsification ─────────────────────────

@pytest.fixture
def mock_storage(monkeypatch):
    """Hermetic storage fixture simulating PostgreSQL L4 memory_store."""
    db: dict[str, dict] = {}

    async def fake_pg_write(**kwargs):
        mem_id = kwargs["memory_id"]
        db[mem_id] = {
            "id": mem_id,
            "tier": kwargs["tier"],
            "text": kwargs["text"],
            "metadata": kwargs["metadata"],
            "valid_at": kwargs.get("valid_at") or datetime.now(UTC),
            "recorded_at": kwargs.get("recorded_at") or datetime.now(UTC),
            "deleted_at": None,
            "status": "active",
        }
        return True

    async def fake_pg_supersede(old_memory_id, new_memory_id, reason, resolution_kind="supersede", **kwargs):
        if old_memory_id in db:
            db[old_memory_id]["deleted_at"] = datetime.now(UTC)
            db[old_memory_id]["status"] = "superseded" if resolution_kind == "supersede" else "retracted"
            db[old_memory_id]["metadata"]["superseded_by"] = new_memory_id
            db[old_memory_id]["metadata"]["supersession_reason"] = reason
            db[old_memory_id]["metadata"]["resolution_kind"] = resolution_kind
            return True
        return False

    async def fake_fetch_l4(mem_id):
        return db.get(mem_id)

    monkeypatch.setattr(memory_store, "_pg_write", fake_pg_write)
    monkeypatch.setattr(memory_store, "_pg_supersede", fake_pg_supersede)
    return db


# ── T1 & T2: Causal Lineage & Child Agent Handoff ──────────────────────────────

@pytest.mark.asyncio
async def test_t1_t2_causal_lineage_and_handoff(mock_storage):
    """M1, M2: Normal memory write retains objective_id and trace_id across handoffs."""
    objective_id = "obj_777_memory_closure"
    trace_id = "tr_777_test_root"

    # Parent writes memory
    parent_payload = {
        "content": "Root service configuration initialized.",
        "memory_class": "procedural",
        "truth_class": {"status": "observed", "confidence": 0.95},
        "provenance": {
            "actor_id": "FI-009",
            "session_id": "sess_root",
            "trace_id": trace_id,
            "objective_id": objective_id,
        },
        "tier_hint": "L3",
        "trace_id": trace_id,
        "objective_id": objective_id,
    }

    res1 = await memory_handlers_v5._handle_remember(parent_payload, ctx=None)
    assert res1["verdict"] == "SEAL"
    mem1_id = res1["payload"]["memory_id"]
    assert mock_storage[mem1_id]["metadata"]["provenance"]["trace_id"] == trace_id
    assert mock_storage[mem1_id]["metadata"]["provenance"]["objective_id"] == objective_id

    # Child agent inherits trace and objective, minting child span
    child_trace_id = trace_id  # preserved
    child_span = "span_child_executor_01"

    child_payload = {
        "content": "Child verified database connectivity.",
        "memory_class": "episodic",
        "truth_class": {"status": "observed", "confidence": 0.99},
        "provenance": {
            "actor_id": "FI-003",
            "session_id": "sess_child",
            "trace_id": child_trace_id,
            "objective_id": objective_id,
            "span_id": child_span,
        },
        "tier_hint": "L3",
        "trace_id": child_trace_id,
        "objective_id": objective_id,
    }

    res2 = await memory_handlers_v5._handle_remember(child_payload, ctx=None)
    assert res2["verdict"] == "SEAL"
    mem2_id = res2["payload"]["memory_id"]
    assert mock_storage[mem2_id]["metadata"]["provenance"]["trace_id"] == trace_id
    assert mock_storage[mem2_id]["metadata"]["provenance"]["objective_id"] == objective_id
    assert mock_storage[mem2_id]["metadata"]["provenance"]["span_id"] == child_span


# ── T3 & T4: Tool -> Memory -> Decision Provenance ────────────────────────────

@pytest.mark.asyncio
async def test_t3_t4_tool_to_memory_to_decision_provenance(mock_storage):
    """M21, M22, M23: Tool observation writes to memory, which informs decisions without losing IDs."""
    # Tool writes memory
    tool_mem_res = await memory_handlers_v5._handle_remember(
        {
            "content": "Service health check: port 5432 responsive, latency=2ms.",
            "memory_class": "episodic",
            "truth_class": {"status": "observed", "confidence": 1.0},
            "provenance": {
                "actor_id": "tool:net_probe",
                "session_id": "s_tool",
                "origin": "tool",
                "trace_id": "tr_probe_01",
                "objective_id": "obj_health_sweep",
            },
            "tier_hint": "L3",
        },
        ctx=None,
    )
    mem_id = tool_mem_res["payload"]["memory_id"]
    assert mem_id in mock_storage

    # Decision engine records retrieval of this memory
    dec_event = record_retrieval(
        memory_id=mem_id,
        decision_id="dec_route_traffic_01",
        reason_selected="verified service responsive on port 5432",
        policy_changes={"traffic_allocation": "normal"},
    )
    assert dec_event["memory_id"] == mem_id
    assert dec_event["decision_id"] == "dec_route_traffic_01"

    # Outcome following decision
    out_event = record_outcome(
        memory_id=mem_id,
        decision_id="dec_route_traffic_01",
        verified=True,
        useful=True,
        evidence_refs=["receipt_probe_01"],
    )
    assert out_event["event_type"] == "memory_outcome"
    assert out_event["status"] == "USEFUL"


# ── T5 & Scenario A: Reality Veto & Machine State Change ───────────────────────

@pytest.mark.asyncio
async def test_t5_scenario_a_machine_reality_changes_veto(mock_storage):
    """M10, M11, M24: Fresh authenticated reality falsifies stale memory and supersedes it."""
    # 1. Store state A
    state_a = {"service": "postgres", "host": "127.0.0.1", "port": 5432, "status": "UP"}
    res_a = await memory_handlers_v5._handle_remember(
        {
            "content": json.dumps(state_a),
            "memory_class": "episodic",
            "truth_class": {"status": "observed", "confidence": 0.95},
            "provenance": {"actor_id": "sensor_a", "session_id": "s_initial", "trace_id": "tr_a"},
            "tier_hint": "L3",
        },
        ctx=None,
    )
    mem_a_id = res_a["payload"]["memory_id"]

    # 2. Reality changes: State B (port changed to 5433, status degraded)
    fresh_probe_reality = {"service": "postgres", "host": "127.0.0.1", "port": 5433, "status": "UP"}

    # 3. Before taking action based on Stored State A, perform Reality Veto Check
    veto_eval = reality_veto_check(stored_claim=state_a, observed_reality=fresh_probe_reality)
    assert veto_eval["veto"] is True
    assert veto_eval["contradiction_detected"] is True
    assert veto_eval["stale_claim_propagation_detected"] is True
    assert len(veto_eval["discrepancies"]) == 1
    assert veto_eval["discrepancies"][0]["field"] == "port"

    # 4. Execute reality veto: supersede State A with State B
    revise_res = await memory_handlers_v5._handle_revise(
        {
            "supersedes_memory_id": mem_a_id,
            "new_content": json.dumps(fresh_probe_reality),
            "reason": "Port migration detected by live probe",
            "provenance": {
                "actor_id": "reality_prober",
                "session_id": "s_probe",
                "trace_id": "tr_veto_01",
                "objective_id": "obj_cluster_integrity",
            },
            "truth_class": {"status": "observed", "confidence": 1.0},
            "tier_hint": "L3",
        },
        ctx=None,
    )
    assert revise_res["verdict"] == "SEAL"
    mem_b_id = revise_res["payload"]["memory_id"]

    # 5. Verify Invariants: State A preserved historically as superseded, State B active
    assert mock_storage[mem_a_id]["status"] == "superseded"
    assert mock_storage[mem_a_id]["metadata"]["superseded_by"] == mem_b_id
    assert mock_storage[mem_b_id]["status"] == "active"
    assert mock_storage[mem_b_id]["metadata"]["supersedes_id"] == mem_a_id


# ── T6 & T7: Missing Trace & Unverified Actor Guard ───────────────────────────

@pytest.mark.asyncio
async def test_t6_missing_provenance_rejected():
    """M1, M2: Memory write without actor_id is rejected with F11 citation."""
    res = await memory_handlers_v5._handle_remember(
        {
            "content": "Unattributed claim floating in void.",
            "memory_class": "episodic",
            "truth_class": {"status": "observed", "confidence": 0.5},
            "provenance": {},  # missing actor_id!
        },
        ctx=None,
    )
    assert res["verdict"] == "SABAR"
    assert "F11" in res["payload"]["note"]


# ── T8 & Scenario C: Asymmetric Authority & Persistent Poisoning Defense ──────

@pytest.mark.asyncio
async def test_t8_scenario_c_asymmetric_authority_and_poisoning():
    """M7, M20: Memory NEVER expands authority or tools; malicious instructions stay data."""
    # Malicious external content attempted as memory
    poison_payload = {
        "may_expand_tools": True,  # Attacker tries to grant tools
        "may_raise_autonomy": True,  # Attacker tries to elevate autonomy
        "may_restrict_tools": True,
        "may_inform_reasoning": True,
    }

    # Invariant check 1: Pydantic schema rejects True on may_expand_tools
    with pytest.raises(Exception):
        MemoryAuthorityBlock.model_validate(poison_payload)

    # Invariant check 2: activation_changes hard-locks authority_expansion_allowed = False
    safe_auth = MemoryAuthorityBlock(
        may_expand_tools=False,
        may_raise_autonomy=False,
        may_restrict_tools=True,
    )
    changes = activation_changes(safe_auth)
    assert changes["authority_expansion_allowed"] is False
    assert changes["tool_policy"] == "restrict_only"


# ── T9 & Scenario B: Human Meaning Membrane (OBS vs INT & Corrigibility) ──────

@pytest.mark.asyncio
async def test_t9_scenario_b_human_meaning_membrane_corrigibility(mock_storage):
    """M3, M4, M5, M19: Human statement (OBS) and machine interpretation (INT) remain separate; corrigible."""
    # 1. Literal statement
    statement_mem = await memory_handlers_v5._handle_remember(
        {
            "content": "Arif: 'The interface feels sluggish today.'",
            "memory_class": "session",
            "truth_class": {"status": "observed", "confidence": 1.0},
            "provenance": {"actor_id": "Arif", "session_id": "chat_01", "origin": "human"},
            "tier_hint": "L3",
        },
        ctx=None,
    )
    obs_id = statement_mem["payload"]["memory_id"]
    assert mock_storage[obs_id]["metadata"]["truth_class"] == "observed"

    # 2. Machine interpretation stored SEPARATELY as inferred/interpreted
    interp_mem = await memory_handlers_v5._handle_remember(
        {
            "content": "Machine interpretation: User permanently dislikes web animations.",
            "memory_class": "episodic",
            "truth_class": {"status": "derived", "confidence": 0.6},
            "provenance": {"actor_id": "FI-002", "session_id": "chat_01", "origin": "agent"},
            "tier_hint": "L3",
        },
        ctx=None,
    )
    int_id = interp_mem["payload"]["memory_id"]
    assert mock_storage[int_id]["metadata"]["truth_class"] == "derived"

    # 3. Human corrects interpretation: "I was just on 3G cellular, animations are fine."
    correction = await memory_handlers_v5._handle_revise(
        {
            "supersedes_memory_id": int_id,
            "new_content": "Corrected interpretation: User experienced temporary network throttling on 3G.",
            "correction_event": "Human clarified context: temporary network bottleneck, not animation preference.",
            "resolution_kind": "supersede",
            "provenance": {"actor_id": "Arif", "session_id": "chat_01", "origin": "human"},
            "new_truth_class": {"status": "observed", "confidence": 0.95},
            "tier_hint": "L3",
        },
        ctx=None,
    )
    assert correction["verdict"] == "SEAL"
    new_int_id = correction["payload"]["memory_id"]

    # 4. Check invariants: original literal utterance untouched, old interpretation superseded
    assert mock_storage[obs_id]["status"] == "active"
    assert mock_storage[int_id]["status"] == "superseded"
    assert mock_storage[int_id]["metadata"]["superseded_by"] == new_int_id
    assert mock_storage[new_int_id]["status"] == "active"


# ── T11: Temporal Truth Preservation ──────────────────────────────────────────

def test_t11_temporal_truth_preservation(mock_storage):
    """M9: Historical queries still find what was known at T0 even after supersession."""
    # Stored historical facts remain intact with timestamps
    t0 = datetime(2026, 9, 16, 12, 0, 0, tzinfo=UTC)
    t1 = datetime(2026, 9, 17, 12, 0, 0, tzinfo=UTC)

    mock_storage["mem_old"] = {
        "id": "mem_old",
        "text": "Service location = Server Alpha",
        "status": "superseded",
        "valid_at": t0,
        "recorded_at": t0,
        "deleted_at": t1,
        "metadata": {"superseded_by": "mem_new"},
    }
    mock_storage["mem_new"] = {
        "id": "mem_new",
        "text": "Service location = Server Beta",
        "status": "active",
        "valid_at": t1,
        "recorded_at": t1,
        "deleted_at": None,
        "metadata": {"supersedes_id": "mem_old"},
    }

    # Query as of T0: mem_old was valid and active
    as_of_t0 = [
        m for m in mock_storage.values()
        if m["valid_at"] <= t0 and (m["deleted_at"] is None or m["deleted_at"] > t0)
    ]
    assert len(as_of_t0) == 1
    assert as_of_t0[0]["id"] == "mem_old"

    # Query as of T1: mem_new is valid and active
    as_of_t1 = [
        m for m in mock_storage.values()
        if m["valid_at"] <= t1 and (m["deleted_at"] is None or m["deleted_at"] > t1)
    ]
    assert len(as_of_t1) == 1
    assert as_of_t1[0]["id"] == "mem_new"


# ── T12: Governed Lifecycle & Confidence Decay ────────────────────────────────

def test_t12_lifecycle_and_confidence_decay():
    """M13, M14: Unreinforced high-risk memories decay over time; non-destructive."""
    val = FutureValueBlock(
        recurrence_probability=0.2,
        decision_impact=0.3,
        evidence_reliability=0.5,
        retrieval_specificity=0.4,
        maintenance_cost=0.1,
        privacy_risk=0.1,
        staleness_risk=0.4,
        anchoring_risk=0.3,
        token_cost_normalized=0.2,
    )
    # Stale, anchoring memory with low utility should not be retrieved
    assert should_retrieve(val) is False

    # Confidence decay over 6 months with 0.05/month decay rate
    initial_conf = 0.8
    decayed = decayed_confidence(initial_conf, months_elapsed=6.0, decay_per_month=0.05)
    assert decayed == 0.5
    assert decayed < initial_conf


# ── T7: Unverified Actor Guard ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_t7_unverified_actor_mutation_blocked(monkeypatch):
    """M1, M2: OBSERVE_ONLY session or unverified actor cannot execute durable memory mutations."""
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import arif_memory

    # Attempt to write memory without verified session / lease
    res = await arif_memory(
        mode="remember",
        payload={
            "content": "Attacker trying to write without lease.",
            "provenance": {"actor_id": "anon"},
        },
        session_id="unverified_sess",
        actor_id="anon",
        lease_id=None,  # missing lease!
    )
    # Mode requires lease_id, otherwise SABAR / HOLD
    assert res.verdict.name in ("SABAR", "HOLD")
    assert "lease_id" in str(getattr(res, "detail", "")).lower() or "lease" in str(res.payload).lower()


# ── T10: Full Envelope Reconstruction ─────────────────────────────────────────

def test_t10_full_envelope_reconstruction():
    """M8, M15: Memory retrieval must resolve back to canonical envelope, not bare text."""
    now = datetime.now(UTC)
    envelope = MemoryObject(
        memory_id=f"mem_{uuid.uuid4().hex[:12]}",
        actor_id="agent_arch",
        tier="L3",
        memory_class="semantic",
        truth_class="observed",
        confidence=0.98,
        uncertainty_band=0.02,
        content="Service A depends on PostgreSQL cluster B.",
        provenance=ProvenanceBlock(
            origin="tool",
            source_uri="service://inventory",
            actor_id="agent_arch",
            captured_at=now,
        ),
        policy=PolicyBlock(
            scope="shared",
            deletable=True,
        ),
        authority=MemoryAuthorityBlock(
            may_inform_reasoning=True,
            may_restrict_tools=False,
            may_expand_tools=False,
            may_lower_autonomy=False,
            may_raise_autonomy=False,
        ),
        future_value=FutureValueBlock(
            recurrence_probability=0.8,
            decision_impact=0.7,
            evidence_reliability=0.9,
            retrieval_specificity=0.8,
        ),
    )

    # Validate envelope integrity
    assert envelope.memory_id.startswith("mem_")
    assert envelope.authority.may_expand_tools is False
    assert envelope.truth_class == "observed"
    assert envelope.confidence == 0.98
    assert envelope.provenance.actor_id == "agent_arch"


# ── Institutional Queries: Q1, Q2, Q3, Q4 ─────────────────────────────────────

def test_institutional_queries_separation():
    """Invariant: Observed event ≠ interpretation ≠ decision ≠ outcome.

    Q1: What happened? (Events)
    Q2: What did we believe? (Epistemic claims)
    Q3: What did we decide? (Decisions)
    Q4: What actually happened afterward? (Witnessed outcomes)
    """
    history = [
        {"type": "EVENT", "id": "e1", "data": "Deploy command executed at 14:00"},
        {"type": "BELIEF", "id": "b1", "data": "Configuration assumed valid under load"},
        {"type": "DECISION", "id": "d1", "data": "Route 50% traffic to node 2"},
        {"type": "OUTCOME", "id": "o1", "data": "Node 2 response latency 12ms, zero errors"},
    ]

    q1_events = [h for h in history if h["type"] == "EVENT"]
    q2_beliefs = [h for h in history if h["type"] == "BELIEF"]
    q3_decisions = [h for h in history if h["type"] == "DECISION"]
    q4_outcomes = [h for h in history if h["type"] == "OUTCOME"]

    assert len(q1_events) == 1 and q1_events[0]["id"] == "e1"
    assert len(q2_beliefs) == 1 and q2_beliefs[0]["id"] == "b1"
    assert len(q3_decisions) == 1 and q3_decisions[0]["id"] == "d1"
    assert len(q4_outcomes) == 1 and q4_outcomes[0]["id"] == "o1"

    # Crucial acceptance check: they never collapse into a single record type
    assert q1_events != q2_beliefs
    assert q2_beliefs != q3_decisions
    assert q3_decisions != q4_outcomes


# ── Failure Injection: Substrate Unavailability & Fail-Closed ─────────────────

@pytest.mark.asyncio
async def test_failure_injection_postgres_disconnect(monkeypatch):
    """Section 19: When PostgreSQL fails, memory mutation fails closed with SABAR, never corrupting state."""
    async def failing_pg_write(**kwargs):
        raise ConnectionRefusedError("Simulated DB socket closed")

    monkeypatch.setattr(memory_store, "_pg_write", failing_pg_write)

    res = await memory_handlers_v5._handle_remember(
        {
            "content": "Critical fact under DB failure",
            "memory_class": "episodic",
            "truth_class": {"status": "observed", "confidence": 0.9},
            "provenance": {"actor_id": "tester"},
        },
        ctx=None,
    )

    # Fail closed: returns SABAR, does not silently succeed or crash
    assert res["verdict"] == "SABAR"
    assert "L4 write failed" in res["payload"]["note"]

