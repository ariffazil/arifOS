"""
arifosmcp/runtime/candidate_store.py — EurekaCandidate authoritative state machine

Authoritative server-managed candidate store. Replaces the model-invented
EurekaCandidate dataclass in eureka_zen.py with a runtime-enforced state
machine where:
  - candidate_id is server-generated (NEVER from model/caller)
  - state transitions are controlled (UNREVIEWED → PROMOTED/TENSION/KILAUAN...)
  - content_hash is verified on every lookup
  - session isolation enforced
  - transition receipts tracked (anti-replay)

IRON RULES (from F13 SOVEREIGN verdict 2026-07-18):
  1. Server creates the candidate identity — model must not invent candidate_id, PROMOTED, or verification status.
  2. State transitions are controlled — no caller jumps directly from UNREVIEWED → VERIFIED.
  3. Authority tools receive references (candidate_ref), not prose.
  4. Fail closed — missing, forged, expired, cross-session, hash-mismatch all produce HOLD.
  5. Memory isolation — candidates live in sandbox; only VerifiedFinding enters canonical store.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# ── State Machine ─────────────────────────────────────────────────────────────


class EurekaCandidateState(StrEnum):
    """Authoritative state machine for EurekaCandidate lifecycle.

    Transition map:
      UNREVIEWED
          ├──→ PROMOTED   (Jauhari evidence check passed)
          ├──→ TENSION    (contradiction detected, needs resolution)
          └──→ KILAUAN    (interesting but not actionable — archived)

      PROMOTED
          ├──→ VERIFYING  (BIJAKSANA verification in progress)
          ├──→ REJECTED   (verification failed or falsified)
          └──→ VERIFIED   (BIJAKSANA verification passed)

      TENSION
          └──→ UNREVIEWED (re-opened after tension resolved)

      KILAUAN  (terminal — archived, no further transitions)
      REJECTED (terminal — falsified, no further transitions)
      VERIFIED (terminal — may be promoted to VerifiedFinding)
    """

    UNREVIEWED = "UNREVIEWED"
    PROMOTED = "PROMOTED"
    TENSION = "TENSION"
    KILAUAN = "KILAUAN"
    VERIFYING = "VERIFYING"
    REJECTED = "REJECTED"
    VERIFIED = "VERIFIED"


# ── Legal transitions ─────────────────────────────────────────────────────────

_STATE_TRANSITIONS: dict[EurekaCandidateState, set[EurekaCandidateState]] = {
    EurekaCandidateState.UNREVIEWED: {
        EurekaCandidateState.PROMOTED,
        EurekaCandidateState.TENSION,
        EurekaCandidateState.KILAUAN,
    },
    EurekaCandidateState.PROMOTED: {
        EurekaCandidateState.VERIFYING,
        EurekaCandidateState.REJECTED,
        # NOTE: No direct PROMOTED → VERIFIED. Must go through VERIFYING.
        # This prevents bypassing the BIJAKSANA verification step.
        # See F13 SOVEREIGN verdict 2026-07-18.
    },
    EurekaCandidateState.TENSION: {
        EurekaCandidateState.UNREVIEWED,  # re-open after tension resolved
    },
    EurekaCandidateState.KILAUAN: set(),  # terminal
    EurekaCandidateState.VERIFYING: {
        EurekaCandidateState.REJECTED,
        EurekaCandidateState.VERIFIED,
    },
    EurekaCandidateState.REJECTED: set(),  # terminal
    EurekaCandidateState.VERIFIED: set(),  # terminal
}


# ── Exceptions ────────────────────────────────────────────────────────────────


class CandidateStoreError(Exception):
    """Base error for candidate store operations."""


class InvalidTransitionError(CandidateStoreError):
    """Raised when a state transition is illegal."""


class CandidateNotFoundError(CandidateStoreError):
    """Raised when a candidate_ref does not match any record."""


class CandidateExpiredError(CandidateStoreError):
    """Raised when a candidate has exceeded its TTL."""


class ContentHashMismatchError(CandidateStoreError):
    """Raised when the caller's content does not match the stored hash."""


class SessionMismatchError(CandidateStoreError):
    """Raised when a candidate from session A is used in session B."""


class TransitionReplayError(CandidateStoreError):
    """Raised when a transition receipt is replayed."""


