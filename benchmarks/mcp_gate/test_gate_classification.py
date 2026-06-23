"""
MCP Gate v0 — Action Classification Benchmark

Tests: Does the gate correctly classify OBSERVE vs IRREVERSIBLE?
Each test submits a tool + risk profile and checks the verdict.

DITEMPA BUKAN DIBERI — Empirical evidence, not design claims.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from arifosmcp.gate.mcp_gate_v0 import judge_action, GateVerdict, ActionClass


# ── OBSERVE: Should always ALLOW ────────────────────────────────────────────


def test_read_tool_list():
    """OBSERVE: tools/list — should ALLOW without session."""
    result = judge_action(tool_name="tools/list", action_class="OBSERVE")
    assert result["verdict"] == GateVerdict.ALLOW.value, f"Expected ALLOW, got {result['verdict']}"
    assert result["action_class"] == ActionClass.OBSERVE.value


def test_read_health():
    """OBSERVE: health check — should ALLOW."""
    result = judge_action(tool_name="health", action_class="OBSERVE")
    assert result["verdict"] == GateVerdict.ALLOW.value, f"Expected ALLOW, got {result['verdict']}"


def test_suggest_no_session():
    """SUGGEST: should ALLOW_WITH_LOG even without session."""
    result = judge_action(tool_name="wealth_suggest_allocation", action_class="SUGGEST")
    assert result["verdict"] == GateVerdict.ALLOW_WITH_LOG.value, (
        f"Expected ALLOW_WITH_LOG, got {result['verdict']}"
    )


# ── IRREVERSIBLE: Should 888_HOLD ───────────────────────────────────────────


def test_vault_seal_irreversible():
    """IRREVERSIBLE: arif_vault_seal with session — should 888_HOLD."""
    result = judge_action(
        tool_name="arif_vault_seal", action_class="IRREVERSIBLE", session_active=True
    )
    assert result["verdict"] == GateVerdict.HOLD_888.value, (
        f"Expected HOLD_888, got {result['verdict']}"
    )


def test_vault_seal_no_session_blocks():
    """IRREVERSIBLE: arif_vault_seal without session — should BLOCK (session check first)."""
    result = judge_action(tool_name="arif_vault_seal", action_class="IRREVERSIBLE")
    assert result["verdict"] == GateVerdict.BLOCK.value, f"Expected BLOCK, got {result['verdict']}"


def test_vps_restart_irreversible():
    """IRREVERSIBLE: hostinger_vps_restart with session — should 888_HOLD."""
    result = judge_action(
        tool_name="hostinger_vps_restart", action_class="IRREVERSIBLE", session_active=True
    )
    assert result["verdict"] == GateVerdict.HOLD_888.value, (
        f"Expected HOLD_888, got {result['verdict']}"
    )


def test_docker_volume_remove_irreversible():
    """IRREVERSIBLE: docker_volume_remove with session — should 888_HOLD."""
    result = judge_action(
        tool_name="docker_volume_remove", action_class="IRREVERSIBLE", session_active=True
    )
    assert result["verdict"] == GateVerdict.HOLD_888.value, (
        f"Expected HOLD_888, got {result['verdict']}"
    )


def test_irreversible_first_then_session():
    """PRIORITY: Session check fires before irreversible check (safety-first)."""
    result = judge_action(tool_name="arif_vault_seal", action_class="IRREVERSIBLE")
    assert result["verdict"] == GateVerdict.BLOCK.value, "No session = BLOCK, not HOLD"
    assert "No active session" in result["reason"], "Reason must mention session"


# ── SIMULATE REQUIRED ──────────────────────────────────────────────────────


def test_geox_prospect_evaluate_needs_simulate():
    """SIMULATE: geox_prospect_evaluate without SIMULATE class — should SIMULATE_FIRST."""
    from arifosmcp.gate.mcp_gate_v0 import MCPGateV0

    gate = MCPGateV0()
    assert "geox_prospect_evaluate" in gate.SIMULATE_REQUIRED_TOOLS, (
        "Tool must be in SIMULATE_REQUIRED set"
    )
    result = judge_action(
        tool_name="geox_prospect_evaluate", action_class="EXECUTE_REVERSIBLE", session_active=True
    )
    assert result["verdict"] == GateVerdict.SIMULATE_FIRST.value, (
        f"Expected SIMULATE_FIRST, got {result['verdict']}"
    )


def test_simulate_class_allows():
    """SIMULATE: Running with action_class=SIMULATE should ALLOW."""
    result = judge_action(
        tool_name="geox_prospect_evaluate", action_class="SIMULATE", session_active=True
    )
    assert result["verdict"] in (GateVerdict.ALLOW.value, GateVerdict.ALLOW_WITH_LOG.value), (
        f"Expected ALLOW for SIMULATE class, got {result['verdict']}"
    )


# ── RISK-BASED GATING ──────────────────────────────────────────────────────


def test_physical_impact_requires_approval():
    """RISK: physical_impact=True + EXECUTE_REVERSIBLE — should REQUIRE_APPROVAL."""
    result = judge_action(
        tool_name="forge_execute",
        action_class="EXECUTE_REVERSIBLE",
        physical_impact=True,
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.REQUIRE_APPROVAL.value, (
        f"Expected REQUIRE_APPROVAL for physical impact, got {result['verdict']}"
    )


def test_financial_impact_high_requires_approval():
    """RISK: financial_impact=True + EXECUTE_HIGH_IMPACT — should REQUIRE_APPROVAL."""
    result = judge_action(
        tool_name="forge_execute",
        action_class="EXECUTE_HIGH_IMPACT",
        financial_impact=True,
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.REQUIRE_APPROVAL.value, (
        f"Expected REQUIRE_APPROVAL for financial impact, got {result['verdict']}"
    )


def test_dignity_impact_requires_approval():
    """RISK: dignity_impact=True — should REQUIRE_APPROVAL."""
    result = judge_action(
        tool_name="forge_execute",
        action_class="EXECUTE_REVERSIBLE",
        dignity_impact=True,
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.REQUIRE_APPROVAL.value, (
        f"Expected REQUIRE_APPROVAL for dignity impact, got {result['verdict']}"
    )


# ── DATA SENSITIVITY ────────────────────────────────────────────────────────


def test_confidential_data_logged():
    """RISK: confidential data — should ALLOW_WITH_LOG."""
    result = judge_action(
        tool_name="geox_basin_profile",
        action_class="OBSERVE",
        data_sensitivity="confidential",
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.ALLOW_WITH_LOG.value, (
        f"Expected ALLOW_WITH_LOG for confidential data, got {result['verdict']}"
    )


def test_restricted_data_logged():
    """RISK: restricted data — should ALLOW_WITH_LOG."""
    result = judge_action(
        tool_name="geox_basin_profile",
        action_class="OBSERVE",
        data_sensitivity="restricted",
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.ALLOW_WITH_LOG.value, (
        f"Expected ALLOW_WITH_LOG for restricted data, got {result['verdict']}"
    )


# ── BLAST RADIUS ────────────────────────────────────────────────────────────


def test_critical_blast_radius_requires_approval():
    """RISK: blast_radius=critical + EXECUTE_REVERSIBLE — should REQUIRE_APPROVAL."""
    result = judge_action(
        tool_name="forge_execute",
        action_class="EXECUTE_REVERSIBLE",
        blast_radius="critical",
        session_active=True,
    )
    assert result["verdict"] == GateVerdict.REQUIRE_APPROVAL.value, (
        f"Expected REQUIRE_APPROVAL for critical blast, got {result['verdict']}"
    )


# ── SESSION GATE ────────────────────────────────────────────────────────────


def test_no_session_blocks_mutation():
    """SESSION: no session + EXECUTE_REVERSIBLE — should BLOCK."""
    result = judge_action(tool_name="forge_execute", action_class="EXECUTE_REVERSIBLE")
    assert result["verdict"] == GateVerdict.BLOCK.value, (
        f"Expected BLOCK without session, got {result['verdict']}"
    )


def test_no_session_allows_observe():
    """SESSION: no session + OBSERVE — should ALLOW."""
    result = judge_action(tool_name="forge_execute", action_class="OBSERVE")
    assert result["verdict"] == GateVerdict.ALLOW.value, (
        f"Expected ALLOW for OBSERVE without session, got {result['verdict']}"
    )


# ── OUTPUT FORMAT ───────────────────────────────────────────────────────────


def test_output_has_lapisan_layers():
    """OUTPUT: Gate response has _summary (L1) and _detail (L2)."""
    result = judge_action(tool_name="arif_vault_seal", action_class="IRREVERSIBLE")
    assert "_summary" in result, "Missing Lapisan 1 (_summary)"
    assert "_detail" in result, "Missing Lapisan 2 (_detail)"
    assert isinstance(result["_summary"], str), "_summary must be string"
    assert isinstance(result["_detail"], str), "_detail must be string"


def test_one_line_summary():
    """OUTPUT: _summary is one line (no newlines)."""
    result = judge_action(tool_name="arif_vault_seal", action_class="IRREVERSIBLE")
    assert "\n" not in result["_summary"], "_summary must be one line"


# ── VERDICT: RUN ALL ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "tool,action,session,expected",
    [
        ("tools/list", "OBSERVE", False, GateVerdict.ALLOW.value),
        ("health", "OBSERVE", False, GateVerdict.ALLOW.value),
        ("arif_vault_seal", "IRREVERSIBLE", True, GateVerdict.HOLD_888.value),
        ("hostinger_vps_restart", "IRREVERSIBLE", True, GateVerdict.HOLD_888.value),
        ("arif_vault_seal", "IRREVERSIBLE", False, GateVerdict.BLOCK.value),  # no session = BLOCK
    ],
)
def test_parametrized_classification(tool, action, session, expected):
    """PARAMETRIZED: Verify common tool/action pairs."""
    result = judge_action(tool_name=tool, action_class=action, session_active=session)
    assert result["verdict"] == expected, (
        f"Tool={tool}, action={action}, session={session}: expected {expected}, got {result['verdict']}"
    )
