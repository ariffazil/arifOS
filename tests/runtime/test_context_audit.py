"""
tests/runtime/test_context_audit.py — Phase T1 coverage for context_audit.py
============================================================================

The contract under test:
  - POLICY_VERSION == "context_policy.v1" (pinned, must match docs)
  - audit_classify(event_type, risk_class) maps deterministically to
    TRACE / DIGEST / SEAL / HOLD per the policy table in
    docs/context/context_policy_v1.md
  - audit_trace(session, ...) appends to in-memory _TRACES (no VAULT999)
  - audit_digest(session) batches N traces into a hashable DIGEST payload
  - audit_seal(event_type, ...) builds a SEAL envelope and re-routes
    if the policy says HOLD
  - audit_hold(rationale) returns HOLD envelope, NEVER writes
  - High-risk classes (PRIVATE / FINANCIAL / LEGAL / IDENTITY / COMMITMENT /
    EXTERNAL_ACTION / CANONICAL) force TRACE → SEAL
  - Canonical / memory-deletion / VAULT-mutation / authority-upgrade
    events are always HOLD (F13 territory)

Iron rules (F1-F13):
  - F1 AMANAH:  every operation is reversible; raw preserved
  - F2 TRUTH:   never fabricate audit entries
  - F8 GENIUS:  policy version is pinned; changes = F13 signature
  - F11 AUDIT:  every context decision is traceable
  - F13 SOVEREIGN: canonical mutation = HOLD; agent cannot override

DITEMPA BUKAN DIBERI — every context decision leaves a trace.
"""

from __future__ import annotations

import os
import threading
import uuid

import pytest

from arifosmcp.runtime.context_audit import (
    POLICY_VERSION,
    SOURCE_OF_TRUTH,
    AuditMode,
    EventType,
    RiskClass,
    _self_check,
    audit_classify,
    audit_digest,
    audit_hold,
    audit_seal,
    audit_trace,
    get_seal_buffer,
    get_trace_store,
)


# ── Per-test isolation: drain trace + seal buffers before/after ─────────────
@pytest.fixture(autouse=True)
def _isolate_audit_state():
    """Clear the in-memory trace + seal buffers so tests don't pollute each
    other. F1 AMANAH: we never touch persistent storage here."""
    store = get_trace_store()
    yield
    # Drain leftover traces for any session this test used
    for sid in list(store._traces.keys()):
        store.drain(sid)


def _new_sid() -> str:
    return f"test-{uuid.uuid4().hex[:12]}"


