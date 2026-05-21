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
from datetime import UTC, datetime
from enum import Enum

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
    plan_id: str | None = None
    last_verdict: str | None = None
    last_tool: str | None = None
    tool_call_history: list[str] = field(default_factory=list)
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
    """Get an existing session or create a new one.

    Reads from both the governance store (_session_store) and the kernel
    store (runtime.tools._SESSIONS) so that sessions created by
    arif_session_init are visible to governance apps.
    """
    # Check governance store first
    if session_id in _session_store:
        return _session_store[session_id]

    # Check kernel session store (arif_session_init uses this)
    try:
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id in _SESSIONS:
            kernel_sess = _SESSIONS[session_id]
            # Mirror into governance store
            _session_store[session_id] = SessionState(
                session_id=session_id,
                actor_id=kernel_sess.get("actor_id", actor_id),
                stage=kernel_sess.get("stage", "000"),
                lane=kernel_sess.get("lane", "AGI"),
                created_at=kernel_sess.get("created_at", datetime.now(UTC).isoformat()),
            )
            return _session_store[session_id]
    except Exception:
        pass  # runtime.tools not available — fall through to create

    # Create new governance session
    _session_store[session_id] = SessionState(
        session_id=session_id,
        actor_id=actor_id,
        created_at=datetime.now(UTC).isoformat(),
    )
    return _session_store[session_id]


def advance_session(
    session_id: str,
    new_state: LifecycleState,
    tool: str | None = None,
) -> SessionState:
    """Advance a session to a new lifecycle state."""
    s = get_or_create_session(session_id)
    s.lifecycle = new_state
    if tool:
        s.last_tool = tool
        s.tool_call_history.append(tool)
    return s


def record_tool_call(session_id: str, tool_name: str) -> None:
    """Record a tool call in the session history. F9 TAQWA tracking."""
    if not session_id:
        return
    s = get_or_create_session(session_id)
    s.tool_call_history.append(tool_name)


def was_tool_called(session_id: str, tool_name: str) -> bool:
    """Check if a tool was called in the current session chain. F9 TAQWA gate."""
    if not session_id:
        return False
    try:
        s = get_or_create_session(session_id)
        return tool_name in s.tool_call_history
    except Exception:
        return False


def reset_session_store() -> None:
    """Reset all sessions. Used in tests only."""
    global _session_store
    _session_store = {}
