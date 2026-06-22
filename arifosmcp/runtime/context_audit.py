"""
arifOS v2.0 — Context Audit (Phase 1, Context Engine A)
═══════════════════════════════════════════════════════════════════════════
Implements the 4-mode audit policy from docs/context/context_policy_v1.md.

Audit modes:
  TRACE  — cheap session-local record (L2/in-memory), no VAULT999
  DIGEST — batched hash flushed to VAULT999 periodically
  SEAL   — immediate VAULT999 append (compaction, high-risk retrieval)
  HOLD   — refuses to write; requires F13 sovereign signature

Iron rules:
  - F1 AMANAH: every operation is reversible if its raw state is preserved
  - F2 TRUTH: never fabricate audit entries; if uncertain, refuse
  - F8 GENIUS: changing this module's policy version requires F13 signature
  - F11 AUDITABILITY: every context decision is traceable
  - F13 SOVEREIGN: canonical mutation, deletion, VAULT999 mutation = HOLD

Phase 1 (this module):
  - audit_trace(trace_payload)        (in-memory append)
  - audit_digest(session_id)          (flush batched traces to VAULT999)
  - audit_seal(seal_payload)          (immediate VAULT999 append)
  - audit_hold(rationale)             (returns HOLD envelope, refuses to write)
  - audit_classify(event_type, risk)  (decides TRACE/DIGEST/SEAL/HOLD per policy)

NOT in this module (Phase 2+):
  - actual VAULT999 HTTP writes (the seal function calls arif_seal
    via MCP — F13-gated path. Phase 1 only collects payloads; Phase 2 wires
    the actual write. Until then, audit_seal returns a VAULT999-READY
    payload that the next session can drain into the canonical ledger.)
  - LLM-driven summarization (Phase 4)
  - autonomous context loop (Phase 5)

DITEMPA BUKAN DIBERI — every context decision is forged, not given, and
every context decision leaves a trace.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections import defaultdict
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Iron Constants ────────────────────────────────────────────────────────
POLICY_VERSION = "context_policy.v1"  # MUST match docs/context/context_policy_v1.md
SOURCE_OF_TRUTH = "docs/context/context_policy_v1.md"


# Event types per policy
class AuditMode(StrEnum):
    TRACE = "TRACE"
    DIGEST = "DIGEST"
    SEAL = "SEAL"
    HOLD = "HOLD"


class EventType(StrEnum):
    CONTEXT_RETRIEVAL_TRACE = "CONTEXT_RETRIEVAL_TRACE"
    CONTEXT_RETRIEVAL_HIGH_RISK = "CONTEXT_RETRIEVAL_HIGH_RISK"
    CONTEXT_COMPACTION = "CONTEXT_COMPACTION"
    CONTEXT_DIGEST = "CONTEXT_DIGEST"
    CONTEXT_SUMMARY_REPLACED = "CONTEXT_SUMMARY_REPLACED"
    CONTEXT_CANONICAL_WRITE = "CONTEXT_CANONICAL_WRITE"
    CONTEXT_MEMORY_DELETION = "CONTEXT_MEMORY_DELETION"
    CONTEXT_VAULT_MUTATION = "CONTEXT_VAULT_MUTATION"
    CONTEXT_POLICY_CHANGE = "CONTEXT_POLICY_CHANGE"
    CONTEXT_THRESHOLD_CHANGE = "CONTEXT_THRESHOLD_CHANGE"
    CONTEXT_SUMMARIZER_PROMPT_CHANGE = "CONTEXT_SUMMARIZER_PROMPT_CHANGE"
    CONTEXT_AUTHORITY_UPGRADE = "CONTEXT_AUTHORITY_UPGRADE"


# Risk classes (per policy table)
class RiskClass(StrEnum):
    PRIVATE = "private"
    FINANCIAL = "financial"
    LEGAL = "legal"
    IDENTITY = "identity"
    COMMITMENT = "commitment"
    EXTERNAL_ACTION = "external_action"
    CANONICAL = "canonical"
    ROUTINE = "routine"


# ─── Mode Assignment (per policy table) ───────────────────────────────────
# Deterministic mapping. F2 TRUTH: same input → same mode.
MODE_MAP: dict[EventType, AuditMode] = {
    # TRACE-level
    EventType.CONTEXT_RETRIEVAL_TRACE: AuditMode.TRACE,
    # SEAL-level
    EventType.CONTEXT_RETRIEVAL_HIGH_RISK: AuditMode.SEAL,
    EventType.CONTEXT_COMPACTION: AuditMode.SEAL,
    EventType.CONTEXT_SUMMARY_REPLACED: AuditMode.SEAL,
    EventType.CONTEXT_POLICY_CHANGE: AuditMode.SEAL,
    EventType.CONTEXT_THRESHOLD_CHANGE: AuditMode.SEAL,
    EventType.CONTEXT_SUMMARIZER_PROMPT_CHANGE: AuditMode.SEAL,
    # DIGEST-level (batched)
    EventType.CONTEXT_DIGEST: AuditMode.DIGEST,
    # HOLD-level (F13 territory)
    EventType.CONTEXT_CANONICAL_WRITE: AuditMode.HOLD,
    EventType.CONTEXT_MEMORY_DELETION: AuditMode.HOLD,
    EventType.CONTEXT_VAULT_MUTATION: AuditMode.HOLD,
    EventType.CONTEXT_AUTHORITY_UPGRADE: AuditMode.HOLD,
}


# Risk classes that force SEAL (overrides DIGEST)
HIGH_RISK_CLASSES = frozenset(
    {
        RiskClass.PRIVATE,
        RiskClass.FINANCIAL,
        RiskClass.LEGAL,
        RiskClass.IDENTITY,
        RiskClass.COMMITMENT,
        RiskClass.EXTERNAL_ACTION,
        RiskClass.CANONICAL,
    }
)


def audit_classify(event_type: str, risk_class: str = "routine") -> AuditMode:
    """
    Classify an event into one of 4 audit modes per the policy table.

    Args:
        event_type: one of EventType enum values
        risk_class: one of RiskClass enum values (default: routine)

    Returns:
        AuditMode enum value

    Note:
        Even if the event_type would default to TRACE, a high risk_class
        forces SEAL. Even if event_type would default to SEAL, a canonical
        write forces HOLD. Deterministic precedence.
    """
    try:
        et = EventType(event_type)
    except ValueError:
        # Unknown event — fail-closed to HOLD (F2 + F13)
        logger.warning(f"[context_audit] unknown event_type={event_type!r}; defaulting to HOLD")
        return AuditMode.HOLD

    try:
        rc = RiskClass(risk_class)
    except ValueError:
        rc = RiskClass.ROUTINE

    # Precedence: HOLD > SEAL > DIGEST > TRACE
    if et in (
        EventType.CONTEXT_CANONICAL_WRITE,
        EventType.CONTEXT_MEMORY_DELETION,
        EventType.CONTEXT_VAULT_MUTATION,
        EventType.CONTEXT_AUTHORITY_UPGRADE,
    ):
        return AuditMode.HOLD

    base_mode = MODE_MAP.get(et, AuditMode.HOLD)  # default unknown → HOLD

    if base_mode == AuditMode.TRACE and rc in HIGH_RISK_CLASSES:
        return AuditMode.SEAL

    return base_mode


# ─── Session-Local Trace Store (in-memory) ────────────────────────────────
class _TraceStore:
    """
    Thread-safe in-memory buffer of TRACE events.
    Flushed to DIGEST (and eventually VAULT999) by audit_digest().
    NOT persistent across kernel restarts (Phase 2: add L2 Redis).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._traces: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._max_per_session = 10_000
        self._last_flush_at: dict[str, float] = {}

    def append(self, session_id: str, trace: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if len(self._traces[session_id]) >= self._max_per_session:
                # Auto-evict oldest 10% to prevent unbounded growth
                evict_count = self._max_per_session // 10
                self._traces[session_id] = self._traces[session_id][evict_count:]
            self._traces[session_id].append(trace)
            return {
                "appended": True,
                "trace_count": len(self._traces[session_id]),
            }

    def drain(self, session_id: str) -> list[dict[str, Any]]:
        """Return and clear traces for a session (for DIGEST batch)."""
        with self._lock:
            traces = self._traces.pop(session_id, [])
            return traces

    def peek(self, session_id: str) -> list[dict[str, Any]]:
        """Read without removing (for diagnostics)."""
        with self._lock:
            return list(self._traces.get(session_id, []))

    def count(self, session_id: str) -> int:
        with self._lock:
            return len(self._traces.get(session_id, []))


# ─── Singleton ─────────────────────────────────────────────────────────────
_TRACES = _TraceStore()
_SEAL_BUFFER: list[dict[str, Any]] = []  # SEAL payloads ready for VAULT999
_SEAL_BUFFER_LOCK = threading.Lock()


def get_trace_store() -> _TraceStore:
    return _TRACES


def get_seal_buffer() -> list[dict[str, Any]]:
    """Read-only view of pending SEAL payloads."""
    with _SEAL_BUFFER_LOCK:
        return list(_SEAL_BUFFER)


# ─── Hash Helper (deterministic, no LLM) ──────────────────────────────────
def _hash_payload(payload: dict[str, Any]) -> str:
    try:
        s = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        import hashlib

        return hashlib.sha256(s.encode()).hexdigest()
    except Exception:
        return "unhashable"


def _now_iso() -> str:
    import datetime

    return datetime.datetime.now(datetime.UTC).isoformat()


# ─── Public API: 4 Audit Operations ───────────────────────────────────────
def audit_trace(
    session_id: str,
    query_hash: str,
    retrieved_memory_ids: list[str],
    selected_ids: list[str],
    dropped_count: int = 0,
    tier_origin: str = "L3",
    ttl_seconds: int = 3600,
    **extra: Any,
) -> dict[str, Any]:
    """
    Record a routine retrieval as TRACE. No VAULT999. L2/in-memory only.

    Returns:
        dict with: mode, trace_hash, appended, trace_count
    """
    payload = {
        "event_type": EventType.CONTEXT_RETRIEVAL_TRACE.value,
        "policy_version": POLICY_VERSION,
        "session_id": session_id,
        "ts_utc": _now_iso(),
        "query_hash": query_hash,
        "retrieved_memory_ids": retrieved_memory_ids,
        "selected_ids": selected_ids,
        "dropped_count": dropped_count,
        "tier_origin": tier_origin,
        "ttl_seconds": ttl_seconds,
        **extra,
    }
    payload["trace_hash"] = _hash_payload(payload)
    result = _TRACES.append(session_id, payload)
    return {
        "mode": AuditMode.TRACE.value,
        "trace_hash": payload["trace_hash"],
        "appended": result["appended"],
        "trace_count": result["trace_count"],
        "policy_version": POLICY_VERSION,
    }


def audit_digest(session_id: str, window_start: str = "", window_end: str = "") -> dict[str, Any]:
    """
    Flush all TRACE events for a session as a single DIGEST to VAULT999.

    Phase 1: this returns a DIGEST payload ready for VAULT999 but does NOT
    actually call arif_seal. Phase 2 will wire the MCP call.

    Returns:
        dict with: mode, digest_hash, n_traces, vault999_status, payload
    """
    traces = _TRACES.drain(session_id)
    if not traces:
        return {
            "mode": AuditMode.DIGEST.value,
            "n_traces": 0,
            "vault999_status": "no_traces_to_digest",
            "policy_version": POLICY_VERSION,
        }

    trace_hashes = [t.get("trace_hash", "") for t in traces]
    digest_input = {
        "event_type": EventType.CONTEXT_DIGEST.value,
        "policy_version": POLICY_VERSION,
        "session_id": session_id,
        "ts_utc": _now_iso(),
        "window_start": window_start or traces[0].get("ts_utc", ""),
        "window_end": window_end or traces[-1].get("ts_utc", ""),
        "n_traces": len(traces),
        "trace_digest": _hash_payload({"hashes": trace_hashes}),
        "first_trace_hash": trace_hashes[0] if trace_hashes else "",
        "last_trace_hash": trace_hashes[-1] if trace_hashes else "",
    }
    digest_input["digest_hash"] = _hash_payload(digest_input)

    # Phase 1: queue for next VAULT999 flush (Phase 2 wires the call)
    with _SEAL_BUFFER_LOCK:
        _SEAL_BUFFER.append(digest_input)

    return {
        "mode": AuditMode.DIGEST.value,
        "digest_hash": digest_input["digest_hash"],
        "n_traces": len(traces),
        "vault999_status": "queued_for_phase2_flush",
        "policy_version": POLICY_VERSION,
        "payload": digest_input,
    }


def audit_seal(
    event_type: str,
    session_id: str,
    actor_id: str = "",
    risk_class: str = "routine",
    **payload_fields: Any,
) -> dict[str, Any]:
    """
    Immediate VAULT999 append for compaction / high-risk retrieval.

    Phase 1: queues the SEAL payload. Phase 2 wires arif_seal MCP call.
    Caller must provide all required fields per the manifest schema in
    docs/context/context_policy_v1.md.

    Returns:
        dict with: mode, seal_hash, vault999_status, envelope
    """
    # Defense in depth: re-classify even if caller passed risk_class
    actual_mode = audit_classify(event_type, risk_class)
    if actual_mode != AuditMode.SEAL:
        # Re-routing: caller thought SEAL but policy says otherwise
        return {
            "mode": actual_mode.value,
            "vault999_status": f"rerouted_to_{actual_mode.value}",
            "policy_version": POLICY_VERSION,
            "rationale": f"event_type={event_type!r} risk_class={risk_class!r} classified as {actual_mode.value} not SEAL",
        }

    seal_payload = {
        "event_type": event_type,
        "policy_version": POLICY_VERSION,
        "session_id": session_id,
        "actor_id": actor_id,
        "ts_utc": _now_iso(),
        "risk_class": risk_class,
        **payload_fields,
    }
    seal_payload["seal_hash"] = _hash_payload(seal_payload)

    # Phase 1: queue for next VAULT999 flush
    with _SEAL_BUFFER_LOCK:
        _SEAL_BUFFER.append(seal_payload)

    return {
        "mode": AuditMode.SEAL.value,
        "seal_hash": seal_payload["seal_hash"],
        "vault999_status": "queued_for_phase2_flush",
        "policy_version": POLICY_VERSION,
        "envelope": seal_payload,
    }


def audit_hold(rationale: str, event_type: str = "", session_id: str = "") -> dict[str, Any]:
    """
    Refuse to write. Returns HOLD envelope. Caller must escalate to F13
    sovereign via arif_seal with ack_irreversible=True.

    This function NEVER writes anywhere. It is a circuit breaker.
    """
    return {
        "mode": AuditMode.HOLD.value,
        "verdict": "HOLD",
        "rationale": rationale,
        "event_type": event_type,
        "session_id": session_id,
        "policy_version": POLICY_VERSION,
        "required_action": "escalate_to_F13_sovereign",
        "required_signature": "ed25519:arif-fazil",
        "ts_utc": _now_iso(),
        "note": (
            "This operation is F13 SOVEREIGN territory. "
            "The agent does not have authority. "
            "Use arif_seal(mode=seal, ack_irreversible=True, "
            "actor_signature=<ed25519>) to proceed."
        ),
    }


# ─── Self-Check (deterministic, no I/O) ───────────────────────────────────
def _self_check() -> dict[str, Any]:
    """
    Verify policy mapping + 4-mode behavior.
    """
    results = []

    # 1. Routine retrieval → TRACE
    r = audit_classify("CONTEXT_RETRIEVAL_TRACE", "routine") == "TRACE"
    results.append(("routine_retrieval_is_TRACE", r))

    # 2. Routine retrieval + private memory → SEAL (override)
    r = audit_classify("CONTEXT_RETRIEVAL_TRACE", "private") == "SEAL"
    results.append(("private_routine_forces_SEAL", r))

    # 3. Compaction → SEAL
    r = audit_classify("CONTEXT_COMPACTION", "routine") == "SEAL"
    results.append(("compaction_is_SEAL", r))

    # 4. Memory deletion → HOLD
    r = audit_classify("CONTEXT_MEMORY_DELETION", "routine") == "HOLD"
    results.append(("memory_deletion_is_HOLD", r))

    # 5. VAULT999 mutation → HOLD
    r = audit_classify("CONTEXT_VAULT_MUTATION", "routine") == "HOLD"
    results.append(("vault_mutation_is_HOLD", r))

    # 6. Policy change → SEAL
    r = audit_classify("CONTEXT_POLICY_CHANGE", "routine") == "SEAL"
    results.append(("policy_change_is_SEAL", r))

    # 7. Unknown event → HOLD (fail-closed)
    r = audit_classify("UNKNOWN_EVENT_XYZ", "routine") == "HOLD"
    results.append(("unknown_event_is_HOLD", r))

    # 8. audit_hold never writes
    h = audit_hold("test")
    r = h["mode"] == "HOLD" and h["verdict"] == "HOLD" and "F13" in h["required_action"]
    results.append(("audit_hold_refuses_to_write", r))

    # 9. audit_trace appends
    t = audit_trace("sess-test-1", "qh-abc", ["L3:a", "L3:b"], ["L3:a"], 1)
    r = t["mode"] == "TRACE" and t["appended"] is True and t["trace_count"] == 1
    results.append(("audit_trace_appends", r))

    # 10. audit_digest drains
    d = audit_digest("sess-test-1")
    r = d["mode"] == "DIGEST" and d["n_traces"] == 1 and "digest_hash" in d
    results.append(("audit_digest_drains", r))

    # 11. audit_seal re-routes non-SEAL events
    s = audit_seal("CONTEXT_RETRIEVAL_TRACE", "sess-test-1", actor_id="arif", risk_class="routine")
    r = "rerouted" in s.get("vault999_status", "")
    results.append(("audit_seal_reroutes_non_seal", r))

    # 12. Policy version is canonical
    r = POLICY_VERSION == "context_policy.v1"
    results.append(("policy_version_canonical", r))

    # 13. Mode assignment is deterministic
    a = audit_classify("CONTEXT_COMPACTION", "routine")
    b = audit_classify("CONTEXT_COMPACTION", "routine")
    r = a == b
    results.append(("classification_is_deterministic", r))

    # 14. Hash is deterministic
    p1 = {"a": 1, "b": 2}
    p2 = {"b": 2, "a": 1}
    r = _hash_payload(p1) == _hash_payload(p2)
    results.append(("hash_is_deterministic", r))

    all_pass = all(passed for _, passed in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
    }


if os.getenv("ARIFOS_SELFTEST", "0") == "1":
    _selftest = _self_check()
    if _selftest["all_pass"]:
        logger.info(f"[context_audit] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}")
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[context_audit] selftest FAIL: {failed}")


__all__ = [
    "POLICY_VERSION",
    "SOURCE_OF_TRUTH",
    "AuditMode",
    "EventType",
    "RiskClass",
    "audit_classify",
    "audit_trace",
    "audit_digest",
    "audit_seal",
    "audit_hold",
    "get_trace_store",
    "get_seal_buffer",
    "_self_check",  # exported for tests
]
