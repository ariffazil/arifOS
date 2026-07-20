"""
vault_outbox.py — arifOS D2: Transactional VAULT Append via Outbox

Per D2 (2026-07-13 corrective): do NOT call the VAULT writer casually
from the session shutdown hook. Use a transactional outbox:

  PENDING → CLAIMED → APPENDED → VERIFIED
                              ↓
                       FAILED_RETRYABLE → PENDING (retry)
                       HOLD              (manual intervention)

The outbox records:
  - event_id           — unique identifier
  - session_id         — which session created this
  - receipt_class      — SESSION_OBSERVED | SESSION_CLOSURE | SOVEREIGN_DECISION
  - payload_hash       — exact payload hash bound to capability
  - required_capability — what capability is needed to append
  - idempotency_key    — dedup key (never append twice)
  - status             — state machine value
  - attempts           — retry counter
  - created_at         — when queued
  - last_attempt_at    — most recent append attempt
  - appended_at        — when verified appended
  - last_error         — most recent failure reason
  - va_chain_hash      — VAULT chain hash when appended

Session closure states:

  CLOSING                  — session ending, in-flight
  CLOSED_PENDING_RECEIPT   — operational authority closed, audit append pending
  CLOSED_SEALED            — VAULT append verified
  CLOSED_UNSEALED          — close authority revoked but VAULT failed
  CLOSURE_HOLD             — operational hold; manual intervention required

Do NOT keep a session artificially active because VAULT is unavailable. Close
operational authority, mark audit closure pending.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# STATE MACHINES
# ═══════════════════════════════════════════════════════════════════════════════


class OutboxStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    APPENDED = "appended"
    VERIFIED = "verified"
    FAILED_RETRYABLE = "failed_retryable"
    HOLD = "hold"


class ClosureState(str, Enum):
    CLOSING = "closing"
    CLOSED_PENDING_RECEIPT = "closed_pending_receipt"
    CLOSED_SEALED = "closed_sealed"
    CLOSED_UNSEALED = "closed_unsealed"
    CLOSURE_HOLD = "closure_hold"


# ═══════════════════════════════════════════════════════════════════════════════
# CLOSURE RECEIPT SCHEMA (per D2 spec)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ClosureReceipt:
    """Append-only closure receipt for VAULT999.

    Fields per D2 spec:
      event_type              — SESSION_CLOSURE
      session_id              — which session
      principal_id            — bound sovereign principal (if any)
      agent_instances         — list of agents active in session
      started_at              — ISO8601
      ended_at                — ISO8601
      authority_band          — SOVEREIGN | OPERATOR | OBSERVE_ONLY | OBSERVER
      final_verdict           — PASS | HOLD | DENY | REVOKED
      task_refs               — list of task IDs
      artifact_hashes         — list of artifact content hashes
      tool_call_root          — merkle root of tool call history
      memory_revision_root    — merkle root of memory writes
      cooling_entry_ref       — ref to cooling ledger entry
      gate_fire_root          — merkle root of gate-fire entries
      constitution_hash       — sha256:<hex>
      runtime_manifest_hash   — sha256:<hex>
    """

    event_type: str = "SESSION_CLOSURE"
    session_id: str = ""
    principal_id: str = ""
    agent_instances: tuple[str, ...] = ()
    started_at: str = ""
    ended_at: str = ""
    authority_band: str = "OBSERVER"
    final_verdict: str = "PASS"
    task_refs: tuple[str, ...] = ()
    artifact_hashes: tuple[str, ...] = ()
    tool_call_root: str = ""
    memory_revision_root: str = ""
    cooling_entry_ref: str = ""
    gate_fire_root: str = ""
    constitution_hash: str = ""
    runtime_manifest_hash: str = ""

    def payload_hash(self) -> str:
        """Stable hash of closure receipt contents — bind to capability."""
        canonical = repr(sorted(self.__dict__.items()))
        return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"

    def to_dict(self) -> dict:
        return {**self.__dict__, "payload_hash": self.payload_hash()}


# ═══════════════════════════════════════════════════════════════════════════════
# OUTBOX ENTRY
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class OutboxEntry:
    """One outbox entry — appended to VAULT999 transactionally."""

    event_id: str
    session_id: str
    receipt_class: str  # ReceiptClass value
    payload_hash: str  # exact payload hash bound to capability
    required_capability: str  # what capability is needed
    idempotency_key: str
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0
    created_at: str = ""
    last_attempt_at: str | None = None
    appended_at: str | None = None
    last_error: str | None = None
    va_chain_hash: str | None = None
    closure_receipt: ClosureReceipt | None = None
    max_attempts: int = 5

    def is_terminal(self) -> bool:
        return self.status in (
            OutboxStatus.VERIFIED,
            OutboxStatus.HOLD,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# IN-PROCESS OUTBOX STORE
# (would be Supabase + VAULT in production — this is the structural shape)
# ═══════════════════════════════════════════════════════════════════════════════

_OUTBOX: dict[str, OutboxEntry] = {}
_IDEMPOTENCY_INDEX: dict[str, str] = {}  # idempotency_key → event_id
_SESSION_CLOUT: dict[str, ClosureState] = {}  # session_id → state
_VERIFIED_IDS: set[str] = set()  # idempotency keys already appended (no retry)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _fresh_event_id() -> str:
    return f"ev_{hashlib.sha256(os.urandom(16)).hexdigest()[:24]}"


def _compute_idempotency_key(
    session_id: str,
    receipt_class: str,
    payload_hash: str,
) -> str:
    """Deterministic idempotency key — same triple always → same key."""
    canonical = f"{session_id}:{receipt_class}:{payload_hash}"
    return f"idem_{hashlib.sha256(canonical.encode()).hexdigest()[:24]}"


# ═══════════════════════════════════════════════════════════════════════════════
# OUTBOX API
# ═══════════════════════════════════════════════════════════════════════════════


def enqueue(
    session_id: str,
    receipt_class: str,
    payload_hash: str,
    required_capability: str,
    closure_receipt: ClosureReceipt | None = None,
) -> OutboxEntry:
    """Enqueue an outbox event. Idempotent on (session_id, receipt_class, payload_hash)."""
    idem = _compute_idempotency_key(session_id, receipt_class, payload_hash)
    # Idempotency: already verified → return existing entry
    if idem in _IDEMPOTENCY_INDEX:
        existing_ev = _IDEMPOTENCY_INDEX[idem]
        existing = _OUTBOX.get(existing_ev)
        if existing and existing.status == OutboxStatus.VERIFIED:
            return existing
    # Already pending? return existing entry (no duplicate enqueue)
    if idem in _IDEMPOTENCY_INDEX:
        ev = _IDEMPOTENCY_INDEX[idem]
        existing = _OUTBOX.get(ev)
        if existing:
            return existing

    ev = _fresh_event_id()
    entry = OutboxEntry(
        event_id=ev,
        session_id=session_id,
        receipt_class=receipt_class,
        payload_hash=payload_hash,
        required_capability=required_capability,
        idempotency_key=idem,
        status=OutboxStatus.PENDING,
        attempts=0,
        created_at=_now_iso(),
        closure_receipt=closure_receipt,
    )
    _OUTBOX[ev] = entry
    _IDEMPOTENCY_INDEX[idem] = ev
    return entry


def claim(event_id: str) -> bool:
    """Atomically transition PENDING → CLAIMED. Idempotent."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    if entry.status != OutboxStatus.PENDING:
        return False
    entry.status = OutboxStatus.CLAIMED
    entry.attempts += 1
    entry.last_attempt_at = _now_iso()
    return True


