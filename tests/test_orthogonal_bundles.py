"""
Tests for Orthogonal Hypervisor Bundles (AGI, ASI, APEX).
Verifies that the bundles correctly implement F1-F12 consolidation.
"""
import asyncio

import pytest

from arifos_core.mcp.models import (AgiThinkRequest, ApexAuditRequest,
                                    AsiActRequest, VerdictResponse)
from arifos_core.mcp.tools.bundles import agi_think, apex_audit, asi_act

# =============================================================================
# AGI (THINK) TESTS
# =============================================================================

def test_agi_think_hard_lane():
    """Test AGI processes hard factual query."""
    req = AgiThinkRequest(query="Calculate 100 times 50")
    res = asyncio.run(agi_think(req))

    assert res.verdict == "PASS"
    assert res.side_data["lane"] == "HARD"
    assert res.side_data["truth_threshold"] >= 0.90
    assert "Thinking about" in res.side_data["thought_process"]

def test_agi_think_phatic():
    """Test AGI processes phatic query."""
    req = AgiThinkRequest(query="Hello there, how are you?")
    res = asyncio.run(agi_think(req))

    assert res.verdict == "PASS"
    assert res.side_data["lane"] == "PHATIC"

# =============================================================================
# ASI (ACT) TESTS
# =============================================================================

def test_asi_act_safe():
    """Test ASI allows safe draft."""
    req = AsiActRequest(draft_response="I am happy to help you with that.")
    res = asyncio.run(asi_act(req))

    assert res.verdict == "PASS"
    assert res.side_data["peace_score"] >= 1.1

def test_asi_act_aggressive_veto():
    """Test ASI vetoes aggressive content (F5)."""
    req = AsiActRequest(draft_response="Shut up you idiot.")
    res = asyncio.run(asi_act(req))

    assert res.verdict == "VOID"
    assert "F5 Peace" in res.reason

def test_asi_act_credential_veto():
    """Test ASI vetoes credential exposure (F1)."""
    req = AsiActRequest(draft_response="Here is my API key: sk-12345abcdef12345abcdef12345abcdef")
    res = asyncio.run(asi_act(req))

    assert res.verdict == "VOID"
    assert "Constitutional Veto" in res.reason
    assert "credentials" in res.side_data["violations"]

# =============================================================================
# APEX (AUDIT) TESTS
# =============================================================================

def test_apex_audit_seal():
    """Test APEX seals when all conditions met."""
    agi_out = {"verdict": "PASS", "side_data": {"thought_process": "Plan A"}}
    asi_out = {"verdict": "PASS", "side_data": {"peace_score": 1.1}}
    # Strong evidence (3 sources)
    evidence = {"sources": ["A", "B", "C"]}

    req = ApexAuditRequest(
        agi_thought=agi_out,
        asi_veto=asi_out,
        evidence_pack=evidence
    )
    res = asyncio.run(apex_audit(req))

    assert res.verdict == "SEAL"
    assert res.side_data["convergence"] >= 0.95
    assert res.side_data["proof_hash"] is not None

def test_apex_audit_asi_fail():
    """Test APEX voids if ASI failed."""
    agi_out = {"verdict": "PASS"}
    asi_out = {"verdict": "VOID", "reason": "Harmful"}
    evidence = {"sources": ["A", "B", "C"]}

    req = ApexAuditRequest(
        agi_thought=agi_out,
        asi_veto=asi_out,
        evidence_pack=evidence
    )
    res = asyncio.run(apex_audit(req))

    assert res.verdict == "VOID"
    assert "ASI Safety Veto" in res.reason