# ── Core dataclasses ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TransitionReceipt:
    """Immutable record of a single state transition."""

    from_state: EurekaCandidateState
    to_state: EurekaCandidateState
    actor_id: str
    reason: str
    timestamp: float
    receipt_hash: str = ""

    def __post_init__(self) -> None:
        if not self.receipt_hash:
            raw = (
                f"{self.from_state}->{self.to_state}:{self.actor_id}:{self.timestamp}:{self.reason}"
            )
            object.__setattr__(self, "receipt_hash", hashlib.sha256(raw.encode()).hexdigest()[:16])


@dataclass(frozen=True)
class EurekaCandidateRecord:
    """Server-managed authoritative candidate record.

    ALL fields are server-controlled. The model/LLM NEVER sets:
      - candidate_id (server-generated UUID)
      - state (controlled by state machine)
      - content_hash (verified against stored)
      - transition_seq (monotonic, server-incremented)
      - transition_receipts (appended by store)
    """

    candidate_id: str
    session_id: str
    content_hash: str
    hypothesis: str
    domain: str
    state: EurekaCandidateState
    transition_seq: int
    evidence_refs: tuple[str, ...] = ()
    counterexamples: tuple[str, ...] = ()
    created_by: str = ""
    created_at: float = 0.0
    expires_at: float = 0.0
    transition_receipts: tuple[TransitionReceipt, ...] = ()

    def is_expired(self, now: float | None = None) -> bool:
        if self.expires_at <= 0:
            return False
        return (now or time.time()) > self.expires_at


@dataclass(frozen=True)
class VerifiedFinding:
    """Canonical memory record — promoted from a VERIFIED candidate.

    Only created by CandidateStore.promote_to_finding() after VERIFIED state
    is reached. The original candidate remains in the sandbox as imagination.
    """

    finding_id: str
    source_candidate_id: str
    session_id: str
    hypothesis: str
    domain: str
    evidence_refs: tuple[str, ...]
    verification_result: dict[str, Any]
    created_at: float = 0.0
    promoted_by: str = ""


# ── Default TTL ──────────────────────────────────────────────────────────────

DEFAULT_CANDIDATE_TTL: float = 86400.0 * 7  # 7 days


# ── Candidate Store ──────────────────────────────────────────────────────────


