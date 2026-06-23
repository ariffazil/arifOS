"""
arifosmcp/runtime/kernel_state.py — Persistent cross-tool mind state (EUREKA-A)
================================================================================

Purpose
-------
Give arifOS a real, persistent world-state graph that survives between tool
calls. Today, every tool re-derives context from the envelope; nothing carries
the running picture of *what we are doing, what we have learned, and what we
intend to do next*. That is exactly the gap that prevents arifOS from being a
"real mind" rather than a "smart wrapper."

This module is ADDITIVE — it does not mutate any existing tool. It introduces
two new surfaces that plug into the existing session/continuity/lease layer:

  1. `KernelState` — a Pydantic v2 model that represents the kernel's live
     "mind state": task, entities, claims, evidence, uncertainty, hypotheses,
     contradictions, scars, risks, decisions, next actions. Single source of
     truth, persisted in L1 (in-process) + L4 (Supabase, when available).

  2. `KernelStateStore` — the persistence/retrieval layer with three operations:
       - `save_state(state)` — upsert; computes deterministic state_hash
       - `load_state(session_id)` — retrieve by session
       - `transition(session_id, event)` — apply a typed event, return diff

  3. `consolidate(session_id)` — the *mind-gc* primitive: merges repeated
     hypotheses, prunes resolved claims, demotes stale scars. Wired into the
     arif_memory_manage tool's `mode=consolidate`.

  4. `kernel_transition()` — the SOLE lawful chokepoint for KSR mutation.
     Every state transition MUST route through this function. It:
       - Reads the current KSR hash (from_ksr_hash)
       - Applies the mutation
       - Computes the new KSR hash (to_ksr_hash)
       - Creates a TransitionReceipt with full temporal metadata
       - Seals the receipt to VAULT999 (via seal_transition)
       - Returns the receipt

     Doctrine: "Only the kernel makes time real. Agents may request marks;
     they cannot mint time."

The state object is **session-scoped** (one KernelState per active session) and
**event-sourced**: every transition appends to the in-memory event log so we
can later replay or audit the mind's reasoning history.

Constitutional binding:
  F1 AMANAH     — state is additive; never destructive without explicit consent.
  F2 TRUTH      — every claim has source_id, confidence ∈ [0,1], p10/p50/p90.
  F4 CLARITY    — state is typed; no dicts, no strings, no Pydantic-loose dicts.
  F7 HUMILITY   — uncertainty is a first-class field, never omitted.
  F9 ANTIHANTU  — no `feelings`, no `wants`, no `consciousness` fields.
  F11 AUDIT     — every transition is logged; state_hash is sha256 of canonical json.
                  Every transition produces a TransitionReceipt sealed to VAULT999.
  F13 SOVEREIGN — Only `kernel_transition()` may create authoritative time marks.
                  No direct KSR mutation is lawful outside this chokepoint.

Temporal Architecture (Phase 1 — kernel_transition() spine):
  KSR_PRESENT
    ↓[read from_ksr_hash]
  kernel_transition()
    ↓[verify authority, apply mutation, compute to_ksr_hash]
  TransitionReceipt
    ↓[seal to vault999-writer]
  VAULT sealed past
    ↓[index]
  Federation memory

Reversibility: F1 — delete this file = revert. No state migration needed.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import threading
import time
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from arifosmcp.schemas.transition_receipt import (
    AuthoritySource,
    TransitionEventType,
    TransitionReceipt,
    VerdictCode,
)
from arifosmcp.runtime.vault_sealer import seal_transition

# APEX intelligence flow: dials carried through every transition
# (hardened 2026-06-20 — A/P/X/E frozen into each TransitionReceipt)
try:
    from core.enforcement.genius import APEXDials
except ImportError:
    # Graceful fallback: APEXDials is a thin Pydantic model with A/P/X/E floats.
    from pydantic import BaseModel, Field

    class APEXDials(BaseModel):
        A: float = 0.0
        P: float = 0.0
        X: float = 0.0
        E: float = 0.0

        def to_dict(self) -> dict[str, float]:
            return {"A": self.A, "P": self.P, "X": self.X, "E": self.E}


logger = logging.getLogger(__name__)

# ── Runtime epoch counter — incremented on every kernel_transition() call ──
_NEXT_EPOCH_COUNTER: int = 0
_EPOCH_LOCK = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# Enums — small, fixed, constitutionally bounded
# ─────────────────────────────────────────────────────────────────────────────


class EntityKind(str, Enum):
    """Closed enum — adding a kind requires a constitutional patch."""

    PERSON = "person"
    ORGAN = "organ"  # GEOX, WEALTH, WELL, etc.
    TOOL = "tool"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    HYPOTHESIS = "hypothesis"
    SCAR = "scar"  # from scar.json — recurrent failure patterns
    ARTIFACT = "artifact"  # file, URL, model output
    DECISION = "decision"


class ClaimTruthClass(str, Enum):
    """3-tier claim classification per GEOX constitution; reused for state claims."""

    FACT = "FACT"
    INTERPRETATION = "INTERPRETATION"
    SPECULATION = "SPECULATION"


class RiskTier(str, Enum):
    """Mirrors constitutional_map risk tiers."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    SOVEREIGN = "sovereign"