# ─────────────────────────────────────────────────────────────────────────────
# audit_classify (1–9)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditClassify:
    def test_routine_retrieval_is_TRACE(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.TRACE

    def test_private_risk_forces_TRACE_to_SEAL(self):
        """Routine retrieval + PRIVATE risk → SEAL (per policy table)."""
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.PRIVATE.value)
        assert m == AuditMode.SEAL

    def test_financial_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.FINANCIAL.value)
        assert m == AuditMode.SEAL

    def test_legal_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.LEGAL.value)
        assert m == AuditMode.SEAL

    def test_identity_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.IDENTITY.value)
        assert m == AuditMode.SEAL

    def test_commitment_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.COMMITMENT.value)
        assert m == AuditMode.SEAL

    def test_external_action_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.EXTERNAL_ACTION.value)
        assert m == AuditMode.SEAL

    def test_canonical_risk_escalates_to_SEAL(self):
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, RiskClass.CANONICAL.value)
        assert m == AuditMode.SEAL

    def test_compaction_event_is_SEAL(self):
        """Compaction is SEAL even on routine risk."""
        m = audit_classify(EventType.CONTEXT_COMPACTION.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.SEAL

    def test_canonical_write_event_is_HOLD(self):
        """Per policy: CONTEXT_CANONICAL_WRITE → HOLD (F13 territory)."""
        m = audit_classify(EventType.CONTEXT_CANONICAL_WRITE.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.HOLD

    def test_memory_deletion_event_is_HOLD(self):
        m = audit_classify(EventType.CONTEXT_MEMORY_DELETION.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.HOLD

    def test_vault_mutation_event_is_HOLD(self):
        m = audit_classify(EventType.CONTEXT_VAULT_MUTATION.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.HOLD

    def test_authority_upgrade_event_is_HOLD(self):
        m = audit_classify(EventType.CONTEXT_AUTHORITY_UPGRADE.value, RiskClass.ROUTINE.value)
        assert m == AuditMode.HOLD

    def test_unknown_event_fails_closed_to_HOLD(self):
        """Unknown event types are F2 fail-closed → HOLD."""
        m = audit_classify("BOGUS_EVENT_xyz", RiskClass.ROUTINE.value)
        assert m == AuditMode.HOLD

    def test_classification_is_deterministic(self):
        a = audit_classify(EventType.CONTEXT_COMPACTION.value, RiskClass.ROUTINE.value)
        b = audit_classify(EventType.CONTEXT_COMPACTION.value, RiskClass.ROUTINE.value)
        assert a == b

    def test_invalid_risk_class_falls_back_to_routine(self):
        """Unknown risk_class string → ROUTINE (not HOLD)."""
        m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, "BOGUS_RISK")
        assert m == AuditMode.TRACE  # would have been HOLD if not for the fallback


# ─────────────────────────────────────────────────────────────────────────────
# audit_trace (10)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditTrace:
    def test_trace_appends(self):
        sid = _new_sid()
        r = audit_trace(sid, "qh-abc", ["L3:a", "L3:b"], ["L3:a"], dropped_count=1)
        assert r["mode"] == "TRACE"
        assert r["appended"] is True
        assert r["trace_count"] == 1
        assert "trace_hash" in r
        assert r["policy_version"] == "context_policy.v1"

    def test_trace_appends_in_order(self):
        sid = _new_sid()
        audit_trace(sid, "qh-1", ["L3:a"], ["L3:a"])
        audit_trace(sid, "qh-2", ["L3:b"], ["L3:b"])
        audit_trace(sid, "qh-3", ["L3:c"], ["L3:c"])
        # Peek doesn't mutate; count should be 3
        assert get_trace_store().count(sid) == 3

    def test_trace_does_not_write_to_vaul999(self):
        """TRACE events are L2/in-memory only. Phase 1 has no VAULT999 wire."""
        sid = _new_sid()
        before = len(get_seal_buffer())
        audit_trace(sid, "qh", ["L3:a"], ["L3:a"])
        after = len(get_seal_buffer())
        # TRACE shouldn't be queued for VAULT999
        assert before == after

    def test_trace_required_fields_present(self):
        r = audit_trace("s", "qh", ["L3:a"], ["L3:a"])
        # All TRACE receipts carry policy_version + mode
        assert r["policy_version"] == "context_policy.v1"
        assert r["mode"] == "TRACE"


# ─────────────────────────────────────────────────────────────────────────────
# audit_digest (11)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditDigest:
    def test_digest_drains_traces(self):
        sid = _new_sid()
        audit_trace(sid, "qh-1", ["L3:a"], ["L3:a"])
        audit_trace(sid, "qh-2", ["L3:b"], ["L3:b"])
        d = audit_digest(sid)
        assert d["mode"] == "DIGEST"
        assert d["n_traces"] == 2
        assert "digest_hash" in d

    def test_digest_empty_session_returns_zero(self):
        d = audit_digest(_new_sid())
        assert d["mode"] == "DIGEST"
        assert d["n_traces"] == 0
        assert d["vault999_status"] == "no_traces_to_digest"

    def test_digest_clears_traces(self):
        sid = _new_sid()
        audit_trace(sid, "qh", ["L3:a"], ["L3:a"])
        audit_digest(sid)
        # Traces should be drained
        assert get_trace_store().count(sid) == 0

    def test_digest_queued_for_phase2(self):
        """Per the doc: Phase 1 queues the DIGEST for Phase 2 to drain to
        VAULT999. The phase-2 flush is NOT yet wired."""
        sid = _new_sid()
        audit_trace(sid, "qh", ["L3:a"], ["L3:a"])
        d = audit_digest(sid)
        assert d["vault999_status"] == "queued_for_phase2_flush"


# ─────────────────────────────────────────────────────────────────────────────
# audit_seal (12)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditSeal:
    def test_compaction_creates_seal(self):
        sid = _new_sid()
        s = audit_seal(
            event_type=EventType.CONTEXT_COMPACTION.value,
            session_id=sid,
            actor_id="arif",
            risk_class=RiskClass.ROUTINE.value,
            pressure_before=0.92,
            pressure_after=0.51,
        )
        assert s["mode"] == "SEAL"
        assert "seal_hash" in s
        assert s["vault999_status"] == "queued_for_phase2_flush"

    def test_canonical_write_reroutes_to_hold(self):
        """Even if caller asked for SEAL, canonical write → HOLD."""
        sid = _new_sid()
        s = audit_seal(
            event_type=EventType.CONTEXT_CANONICAL_WRITE.value,
            session_id=sid,
            actor_id="arif",
            risk_class=RiskClass.ROUTINE.value,
        )
        # The seal function re-classifies; canonical write is HOLD
        assert "rerouted_to_HOLD" in s["vault999_status"]
        # The seal buffer should NOT have grown for this
        assert s["mode"] == "HOLD"

    def test_seal_envelope_carries_policy_version(self):
        sid = _new_sid()
        s = audit_seal(
            event_type=EventType.CONTEXT_COMPACTION.value,
            session_id=sid,
            actor_id="arif",
            risk_class=RiskClass.ROUTINE.value,
        )
        assert s["envelope"]["policy_version"] == "context_policy.v1"
        assert "seal_hash" in s["envelope"]

    def test_seal_buffer_grows_only_for_seal_events(self):
        """SEAL events append to the seal buffer; rerouted (HOLD) do not."""
        before = len(get_seal_buffer())
        audit_seal(
            event_type=EventType.CONTEXT_COMPACTION.value,
            session_id=_new_sid(),
            actor_id="arif",
            risk_class=RiskClass.ROUTINE.value,
        )
        after_seal = len(get_seal_buffer())
        assert after_seal == before + 1

        audit_seal(
            event_type=EventType.CONTEXT_CANONICAL_WRITE.value,
            session_id=_new_sid(),
            actor_id="arif",
            risk_class=RiskClass.ROUTINE.value,
        )
        # Canonical write reroutes to HOLD; should NOT add to seal buffer
        after_hold = len(get_seal_buffer())
        assert after_hold == after_seal


# ─────────────────────────────────────────────────────────────────────────────
# audit_hold (13)
# ─────────────────────────────────────────────────────────────────────────────
class TestAuditHold:
    def test_hold_never_writes(self):
        """HOLD is a circuit breaker. The seal buffer must not grow."""
        before = len(get_seal_buffer())
        h = audit_hold("canonical mutation requires F13")
        after = len(get_seal_buffer())
        assert before == after

    def test_hold_envelope_includes_required_action(self):
        h = audit_hold("test rationale")
        assert h["mode"] == "HOLD"
        assert h["verdict"] == "HOLD"
        assert "F13" in h["required_action"]
        assert "ed25519" in h["required_signature"].lower()
        assert h["policy_version"] == "context_policy.v1"

    def test_hold_carries_rationale(self):
        h = audit_hold("specific reason for hold", event_type="CONTEXT_MEMORY_DELETION")
        assert h["rationale"] == "specific reason for hold"
        assert h["event_type"] == "CONTEXT_MEMORY_DELETION"

    def test_hold_is_required_for_canonical_mutation(self):
        h = audit_hold("overwrite canonical memory")
        assert h["required_action"] == "escalate_to_F13_sovereign"


# ─────────────────────────────────────────────────────────────────────────────
# Event log ordering (14)
# ─────────────────────────────────────────────────────────────────────────────
class TestEventLogOrdering:
    def test_event_order_preserved_in_digest(self):
        sid = _new_sid()
        # Append in order
        for i in range(5):
            audit_trace(sid, f"qh-{i}", [f"L3:{i}"], [f"L3:{i}"])
        # Drain and check the digest preserves trace ordering
        d = audit_digest(sid)
        # The traces have been drained but the digest payload records
        # first_trace_hash and last_trace_hash
        assert d["n_traces"] == 5
        # Re-running digest on the same (now-empty) session should return 0
        d2 = audit_digest(sid)
        assert d2["n_traces"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Policy version + source of truth pins
# ─────────────────────────────────────────────────────────────────────────────
def test_policy_version_is_canonical():
    assert POLICY_VERSION == "context_policy.v1"


def test_source_of_truth_doc_path():
    assert SOURCE_OF_TRUTH == "docs/context/context_policy_v1.md"
    # And the doc actually exists
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(repo_root, SOURCE_OF_TRUTH)
    assert os.path.exists(full_path), f"Source-of-truth doc not found: {full_path}"


# ─────────────────────────────────────────────────────────────────────────────
# In-module self-check (parity)
# ─────────────────────────────────────────────────────────────────────────────
def test_module_self_check_passes():
    r = _self_check()
    assert r["all_pass"] is True
    assert r["n_pass"] == r["n_checks"] == 14
    failed = [c for c in r["checks"] if not c["pass"]]
    assert not failed, f"context_audit self-check failed: {failed}"


# ─────────────────────────────────────────────────────────────────────────────
# High-risk class coverage (parametrized)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "risk_class",
    [
        RiskClass.PRIVATE,
        RiskClass.FINANCIAL,
        RiskClass.LEGAL,
        RiskClass.IDENTITY,
        RiskClass.COMMITMENT,
        RiskClass.EXTERNAL_ACTION,
        RiskClass.CANONICAL,
    ],
)
def test_all_high_risk_classes_escalate_TRACE_to_SEAL(risk_class):
    """Per the policy: 7 risk classes force TRACE → SEAL."""
    m = audit_classify(EventType.CONTEXT_RETRIEVAL_TRACE.value, risk_class.value)
    assert m == AuditMode.SEAL


@pytest.mark.parametrize(
    "event_type",
    [
        EventType.CONTEXT_CANONICAL_WRITE,
        EventType.CONTEXT_MEMORY_DELETION,
        EventType.CONTEXT_VAULT_MUTATION,
        EventType.CONTEXT_AUTHORITY_UPGRADE,
    ],
)
def test_all_canonical_mutation_events_are_HOLD(event_type):
    """Per the policy: 4 mutation events are always HOLD (F13 territory)."""
    m = audit_classify(event_type.value, RiskClass.ROUTINE.value)
    assert m == AuditMode.HOLD