def mark_appended(event_id: str, va_chain_hash: str) -> bool:
    """Transition CLAIMED → APPENDED after successful write to VAULT."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    if entry.status != OutboxStatus.CLAIMED:
        return False
    entry.va_chain_hash = va_chain_hash
    entry.appended_at = _now_iso()
    entry.status = OutboxStatus.APPENDED
    _VERIFIED_IDS.add(entry.idempotency_key)
    return True


def verify_appended(event_id: str) -> bool:
    """Transition APPENDED → VERIFIED after chain head confirms receipt."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    if entry.status != OutboxStatus.APPENDED:
        return False
    entry.status = OutboxStatus.VERIFIED
    return True


def mark_failed_retryable(event_id: str, error: str) -> bool:
    """Transition to FAILED_RETRYABLE — will retry up to max_attempts."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    if entry.attempts >= entry.max_attempts:
        entry.status = OutboxStatus.HOLD
        entry.last_error = f"max_attempts={entry.max_attempts}: {error}"
        return True
    entry.status = OutboxStatus.FAILED_RETRYABLE
    entry.last_error = error
    return True


def mark_hold(event_id: str, reason: str) -> bool:
    """Operator escalation — manual review required."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    entry.status = OutboxStatus.HOLD
    entry.last_error = reason
    return True


