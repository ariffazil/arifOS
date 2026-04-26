"""
session_state.py — arifOS Command Center Session State Machine
═════════════════════════════════════════════════════════════
Tracks: stage (000-999), actor, plan_id, lifecycle state.

MVP: in-memory with optional JSON persistence.
Sessions are ephemeral — reset on server restart.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

STAGE_MIN_FORGE = 777  # Forge requires stage 777 or higher


class LifecycleState(Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    RISK_REVIEWED = "risk_reviewed"
    JUDGE_REVIEWED = "judge_reviewed"
    APPROVED = "approved"
    EXECUTED = "executed"
    SEALED = "sealed"
    BLOCKED = "blocked"


@dataclass
class SessionState:
    session_id: str
    actor_id: str = "arif"
    stage: str = "000"
    lane: str = "AGI"
    lifecycle: LifecycleState = LifecycleState.DRAFT
    plan_id: Optional[str] = None
    last_verdict: Optional[str] = None
    last_tool: Optional[str] = None
    created_at: str = ""

    def can_advance_to(self, target_stage: str) -> bool:
        """Check if session can advance to target stage."""
        return int(self.stage) <= int(target_stage)

    def requires_human(self) -> bool:
        """Return True if this lifecycle state requires human presence."""
        return self.lifecycle in {
            LifecycleState.JUDGE_REVIEWED,
            LifecycleState.APPROVED,
        }


# In-memory session store — ephemeral for v0.1
_session_store: dict[str, SessionState] = {}


def get_or_create_session(session_id: str, actor_id: str = "arif") -> SessionState:
    """Get an existing session or create a new one."""
    if session_id not in _session_store:
        _session_store[session_id] = SessionState(
            session_id=session_id,
            actor_id=actor_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
    return _session_store[session_id]


def advance_session(
    session_id: str,
    new_state: LifecycleState,
    tool: Optional[str] = None,
) -> SessionState:
    """Advance a session to a new lifecycle state."""
    s = get_or_create_session(session_id)
    s.lifecycle = new_state
    if tool:
        s.last_tool = tool
    return s


def reset_session_store() -> None:
    """Reset all sessions. Used in tests only."""
    global _session_store
    _session_store = {}