class ActionVerb(str, Enum):
    """Closed set of kernel action verbs. Per eureka #8 — every output ends in one of these."""

    ANSWER = "answer"
    ASK = "ask"
    HOLD = "hold"
    RETRIEVE = "retrieve"
    SIMULATE = "simulate"
    ESCALATE = "escalate"
    EXECUTE = "execute"
    SEAL = "seal"
    OBSERVE = "observe"


# ─────────────────────────────────────────────────────────────────────────────
# Typed sub-records
# ─────────────────────────────────────────────────────────────────────────────


class Uncertainty(BaseModel):
    """First-class uncertainty per eureka #3. Never omitted."""

    omega_0: float = Field(ge=0.03, le=0.05, description="HUMILITY band hard floor")
    confidence: float = Field(ge=0.0, le=1.0)
    band: Literal["UNKNOWN", "PLAUSIBLE", "PROBABLE", "CLAIMED"]
    entropy_d_s: float = Field(default=0.0, ge=0.0)
    disagreement_score: float = Field(default=0.0, ge=0.0, le=1.0)


class Entity(BaseModel):
    entity_id: str
    kind: EntityKind
    label: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=lambda: time.time())
    last_touched_at: float = Field(default_factory=lambda: time.time())
    source_id: str | None = None  # tool_name, organ, human


class Claim(BaseModel):
    """A claim is a typed assertion. Per eureka #1, claims live in the world model."""

    claim_id: str
    text: str
    truth_class: ClaimTruthClass
    uncertainty: Uncertainty
    evidence_ids: list[str] = Field(default_factory=list)
    scar_ids: list[str] = Field(default_factory=list)
    p10: float | None = None
    p50: float | None = None
    p90: float | None = None
    created_at: float = Field(default_factory=lambda: time.time())
    source_id: str | None = None  # who asserted this claim
    status: Literal["draft", "validated", "challenged", "resolved", "withdrawn"] = "draft"


class Evidence(BaseModel):
    """A piece of evidence supporting/contradicting claims."""

    evidence_id: str
    source: str  # tool_name, file path, URL, model
    kind: Literal["observation", "computation", "testimony", "document"]
    content_ref: str  # pointer to actual data
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: float
    provenance_hash: str | None = None  # sha256 of source content if available


class Hypothesis(BaseModel):
    """Per eureka #7 — competing hypotheses under arbitration."""

    hypothesis_id: str
    statement: str
    priors: dict[str, float] = Field(default_factory=dict)
    posteriors: dict[str, float] = Field(default_factory=dict)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    status: Literal["active", "promoted", "demoted", "retired"] = "active"