def reset_to_pending(event_id: str) -> bool:
    """Reset FAILED_RETRYABLE → PENDING for re-claim."""
    entry = _OUTBOX.get(event_id)
    if entry is None:
        return False
    if entry.status not in (
        OutboxStatus.FAILED_RETRYABLE,
        OutboxStatus.CLAIMED,
    ):
        return False
    entry.status = OutboxStatus.PENDING
    return True


def get_entry(event_id: str) -> OutboxEntry | None:
    return _OUTBOX.get(event_id)


def list_pending() -> list[OutboxEntry]:
    return [
        e
        for e in _OUTBOX.values()
        if e.status in (OutboxStatus.PENDING, OutboxStatus.FAILED_RETRYABLE)
    ]


def list_verified() -> list[OutboxEntry]:
    return [e for e in _OUTBOX.values() if e.status == OutboxStatus.VERIFIED]


# ═══════════════════════════════════════════════════════════════════════════════
# CLOSURE STATE
# ═══════════════════════════════════════════════════════════════════════════════


def begin_closure(session_id: str) -> ClosureState:
    """Session enters CLOSING — operational freeze begins."""
    _SESSION_CLOUT[session_id] = ClosureState.CLOSING
    return ClosureState.CLOSING


def mark_closure_pending(session_id: str) -> ClosureState:
    """Operational authority closed; audit append pending (VAULT outage)."""
    _SESSION_CLOUT[session_id] = ClosureState.CLOSED_PENDING_RECEIPT
    return ClosureState.CLOSED_PENDING_RECEIPT


def mark_closure_sealed(session_id: str) -> ClosureState:
    """Audit append verified → CLOSED_SEALED."""
    _SESSION_CLOUT[session_id] = ClosureState.CLOSED_SEALED
    return ClosureState.CLOSED_SEALED


def mark_closure_unsealed(session_id: str) -> ClosureState:
    """Operational authority closed but VAULT refused → CLOSED_UNSEALED (operational)."""
    _SESSION_CLOUT[session_id] = ClosureState.CLOSED_UNSEALED
    return ClosureState.CLOSED_UNSEALED


def mark_closure_hold(session_id: str) -> ClosureState:
    """Closure on hold pending operator review."""
    _SESSION_CLOUT[session_id] = ClosureState.CLOSURE_HOLD
    return ClosureState.CLOSURE_HOLD


def get_closure_state(session_id: str) -> ClosureState:
    """Return current closure state (default: CLOSING if registered, else CLOSING)."""
    return _SESSION_CLOUT.get(session_id, ClosureState.CLOSING)


# ═══════════════════════════════════════════════════════════════════════════════
# IDEMPOTENCY PROTECTION (retry-safe)
# ═══════════════════════════════════════════════════════════════════════════════


def is_already_verified(idempotency_key: str) -> bool:
    return idempotency_key in _VERIFIED_IDS


__all__ = [
    "OutboxStatus",
    "ClosureState",
    "ClosureReceipt",
    "OutboxEntry",
    "enqueue",
    "claim",
    "mark_appended",
    "verify_appended",
    "mark_failed_retryable",
    "mark_hold",
    "reset_to_pending",
    "get_entry",
    "list_pending",
    "list_verified",
    "is_already_verified",
    "begin_closure",
    "mark_closure_pending",
    "mark_closure_sealed",
    "mark_closure_unsealed",
    "mark_closure_hold",
    "get_closure_state",
    "_compute_idempotency_key",  # exposed for closure receipt builder
]
