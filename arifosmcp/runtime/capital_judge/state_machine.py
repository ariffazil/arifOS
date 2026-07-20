"""
PR5 — State machine and core data types for the Capital Judge.

State diagram (audit-4):

  RECEIVED → AUTHENTICATED → VALIDATED → COMPUTED → JUDGED
                                                     │
                                                     ├─ DENY → TERMINATED
                                                     │
                                                     ├─ HOLD → returns to JUDGED with active_holds
                                                     │
                                                     └─ PROCEED + ratification_required
                                                          │
                                                          ▼
                                                          HUMAN_HOLD ──→ RATIFIED
                                                          │
                                                          ▼
                                                          SEALED → EXECUTED (only via A-FORGE)
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class State(str, Enum):
    RECEIVED = "RECEIVED"
    AUTHENTICATED = "AUTHENTICATED"
    VALIDATED = "VALIDATED"
    COMPUTED = "COMPUTED"
    JUDGED = "JUDGED"
    HUMAN_HOLD = "HUMAN_HOLD"
    RATIFIED = "RATIFIED"
    SEALED = "SEALED"
    EXECUTED = "EXECUTED"
    TERMINATED = "TERMINATED"

    def __str__(self) -> str:
        return self.value


# Legal transitions. Anything not in this set raises TransitionError.
_LEGAL_TRANSITIONS: dict[State, set[State]] = {
    State.RECEIVED: {State.AUTHENTICATED, State.TERMINATED},
    State.AUTHENTICATED: {State.VALIDATED, State.TERMINATED},
    State.VALIDATED: {State.COMPUTED, State.TERMINATED},
    State.COMPUTED: {State.JUDGED, State.TERMINATED},
    State.JUDGED: {State.HUMAN_HOLD, State.TERMINATED, State.SEALED, State.RATIFIED},
    State.HUMAN_HOLD: {State.RATIFIED, State.TERMINATED},
    State.RATIFIED: {State.SEALED, State.TERMINATED},
    State.SEALED: {State.EXECUTED, State.TERMINATED},
    State.EXECUTED: set(),  # terminal
    State.TERMINATED: set(),  # terminal
}


class TransitionError(Exception):
    """Raised when an orchestrator attempts an illegal transition."""

    def __init__(self, frm: State, to: State, reason: str = ""):
        self.from_state = frm
        self.to_state = to
        self.reason = reason
        super().__init__(f"Illegal transition {frm.value} → {to.value}: {reason}")


def _hash(value: Any) -> str:
    try:
        canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        canonical = str(value)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class CapitalCase:
    """A typed capital case the audit mandates."""

    case_id: str
    actor: dict[str, Any]
    purpose: dict[str, Any]
    valuation: dict[str, Any]
    inputs: dict[str, Any]
    evidence: dict[str, Any] = field(default_factory=dict)
    governance: dict[str, Any] = field(default_factory=dict)
    expected_outputs: dict[str, Any] = field(default_factory=dict)
    issuer: str = "arifOS"  # F13 binding: the kernel is the issuer
    trace_id: str = field(default_factory=lambda: f"trc-{uuid.uuid4().hex[:12]}")


@dataclass
class Receipt:
    """Generic receipt — one of the four audit-mandated types."""

    receipt_type: str
    data: dict[str, Any]
    emitted_at: str = field(default_factory=_now)

    def hash(self) -> str:
        return _hash(self.data)


class StateMachine:
    """Strict, queryable state machine. Every transition emits a receipt."""

    def __init__(self, case: CapitalCase) -> None:
        self.case = case
        self.state: State = State.RECEIVED
        self.receipts: list[Receipt] = []
        self._seen_states: set[State] = {State.RECEIVED}

    def transition(self, to: State, *, receipt: Receipt | None = None, reason: str = "") -> State:
        """Apply `to` if it is a legal transition from the current state.

        Raises TransitionError on any illegal move. Records `receipt` to the
        per-case log; the orchestrator is responsible for emitting externally.
        """
        legal = _LEGAL_TRANSITIONS.get(self.state, set())
        if to not in legal:
            raise TransitionError(self.state, to, reason=reason or "not in legal transition set")
        self.state = to
        self._seen_states.add(to)
        if receipt is not None:
            self.receipts.append(receipt)
        return self.state

    def can_transition_to(self, to: State) -> bool:
        return to in _LEGAL_TRANSITIONS.get(self.state, set())

    def legal_next_states(self) -> set[State]:
        return set(_LEGAL_TRANSITIONS.get(self.state, set()))

    def has_receipt_type(self, receipt_type: str) -> bool:
        return any(r.receipt_type == receipt_type for r in self.receipts)
