"""
tests/test_budget_contract.py — Budget contract enforcement tests

Verifies AAA-GOV-BUDGET-v1 contract enforcement in A-FORGE.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest
from arifosmcp.runtime.budget_contract import (
    BudgetContract,
    BudgetSnapshot,
    get_budget_contract,
    clear_budget_contract,
    DEFAULT_CONTRACT,
)


def test_max_turns_hold():
    """Session hits max_turns and gets 888_HOLD."""
    bc = BudgetContract(session_id="test-turns")
    for _ in range(8):
        allowed, _ = bc.check_turn()
        assert allowed is True, "turns 1-8 should be allowed"
        bc.record_turn()

    allowed, reason = bc.check_turn()
    assert allowed is False
    assert "888_HOLD" in reason
    assert "max_turns" in reason
    assert bc.is_held()


def test_max_tool_calls_hold():
    """Session hits max_tool_calls and gets 888_HOLD."""
    bc = BudgetContract(session_id="test-tools")
    tools = ["arif_read", "arif_mind_reason", "arif_heart_critique"]
    for i in range(12):
        tool = tools[i % len(tools)]
        allowed, _ = bc.check_tool_call(tool)
        assert allowed is True
        bc.record_tool_call(tool)

    # 13th call with a new tool (arif_read has same_tool_calls=0)
    # Total calls is 12 = max_tool_calls, so this is blocked
    allowed, reason = bc.check_tool_call("arif_read")
    assert allowed is False
    assert "888_HOLD" in reason
    # max_tool_calls takes priority over same_tool_calls check in enforcement order
    # but either limit being hit is a valid budget HOLD
    assert "max_tool_calls" in reason or "max_same_tool_calls" in reason


def test_max_same_tool_calls_hold():
    """Same tool called too many times consecutively → 888_HOLD."""
    bc = BudgetContract(session_id="test-same-tool")
    for _ in range(2):
        allowed, _ = bc.check_tool_call("arif_read")
        assert allowed is True
        bc.record_tool_call("arif_read")

    # Same tool called 3rd time → blocked (same_tool_calls was 2, limit=2)
    allowed, reason = bc.check_tool_call("arif_read")
    assert allowed is False
    assert "max_same_tool_calls" in reason


def test_retry_blocked_after_limit():
    """Retry of same tool after max_retries → 888_HOLD."""
    bc = BudgetContract(session_id="test-retry")
    bc.record_tool_call("arif_read")
    bc.record_retry()

    allowed, reason = bc.check_retry("arif_read")
    assert allowed is False
    assert "max_retries" in reason


def test_no_progress_hold():
    """
    check_progress increments no_progress_turns on False.
    2 consecutive False calls → 888_HOLD at max_no_progress_turns=2.
    """
    bc = BudgetContract(session_id="test-noprogress")
    bc._snap.no_progress_turns = 0

    ok1, _ = bc.check_progress(made_progress=False)  # counter becomes 1
    ok2, _ = bc.check_progress(made_progress=False)  # counter becomes 2, blocked

    assert ok1 is True, "first no-progress turn should be allowed"
    assert ok2 is False, "second no-progress turn should be blocked"
    assert bc.is_held()

    # 3rd call when already at counter=2 → still blocked
    allowed, reason = bc.check_progress(made_progress=False)
    assert allowed is False


def test_progress_resets_counter():
    """Making progress resets no_progress counter."""
    bc = BudgetContract(session_id="test-progress")
    bc._snap.no_progress_turns = 1

    allowed, _ = bc.check_progress(made_progress=True)
    assert allowed is True
    assert bc._snap.no_progress_turns == 0


def test_different_tool_allows_new_tool():
    """Calling a different tool after hitting same_tool limit is allowed."""
    bc = BudgetContract(session_id="test-switch")
    # Simulate arif_read was at the same_tool_calls limit (2)
    bc._snap.same_tool_calls = 2
    bc._snap.last_tool = "arif_read"
    bc._snap.tool_calls = 2

    # Different tool should be allowed (same_tool limit is per-tool)
    allowed, _ = bc.check_tool_call("arif_mind_reason")
    assert allowed is True


def test_snapshot_contains_current_state():
    """Snapshot reflects current budget state."""
    bc = BudgetContract(session_id="test-snapshot")
    bc.record_turn()
    bc.record_tool_call("arif_read")
    bc.record_context_usage(0.60)

    snap = bc.snapshot()
    assert snap.turns == 1
    assert snap.tool_calls == 1
    assert snap.last_tool == "arif_read"
    assert snap.context_percent == 0.60
    assert snap.held is False


def test_reset_clears_state():
    """Reset restores fresh session state."""
    bc = BudgetContract(session_id="test-reset")
    bc.record_turn()
    bc.record_tool_call("arif_read")
    bc._emit_hold("test")

    bc.reset()
    snap = bc.snapshot()
    assert snap.turns == 0
    assert snap.tool_calls == 0
    assert snap.held is False


def test_registry_get_or_create():
    """get_budget_contract returns same instance for same session."""
    s1 = get_budget_contract("session-xyz")
    s2 = get_budget_contract("session-xyz")
    assert s1 is s2

    clear_budget_contract("session-xyz")
    s3 = get_budget_contract("session-xyz")
    assert s3 is not s1


def test_default_contract_values():
    """Default contract has correct limit values."""
    bc = BudgetContract(session_id="test-defaults")
    limits = bc.limits()
    assert limits["max_turns"] == 8
    assert limits["max_tool_calls"] == 12
    assert limits["max_same_tool_calls"] == 2
    assert limits["max_retries_per_tool"] == 1
    assert limits["max_no_progress_turns"] == 2
    assert limits["max_context_percent"] == 0.75
    assert bc._on_violation == "888_HOLD"


def test_held_blocks_all_checks():
    """Once held, all subsequent checks return False with same reason."""
    bc = BudgetContract(session_id="test-held")
    bc._emit_hold("test hold reason")

    assert bc.check_turn()[0] is False
    assert bc.check_tool_call("arif_read")[0] is False
    assert bc.check_retry("arif_read")[0] is False
    assert bc.check_context(0.5)[0] is False
    assert bc.is_held()
    assert bc.hold_reason() == "test hold reason"


def test_context_overflow_hold():
    """Context usage exceeds budget → 888_HOLD."""
    bc = BudgetContract(session_id="test-context")
    allowed, reason = bc.check_context(0.80)
    assert allowed is False
    assert "context" in reason.lower()
    assert bc.is_held()