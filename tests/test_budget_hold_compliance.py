"""
Phase 1 Compliance Tests — Budget HOLD Envelope
===============================================
Verifies budget contract enforcement returns fully governed HOLD responses
with reasons[], output_policy=DOMAIN_VOID, and nine_signal.

Acceptance criteria:
  - max_turns violation  → HOLD + DOMAIN_VOID + reasons[]
  - max_tool_calls violation → HOLD + DOMAIN_VOID + reasons[]
  - No silent HOLD allowed
"""

from unittest.mock import patch


class FakeBudgetContract:
    """Minimal budget contract with configurable exhaustion."""

    def __init__(self, turns_ok=True, turn_reason="", tool_calls_ok=True, tool_reason=""):
        self._turns_ok = turns_ok
        self._turn_reason = turn_reason
        self._tool_calls_ok = tool_calls_ok
        self._tool_reason = tool_reason
        self._turns = 0
        self._tool_calls = 0

    def check_turn(self):
        return self._turns_ok, self._turn_reason

    def check_tool_call(self, tool_name):
        return self._tool_calls_ok, self._tool_reason

    def record_turn(self, action=""):
        pass

    def record_tool_call(self, tool_name):
        pass


# ─── Tests ──────────────────────────────────────────────────────────────────


def test_budget_hold_includes_reasons():
    """Budget max_turns violation MUST include non-empty reasons[]."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=False,
        turn_reason="max_turns exhausted (8/8)",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_mind_reason",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD", f"Expected HOLD, got {result['verdict']}"
    assert "reasons" in result, "HOLD response MUST include 'reasons' field"
    assert isinstance(result["reasons"], list), "'reasons' must be a list"
    assert len(result["reasons"]) > 0, "'reasons' must be non-empty"
    assert any(
        "max_turns" in r for r in result["reasons"]
    ), f"reasons[] must mention 'max_turns': {result['reasons']}"
    assert "reason" not in result or result.get("reason") is None


def test_budget_hold_includes_domain_void():
    """Budget violation MUST set output_policy = DOMAIN_VOID."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=False,
        turn_reason="max_turns exhausted (8/8)",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_mind_reason",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD"
    assert "output_policy" in result, "HOLD response MUST include 'output_policy'"
    assert (
        result["output_policy"] == "DOMAIN_VOID"
    ), f"output_policy must be DOMAIN_VOID, got {result.get('output_policy')}"


def test_budget_hold_includes_nine_signal():
    """Budget violation MUST include nine_signal block."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=False,
        turn_reason="max_turns exhausted (8/8)",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_mind_reason",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD"
    assert "nine_signal" in result, "HOLD response MUST include 'nine_signal'"
    ns = result["nine_signal"]
    assert "overall" in ns, "nine_signal must have 'overall' field"
    assert ns["overall"] == "RETAK", f"nine_signal.overall must be RETAK, got {ns['overall']}"
    assert "delta" in ns and "psi" in ns and "omega" in ns, "nine_signal must have delta/psi/omega"


def test_budget_tool_call_hold_includes_reasons():
    """Budget max_tool_calls violation MUST include non-empty reasons[]."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=True,
        tool_calls_ok=False,
        tool_reason="max_tool_calls exhausted (12/12) for arif_forge_execute",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_forge_execute",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD"
    assert "reasons" in result
    assert len(result["reasons"]) > 0
    assert any(
        "max_tool_calls" in r for r in result["reasons"]
    ), f"reasons[] must mention 'max_tool_calls': {result['reasons']}"


def test_budget_tool_call_hold_includes_domain_void():
    """Budget max_tool_calls violation MUST set output_policy = DOMAIN_VOID."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=True,
        tool_calls_ok=False,
        tool_reason="max_tool_calls exhausted (12/12)",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_forge_execute",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD"
    assert result.get("output_policy") == "DOMAIN_VOID"


def test_budget_tool_call_hold_includes_nine_signal():
    """Budget max_tool_calls violation MUST include nine_signal block."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(
        turns_ok=True,
        tool_calls_ok=False,
        tool_reason="max_tool_calls exhausted (12/12)",
    )

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_forge_execute",
            params={"session_id": "test-session"},
            actor_id=None,
        )

    assert result["verdict"] == "HOLD"
    assert "nine_signal" in result
    assert result["nine_signal"]["overall"] == "RETAK"


def test_budget_clear_allows_seal():
    """When budget is clear, check_floors must NOT return HOLD for budget reasons."""
    from arifosmcp.runtime.floor import check_floors

    fake = FakeBudgetContract(turns_ok=True, tool_calls_ok=True)

    with patch("arifosmcp.runtime.floor._get_budget_contract", return_value=fake):
        result = check_floors(
            tool_name="arif_mind_reason",
            params={"session_id": "test-session", "mode": "reason", "query": "test"},
            actor_id=None,
        )

    # With NIAT free-pass, REASON mode returns SEAL directly — no budget HOLD
    assert result["verdict"] != "HOLD" or result.get("failed_floors", []) != [
        "BUDGET"
    ], "Budget-clear session should not produce BUDGET HOLD"


def test_budget_exception_is_non_blocking():
    """If budget contract check throws, check_floors must NOT hard-fail — budget is non-blocking."""
    from arifosmcp.runtime.floor import check_floors

    with patch(
        "arifosmcp.runtime.floor._get_budget_contract", side_effect=RuntimeError("DB error")
    ):
        result = check_floors(
            tool_name="arif_mind_reason",
            params={"session_id": "test-session", "mode": "reason", "query": "test"},
            actor_id=None,
        )

    # Must not raise; verdict should still be returned (NIAT free-pass SEAL)
    assert "verdict" in result
    assert result.get("failed_floors", []) != [
        "BUDGET"
    ], "Budget exception should not cause BUDGET floor to appear"