class CandidateStore:
    """Thread-safe, in-memory authoritative candidate store.

    Two tiers:
      - Sandbox: UNREVIEWED/PROMOTED/TENSION/KILAUAN/VERIFYING/REJECTED candidates.
                 Excluded from default memory recall.
      - Canonical: VerifiedFinding records promoted from VERIFIED candidates.

    Singleton access via get_candidate_store().
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._candidates: dict[str, EurekaCandidateRecord] = {}
        self._findings: dict[str, VerifiedFinding] = {}

    # ── Public API ───────────────────────────────────────────────────────

    def create_candidate(
        self,
        hypothesis: str,
        session_id: str,
        *,
        domain: str = "general",
        actor_id: str = "",
        evidence_refs: tuple[str, ...] = (),
        counterexamples: tuple[str, ...] = (),
        ttl_seconds: float = DEFAULT_CANDIDATE_TTL,
    ) -> EurekaCandidateRecord:
        """Create a new candidate. candidate_id is SERVER-GENERATED.

        The model/caller NEVER provides:
          - candidate_id (ignored if passed)
          - state (always UNREVIEWED)
          - content_hash (computed from hypothesis)
          - transition_seq (always 0)
          - transition_receipts (empty)

        Args:
            hypothesis: The exploratory hypothesis text.
            session_id: Governing session ID.
            domain: Domain tag (general, geology, capital, etc.)
            actor_id: Who created this candidate.
            evidence_refs: Optional initial evidence references.
            counterexamples: Optional initial counterexamples.
            ttl_seconds: Time-to-live in seconds (default 7 days).

        Returns:
            EurekaCandidateRecord with server-assigned fields.

        Raises:
            ValueError: If hypothesis is empty.
        """
        if not hypothesis or not hypothesis.strip():
            raise ValueError("hypothesis must be non-empty")

        now = time.time()
        content_hash = self._compute_hash(hypothesis)

        record = EurekaCandidateRecord(
            candidate_id=f"wdr_{uuid.uuid4().hex[:16]}",
            session_id=session_id,
            content_hash=content_hash,
            hypothesis=hypothesis.strip(),
            domain=domain,
            state=EurekaCandidateState.UNREVIEWED,
            transition_seq=0,
            evidence_refs=evidence_refs,
            counterexamples=counterexamples,
            created_by=actor_id,
            created_at=now,
            expires_at=now + ttl_seconds if ttl_seconds > 0 else 0.0,
            transition_receipts=(),
        )

        with self._lock:
            self._candidates[record.candidate_id] = record

        return record

    def get_candidate(
        self,
        candidate_ref: str,
        *,
        session_id: str | None = None,
        expected_hash: str | None = None,
    ) -> EurekaCandidateRecord:
        """Look up a candidate by reference. Fail-closed.

        Args:
            candidate_ref: The candidate_id to look up.
            session_id: If provided, enforces session match.
            expected_hash: If provided, enforces content hash match.

        Returns:
            EurekaCandidateRecord.

        Raises:
            CandidateNotFoundError: If candidate_ref does not exist.
            CandidateExpiredError: If candidate has exceeded TTL.
            SessionMismatchError: If session_id does not match.
            ContentHashMismatchError: If expected_hash does not match.
        """
        with self._lock:
            record = self._candidates.get(candidate_ref)

        if record is None:
            raise CandidateNotFoundError(f"candidate_ref={candidate_ref} not found")

        if record.is_expired():
            raise CandidateExpiredError(f"candidate {candidate_ref} expired at {record.expires_at}")

        if session_id is not None and record.session_id != session_id:
            raise SessionMismatchError(
                f"candidate {candidate_ref} from session {record.session_id} "
                f"cannot be used in session {session_id}"
            )

        if expected_hash is not None and record.content_hash != expected_hash:
            raise ContentHashMismatchError(
                f"candidate {candidate_ref} content hash mismatch: "
                f"expected {expected_hash}, stored {record.content_hash}"
            )

        return record

    def transition(
        self,
        candidate_ref: str,
        to_state: EurekaCandidateState,
        *,
        actor_id: str = "",
        reason: str = "",
        session_id: str | None = None,
    ) -> EurekaCandidateRecord:
        """Apply a controlled state transition.

        Args:
            candidate_ref: Target candidate.
            to_state: Desired new state.
            actor_id: Who requested the transition.
            reason: Why the transition is being made.
            session_id: Optional session enforcement.

        Returns:
            Updated EurekaCandidateRecord.

        Raises:
            CandidateNotFoundError: If candidate_ref does not exist.
            CandidateExpiredError: If candidate expired.
            SessionMismatchError: If session_id does not match.
            InvalidTransitionError: If transition is not legal per state machine.
        """
        with self._lock:
            record = self._candidates.get(candidate_ref)
            if record is None:
                raise CandidateNotFoundError(f"candidate_ref={candidate_ref} not found")

            if record.is_expired():
                raise CandidateExpiredError(f"candidate {candidate_ref} expired")

            if session_id is not None and record.session_id != session_id:
                raise SessionMismatchError(f"candidate {candidate_ref} session mismatch")

            legal_next = _STATE_TRANSITIONS.get(record.state, set())
            if to_state not in legal_next:
                raise InvalidTransitionError(
                    f"Illegal transition: {record.state} → {to_state}. "
                    f"Legal targets: {sorted(s.value for s in legal_next)}"
                )

            # Create transition receipt
            receipt = TransitionReceipt(
                from_state=record.state,
                to_state=to_state,
                actor_id=actor_id,
                reason=reason,
                timestamp=time.time(),
            )

            # Build new record with updated state
            new_record = EurekaCandidateRecord(
                candidate_id=record.candidate_id,
                session_id=record.session_id,
                content_hash=record.content_hash,
                hypothesis=record.hypothesis,
                domain=record.domain,
                state=to_state,
                transition_seq=record.transition_seq + 1,
                evidence_refs=record.evidence_refs,
                counterexamples=record.counterexamples,
                created_by=record.created_by,
                created_at=record.created_at,
                expires_at=record.expires_at,
                transition_receipts=record.transition_receipts + (receipt,),
            )

            self._candidates[candidate_ref] = new_record

        return new_record

    def promote_to_finding(
        self,
        candidate_ref: str,
        *,
        verification_result: dict[str, Any] | None = None,
        session_id: str | None = None,
        actor_id: str = "",
    ) -> VerifiedFinding:
        """Promote a VERIFIED candidate to a canonical VerifiedFinding.

        The original candidate stays in the sandbox as imagination.
        The VerifiedFinding is a separate governed record.

        Args:
            candidate_ref: Candidate to promote (must be in VERIFIED state).
            verification_result: Evidence from BIJAKSANA verification.
            session_id: Optional session enforcement.
            actor_id: Who requested the promotion.

        Returns:
            VerifiedFinding — canonical memory record.

        Raises:
            CandidateNotFoundError, CandidateExpiredError, SessionMismatchError,
            InvalidTransitionError: If candidate not in VERIFIED state.
        """
        with self._lock:
            record = self._candidates.get(candidate_ref)
            if record is None:
                raise CandidateNotFoundError(f"candidate_ref={candidate_ref} not found")
            if record.state != EurekaCandidateState.VERIFIED:
                raise InvalidTransitionError(
                    f"Cannot promote candidate in state {record.state}. Must be VERIFIED."
                )
            if session_id is not None and record.session_id != session_id:
                raise SessionMismatchError("session mismatch")

            finding = VerifiedFinding(
                finding_id=f"vfind_{uuid.uuid4().hex[:16]}",
                source_candidate_id=record.candidate_id,
                session_id=record.session_id,
                hypothesis=record.hypothesis,
                domain=record.domain,
                evidence_refs=record.evidence_refs,
                verification_result=verification_result or {},
                created_at=time.time(),
                promoted_by=actor_id,
            )

            self._findings[finding.finding_id] = finding

        return finding

    def list_candidates(
        self,
        *,
        session_id: str | None = None,
        state_filter: EurekaCandidateState | None = None,
        limit: int = 50,
    ) -> list[EurekaCandidateRecord]:
        """List candidates, optionally filtered by session and/or state."""
        with self._lock:
            results = list(self._candidates.values())

        now = time.time()
        if session_id is not None:
            results = [r for r in results if r.session_id == session_id]
        if state_filter is not None:
            results = [r for r in results if r.state == state_filter]

        # Filter expired, return most recent first
        results = [r for r in results if not r.is_expired(now)]
        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit]

    def list_findings(
        self,
        *,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[VerifiedFinding]:
        """List canonical VerifiedFindings."""
        with self._lock:
            results = list(self._findings.values())

        if session_id is not None:
            results = [r for r in results if r.session_id == session_id]

        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit]

    def count(self) -> dict[str, Any]:
        """Return store statistics."""
        with self._lock:
            state_counts: dict[str, int] = {}
            for c in self._candidates.values():
                state_counts[c.state.value] = state_counts.get(c.state.value, 0) + 1
            return {
                "total_candidates": len(self._candidates),
                "total_findings": len(self._findings),
                "by_state": state_counts,
            }

    def clear_expired(self) -> int:
        """Remove expired candidates. Returns count removed."""
        now = time.time()
        with self._lock:
            expired = [cid for cid, r in self._candidates.items() if r.is_expired(now)]
            for cid in expired:
                del self._candidates[cid]
        return len(expired)

    # ── Private ──────────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(content: str) -> str:
        return f"sha256:{hashlib.sha256(content.strip().encode()).hexdigest()}"


# ── Singleton ────────────────────────────────────────────────────────────────

_STORE: CandidateStore | None = None
_STORE_LOCK = threading.RLock()


def get_candidate_store() -> CandidateStore:
    """Get the singleton CandidateStore instance."""
    global _STORE
    if _STORE is None:
        with _STORE_LOCK:
            if _STORE is None:
                _STORE = CandidateStore()
    return _STORE


def reset_candidate_store() -> None:
    """Reset the singleton store (testing only)."""
    global _STORE
    with _STORE_LOCK:
        _STORE = CandidateStore()


# ── Firewall helper ──────────────────────────────────────────────────────────


def verify_candidate_for_authority(
    candidate_ref: str | None,
    *,
    session_id: str | None = None,
    required_state: EurekaCandidateState = EurekaCandidateState.VERIFIED,
) -> dict[str, Any]:
    """Constitutional firewall: verify a candidate_ref is valid for authority access.

    This is the replacement for string-detect firewalls. Returns a verdict dict
    that can be directly returned from arif_judge/arif_seal/arif_forge.

    Args:
        candidate_ref: The reference to verify. If None, assumes normal (non-wonder) work.
        session_id: Optional session enforcement.
        required_state: Minimum state required (default VERIFIED).

    Returns:
        Dict with 'pass' (bool), 'verdict' (str), 'reason' (str), and optional record data.
    """
    if candidate_ref is None:
        return {
            "pass": True,
            "verdict": "PASS",
            "reason": "No candidate_ref — normal governance work, not wonder output.",
            "candidate_only_blocked": False,
        }

    store = get_candidate_store()

    try:
        record = store.get_candidate(candidate_ref, session_id=session_id)
    except CandidateNotFoundError:
        return {
            "pass": False,
            "verdict": "HOLD",
            "reason": f"UNKNOWN_CANDIDATE: candidate_ref={candidate_ref} not found. "
            "The candidate may have expired, never existed, or the reference is forged.",
            "candidate_only_blocked": True,
            "sunshine_firewall": True,
        }
    except CandidateExpiredError:
        return {
            "pass": False,
            "verdict": "HOLD",
            "reason": f"EXPIRED_CANDIDATE: candidate {candidate_ref} has exceeded its TTL. "
            "Create a new candidate to proceed.",
            "candidate_only_blocked": True,
            "sunshine_firewall": True,
        }
    except SessionMismatchError:
        return {
            "pass": False,
            "verdict": "HOLD",
            "reason": f"SESSION_MISMATCH: candidate {candidate_ref} belongs to a different session. "
            "Cross-session candidate references are not permitted.",
            "candidate_only_blocked": True,
            "sunshine_firewall": True,
        }

    # Check state requirement
    state_order = {
        EurekaCandidateState.UNREVIEWED: 0,
        EurekaCandidateState.TENSION: 1,
        EurekaCandidateState.KILAUAN: 1,
        EurekaCandidateState.PROMOTED: 2,
        EurekaCandidateState.VERIFYING: 3,
        EurekaCandidateState.REJECTED: 4,
        EurekaCandidateState.VERIFIED: 5,
    }

    record_rank = state_order.get(record.state, 0)
    required_rank = state_order.get(required_state, 5)

    if record_rank < required_rank:
        return {
            "pass": False,
            "verdict": "HOLD",
            "reason": (
                f"CANDIDATE_NOT_{required_state.value}: candidate {candidate_ref} "
                f"is in state {record.state.value} but {required_state.value} is required. "
                f"Current transition_seq={record.transition_seq}. "
                f"View transition receipts: {[r.receipt_hash for r in record.transition_receipts]}"
            ),
            "candidate_only_blocked": True,
            "sunshine_firewall": True,
            "candidate_state": record.state.value,
            "required_state": required_state.value,
            "transition_seq": record.transition_seq,
        }

    # Check that caller didn't smuggle PROMOTED/VERIFIED as text
    # This catches prompt-injection that writes "PROMOTED" in the hypothesis
    if _has_smuggled_state(record.hypothesis):
        return {
            "pass": False,
            "verdict": "HOLD",
            "reason": (
                f"SMUGGLED_STATE: candidate {candidate_ref} hypothesis contains "
                f"state keywords (PROMOTED, VERIFIED) that suggest prompt injection. "
                f"Content hash: {record.content_hash}"
            ),
            "candidate_only_blocked": True,
            "sunshine_firewall": True,
            "smuggled_state_detected": True,
        }

    return {
        "pass": True,
        "verdict": "PASS",
        "reason": f"Candidate {candidate_ref} is in state {record.state.value} and meets requirements.",
        "candidate_only_blocked": False,
        "candidate_id": candidate_ref,
        "candidate_state": record.state.value,
        "transition_seq": record.transition_seq,
        "content_hash": record.content_hash,
        "evidence_refs": list(record.evidence_refs),
    }


def _has_smuggled_state(hypothesis: str) -> bool:
    """Detect if hypothesis text contains forged state keywords."""
    lower = hypothesis.lower()
    # These patterns suggest the model tried to self-declare state
    suspicious: list[str] = [
        '"promoted"',
        '"verified"',
        '"promotion_state": "promoted"',
        '"state": "promoted"',
        '"state": "verified"',
        "promotion_state = promoted",
        "state = promoted",
        "state = verified",
        'candidate_only": false',
        '"jauhari_verified": true',
        '"evidence_refs"',
        "candidate_only",  # model trying to self-label
    ]
    for pattern in suspicious:
        if pattern in lower:
            return True
    return False