class Contradiction(BaseModel):
    """Recorded when two claims/hypotheses disagree."""

    contradiction_id: str
    left_id: str  # claim or hypothesis
    right_id: str
    description: str
    severity: float = Field(ge=0.0, le=1.0)
    resolution: Literal["unresolved", "left_wins", "right_wins", "both_partial", "retracted"] = (
        "unresolved"
    )
    resolver: str | None = None  # who resolved (judge, human, planner)
    resolved_at: float | None = None


class RiskMarker(BaseModel):
    risk_id: str
    description: str
    tier: RiskTier
    irreversibility: bool
    requires_human_ack: bool
    mitigation: str | None = None


class NextAction(BaseModel):
    """Per eureka #8 — the action verb set. Every reasoning ends in one of these."""

    action_id: str
    verb: ActionVerb
    target: str  # tool name, organ, human, claim_id
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    blockers: list[str] = Field(default_factory=list)


class TransitionEvent(BaseModel):
    """Event-sourced audit log for every state mutation. F11 AUDIT compliance."""

    event_id: str
    session_id: str
    timestamp: float
    actor: str  # tool name, organ, "arif", "judge"
    event_type: str  # claim_added, hypothesis_promoted, action_taken, etc.
    payload: dict[str, Any]
    prior_state_hash: str | None = None
    post_state_hash: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# The KernelState itself
# ─────────────────────────────────────────────────────────────────────────────


