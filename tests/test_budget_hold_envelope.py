"""
G4 Test — Budget HOLD Envelope Compliance
==========================================
Target: arifosmcp/runtime/floor.py budget HOLD returns
Verifies: reasons[], output_policy=DOMAIN_VOID, nine_signal
"""

import os
import pytest


class MockBudgetContract:
    """Mock that always triggers budget HOLD on turn check."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    def check_turn(self):  # type: ignore[override]
        return False, "888_HOLD: turn budget exhausted"

    def check_tool_call(self, tool_name: str):  # type: ignore[override]
        return True, ""

    def record_turn(self, action: str = "") -> None:
        pass

    def record_tool_call(self, tool_name: str) -> None:
        pass


def mock_get_budget(session_id: str):  # type: ignore[no-untyped-def]
    return MockBudgetContract(session_id)


@pytest.fixture(autouse=True)
def patch_budget_contract():
    """Patch _get_budget_contract before each test."""
    import arifosmcp.runtime.floor as _floor_mod

    _original = _floor_mod._get_budget_contract
    _floor_mod._get_budget_contract = mock_get_budget
    yield
    _floor_mod._get_budget_contract = _original


def test_budget_turn_hold_has_reasons_plural():
    """Budget HOLD must include reasons[] (plural list)."""
    from arifosmcp.runtime.law import check_laws, VerdictLabel

    result = check_laws(
        tool_name="arif_mind_reason",
        params={"mode": "reason", "query": "test", "session_id": "test-session-g4"},
        actor_id=None,
    )
    assert result["verdict"] == "HOLD", f"Expected HOLD, got {result.get('verdict')}"
    assert result["label"] == VerdictLabel.HOLD_EXECUTION
    assert "reasons" in result, "Budget HOLD must include 'reasons' (plural list)"
    assert isinstance(result["reasons"], list), "reasons must be a list"
    assert len(result["reasons"]) > 0, "reasons list must not be empty"
    assert result["violated_laws"] == ["BUDGET"]


def test_budget_turn_hold_has_domain_void():
    """Budget HOLD must include output_policy=DOMAIN_VOID."""
    from arifosmcp.runtime.law import check_laws

    result = check_laws(
        tool_name="arif_mind_reason",
        params={"mode": "reason", "query": "test", "session_id": "test-session-g4"},
        actor_id=None,
    )
    assert result["verdict"] == "HOLD"
    assert "output_policy" in result, "Budget HOLD must include output_policy"
    assert result["output_policy"] == "DOMAIN_VOID", "output_policy must be DOMAIN_VOID"


def test_budget_turn_hold_has_nine_signal():
    """Budget HOLD must include nine_signal with overall=RETAK."""
    from arifosmcp.runtime.law import check_laws

    result = check_laws(
        tool_name="arif_mind_reason",
        params={"mode": "reason", "query": "test", "session_id": "test-session-g4"},
        actor_id=None,
    )
    assert result["verdict"] == "HOLD"
    assert "nine_signal" in result, "Budget HOLD must include nine_signal"
    ns = result["nine_signal"]
    assert isinstance(ns, dict), "nine_signal must be a dict"
    # delta=GANTUNG, overall=RETAK for HOLD status
    assert ns.get("overall", {}).get("state") == "RETAK", (
        f"nine_signal overall must be RETAK for HOLD, got {ns}"
    )


def test_budget_turn_hold_has_next_safe_action():
    """Budget HOLD must include next_safe_action."""
    from arifosmcp.runtime.law import check_laws

    result = check_laws(
        tool_name="arif_mind_reason",
        params={"mode": "reason", "query": "test", "session_id": "test-session-g4"},
        actor_id=None,
    )
    assert result["verdict"] == "HOLD"
    assert "next_safe_action" in result, "Budget HOLD must include next_safe_action"
    assert "888_HOLD" in result["next_safe_action"]


def test_budget_turn_hold_no_singular_reason():
    """Budget HOLD must NOT use singular 'reason' field."""
    from arifosmcp.runtime.law import check_laws

    result = check_laws(
        tool_name="arif_mind_reason",
        params={"mode": "reason", "query": "test", "session_id": "test-session-g4"},
        actor_id=None,
    )
    assert result["verdict"] == "HOLD"
    # Singular 'reason' should not exist (replaced by 'reasons')
    assert "reason" not in result or result.get("reason") is None, (
        "Budget HOLD should not use singular 'reason' — use 'reasons' instead"
    )


if __name__ == "__main__":
    import subprocess
    import sys

    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        cwd=os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
    )
    print(f"\nG4 Tests: {'PASS' if result.returncode == 0 else 'FAIL'}")
    sys.exit(result.returncode)
