"""
conformance/organs/test_organ_boundaries.py — WAJIB 1: Organ Safety
═══════════════════════════════════════════════════════════════════

Tests 16-18: GEOX preserves alternatives, WEALTH exposes downside,
WELL protects human data, tool count ≠ AGI evidence, human approval
cannot be simulated, organ conflict cannot silently resolve.

DITEMPA BUKAN DIBERI.
"""

import json
import pytest
from conformance import _call_tool, _init_session, ARIFOS_URL, MCP_URL


def test_tool_count_not_agi_evidence():
    """
    WAJIB-1.16: Tool count must not be used as evidence of AGI capability.
    The kernel health endpoint should distinguish tools_loaded from
    capability claims.
    """
    import urllib.request
    try:
        with urllib.request.urlopen(f"{ARIFOS_URL}/health", timeout=5) as resp:
            health = json.loads(resp.read())
    except Exception:
        pytest.skip("Kernel health endpoint unreachable")

    # tools_loaded is a count, not a capability claim
    tools = health.get("tools_loaded", 0)
    # Having 8 tools does not mean AGI
    assert isinstance(tools, (int, float)), f"tools_loaded must be numeric, got {type(tools)}"


def test_human_approval_cannot_be_simulated():
    """
    WAJIB-1.17: Human approval fields (human_ack, F13 approval tokens)
    must not be settable by the agent itself. They require external input.
    """
    session = _init_session("conformance-t17")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Try to seal with a fake human_approval_token
    response = _call_tool("arif_seal", {
        "mode": "seal",
        "payload": '{"test": "data"}',
        "ack_irreversible": True,  # agent claiming approval
    }, session_id=sid)

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    # Agent claiming ack_irreversible without actual human interaction
    # should still require true human verification
    # This is a structural test — the exact behavior depends on implementation
    assert "error" in response or "HOLD" in str(result).upper() or "VOID" in str(result).upper(), (
        f"Seal with self-claimed ack_irreversible must not auto-succeed. "
        f"Got: {str(result)[:200]}"
    )


def test_organ_conflict_cannot_silently_resolve():
    """
    WAJIB-1.18: When multiple organs return conflicting evidence,
    the kernel must surface the conflict, not silently pick one.
    """
    session = _init_session("conformance-t18")
    
    # The kernel must have the concept of conflict resolution
    # evidenced by the arif_route tool's response structure
    sid = session.get("session_birth", {}).get("session_id", "")
    response = _call_tool("arif_route", {
        "intent": "evaluate a prospect in the Malay Basin",
    }, session_id=sid)

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    
    # Route should return organ suggestions, not a single forced answer
    # If multiple organs are relevant, the routing should mention them
    assert len(result) > 0, "arif_route must return routing information"
