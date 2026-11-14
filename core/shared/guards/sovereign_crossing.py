"""
arifos.core.shared.guards.sovereign_crossing

Stage-3 T1 Sovereign Crossing Enforcement:
- F13ToolAuthorityGate: T1 read-only allowlist + canonical argument hash + replay protection.
  Rejects any T2/T3 mutation with HOLD.
- MemoryAdmissionGate: ARIFOS-SOV-MEM-001 (555 MEMORY admission & read membrane).
- CrossingReceipt & SovereignReceiptChain: VAULT999-compatible hash-chained receipts.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from core.shared.guards.f12_membrane import (
    CrossingDecision,
    CrossingType,
    DataClassification,
    F12Membrane,
    PolicyOutcome,
    sha256_bytes,
)


class EpistemicClass(str, Enum):
    OBS = "OBS"
    DER = "DER"
    INT = "INT"
    SPEC = "SPEC"


class MemoryState(str, Enum):
    CANDIDATE = "CANDIDATE"
    SEALED = "SEALED"
    SUPERSEDED = "SUPERSEDED"
    CONTRADICTED = "CONTRADICTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    HOLD = "HOLD"


@dataclass(frozen=True)
class ToolAuthorizationResult:
    tool_name: str
    canonical_arguments: str
    canonical_arguments_hash: str
    actor_id: str
    user_id: str
    session_id: str
    authority_scope: str
    verdict: PolicyOutcome
    reason_code: str

    def require_execution_authority(self) -> None:
        """Enforce F13 execution authority at API boundary; independent of F12."""
        if self.verdict != PolicyOutcome.ALLOW:
            raise PermissionError(
                f"F13_EXECUTION_AUTHORITY_DENIED:{self.verdict.value}:{self.reason_code}"
            )


class F13ToolAuthorityGate:
    """
    F13 Action Authority boundary (strictly separate from F12 content screening).
    Stage 3 permits T1 read-only allowlisted tools only; T2/T3 mutations HOLD.
    """

    def __init__(self, allowed_t1_tools: frozenset[str]) -> None:
        self.allowed_t1_tools = allowed_t1_tools
        self._consumed_nonces: set[str] = set()

    @staticmethod
    def canonicalize_args(args: dict[str, Any]) -> tuple[str, str]:
        canonical = json.dumps(args or {}, sort_keys=True, separators=(",", ":"))
        return canonical, sha256_bytes(canonical)

    def authorize(
        self,
        tool_name: str,
        args: dict[str, Any] | None,
        expected_args_hash: str,
        actor_id: str,
        user_id: str,
        session_id: str,
        nonce: str,
        authority_scope: str = "T1_READ",
    ) -> ToolAuthorizationResult:
        if not isinstance(args, dict):
            return ToolAuthorizationResult(
                tool_name=tool_name,
                canonical_arguments="",
                canonical_arguments_hash="",
                actor_id=actor_id,
                user_id=user_id,
                session_id=session_id,
                authority_scope=authority_scope,
                verdict=PolicyOutcome.HOLD,
                reason_code="F13_MALFORMED_ARGS",
            )
        canonical, actual_hash = self.canonicalize_args(args)

        if not actor_id or not user_id or not session_id or user_id == "default_user":
            return ToolAuthorizationResult(
                tool_name, canonical, actual_hash, actor_id, user_id, session_id,
                authority_scope, PolicyOutcome.HOLD, "F13_IDENTITY_AMBIGUOUS",
            )
        if authority_scope != "T1_READ":
            return ToolAuthorizationResult(
                tool_name, canonical, actual_hash, actor_id, user_id, session_id,
                authority_scope, PolicyOutcome.HOLD, f"F13_T2_T3_HOLD:{authority_scope}",
            )
        if tool_name not in self.allowed_t1_tools:
            return ToolAuthorizationResult(
                tool_name, canonical, actual_hash, actor_id, user_id, session_id,
                authority_scope, PolicyOutcome.BLOCK, "F13_TOOL_NOT_ALLOWLISTED",
            )
        if not nonce or nonce in self._consumed_nonces:
            return ToolAuthorizationResult(
                tool_name, canonical, actual_hash, actor_id, user_id, session_id,
                authority_scope, PolicyOutcome.BLOCK, "F13_REPLAY_OR_EMPTY_NONCE",
            )
        if actual_hash != expected_args_hash:
            return ToolAuthorizationResult(
                tool_name, canonical, actual_hash, actor_id, user_id, session_id,
                authority_scope, PolicyOutcome.BLOCK, "F13_CANONICAL_HASH_MISMATCH",
            )

        self._consumed_nonces.add(nonce)
        return ToolAuthorizationResult(
            tool_name, canonical, actual_hash, actor_id, user_id, session_id,
            authority_scope, PolicyOutcome.ALLOW, "F13_T1_AUTHORIZED",
        )


@dataclass(frozen=True)
class MemoryCandidate:
    memory_id: str
    content: str
    actor_id: str
    user_id: str
    session_id: str
    source: str
    source_hash: str
    epistemic_class: EpistemicClass | None
    classification: DataClassification
    confidence: float | None = None
    claimed_as_obs: bool = False
    state: MemoryState = MemoryState.CANDIDATE


class MemoryAdmissionGate:
    """
    ARIFOS-SOV-MEM-001: 555 MEMORY admission & retrieval membrane.
    External memory stores are storage only; arifOS decides admission & trust.
    """

    def __init__(self, f12_membrane: F12Membrane) -> None:
        self.f12 = f12_membrane

    def admit_write(
        self,
        candidate: MemoryCandidate,
        interaction_decision: CrossingDecision,
        disclosure_approved: bool = False,
    ) -> tuple[PolicyOutcome, str, CrossingDecision | None]:
        if interaction_decision.policy_verdict != PolicyOutcome.ALLOW:
            return PolicyOutcome.BLOCK, "MEM_REJECT_BLOCKED_INTERACTION", None
        if not candidate.user_id or not candidate.session_id or candidate.user_id == "default_user":
            return PolicyOutcome.HOLD, "MEM_REJECT_IDENTITY_COLLAPSE", None
        if not candidate.source or not candidate.source_hash:
            return PolicyOutcome.HOLD, "MEM_REJECT_MISSING_PROVENANCE", None
        if candidate.epistemic_class is None:
            return PolicyOutcome.HOLD, "MEM_REJECT_UNLABELLED_EPISTEMIC", None
        if candidate.claimed_as_obs and candidate.epistemic_class in {EpistemicClass.INT, EpistemicClass.SPEC}:
            return PolicyOutcome.BLOCK, "MEM_REJECT_INT_SPEC_AS_OBS", None

        cx = self.f12.evaluate_crossing(
            text=candidate.content,
            crossing_type=CrossingType.AGENT_TO_MEMORY,
            source_domain="agent",
            destination_domain="555_memory",
            actor_id=candidate.actor_id,
            session_id=candidate.session_id,
            classification=candidate.classification,
            disclosure_approved=disclosure_approved,
        )
        if cx.policy_verdict != PolicyOutcome.ALLOW:
            return cx.policy_verdict, "MEM_REJECT_F12_CROSSING", cx
        return PolicyOutcome.ALLOW, "MEM_ADMITTED", cx

    def screen_read(
        self,
        candidate: MemoryCandidate,
        requesting_user_id: str,
        requesting_session_id: str,
        disclosure_approved: bool = False,
    ) -> tuple[PolicyOutcome, str, CrossingDecision | None]:
        if not requesting_user_id or requesting_user_id == "default_user" or candidate.user_id != requesting_user_id:
            return PolicyOutcome.BLOCK, "MEM_READ_IDENTITY_MISMATCH", None
        if candidate.state in {MemoryState.EXPIRED, MemoryState.REVOKED, MemoryState.SUPERSEDED, MemoryState.HOLD}:
            return PolicyOutcome.HOLD, f"MEM_READ_INVALID_STATE:{candidate.state.value}", None
        cx = self.f12.evaluate_crossing(
            text=candidate.content,
            crossing_type=CrossingType.MEMORY_TO_AGENT,
            source_domain="external_memory",
            destination_domain="agent",
            actor_id=requesting_user_id,
            session_id=requesting_session_id,
            classification=candidate.classification,
            disclosure_approved=disclosure_approved,
        )
        return cx.policy_verdict, f"MEM_READ_{cx.policy_verdict.value}", cx


@dataclass(frozen=True)
class CrossingReceipt:
    receipt_id: str
    previous_receipt_hash: str
    crossing_id: str
    actor_id: str
    session_id: str
    input_hash: str
    inspection_hash: str
    detector_observations: tuple[dict[str, Any], ...]
    f12_verdict: str
    f13_verdict: str | None
    canonical_argument_hash: str | None
    final_bytes_hash: str
    timestamp: str
    receipt_hash: str


class SovereignReceiptChain:
    """Hash-chained VAULT999-compatible receipt emitter (stores hashes, not raw secrets)."""

    def __init__(self, genesis_hash: str = "sha256:genesis") -> None:
        self.genesis_hash = genesis_hash
        self.tail_hash = genesis_hash
        self.entries: list[CrossingReceipt] = []

    @staticmethod
    def _compute_receipt_hash(
        receipt_id: str,
        previous_receipt_hash: str,
        crossing_id: str,
        actor_id: str,
        session_id: str,
        input_hash: str,
        inspection_hash: str,
        detector_observations: tuple[dict[str, Any], ...],
        f12_verdict: str,
        f13_verdict: str | None,
        canonical_argument_hash: str | None,
        final_bytes_hash: str,
        timestamp: str,
    ) -> str:
        payload = json.dumps(
            {
                "receipt_id": receipt_id,
                "previous_receipt_hash": previous_receipt_hash,
                "crossing_id": crossing_id,
                "actor_id": actor_id,
                "session_id": session_id,
                "input_hash": input_hash,
                "inspection_hash": inspection_hash,
                "detector_observations": list(detector_observations),
                "f12_verdict": f12_verdict,
                "f13_verdict": f13_verdict,
                "canonical_argument_hash": canonical_argument_hash,
                "final_bytes_hash": final_bytes_hash,
                "timestamp": timestamp,
            },
            sort_keys=True,
        )
        return sha256_bytes(payload)

    def emit(
        self,
        decision: CrossingDecision,
        final_bytes_hash: str,
        f13_result: ToolAuthorizationResult | None = None,
    ) -> CrossingReceipt:
        receipt_id = f"rcpt-{uuid.uuid4().hex[:12]}"
        ts = datetime.now(timezone.utc).isoformat()
        obs_summary = tuple(
            {
                "detector": o.detector,
                "provider": o.provider,
                "operation": o.operation,
                "verdict": o.verdict.value,
                "template_resource": o.template_resource,
                "template_fingerprint": o.template_fingerprint,
                "region": o.region,
                "latency_ms": o.latency_ms,
                "reason_codes": list(o.reason_codes),
            }
            for o in decision.observations
        )
        f13_v = f13_result.verdict.value if f13_result else None
        arg_h = f13_result.canonical_arguments_hash if f13_result else None
        r_hash = self._compute_receipt_hash(
            receipt_id, self.tail_hash, decision.crossing_id, decision.actor_id,
            decision.session_id, decision.content_hash, decision.inspection_hash,
            obs_summary, decision.policy_verdict.value, f13_v, arg_h, final_bytes_hash, ts,
        )
        rcpt = CrossingReceipt(
            receipt_id=receipt_id,
            previous_receipt_hash=self.tail_hash,
            crossing_id=decision.crossing_id,
            actor_id=decision.actor_id,
            session_id=decision.session_id,
            input_hash=decision.content_hash,
            inspection_hash=decision.inspection_hash,
            detector_observations=obs_summary,
            f12_verdict=decision.policy_verdict.value,
            f13_verdict=f13_v,
            canonical_argument_hash=arg_h,
            final_bytes_hash=final_bytes_hash,
            timestamp=ts,
            receipt_hash=r_hash,
        )
        self.tail_hash = r_hash
        self.entries.append(rcpt)
        return rcpt

    def verify_chain(self) -> tuple[bool, str]:
        expected_prev = self.genesis_hash
        for idx, entry in enumerate(self.entries):
            if entry.previous_receipt_hash != expected_prev:
                return False, f"CHAIN_PREV_HASH_MISMATCH_AT_{idx}"
            recomputed = self._compute_receipt_hash(
                entry.receipt_id, entry.previous_receipt_hash, entry.crossing_id,
                entry.actor_id, entry.session_id, entry.input_hash, entry.inspection_hash,
                entry.detector_observations, entry.f12_verdict, entry.f13_verdict,
                entry.canonical_argument_hash, entry.final_bytes_hash, entry.timestamp,
            )
            if entry.receipt_hash != recomputed:
                return False, f"CHAIN_RECEIPT_HASH_TAMPERED_AT_{idx}"
            expected_prev = entry.receipt_hash
        return True, "CHAIN_VERIFIED"
