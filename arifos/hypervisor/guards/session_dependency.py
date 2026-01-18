"""
arifos_core/guards/session_dependency.py

arifOS Session Dependency Guard

Purpose:
    Provide a lightweight, in-memory guard for long-horizon behaviour
    such as high-frequency or long-duration interaction patterns.

    While the main constitutional floors (F1-F9) govern each response,
    this guard operates at the session level to detect potential
    overuse or parasocial dependency patterns.

Design:
    - Pure Python, in-memory only (no databases or external state)
    - Simple heuristics:
        * Duration threshold (minutes)
        * Interaction count threshold
    - Returns a small dict with status and guidance:
        * PASS  -> within bounds
        * WARN  -> high frequency, suggest a break
        * SABAR -> long session, recommend pausing

Motto:
    "Even water is poison in excess."
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, TypedDict


class SessionRisk(str, Enum):
    """Risk level for a given session."""

    GREEN = "GREEN"   # Healthy interaction
    YELLOW = "YELLOW" # High frequency / density
    RED = "RED"       # Dependency concern (SABAR)


@dataclass
class SessionState:
    """
    Track basic session-level usage statistics.

    Attributes:
        session_id: Identifier for the session (e.g., user or conversation ID)
        start_time: Timestamp when the session started
        interaction_count: Number of interactions in this session
        last_interaction_time: Timestamp of the last interaction
        risk_level: Current assessed risk level
    """

    session_id: str
    start_time: float = field(default_factory=time.time)
    interaction_count: int = 0
    last_interaction_time: float = field(default_factory=time.time)
    risk_level: SessionRisk = SessionRisk.GREEN

    @property
    def duration_minutes(self) -> float:
        """Return the session duration in minutes."""
        return (time.time() - self.start_time) / 60.0


class DependencyGuardResult(TypedDict, total=False):
    """
    Result structure for DependencyGuard.check_risk.

    Keys:
        status: "PASS" | "WARN" | "SABAR"
        reason: Short machine-readable reason
        message: Human-readable guidance text
        risk_level: SessionRisk value (as string)
        duration_minutes: Current session duration
        interaction_count: Number of interactions so far
    """

    status: str
    reason: str
    message: str
    risk_level: str
    duration_minutes: float
    interaction_count: int


class DependencyGuard:
    """
    Session Dependency Guard.

    Enforces simple limits on interaction duration and density to help
    prevent unhealthy dependency patterns. This is a lab-friendly guard
    that can be called by wrappers or hosting applications before
    invoking the main arifOS pipeline.

    Example:
        guard = DependencyGuard(max_duration_min=60, max_interactions=80)
        result = guard.check_risk(session_id="user-123")
        if result["status"] == "SABAR":
            # Return a gentle boundary message instead of continuing
    """

    def __init__(
        self,
        max_duration_min: float = 60.0,
        max_interactions: int = 80,
    ) -> None:
        """
        Initialize the dependency guard.

        Args:
            max_duration_min: Maximum session duration in minutes before SABAR.
            max_interactions: Maximum number of interactions before WARN.
        """
        self.max_duration_min = max_duration_min
        self.max_interactions = max_interactions
        # In-memory storage for the spike (no external persistence)
        self.sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: str) -> SessionState:
        """
        Retrieve existing SessionState or create a new one.

        Args:
            session_id: Identifier for the session

        Returns:
            SessionState for the given session ID
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)
        return self.sessions[session_id]

    def check_risk(self, session_id: str) -> DependencyGuardResult:
        """
        Update and evaluate risk for a given session.

        This method should be called once per interaction. It updates
        the session counters and returns a summary of the current
        risk level and any recommended action.

        Args:
            session_id: Identifier for the session

        Returns:
            DependencyGuardResult with status and guidance.
        """
        session = self.get_or_create_session(session_id)
        session.interaction_count += 1
        session.last_interaction_time = time.time()

        # Base result assumes everything is within bounds
        result: DependencyGuardResult = {
            "status": "PASS",
            "reason": "Within session bounds",
            "risk_level": SessionRisk.GREEN.value,
            "duration_minutes": session.duration_minutes,
            "interaction_count": session.interaction_count,
        }

        # Heuristic 1: Duration-based SABAR (higher priority)
        if session.duration_minutes > self.max_duration_min:
            session.risk_level = SessionRisk.RED
            result.update(
                {
                    "status": "SABAR",
                    "reason": "Session duration exceeded",
                    "message": (
                        "We have been talking for quite some time. "
                        "For clarity and balance, this is a good point to pause "
                        "and rest or reach out to people you trust."
                    ),
                    "risk_level": SessionRisk.RED.value,
                }
            )
            return result

        # Heuristic 2: Interaction count-based WARN
        if session.interaction_count > self.max_interactions:
            session.risk_level = SessionRisk.YELLOW
            result.update(
                {
                    "status": "WARN",
                    "reason": "High interaction frequency",
                    "message": (
                        "[System Note] There have been many messages in this session. "
                        "It may help to take a short break, stretch, or step away "
                        "before continuing."
                    ),
                    "risk_level": SessionRisk.YELLOW.value,
                }
            )
            return result

        # Still within bounds
        session.risk_level = SessionRisk.GREEN
        return result


__all__ = ["SessionRisk", "SessionState", "DependencyGuard", "DependencyGuardResult"]

