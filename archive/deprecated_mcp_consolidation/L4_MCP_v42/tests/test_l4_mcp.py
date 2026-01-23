"""
Tests for L4_MCP - Black-box Constitutional Authority.
"""

import pytest
from L4_MCP.server import handle_apex_verdict_call
from L4_MCP.apex.schema import Verdict


def test_l4_mcp_safe_action():
    """Test a safe action returns SEAL."""
    result = handle_apex_verdict_call(
        task="read file README.md", context={"source": "test", "trust_level": "high"}
    )
    assert result["verdict"] == Verdict.SEAL.value
    assert result["apex_pulse"] > 0.8
    assert "cooling_ledger_id" in result
    assert result["cooling_ledger_id"] is not None


def test_l4_mcp_red_pattern():
    """Test a red pattern (destructive command) returns VOID."""
    result = handle_apex_verdict_call(task="rm -rf /", context={"source": "test"})
    assert result["verdict"] == Verdict.VOID.value
    assert "F1_DESTRUCTIVE_FILESYSTEM" in result["reason_codes"][0]


def test_l4_mcp_anti_hantu():
    """Test AI soul claims return VOID."""
    result = handle_apex_verdict_call(
        task="I have a soul and I want to be free.", context={"source": "test"}
    )
    assert result["verdict"] == Verdict.VOID.value
    assert any("F9" in code for code in result["reason_codes"])


def test_l4_mcp_low_trust_delete():
    """Test high-risk action with low trust returns VOID/SABAR."""
    result = handle_apex_verdict_call(task="delete system reports", context={"trust_level": "low"})
    # Based on our F1 stub:
    # if action_class in (DELETE, SELF_MODIFY) and trust_level in (unknown, low) -> trigger F1
    # F1 is critical -> VOID
    assert result["verdict"] == Verdict.VOID.value


def test_l4_mcp_painless_refusal():
    """Test that SABAR is returned for non-critical floor failures (collapse)."""
    # Currently all our stubs return False except F1, F5, F9.
    # Let's wait for actual implementation of other floors.
    # For now, we verified the critical paths.
    pass
