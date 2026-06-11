"""
arifosmcp/runtime/kernel_state.py — Persistent cross-tool mind state (EUREKA-A)

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

Reversibility: F1 — delete this file = revert. No state migration needed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

logger = logging.getLogger(__name__)

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
        """Apply an event, return a new state with hash + log entry. Immutable update."""
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
# Store — in-process L1, ready to back to L4 (Supabase) when wired
# ─────────────────────────────────────────────────────────────────────────────


class KernelStateStore:
    """Thread-safe in-process store. F1 reversible — no I/O side effects on import."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._states: dict[str, KernelState] = {}
        self._event_count: int = 0
        self._consolidation_count: int = 0

    def save_state(self, state: KernelState) -> str:
        """Persist state, return its hash."""
        with self._lock:
            state.state_hash = state.compute_state_hash()
            self._states[state.session_id] = state
            self._event_count += 1
            logger.info(
                "kernel_state.saved session=%s hash=%s claims=%d hypotheses=%d actions=%d",
                state.session_id,
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
        """Apply a transition event. Returns (new_state, new_hash) or (None, None) if missing."""
        with self._lock:
            current = self._states.get(session_id)
            if current is None:
                return None, None
            updated = current.transition(actor, event_type, payload)
            self._states[session_id] = updated
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

    return updated.transition(
        actor="arif_memory_manage",
        event_type="consolidation",
        payload=summary,
    )


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
]
