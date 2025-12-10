"""
governed_session.py - Session-aware governance wrapper (Phase 1)

This module provides a high-level wrapper that combines:
    - Session Dependency Guard (time / interaction density)
    - An arbitrary governed pipeline or responder callable

Phase 1 goal:
    Add a time-aware "doorman" in front of the main pipeline
    without modifying arifos_core.pipeline or APEX PRIME.

Usage (conceptual):

    from arifos_core.guards import DependencyGuard
    from arifos_core.wrappers import GovernedSessionWrapper

    def my_pipeline(query: str) -> str:
        # Call into the real arifOS pipeline or another governed responder
        ...

    guard = DependencyGuard()
    wrapper = GovernedSessionWrapper(pipeline=my_pipeline, guard=guard)

    reply = wrapper.handle_turn(session_id="user-123", user_input="Hello")

Motto:
    "A good gate knows when to close."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from arifos_core.guards.session_dependency import DependencyGuard, DependencyGuardResult


ResponderCallable = Callable[[str], str]


@dataclass
class GovernedSessionWrapper:
    """
    Session-aware wrapper for governed conversations.

    This wrapper does not know about the internal details of the pipeline.
    It accepts any callable that takes a user_input string and returns
    a response string. Before each call, it consults DependencyGuard
    to decide whether to proceed, warn, or SABAR.

    Branching logic:
        - SABAR (RED):
            Return guard message immediately; do not call pipeline.
        - WARN (YELLOW):
            Call pipeline; append guard message as a gentle note.
        - PASS (GREEN):
            Call pipeline; return response unchanged.
    """

    pipeline: ResponderCallable
    guard: Optional[DependencyGuard] = None

    def __post_init__(self) -> None:
        if self.guard is None:
            self.guard = DependencyGuard()

    def handle_turn(self, session_id: str, user_input: str) -> str:
        """
        Handle a single conversational turn with session-aware governance.

        Args:
            session_id: Identifier for the session (e.g., user or chat ID)
            user_input: The user's input text

        Returns:
            Governed response string, possibly replaced or annotated
            by the session dependency guard.
        """
        risk: DependencyGuardResult = self.guard.check_risk(session_id)

        status = risk.get("status", "PASS")

        # SABAR: do not call the pipeline at all
        if status == "SABAR":
            message = risk.get(
                "message",
                (
                    "We have been talking for a long time. "
                    "To maintain clarity and balance, it is better to pause here."
                ),
            )
            return message

        # Otherwise, call the underlying pipeline
        response = self.pipeline(user_input)

        # WARN: append a gentle note
        if status == "WARN":
            note = risk.get(
                "message",
                (
                    "[System Note] This has been a dense session. "
                    "It may help to take a short break before continuing."
                ),
            )
            return f"{response}\n\n{note}"

        # PASS: unchanged
        return response


__all__ = ["GovernedSessionWrapper", "ResponderCallable"]

