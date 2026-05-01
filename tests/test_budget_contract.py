"""
tests/test_budget_contract.py — AAA-GOV-BUDGET-v1 Enforcement Tests
===================================================================

Verifies AAA-GOV-BUDGET-v1 contract enforcement in A-FORGE.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from arifosmcp.runtime.budget_contract import (
    BudgetContract,
    get_budget_contract,
    clear_budget_contract,
)


class TestTurnBudget:
    """max_turns limit enforcement."""

    def test_turns_within_limit(self):
        bc = BudgetContract("session-turns")
        for i in range(8):
            ok, reason = bc.check_turn()
            assert ok is True, f"Turn {i+1} should be allowed"
            bc.record_turn()
        snap = bc.snapshot()
        assert snap.turns == 8

    def test_turns_exceeded(self):
        bc = BudgetContract("session-turns-exceeded")
        for _ in range(8):
            bc.record_turn()
        ok, reason = bc.check_turn()
        assert ok is False
        assert "888_HOLD" in reason
        assert "max_turns" in reason

    def test_session_is_held_after_turn_violation(self):
        bc = BudgetContract("session-held")
        for _ in range(8):
            bc.record_turn()
        bc.check_turn()
        assert bc.is_held() is True

    def test_held_reason_captured(self):
        bc = BudgetContract("session-reason")
        for _ in range(8):
            bc.record_turn()
        _, reason = bc.check_turn()
        assert bc.hold_reason() == reason


class TestToolCallBudget:
    """max_tool_calls and max_same_tool_calls enforcement."""

    def test_tool_calls_within_limit(self):
        bc = BudgetContract("session-tools")
        # Different tools — same_tool_calls check fires per-tool, not cumulative
        tools = ["terminal", "read_file", "grep", "python"]
        for _ in range(3):  # 12 total calls across 4 different tools
            for t in tools:
                ok, reason = bc.check_tool_call(t)
                assert ok is True, reason
                bc.record_tool_call(t)
        assert bc.snapshot().tool_calls == 12

    def test_total_tool_calls_exceeded(self):
        bc = BudgetContract("session-tools-exceeded")
        # Use different tools so same_tool_calls doesn't fire first
        tools = ["terminal", "read_file", "grep", "python"]
        for t in tools:
            for _ in range(3):  # 12 total
                bc.record_tool_call(t)
        ok, reason = bc.check_tool_call("read_file")
        assert ok is False
        assert "max_tool_calls" in reason

    def test_same_tool_repeated_blocked(self):
        bc = BudgetContract("session-same-tool")
        bc.record_tool_call("terminal")
        bc.record_tool_call("terminal")
        ok, reason = bc.check_tool_call("terminal")
        assert ok is False
        assert "max_same_tool_calls" in reason
        assert "terminal" in reason

    def test_different_tools_allowed(self):
        bc = BudgetContract("session-diff-tools")
        tools = ["terminal", "read_file", "search", "python"]
        for t in tools * 3:  # 12 total calls
            ok, reason = bc.check_tool_call(t)
            assert ok is True, f"{t} should be allowed"
            bc.record_tool_call(t)


class TestRetryBudget:
    """max_retries_per_tool enforcement."""

    def test_retry_within_limit(self):
        bc = BudgetContract("session-retry-ok")
        # max_retries=1 means: after 0 retries, one retry is allowed.
        # check_retry: pass when retries < max_retries.
        ok, _ = bc.check_retry("terminal")  # retries=0, 0<1 → pass
        assert ok is True
        bc.record_retry()  # retries becomes 1
        # Now retries==max_retries, next check_retry fails

    def test_retry_exactly_at_limit(self):
        bc = BudgetContract("session-retry-limit")
        ok, _ = bc.check_retry("terminal")  # 0<1 → pass
        bc.record_retry()  # retries=1
        ok2, _ = bc.check_retry("terminal")  # 1>=1 → fail
        assert ok2 is False

    def test_retry_exceeded(self):
        bc = BudgetContract("session-retry-fail")
        bc.record_retry()
        bc.check_retry("terminal")
        ok, reason = bc.check_retry("terminal")
        assert ok is False
        assert "max_retries" in reason


class TestProgressBudget:
    """max_no_progress_turns enforcement."""

    def test_progress_resets_counter(self):
        bc = BudgetContract("session-progress-ok")
        # check_progress(False) increments no_progress_turns (doesn't call record)
        # First two False calls: npt=1, npt=2 → held
        bc.check_progress(False)  # npt=1
        bc.check_progress(False)  # npt=2 → held
        assert bc.snapshot().no_progress_turns == 2
        assert bc.is_held() is True
        # reset() clears the held state
        bc.reset()
        assert bc.snapshot().no_progress_turns == 0
        assert bc.is_held() is False

    def test_no_progress_exceeded(self):
        bc = BudgetContract("session-stuck")
        for _ in range(2):
            bc.check_progress(False)
        ok, reason = bc.check_progress(False)
        assert ok is False
        assert "no_progress" in reason


class TestContextBudget:
    """max_context_percent enforcement."""

    def test_context_within_budget(self):
        bc = BudgetContract("session-ctx-ok")
        ok, reason = bc.check_context(0.74)
        assert ok is True

    def test_context_over_budget(self):
        bc = BudgetContract("session-ctx-high")
        ok, reason = bc.check_context(0.80)
        assert ok is False
        assert "context" in reason.lower()

    def test_context_at_exact_boundary(self):
        bc = BudgetContract("session-ctx-boundary")
        ok, reason = bc.check_context(0.75)
        assert ok is True


class TestBudgetSnapshot:
    """Budget state snapshot accuracy."""

    def test_snapshot_captures_state(self):
        bc = BudgetContract("session-snap")
        bc.record_turn("init")
        bc.record_tool_call("terminal")
        snap = bc.snapshot()
        assert snap.session_id == "session-snap"
        assert snap.turns == 1
        assert snap.tool_calls == 1
        assert snap.last_tool == "terminal"
        assert snap.held is False

    def test_limits_returned(self):
        bc = BudgetContract("session-limits")
        limits = bc.limits()
        assert limits["max_turns"] == 8
        assert limits["max_tool_calls"] == 12
        assert limits["max_same_tool_calls"] == 2


class TestBudgetRegistry:
    """Session-scoped budget registry."""

    def test_get_creates_new(self):
        clear_budget_contract("new-session")
        bc = get_budget_contract("new-session")
        assert bc.snapshot().session_id == "new-session"

    def test_get_returns_same(self):
        clear_budget_contract("shared-session")
        bc1 = get_budget_contract("shared-session")
        bc2 = get_budget_contract("shared-session")
        assert bc1 is bc2

    def test_clear_removes(self):
        clear_budget_contract("to-clear")
        bc = get_budget_contract("to-clear")
        clear_budget_contract("to-clear")
        # After clear, new call returns fresh instance
        bc_new = get_budget_contract("to-clear")
        assert bc_new is not bc
        assert bc_new.snapshot().turns == 0


class TestBudgetReset:
    """Session reset functionality."""

    def test_reset_clears_state(self):
        bc = BudgetContract("session-reset")
        bc.record_turn()
        bc.record_tool_call("terminal")
        bc.reset()
        snap = bc.snapshot()
        assert snap.turns == 0
        assert snap.tool_calls == 0
        assert snap.held is False
