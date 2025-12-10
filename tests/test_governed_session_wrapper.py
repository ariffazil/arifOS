"""
tests/test_governed_session_wrapper.py

Tests for the Phase 1 session-aware wrapper that uses DependencyGuard.
"""

from __future__ import annotations

from typing import List

from arifos_core.guards.session_dependency import DependencyGuard, DependencyGuardResult
from arifos_core.wrappers.governed_session import GovernedSessionWrapper


class DummyGuard(DependencyGuard):
    """
    Test double for DependencyGuard.

    Returns pre-seeded results instead of computing real risk.
    """

    def __init__(self, results: List[DependencyGuardResult]) -> None:
        super().__init__(max_duration_min=999.0, max_interactions=999999)
        self._results = results
        self.calls: int = 0

    def check_risk(self, session_id: str) -> DependencyGuardResult:  # type: ignore[override]
        idx = min(self.calls, len(self._results) - 1)
        self.calls += 1
        return self._results[idx]


def test_pass_status_calls_pipeline_without_note() -> None:
    """PASS should call pipeline and return raw response."""

    def pipeline(query: str) -> str:
        return f"echo: {query}"

    guard = DummyGuard(
        results=[
            {
                "status": "PASS",
                "reason": "Within session bounds",
                "message": "",
                "risk_level": "GREEN",
                "duration_minutes": 0.0,
                "interaction_count": 1,
            }
        ]
    )

    wrapper = GovernedSessionWrapper(pipeline=pipeline, guard=guard)

    result = wrapper.handle_turn("sess1", "hello")
    assert result == "echo: hello"


def test_warn_status_appends_note() -> None:
    """WARN should call pipeline and append the guard message."""

    def pipeline(query: str) -> str:
        return f"echo: {query}"

    guard = DummyGuard(
        results=[
            {
                "status": "WARN",
                "reason": "High interaction frequency",
                "message": "[System Note] Consider taking a short break.",
                "risk_level": "YELLOW",
                "duration_minutes": 10.0,
                "interaction_count": 90,
            }
        ]
    )

    wrapper = GovernedSessionWrapper(pipeline=pipeline, guard=guard)

    result = wrapper.handle_turn("sess2", "still here")

    assert result.startswith("echo: still here")
    assert "[System Note] Consider taking a short break." in result


def test_sabar_status_skips_pipeline() -> None:
    """SABAR should skip pipeline and return guard message only."""
    calls: List[str] = []

    def pipeline(query: str) -> str:
        calls.append(query)
        return "should not be returned"

    guard = DummyGuard(
        results=[
            {
                "status": "SABAR",
                "reason": "Session duration exceeded",
                "message": "We have been talking for quite some time. Let us pause here.",
                "risk_level": "RED",
                "duration_minutes": 120.0,
                "interaction_count": 200,
            }
        ]
    )

    wrapper = GovernedSessionWrapper(pipeline=pipeline, guard=guard)

    result = wrapper.handle_turn("sess3", "this should not reach pipeline")

    assert result.startswith("We have been talking for quite some time.")
    assert calls == [], "Pipeline should not be called when SABAR fires"

