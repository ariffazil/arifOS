"""
tests/test_session_dependency_guard.py

Test suite for arifOS Session Dependency Guard.
"""

from __future__ import annotations

from typing import List

from arifos_core.guards.session_dependency import (
    DependencyGuard,
    SessionRisk,
    SessionState,
)


def test_short_session_passes() -> None:
    """First interaction in a fresh session should PASS and be GREEN."""
    guard = DependencyGuard(max_duration_min=60.0, max_interactions=100)

    result = guard.check_risk("user_short")

    assert result["status"] == "PASS"
    assert result["risk_level"] == SessionRisk.GREEN.value
    assert result["interaction_count"] == 1
    assert result["duration_minutes"] >= 0.0


def test_duration_triggers_sabar(monkeypatch: "pytest.MonkeyPatch") -> None:
    """
    When duration exceeds the configured maximum, guard should trigger SABAR.
    """
    # Small duration for test: 0.01 minutes (~0.6 seconds)
    guard = DependencyGuard(max_duration_min=0.01, max_interactions=100)
    session_id = "user_long"

    # First interaction to create session state
    result_first = guard.check_risk(session_id)
    assert result_first["status"] == "PASS"

    # Simulate time passing by patching SessionState.start_time
    session = guard.sessions[session_id]

    def fake_duration_minutes(self: SessionState) -> float:
        return 2.0  # 2 minutes >> 0.01 threshold

    monkeypatch.setattr(
        SessionState,
        "duration_minutes",
        property(lambda self: fake_duration_minutes(self)),
    )

    # Next interaction should now trigger SABAR
    result = guard.check_risk(session_id)
    assert result["status"] == "SABAR"
    assert result["risk_level"] == SessionRisk.RED.value
    assert "pause" in result["message"].lower()


def test_high_interaction_triggers_warn() -> None:
    """
    When interaction count exceeds max_interactions, guard should WARN.
    """
    guard = DependencyGuard(max_duration_min=60.0, max_interactions=3)
    session_id = "user_dense"

    # 4 interactions -> last one should WARN
    statuses: List[str] = []
    for _ in range(4):
        result = guard.check_risk(session_id)
        statuses.append(result["status"])

    assert statuses[-1] == "WARN"
    last_result = guard.check_risk(session_id)
    assert last_result["status"] == "WARN"
    assert last_result["risk_level"] == SessionRisk.YELLOW.value
    assert "break" in last_result["message"].lower()


def test_sessions_are_isolated() -> None:
    """
    Different session IDs should track independent state.
    """
    guard = DependencyGuard(max_duration_min=60.0, max_interactions=3)

    # Drive one session into WARN
    for _ in range(4):
        guard.check_risk("session_a")

    # New session should start fresh
    result_new = guard.check_risk("session_b")
    assert result_new["status"] == "PASS"
    assert result_new["interaction_count"] == 1
    assert result_new["risk_level"] == SessionRisk.GREEN.value

