"""
cooling_verbs.py — P1.4 Cooling lifecycle verbs for the metabolism loop.

Cooling is how arifOS learns from failure. Each verb is a lifecycle state,
not an equivalent authority level.

Autonomous (no ceremony needed):
  - cooling.observe    — detect and record a failure/symptom
  - cooling.diagnose   — analyze root cause
  - cooling.propose    — suggest a fix

Gated (require approval or ceremony):
  - cooling.approve    — human/constitutional approval of proposal
  - cooling.install    — apply the fix (requires A-FORGE capability)
  - cooling.receipt    — seal the cooling event to VAULT999

Conditional:
  - cooling.verify     — read-only verification (autonomous) vs mutation (gated)
  - cooling.decay      — record that a cooling proposal expired/was superseded

The flow:
  failure → observe → diagnose → propose → [approve] → install → verify → receipt

Decay happens when a proposal is superseded or times out.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CoolingVerb(str, Enum):
    OBSERVE = "cooling.observe"
    DIAGNOSE = "cooling.diagnose"
    PROPOSE = "cooling.propose"
    APPROVE = "cooling.approve"
    INSTALL = "cooling.install"
    VERIFY = "cooling.verify"
    RECEIPT = "cooling.receipt"
    DECAY = "cooling.decay"


class CoolingAuthority(str, Enum):
    """Authority level required for each verb."""

    AUTONOMOUS = "autonomous"  # No ceremony needed
    GATED = "gated"  # Requires approval
    CEREMONY = "ceremony"  # Requires sovereign ceremony
    CONDITIONAL = "conditional"  # Depends on read vs write


# Authority mapping: which verbs need what level of approval
VERB_AUTHORITY: dict[CoolingVerb, CoolingAuthority] = {
    CoolingVerb.OBSERVE: CoolingAuthority.AUTONOMOUS,
    CoolingVerb.DIAGNOSE: CoolingAuthority.AUTONOMOUS,
    CoolingVerb.PROPOSE: CoolingAuthority.AUTONOMOUS,
    CoolingVerb.APPROVE: CoolingAuthority.GATED,
    CoolingVerb.INSTALL: CoolingAuthority.CEREMONY,
    CoolingVerb.VERIFY: CoolingAuthority.CONDITIONAL,
    CoolingVerb.RECEIPT: CoolingAuthority.CEREMONY,
    CoolingVerb.DECAY: CoolingAuthority.AUTONOMOUS,
}


@dataclass
class CoolingEvent:
    """A single cooling lifecycle event."""

    event_id: str
    verb: CoolingVerb
    failure_id: str  # links to the original failure
    timestamp: str
    actor_id: str
    origin: str = "external_failure"
    cooling_depth: int = 0
    parent_cooling_id: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    proposal: dict[str, Any] = field(default_factory=dict)
    approval: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.cooling_depth < 0 or self.cooling_depth > 1:
            raise ValueError("cooling_depth must be 0 or 1")
        if self.cooling_depth == 1 and not self.parent_cooling_id:
            raise ValueError("parent_cooling_id is required when cooling_depth=1")
        if self.cooling_depth == 0 and self.parent_cooling_id:
            raise ValueError("parent_cooling_id is only valid for nested cooling")

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "verb": self.verb.value,
            "failure_id": self.failure_id,
            "timestamp": self.timestamp,
            "actor_id": self.actor_id,
            "origin": self.origin,
            "cooling_depth": self.cooling_depth,
            "parent_cooling_id": self.parent_cooling_id,
            "evidence": self.evidence,
            "proposal": self.proposal,
            "approval": self.approval,
            "metadata": self.metadata,
        }

    def hash(self) -> str:
        """SHA256 of the canonical event."""
        content = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class CoolingCycle:
    """A complete cooling cycle from observe to receipt (or decay)."""

    cycle_id: str
    failure_id: str
    origin: str = "external_failure"
    cooling_depth: int = 0
    parent_cooling_id: str | None = None
    events: list[CoolingEvent] = field(default_factory=list)
    state: str = "OPEN"  # OPEN | APPROVED | INSTALLED | VERIFIED | SEALED | DECAYED
    created_at: str = ""
    closed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "failure_id": self.failure_id,
            "origin": self.origin,
            "cooling_depth": self.cooling_depth,
            "parent_cooling_id": self.parent_cooling_id,
            "events": [e.to_dict() for e in self.events],
            "state": self.state,
            "created_at": self.created_at,
            "closed_at": self.closed_at,
        }

    @property
    def latest_event(self) -> CoolingEvent | None:
        return self.events[-1] if self.events else None


def _generate_event_id() -> str:
    return f"cool-{secrets.token_hex(8)}"


def _generate_cycle_id() -> str:
    return f"cycle-{secrets.token_hex(8)}"


def observe(
    failure_id: str,
    actor_id: str,
    evidence: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Record a failure observation. Autonomous — no ceremony needed."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.OBSERVE,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence=evidence,
        metadata=metadata or {},
    )
    logger.info("Cooling observe: failure=%s event=%s", failure_id, event.event_id)
    return event


def diagnose(
    failure_id: str,
    actor_id: str,
    root_cause: str,
    evidence: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Diagnose root cause. Autonomous — no ceremony needed."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.DIAGNOSE,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence={**evidence, "root_cause": root_cause},
        metadata=metadata or {},
    )
    logger.info("Cooling diagnose: failure=%s cause=%s", failure_id, root_cause)
    return event


def propose(
    failure_id: str,
    actor_id: str,
    proposal: dict[str, Any],
    evidence: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Propose a fix. Autonomous — no ceremony needed."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.PROPOSE,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence=evidence,
        proposal=proposal,
        metadata=metadata or {},
    )
    logger.info("Cooling propose: failure=%s event=%s", failure_id, event.event_id)
    return event


def approve(
    failure_id: str,
    actor_id: str,
    approval: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Approve a proposal. Gated — requires human or constitutional approval."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.APPROVE,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        approval=approval,
        metadata=metadata or {},
    )
    logger.info("Cooling approve: failure=%s by=%s", failure_id, actor_id)
    return event


def install(
    failure_id: str,
    actor_id: str,
    installation: dict[str, Any],
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Install a fix. Ceremony — requires A-FORGE capability."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.INSTALL,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence={"installation": installation},
        metadata=metadata or {},
    )
    logger.info("Cooling install: failure=%s event=%s", failure_id, event.event_id)
    return event


def verify(
    failure_id: str,
    actor_id: str,
    verification: dict[str, Any],
    *,
    read_only: bool = True,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Verify installation result. Autonomous if read-only, gated if mutation."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.VERIFY,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence={"verification": verification, "read_only": read_only},
        metadata=metadata or {},
    )
    logger.info("Cooling verify: failure=%s read_only=%s", failure_id, read_only)
    return event


def receipt(
    failure_id: str,
    actor_id: str,
    cycle: CoolingCycle,
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Seal the cooling cycle to VAULT999. Ceremony — requires sovereign capability."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.RECEIPT,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence={"cycle_summary": cycle.to_dict()},
        metadata=metadata or {},
    )
    logger.info("Cooling receipt: failure=%s cycle=%s", failure_id, cycle.cycle_id)
    return event


def decay(
    failure_id: str,
    actor_id: str,
    reason: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> CoolingEvent:
    """Record that a proposal expired or was superseded. Autonomous."""
    event = CoolingEvent(
        event_id=_generate_event_id(),
        verb=CoolingVerb.DECAY,
        failure_id=failure_id,
        timestamp=datetime.now(UTC).isoformat(),
        actor_id=actor_id,
        evidence={"decay_reason": reason},
        metadata=metadata or {},
    )
    logger.info("Cooling decay: failure=%s reason=%s", failure_id, reason)
    return event


def create_cycle(
    failure_id: str,
    *,
    origin: str = "external_failure",
    cooling_depth: int = 0,
    parent_cooling_id: str | None = None,
) -> CoolingCycle:
    """Create a new cooling cycle for a failure."""
    if cooling_depth < 0 or cooling_depth > 1:
        raise ValueError("cooling_depth must be 0 or 1; recursive cooling is blocked")
    if cooling_depth == 1 and not parent_cooling_id:
        raise ValueError("parent_cooling_id is required when cooling_depth=1")
    if cooling_depth == 0 and parent_cooling_id:
        raise ValueError("parent_cooling_id is only valid for nested cooling")
    return CoolingCycle(
        cycle_id=_generate_cycle_id(),
        failure_id=failure_id,
        origin=origin,
        cooling_depth=cooling_depth,
        parent_cooling_id=parent_cooling_id,
        created_at=datetime.now(UTC).isoformat(),
    )


def append_event(cycle: CoolingCycle, event: CoolingEvent) -> CoolingCycle:
    """Append an event to a cooling cycle and update state."""
    if event.failure_id != cycle.failure_id:
        raise ValueError("event failure_id does not match cooling cycle")
    event.origin = cycle.origin
    event.cooling_depth = cycle.cooling_depth
    event.parent_cooling_id = cycle.parent_cooling_id
    cycle.events.append(event)

    # Update cycle state based on verb
    state_map = {
        CoolingVerb.OBSERVE: "OPEN",
        CoolingVerb.DIAGNOSE: "OPEN",
        CoolingVerb.PROPOSE: "OPEN",
        CoolingVerb.APPROVE: "APPROVED",
        CoolingVerb.INSTALL: "INSTALLED",
        CoolingVerb.VERIFY: "VERIFIED",
        CoolingVerb.RECEIPT: "SEALED",
        CoolingVerb.DECAY: "DECAYED",
    }
    cycle.state = state_map.get(event.verb, cycle.state)

    if event.verb in (CoolingVerb.RECEIPT, CoolingVerb.DECAY):
        cycle.closed_at = event.timestamp

    return cycle


__all__ = [
    "CoolingVerb",
    "CoolingAuthority",
    "CoolingEvent",
    "CoolingCycle",
    "VERB_AUTHORITY",
    "observe",
    "diagnose",
    "propose",
    "approve",
    "install",
    "verify",
    "receipt",
    "decay",
    "create_cycle",
    "append_event",
]
