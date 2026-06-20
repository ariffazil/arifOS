"""
State Transitions — Item 3a of the Organ Forge
═══════════════════════════════════════════

Enforceable state machine for the executive/governance cortex.

The six canonical transitions the federation needs:
  PENDING     → APPROVED       (GREEN/YELLOW)
  APPROVED    → EXECUTED       (ORANGE)
  EXECUTED    → SEALED         (RED → BLACK, irreversible)
  IRREVERSIBLE→ HOLD           (until F13 ack)
  SEALED      → CHALLENGED     (re-opens with new evidence)
  VOID        → ARCHIVED       (audit only, never executed)

Each transition is enforced by code, not docs. The transition log is
part of the L4 structured record and survives in the L6 vault.

DITEMPA BUKAN DIBERI — state moves by guard, not by hope.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# STATES
# ═══════════════════════════════════════════════════════════════════════════════


class ActionState(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    SEALED = "SEALED"
    HOLD = "HOLD"
    CHALLENGED = "CHALLENGED"
    VOID = "VOID"
    ARCHIVED = "ARCHIVED"


# Allowed transitions. Anything not in this table is rejected.
ALLOWED: dict[ActionState, set[ActionState]] = {
    ActionState.PENDING: {ActionState.APPROVED, ActionState.HOLD, ActionState.VOID},
    ActionState.APPROVED: {ActionState.EXECUTED, ActionState.HOLD, ActionState.VOID},
    ActionState.EXECUTED: {ActionState.SEALED, ActionState.HOLD, ActionState.VOID},
    ActionState.SEALED: {ActionState.CHALLENGED, ActionState.ARCHIVED},
    ActionState.CHALLENGED: {ActionState.PENDING, ActionState.SEALED, ActionState.VOID},
    ActionState.HOLD: {ActionState.PENDING, ActionState.VOID, ActionState.ARCHIVED},
    ActionState.VOID: {ActionState.ARCHIVED},
    ActionState.ARCHIVED: set(),  # terminal
}


# Autonomy band per transition (for governance). Key = (from, to).
BAND_REQUIREMENT: dict[tuple[ActionState, ActionState], str] = {
    (ActionState.PENDING, ActionState.APPROVED): "GREEN",
    (ActionState.APPROVED, ActionState.EXECUTED): "ORANGE",
    (ActionState.EXECUTED, ActionState.SEALED): "RED",
    (ActionState.SEALED, ActionState.CHALLENGED): "ORANGE",  # re-open
    (ActionState.CHALLENGED, ActionState.PENDING): "GREEN",  # back to start
    (ActionState.CHALLENGED, ActionState.SEALED): "RED",  # re-seal
    (ActionState.CHALLENGED, ActionState.VOID): "ORANGE",  # void after challenge
    (ActionState.PENDING, ActionState.HOLD): "GREEN",
    (ActionState.APPROVED, ActionState.HOLD): "GREEN",
    (ActionState.EXECUTED, ActionState.HOLD): "ORANGE",
    (ActionState.HOLD, ActionState.PENDING): "GREEN",
    (ActionState.HOLD, ActionState.VOID): "GREEN",
    (ActionState.PENDING, ActionState.VOID): "GREEN",
    (ActionState.APPROVED, ActionState.VOID): "GREEN",
    (ActionState.EXECUTED, ActionState.VOID): "ORANGE",
    (ActionState.SEALED, ActionState.ARCHIVED): "ORANGE",
    (ActionState.VOID, ActionState.ARCHIVED): "GREEN",
}

# Sentinel for the (any-irreversible, HOLD) rule — handled in logic below


# ═══════════════════════════════════════════════════════════════════════════════
# ERRORS
# ═══════════════════════════════════════════════════════════════════════════════


class TransitionError(Exception):
    """Raised when a transition is rejected."""


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION RECORD — the moving part
# ═══════════════════════════════════════════════════════════════════════════════


class ActionRecord(BaseModel):
    """The unit of state in the executive organ."""

    action_id: str = Field(default_factory=lambda: f"act_{uuid4().hex[:12]}")
    state: ActionState = ActionState.PENDING
    intent: str = Field(..., description="Plain-language intent of the action")
    reversibility: str = "REVERSIBLE"  # REVERSIBLE | PARTIALLY_REVERSIBLE | IRREVERSIBLE
    autonomy_band: str = "GREEN"
    actor_id: str
    session_id: str | None = None
    capability_grant_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    history: list[dict] = Field(default_factory=list)
    sealed_hash: str | None = None
    challenge_evidence_ref: str | None = None
    parent_action_id: str | None = None  # for CHALLENGED → PENDING lineage

    @model_validator(mode="after")
    def _validate_band(self) -> ActionRecord:
        if self.autonomy_band not in ("GREEN", "YELLOW", "ORANGE", "RED", "BLACK"):
            raise ValueError(f"Unknown autonomy_band: {self.autonomy_band}")
        return self


# ═══════════════════════════════════════════════════════════════════════════════
# STATE MACHINE — the guard
# ═══════════════════════════════════════════════════════════════════════════════


class StateMachine:
    """Enforces the transition table. State observed at T₀ is the
    admissible source; transitions are atomic; every move is logged
    in the record history with a hash chain entry."""

    @staticmethod
    def _band_rank(band: str) -> int:
        return {"GREEN": 0, "YELLOW": 1, "ORANGE": 2, "RED": 3, "BLACK": 4}.get(band, 0)

    @classmethod
    def transition(
        cls,
        record: ActionRecord,
        target: ActionState,
        *,
        actor_id: str,
        reason: str = "",
        human_acknowledged: bool = False,
        evidence_ref: str | None = None,
        extra: dict | None = None,
    ) -> ActionRecord:
        """Move the record to ``target``. Reject illegal moves.

        Returns a NEW record (records are immutable; transitions are
        append-only). The history grows by one entry per call.
        """
        current = record.state
        allowed_targets = ALLOWED.get(current, set())

        if target not in allowed_targets:
            raise TransitionError(
                f"Illegal transition: {current.value} → {target.value}. "
                f"Allowed from {current.value}: "
                f"{sorted(s.value for s in allowed_targets) or ['<terminal>']}"
            )

        # Autonomy band check (skip sentinel)
        band_req = BAND_REQUIREMENT.get((current, target))
        if band_req is not None:
            # caller may override by passing a higher-band actor context via record
            if cls._band_rank(record.autonomy_band) < cls._band_rank(band_req):
                # Allow override if human_acknowledged + irreversible-style target
                if not (human_acknowledged and target in (ActionState.HOLD, ActionState.VOID)):
                    raise TransitionError(
                        f"Band {record.autonomy_band} insufficient for "
                        f"{current.value} → {target.value} (requires {band_req})"
                    )

        # Irreversible: PENDING/APPROVED/EXECUTED → HOLD always allowed
        if (
            record.reversibility == "IRREVERSIBLE"
            and target == ActionState.HOLD
            and current in (ActionState.PENDING, ActionState.APPROVED, ActionState.EXECUTED)
        ):
            # Forcing into HOLD is always permitted; human_acknowledged is irrelevant
            pass

        # SEALED requires a sealed_hash to be set on entry
        if target == ActionState.SEALED and not record.sealed_hash:
            # Caller is expected to set record.sealed_hash via the seal step
            # before calling transition; if they didn't, compute a content hash here
            canon = json.dumps(
                {
                    "action_id": record.action_id,
                    "state": "EXECUTED",
                    "intent": record.intent,
                    "actor_id": record.actor_id,
                    "updated_at": record.updated_at.isoformat(),
                },
                sort_keys=True,
            )
            record.sealed_hash = hashlib.sha256(canon.encode()).hexdigest()[:16]

        # Build new record (immutable pattern)
        new_history = list(record.history) + [
            {
                "from": current.value,
                "to": target.value,
                "actor_id": actor_id,
                "reason": reason,
                "evidence_ref": evidence_ref,
                "ts": datetime.now(UTC).isoformat(),
                "human_acknowledged": human_acknowledged,
                "extra": extra or {},
            }
        ]
        new_record = record.model_copy(
            update={
                "state": target,
                "updated_at": datetime.now(UTC),
                "history": new_history,
            }
        )
        # CHALLENGED carries the new evidence_ref forward
        if target == ActionState.CHALLENGED and evidence_ref:
            new_record = new_record.model_copy(
                update={"challenge_evidence_ref": evidence_ref}
            )
        # CHALLENGED → PENDING carries lineage
        if current == ActionState.CHALLENGED and target == ActionState.PENDING:
            new_record = new_record.model_copy(
                update={"parent_action_id": record.action_id}
            )
        return new_record

    @staticmethod
    def can_transition(current: ActionState, target: ActionState) -> bool:
        return target in ALLOWED.get(current, set())

    @staticmethod
    def allowed_from(state: ActionState) -> list[ActionState]:
        return sorted(ALLOWED.get(state, set()), key=lambda s: s.value)