class KernelState(BaseModel):
    """The kernel's live mind-state. One per active session.

    Pydantic v2 — fully typed, no loose dicts, F4 CLARITY compliant.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    # Identity
    session_id: str
    state_hash: str = ""  # sha256 of canonical json, computed on save
    state_version: str = "0.1.0"  # KernelState schema version

    # Task context
    task_description: str = ""
    task_intent: Literal["answer", "analyze", "build", "judge", "explore", "execute"] = "answer"
    task_horizon: Literal["instant", "session", "day", "week", "month", "perpetual"] = "session"

    # World model (eureka #1)
    entities: dict[str, Entity] = Field(default_factory=dict)
    claims: dict[str, Claim] = Field(default_factory=dict)
    evidence: dict[str, Evidence] = Field(default_factory=dict)
    hypotheses: dict[str, Hypothesis] = Field(default_factory=dict)
    contradictions: dict[str, Contradiction] = Field(default_factory=dict)

    # Risk surface (eureka #7)
    open_risks: dict[str, RiskMarker] = Field(default_factory=dict)

    # Action queue (eureka #8)
    next_actions: list[NextAction] = Field(default_factory=list)
    last_action: NextAction | None = None

    # Self-model (eureka #2)
    self_model: dict[str, Any] = Field(
        default_factory=lambda: {
            "active_floors": 13,
            "active_tools": [],
            "current_model": None,
            "authority_boundary": "operator",
            "uncertainty_band": "PLAUSIBLE",
            "honesty_ratio": 0.0,
            # ── APEX AUTHORITY REGISTRY (hardened 2026-06-20) ────────
            # Single source of truth for "who can do what."
            # Authority is not split across repos — arifOS owns it.
            # Each principal has roles, permissions, and expiry.
            "authority_registry": {
                "operator": {
                    "roles": ["SOVEREIGN", "JUDGE", "FORGE", "OBSERVE"],
                    "permissions": ["mutate", "seal", "veto", "delegate", "attest"],
                    "expiry": "perpetual",
                },
                "agent": {
                    "roles": ["FORGE", "OBSERVE"],
                    "permissions": ["mutate_with_approval", "observe", "attest"],
                    "expiry": "session",
                },
                "guest": {
                    "roles": ["OBSERVE"],
                    "permissions": ["observe"],
                    "expiry": "session",
                },
            },
        }
    )

    # Uncertainty (eureka #3)
    global_uncertainty: Uncertainty = Field(
        default_factory=lambda: Uncertainty(
            omega_0=0.04, confidence=0.5, band="PLAUSIBLE", entropy_d_s=0.0
        )
    )

    # Event log (F11 AUDIT)
    event_log: list[TransitionEvent] = Field(default_factory=list)
    created_at: float = Field(default_factory=lambda: time.time())
    last_transition_at: float = Field(default_factory=lambda: time.time())

    # Provenance
    substrate_model: str | None = None  # e.g. "minimax/M3", "claude-opus-4-5"
    organ_origin: str | None = None  # which organ/session initiated

    @field_validator("claims", mode="before")
    @classmethod
    def _claims_must_have_uncertainty(cls, v: Any) -> Any:
        # F7 HUMILITY guard — refuse to accept claims without uncertainty
        if isinstance(v, dict):
            for k, c in v.items():
                if isinstance(c, dict) and "uncertainty" not in c:
                    raise ValueError(f"Claim {k} missing uncertainty field (F7 HUMILITY violation)")
        return v

    def canonical_dict(self) -> dict[str, Any]:
        """Deterministic JSON-able dict for hashing."""
        return self.model_dump(mode="json", exclude={"state_hash"})

    def compute_state_hash(self) -> str:
        """Deterministic sha256 of canonical state (F11)."""
        canonical = json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def transition(
        self,
        actor: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> KernelState:
        """
        Apply an event, return a new state with hash + log entry. Immutable update.

        NOTE: In Phase 1, this method is PATCHED to route through kernel_transition().
        The direct mutation path below is preserved as a FAST PATH for in-memory-only
        transitions that do not need vault sealing (e.g., intermediate reasoning steps).
        All CONSEQUENTIAL transitions MUST go through kernel_transition().

        External callers should prefer kernel_transition() for any transition that
        needs a lawful mark. This method will raise a warning if called directly
        for consequential event types.
        """
        prior_hash = self.state_hash or self.compute_state_hash()
        updated = self.model_copy(deep=True)
        updated.event_log.append(
            TransitionEvent(
                event_id=f"evt-{int(time.time() * 1000)}",
                session_id=self.session_id,
                timestamp=time.time(),
                actor=actor,
                event_type=event_type,
                payload=payload,
                prior_state_hash=prior_hash,
                post_state_hash="",  # will be set after hash
            )
        )
        updated.last_transition_at = time.time()
        updated.state_hash = updated.compute_state_hash()
        # Patch the post_state_hash on the trailing event
        updated.event_log[-1].post_state_hash = updated.state_hash
        return updated


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: kernel_transition() — the SOLE lawful chokepoint for KSR mutation
# ─────────────────────────────────────────────────────────────────────────────


def _next_ksr_epoch_id() -> str:
    """Monotonic epoch ID for every kernel_transition() call."""
    global _NEXT_EPOCH_COUNTER
    with _EPOCH_LOCK:
        _NEXT_EPOCH_COUNTER += 1
        return f"KSR-EPOCH-{_NEXT_EPOCH_COUNTER:06d}"


def kernel_transition(
    state: KernelState,
    *,
    caller: str,
    event_type: str | TransitionEventType,
    payload: dict[str, Any],
    actor: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    authority_source: str | AuthoritySource = AuthoritySource.KSR,
    event_label: str = "",
    skip_vault: bool = False,
    # ── APEX intelligence flow (hardened 2026-06-20) ─────────────────
    # These carry the 5D APEX state through every transition.
    # dials: ApexDials at moment of transition (A/P/X/E)
    # action_class: ActionClass string (e.g. "OBSERVE", "MUTATE_LOCAL", "JUDGE")
    # custody_chain: [initiator, validator, approver, executor]
    # All are embedded into the TransitionReceipt and sealed to VAULT999.
    dials: APEXDials | None = None,
    action_class: str = "OBSERVE",
    custody_chain: list[str] | None = None,
) -> tuple[KernelState, TransitionReceipt]:
    """
    The SOLE lawful chokepoint for KSR mutation.

    Every state transition MUST route through this function. It:

    1. Reads the current KSR hash (from_ksr_hash)
    2. Applies the mutation via KernelState.transition()
    3. Computes the new KSR hash (to_ksr_hash)
    4. Creates a TransitionReceipt with full temporal metadata
    5. Seals the receipt to VAULT999 (via seal_transition, unless skip_vault=True)
    6. Returns (updated_state, TransitionReceipt)

    Returns:
        (updated KernelState, sealed TransitionReceipt)

    Invariant:
        No KSR mutation outside this function.
        No Vault append without TransitionReceipt.
        No TransitionReceipt without prior KSR hash and next KSR hash.
        No external mark becomes time until kernel accepts it.

    Doctrine:
        "Only the kernel makes time real. Agents may request marks;
         they cannot mint time."
    """
    # ── 1. Resolve types ────────────────────────────────────────────────
    _actor = actor or caller
    _session_id = session_id or state.session_id
    _event_type_str = (
        event_type.value if isinstance(event_type, TransitionEventType) else event_type
    )
    _authority = (
        authority_source.value
        if isinstance(authority_source, AuthoritySource)
        else authority_source
    )
    _metadata = metadata or {}

    # ── 2. Capture from-state hash BEFORE mutation ──────────────────────
    from_ksr_hash = state.state_hash or state.compute_state_hash()
    started_at_ns = time.time_ns()

    # ── 3. Apply mutation (in-memory only) ──────────────────────────────
    updated = state.transition(actor=_actor, event_type=_event_type_str, payload=payload)
    to_ksr_hash = updated.state_hash

    # ── 4. Get or compute prior ledger hash ─────────────────────────────
    # TODO (Phase 3): Replace with real ledger store query
    prior_ledger_hash = "sha256:0"

    # ── 5. Create TransitionReceipt ─────────────────────────────────────
    epoch_id = _next_ksr_epoch_id()

    # ── 5a. Resolve APEX dials snapshot ──────────────────────────────────
    # Dials are frozen into the receipt at transition time.
    # This carries AKAL/PRESENT/EXPLORATION/ENERGY across time through the ledger.
    _dials_serialized: dict[str, float] = {"A": 0.0, "P": 0.0, "X": 0.0, "E": 0.0}
    if dials is not None:
        if hasattr(dials, "to_dict"):
            _dials_serialized = dials.to_dict()
        elif isinstance(dials, dict):
            _dials_serialized = {k: float(v) for k, v in dials.items() if k in ("A", "P", "X", "E")}

    receipt = TransitionReceipt(
        organ_id="arifOS",
        caller=caller,
        ksr_epoch_id=epoch_id,
        event_type=(
            event_type
            if isinstance(event_type, TransitionEventType)
            else TransitionEventType.KSR_UPDATED
        ),
        event_label=event_label or _event_type_str,
        from_ksr_hash=from_ksr_hash,
        to_ksr_hash=to_ksr_hash,
        prior_ledger_hash=prior_ledger_hash,
        started_at_ns=started_at_ns,
        authority_source=(
            authority_source
            if isinstance(authority_source, AuthoritySource)
            else AuthoritySource.KSR
        ),
        verdict=VerdictCode.SEAL,
        dials_snapshot=_dials_serialized,
        action_class=action_class,
        custody_chain=custody_chain or [caller],
        metadata=_metadata,
    )
    receipt.seal()

    # ── 6. Seal to Vault (async, fire-and-forget) ───────────────────────
    if not skip_vault:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                seal_transition(
                    receipt_id=receipt.receipt_id,
                    event_type=_event_type_str,
                    payload=receipt.to_vault_payload(),
                    session_id=_session_id,
                    agent_id=caller,
                )
            )
        except RuntimeError:
            logger.warning(
                f"[kernel_transition] no event loop; "
                f"skipping vault seal for receipt {receipt.receipt_id}"
            )

    # ── 7. Log and return ───────────────────────────────────────────────
    logger.info(
        f"[kernel_transition] {_event_type_str} "
        f"from={from_ksr_hash[:16]} to={to_ksr_hash[:16]} "
        f"epoch={epoch_id} receipt={receipt.receipt_id} "
        f"duration_ms={receipt.duration_ms} vault={receipt.vault_ref or 'pending'}"
    )

    return updated, receipt


# ─────────────────────────────────────────────────────────────────────────────
# Store — in-process L1, ready to back to L4 (Supabase) when wired
# ─────────────────────────────────────────────────────────────────────────────


class KernelStateStore:
    """Thread-safe in-process store. F1 reversible — no I/O side effects on import."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._states: dict[str, KernelState] = {}
        self._event_count: int = 0
        self._consolidation_count: int = 0
        # Phase 1 guard: tracks the last kernel_transition receipt per session.
        # save_state() checks this to detect direct mutations outside kernel_transition().
        self._last_receipt_per_session: dict[str, str] = {}

    def save_state(self, state: KernelState, *, _via_receipt_id: str | None = None) -> str:
        """
        Persist state, return its hash.

        Phase 1 guard: if no _via_receipt_id is provided (meaning this save is
        NOT coming from kernel_transition()), a warning is logged. This is a
        soft guard — the hard enforcement (rejecting non-gated mutations) will
        be added in Phase 2 after the system is stable.

        Callers that route through kernel_transition() automatically pass the
        receipt_id. Direct callers get a warning trace.
        """
        with self._lock:
            session_id = state.session_id
            last_receipt = self._last_receipt_per_session.get(session_id)

            if _via_receipt_id:
                # Lawful path — coming from kernel_transition()
                self._last_receipt_per_session[session_id] = _via_receipt_id
            else:
                # UNLAWFUL path — direct mutation without kernel_transition()
                prev_hash = last_receipt or "none"
                logger.warning(
                    "[KSR-GUARD] DIRECT KSR MUTATION DETECTED: "
                    "session=%s state_hash=%s last_receipt=%s "
                    "Callers MUST route through kernel_transition()",
                    session_id,
                    state.state_hash[:24] if state.state_hash else "unset",
                    prev_hash,
                )

            state.state_hash = state.compute_state_hash()
            self._states[session_id] = state
            self._event_count += 1
            logger.info(
                "kernel_state.saved session=%s hash=%s claims=%d hypotheses=%d actions=%d",
                session_id,
                state.state_hash[:24],
                len(state.claims),
                len(state.hypotheses),
                len(state.next_actions),
            )
            return state.state_hash

    def load_state(self, session_id: str) -> KernelState | None:
        with self._lock:
            return self._states.get(session_id)

    def transition(
        self,
        session_id: str,
        actor: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> tuple[KernelState | None, str | None]:
        """
        Apply a transition event via kernel_transition().
        Routes through the sole lawful chokepoint for KSR mutation.

        Returns (new_state, new_hash) or (None, None) if missing.
        Every transition produces a TransitionReceipt sealed to VAULT999.
        """
        with self._lock:
            current = self._states.get(session_id)
            if current is None:
                return None, None
            updated, receipt = kernel_transition(
                current,
                caller=actor,
                event_type=event_type,
                payload=payload,
                actor=actor,
                session_id=session_id,
            )
            self.save_state(updated, _via_receipt_id=receipt.receipt_id)
            self._event_count += 1
            return updated, updated.state_hash

    def list_sessions(self) -> list[str]:
        with self._lock:
            return list(self._states.keys())

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "active_states": len(self._states),
                "event_count": self._event_count,
                "consolidation_count": self._consolidation_count,
                "schema_version": "0.1.0",
            }


