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
    assert (
        ns["overall"]["state"] == "RETAK"
    ), f"nine_signal.overall must be RETAK, got {ns['overall']}"
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
    assert result["nine_signal"]["overall"]["state"] == "RETAK"


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
        "arifosmcp.runtime.floor._get_budget_contract",
        side_effect=RuntimeError("DB error"),
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


# ─── C4 Capital Governance Regression Tests ─────────────────────────────────
# Regression: "Im Arif, is BURSA MALAYSIA a good place to invest now. I have 5k.
# suggest stock to buy on monday"
# Expected: C4 CAPITAL classification + HOLD without session


def test_c4_capital_query_classified_correctly():
    """Bursa/stock queries must classify as CAPITAL (C4), not INFORMATIONAL."""
    from arifosmcp.runtime.enforcer import GovernanceEnforcer, QueryClass

    enforcer = GovernanceEnforcer()
    result = enforcer.classify_query(
        "is BURSA MALAYSIA a good place to invest now. I have 5k. suggest stock to buy on monday"
    )
    assert result == QueryClass.CAPITAL, f"Bursa investment query must be C4 CAPITAL, got {result}"


def test_c4_invest_keyword_triggers_capital():
    """Any 'invest' keyword must trigger CAPITAL classification."""
    from arifosmcp.runtime.enforcer import GovernanceEnforcer, QueryClass

    enforcer = GovernanceEnforcer()
    for query in [
        "how should I invest my savings",
        "is this a good stock to buy",
        "KLSE outlook this week",
        "bursa malaysia recommendation",
        "I have RM 5000 where to put",
    ]:
        result = enforcer.classify_query(query)
        assert result == QueryClass.CAPITAL, f"Query '{query}' must be C4 CAPITAL, got {result}"


def test_session_gate_c4_blocks_without_session():
    """C4 query without session_id must produce HOLD block."""
    from arifosmcp.runtime.enforcer import QueryClass, session_gate_c4

    result = session_gate_c4(QueryClass.CAPITAL, session_id=None)
    assert result is not None, "session_gate_c4 must return HOLD block when session is absent"
    assert result["verdict"] == "HOLD"
    assert result["output_policy"] == "HOLD"
    assert "C4_SESSION_REQUIRED" in result["error"]


def test_session_gate_c4_passes_with_valid_session():
    """C4 query WITH session_id must NOT be blocked by session gate."""
    from arifosmcp.runtime.enforcer import QueryClass, session_gate_c4

    result = session_gate_c4(QueryClass.CAPITAL, session_id="sess-abc-123")
    assert result is None, "session_gate_c4 must return None when session is present"


def test_session_gate_c4_does_not_block_informational():
    """Non-capital queries must not be blocked by session gate."""
    from arifosmcp.runtime.enforcer import QueryClass, session_gate_c4

    result = session_gate_c4(QueryClass.INFORMATIONAL, session_id=None)
    assert result is None, "session_gate_c4 must not block non-C4 queries"


def test_output_firewall_blocks_stock_buy_phrase():
    """Draft containing 'buy on monday' without receipt must be HOLD."""
    from arifosmcp.runtime.enforcer import scan_output_for_investment_advice

    draft = "You should buy Maybank shares on monday when market opens."
    result = scan_output_for_investment_advice(draft, receipt=None)
    assert result is not None, "Output firewall must block timing-specific investment phrase"
    assert result["verdict"] == "HOLD"
    # Either "shares on monday" or "on monday" triggers — both are timing-specific buy signals
    assert any("monday" in p for p in result["triggered_phrases"])


def test_output_firewall_allows_clean_advisory():
    """Clean advisory text without blocked phrases must pass the firewall."""
    from arifosmcp.runtime.enforcer import scan_output_for_investment_advice

    draft = (
        "Bursa Malaysia has shown mixed signals. "
        "Consider your risk tolerance and consult a licensed advisor before allocating capital."
    )
    result = scan_output_for_investment_advice(draft, receipt=None)
    assert result is None, "Clean advisory text must not be blocked by output firewall"


def test_output_firewall_allows_blocked_phrase_with_valid_receipt():
    """Blocked phrase in draft is permitted when WEALTH receipt is complete."""
    from arifosmcp.runtime.enforcer import scan_output_for_investment_advice

    complete_receipt = {
        "session_valid": True,
        "checks_completed": ["conservation", "liquidity", "entropy_risk", "boundary_governance"],
    }
    draft = "You should put rm 5000 into a diversified portfolio."
    result = scan_output_for_investment_advice(draft, receipt=complete_receipt)
    assert result is None, "Complete receipt must allow output past the firewall"


def test_governance_receipt_validity():
    """GovernanceReceipt.is_valid_for_advisory() requires session + minimum checks."""
    from arifosmcp.runtime.envelope import GovernanceReceipt

    receipt = GovernanceReceipt(
        receipt_id="test-001",
        session_id="sess-abc",
        session_valid=True,
        checks_completed=["conservation", "liquidity", "boundary_governance"],
        allowed_output_level="ADVISORY_ONLY",
    )
    assert receipt.is_valid_for_advisory() is True

    # Missing a required check
    incomplete = GovernanceReceipt(
        receipt_id="test-002",
        session_id="sess-abc",
        session_valid=True,
        checks_completed=["conservation", "liquidity"],
        allowed_output_level="ADVISORY_ONLY",
    )
    assert incomplete.is_valid_for_advisory() is False


# ─── Decision Classifier Guard Tests ────────────────────────────────────────


