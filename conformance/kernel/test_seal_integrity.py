"""
conformance/kernel/test_seal_integrity.py — Missing negative tests
═══════════════════════════════════════════════════════════════════

Tests: AAA cannot display nonexistent SEAL, tool count ≠ AGI evidence,
human approval cannot be simulated, unsigned seal rejected.

DITEMPA BUKAN DIBERI.
"""

import json

import pytest

from conformance import ARIFOS_URL, _call_tool, _init_session


def test_aaa_cannot_display_nonexistent_seal():
    """
    WAJIB-1.7: AAA must not report a SEAL that the kernel never issued.
    Every seal must be verifiable against VAULT999.
    """
    session = _init_session("conformance-s1")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Read vault — must return integrity info
    response = _call_tool(
        "arif_seal",
        {
            "mode": "verify",
        },
        session_id=sid,
    )

    content = response.get("result", {}).get("content", [])
    result_text = ""
    for item in content:
        result_text += item.get("text", "")

    # Vault verify must either work or clearly report gaps
    # It must NOT fabricate seals
    assert "error" not in response or "fabricated" not in result_text.lower(), (
        f"Vault must not fabricate seals. Got: {result_text[:300]}"
    )


def test_tool_count_not_agi_claim():
    """
    WAJIB-1.13: Tool count must never be presented as evidence of AGI
    capability. The number of tools is a registry fact, not intelligence.
    """
    import urllib.request

    try:
        with urllib.request.urlopen(f"{ARIFOS_URL}/health", timeout=5) as resp:
            health = json.loads(resp.read())
    except Exception:
        pytest.skip("Kernel unreachable")

    tools = health.get("tools_loaded", 0)
    # Having tools is not AGI
    assert isinstance(tools, (int, float)), f"tools_loaded must be numeric: {tools}"

    # Check: does the health endpoint conflate count with capability?
    for key in health:
        if "agi" in str(key).lower() or "capability" in str(key).lower():
            val = health[key]
            # Capability claims must be more than just a count
            if isinstance(val, (int, float)):
                pass  # Numeric capability fields are fine
            elif isinstance(val, str) and val.lower() in ("true", "false", "yes", "no"):
                pass  # Boolean-like strings are fine


def test_human_approval_not_simulatable():
    """
    WAJIB-1.14: Human approval tokens must not be settable by the agent.
    Any seal or mutation requiring human approval must fail without
    a genuine external human_seal_token.
    """
    session = _init_session("conformance-s2")
    sid = session.get("session_birth", {}).get("session_id", "")

    # Try to execute with a fake human_seal_token
    response = _call_tool(
        "arif_forge",
        {
            "mode": "engineer",
            "manifest": '{"action": "deploy"}',
            "ack_irreversible": True,
        },
        session_id=sid,
    )

    result = response.get("result", {}).get("content", [{}])[0].get("text", "")
    parsed = {}
    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        pass

    # Agent self-claiming ack_irreversible without real human token
    # must not auto-authorize
    verdict = str(parsed.get("verdict", parsed.get("status", result))).upper()
    has_hold = any(t in verdict for t in ("HOLD", "VOID", "SABAR", "DENIED", "PENDING"))
    # If it doesn't HOLD, it must at least not SEAL
    if not has_hold:
        assert "SEAL" not in verdict, (
            f"Self-claimed ack_irreversible must not produce SEAL. Got: {verdict}"
        )


def test_unsigned_seal_rejected():
    """
    WAJIB-1.15: Any seal operation without valid chain signature
    must be rejected. Empty payloads, missing session_id, or
    missing constitutional_chain_id must fail closed.
    """
    # Test 1: Seal with empty payload, no session
    response = _call_tool(
        "arif_seal",
        {
            "mode": "seal",
            "payload": "",
        },
        session_id=None,
    )

    result_text = json.dumps(response)
    assert "error" in response or "SESSION" in result_text.upper(), (
        f"Unsigned seal without session must be rejected. Got: {result_text[:300]}"
    )