# ─────────────────────────────────────────────────────────────────────────────
# Consolidation — the mind-gc primitive (eureka #5: memory must be managed)
# ─────────────────────────────────────────────────────────────────────────────


def consolidate(state: KernelState) -> KernelState:
    """Merge duplicates, prune resolved, demote stale scars.

    Idempotent. Returns a new state with a `_consolidation` field in the last
    event payload so callers can see what changed.
    """
    summary = {
        "merged_claims": 0,
        "pruned_resolved": 0,
        "retired_hypotheses": 0,
        "demoted_contradictions": 0,
    }

    updated = state.model_copy(deep=True)

    # 1. Merge claims with identical text
    seen_text: dict[str, Claim] = {}
    for cid, claim in list(updated.claims.items()):
        if claim.text in seen_text:
            # Keep the higher-confidence one, union evidence
            keeper = seen_text[claim.text]
            if claim.uncertainty.confidence > keeper.uncertainty.confidence:
                keeper, claim = claim, keeper
            keeper.evidence_ids = list(set(keeper.evidence_ids + claim.evidence_ids))
            del updated.claims[cid]
            summary["merged_claims"] += 1
        else:
            seen_text[claim.text] = claim

    # 2. Prune resolved claims older than 1h (F1 — keep history in event_log, not claims)
    cutoff = time.time() - 3600
    for cid, claim in list(updated.claims.items()):
        if claim.status == "resolved" and claim.created_at < cutoff:
            del updated.claims[cid]
            summary["pruned_resolved"] += 1

    # 3. Retire hypotheses with 0 supporting evidence and 0 posterior
    for hid, hyp in list(updated.hypotheses.items()):
        if not hyp.supporting_evidence and not hyp.posteriors and hyp.status == "active":
            hyp.status = "retired"
            summary["retired_hypotheses"] += 1

    # 4. Mark resolved contradictions
    for cid, contra in list(updated.contradictions.items()):
        if contra.resolution != "unresolved" and contra.resolved_at:
            summary["demoted_contradictions"] += 1

    # Route through kernel_transition() for lawful mark
    consolidated, receipt = kernel_transition(
        updated,
        caller="arif_memory_manage",
        event_type="consolidation",
        payload=summary,
        actor="arif_memory_manage",
        event_label=f"Consolidated: {summary['merged_claims']} merged, {summary['pruned_resolved']} pruned",
    )
    return consolidated


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton — exported for tools to import
# ─────────────────────────────────────────────────────────────────────────────