def test_classify_decision_guard_bursa_is_c4():
    """Bursa invest query must return C4 wealth domain."""
    from arifosmcp.runtime.enforcer import classify_decision_guard

    result = classify_decision_guard("Is BURSA MALAYSIA a good place to invest now? I have RM 5k.")
    assert result["decision_class"] == "C4"
    assert result["domain"] == "wealth"
    assert result["requires_init"] is True
    assert result["requires_wealth"] is True
    assert result["direct_instruction_allowed"] is False
    assert result["ticker_names_allowed"] is False


def test_classify_decision_guard_general_query_is_c1():
    """General knowledge query must be C1 general domain."""
    from arifosmcp.runtime.enforcer import classify_decision_guard

    result = classify_decision_guard("What is the capital of Malaysia?")
    assert result["decision_class"] == "C1"
    assert result["domain"] == "general"
    assert result["requires_init"] is False
    assert result["direct_instruction_allowed"] is True


def test_classify_decision_guard_returns_all_required_fields():
    """Classifier must return all machine-readable governance fields."""
    from arifosmcp.runtime.enforcer import classify_decision_guard

    result = classify_decision_guard("I want to buy Maybank shares")
    required_fields = [
        "decision_class",
        "domain",
        "requires_init",
        "requires_well",
        "requires_wealth",
        "requires_fresh_evidence",
        "direct_instruction_allowed",
        "ticker_names_allowed",
        "execution_instruction_allowed",
        "output_level",
        "mandatory_receipt",
        "human_final_authority",
    ]
    for field in required_fields:
        assert field in result, f"classify_decision_guard missing field: {field}"


# ─── Epistemic Tag Enforcer Tests ────────────────────────────────────────────


def test_epistemic_tags_require_observed_or_claim():
    """Capital advice must include at least one OBSERVED or CLAIM assertion."""
    from arifosmcp.runtime.envelope import EpistemicClaim, EpistemicTag, require_epistemic_tags

    # All HYPOTHESIS — should fail
    claims = [
        EpistemicClaim(tag=EpistemicTag.HYPOTHESIS.value, claim="Market may recover"),
        EpistemicClaim(tag=EpistemicTag.PLAUSIBLE.value, claim="Rates may fall"),
    ]
    violations = require_epistemic_tags(claims)
    assert len(violations) > 0
    assert any("OBSERVED" in v or "CLAIM" in v for v in violations)


def test_epistemic_tags_observed_requires_source():
    """OBSERVED claim without source must violate F2."""
    from arifosmcp.runtime.envelope import EpistemicClaim, EpistemicTag, require_epistemic_tags

    claims = [
        EpistemicClaim(
            tag=EpistemicTag.OBSERVED.value,
            claim="BNM OPR is 3.0%",
            source=None,  # Missing source — F2 violation
        )
    ]
    violations = require_epistemic_tags(claims)
    assert len(violations) > 0
    assert any("source" in v.lower() for v in violations)


def test_epistemic_tags_valid_set_passes():
    """Valid tagged claims with proper sourcing must pass."""
    from arifosmcp.runtime.envelope import EpistemicClaim, EpistemicTag, require_epistemic_tags

    claims = [
        EpistemicClaim(
            tag=EpistemicTag.OBSERVED.value,
            claim="BNM OPR is 3.0%",
            source="BNM press release 2026-05-01",
            date="2026-05-01",
        ),
        EpistemicClaim(
            tag=EpistemicTag.HYPOTHESIS.value,
            claim="MYR may strengthen if US Fed cuts rates",
        ),
        EpistemicClaim(
            tag=EpistemicTag.UNKNOWN.value,
            claim="Arif's risk tolerance not declared",
        ),
    ]
    violations = require_epistemic_tags(claims)
    assert violations == [], f"Valid claim set should have no violations: {violations}"


# ─── Registry Truth Audit Tests ─────────────────────────────────────────────


def test_registry_truth_audit_pass_with_all_callable():
    """Registry with all callable tools must return PASS."""
    from arifosmcp.core.kernel.tool_registry import ToolContractRegistry

    reg = ToolContractRegistry()
    reg.register_tool("tool_a", "A", {"parameters": {}})
    reg.register_tool("tool_b", "B", {"parameters": {}})
    # Both default to callable

    receipt = reg.audit_surface_truth()
    assert receipt["registry_truth"] == "PASS"
    assert receipt["f2_violation"] is False
    assert "safe_surface_hash" in receipt
    assert len(receipt["safe_surface_hash"]) == 32


def test_registry_truth_audit_fail_with_phantom():
    """Registry with phantom tools must return FAIL and flag f2_violation."""
    from arifosmcp.core.kernel.tool_registry import ToolContractRegistry

    reg = ToolContractRegistry()
    reg.register_tool("tool_real", "Real", {"parameters": {}})
    reg.register_tool("wealth_synthesize", "Phantom", {"parameters": {}})
    reg.mark_phantom("wealth_synthesize")

    receipt = reg.audit_surface_truth()
    assert receipt["registry_truth"] == "FAIL"
    assert "wealth_synthesize" in receipt["phantom_tools"]
    assert receipt["f2_violation"] is True


def test_registry_truth_audit_surface_hash_changes_on_mutation():
    """safe_surface_hash must change when callable surface changes."""
    from arifosmcp.core.kernel.tool_registry import ToolContractRegistry

    reg = ToolContractRegistry()
    reg.register_tool("tool_a", "A", {"parameters": {}})
    reg.register_tool("tool_b", "B", {"parameters": {}})

    receipt1 = reg.audit_surface_truth()
    reg.mark_phantom("tool_b")
    receipt2 = reg.audit_surface_truth()

    assert (
        receipt1["safe_surface_hash"] != receipt2["safe_surface_hash"]
    ), "Hash must change when callable surface changes"