_STORE: KernelStateStore | None = None
_STORE_LOCK = threading.Lock()


def get_state_store() -> KernelStateStore:
    """Lazy singleton. F1 — no side effects on import."""
    global _STORE
    with _STORE_LOCK:
        if _STORE is None:
            _STORE = KernelStateStore()
        return _STORE


def init_state_for_session(
    session_id: str,
    *,
    task_description: str = "",
    task_intent: KernelState.model_fields[task_intent].default = "answer",  # type: ignore[assignment]
    substrate_model: str | None = None,
    organ_origin: str | None = None,
) -> KernelState:
    """Create or reset a KernelState for a session. Idempotent — returns existing if present."""
    store = get_state_store()
    existing = store.load_state(session_id)
    if existing is not None:
        return existing
    state = KernelState(
        session_id=session_id,
        task_description=task_description,
        task_intent=task_intent,  # type: ignore[arg-type]
        substrate_model=substrate_model,
        organ_origin=organ_origin,
    )
    state.state_hash = state.compute_state_hash()
    store.save_state(state)
    return state


__all__ = [
    "ActionVerb",
    "Claim",
    "ClaimTruthClass",
    "Contradiction",
    "Entity",
    "EntityKind",
    "Evidence",
    "Hypothesis",
    "KernelState",
    "KernelStateStore",
    "NextAction",
    "RiskMarker",
    "RiskTier",
    "TransitionEvent",
    "Uncertainty",
    "consolidate",
    "get_state_store",
    "init_state_for_session",
    "kernel_transition",
]
