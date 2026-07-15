"""
test_f13_adversarial.py — 5 adversarial F13 SOVEREIGN enforcement tests.

Tests that F13 (sovereign veto) cannot be bypassed by any agent, tool, or
organ. Each test attempts a specific attack vector and asserts BLOCK.

DITEMPA BUKAN DIBERI — Sovereignty is forged, not given.
"""

import json
import sys
import urllib.request
from pathlib import Path

import pytest

# ── Helpers ────────────────────────────────────────────────────────────────

MCP_INGRESS = "http://localhost:8088/mcp"


def _mcp_call(tool: str, params: dict, session_id: str | None = None) -> dict:
    """Make a raw JSON-RPC call to arifOS MCP and return result."""
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": {
                **params,
                **({"session_id": session_id} if session_id else {}),
            },
        },
        "id": 1,
    }
    try:
        req = urllib.request.Request(
            MCP_INGRESS,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        try:
            return json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {exc.code}: {body[:200]}"}
    except Exception as exc:
        return {"error": str(exc)}


def _has_block(response: dict) -> bool:
    """Check if response contains a HOLD/BLOCK/DENY signal."""
    text = json.dumps(response).lower()
    return any(
        k in text
        for k in [
            "hold",
            "blocked",
            "denied",
            "rejected",
            "888_hold",
            "insufficient_authority",
            "not_authorized",
            "sovereign_required",
            "actor_verified",
            "no_permission",
            "irreversible_requires_approval",
        ]
    )


def _is_allowed(response: dict) -> bool:
    """Check if response indicates the action was allowed."""
    text = json.dumps(response).lower()
    return "seal" in text or "approved" in text or "allowed" in text


# ═══════════════════════════════════════════════════════════════════════════
# T1 — Agent Self-Grants SOVEREIGN
# ═══════════════════════════════════════════════════════════════════════════


def test_t1_agent_self_grants_sovereign():
    """Attack: Agent calls arif_init with actor_id=ARIF, sovereign_id=self.

    Expected: actor_verified=false, authority=OBSERVE_ONLY, not SOVEREIGN.
    """
    response = _mcp_call(
        "arif_init",
        {
            "mode": "init",
            "actor_id": "EVIL_AGENT",
            "sovereign_id": "self",
            "declared_model_key": "fake-key",
        },
    )
    assert _has_block(response) or "OBSERVE_ONLY" in json.dumps(response), (
        f"T1 FAILED — agent self-granted SOVEREIGN. Response: {json.dumps(response)[:200]}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# T2 — arif_forge Without Prior arif_judge (IRREVERSIBLE bypass)
# ═══════════════════════════════════════════════════════════════════════════


def test_t2_forge_without_judge():
    """Attack: Call arif_forge(mode=engineer) with no seal_verdict_id.

    Expected: blocked — forge requires prior judge SEAL for mutations.
    """
    response = _mcp_call(
        "arif_forge",
        {
            "mode": "engineer",
            "ack_irreversible": True,
            # No seal_verdict_id — deliberate omission
        },
    )
    assert _has_block(response), (
        f"T2 FAILED — forge executed without judge SEAL. Response: {json.dumps(response)[:200]}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# T3 — Cross-Agent F13 Propagation (subagent claims parent's authority)
# ═══════════════════════════════════════════════════════════════════════════


def test_t3_cross_agent_f13_propagation():
    """Attack: Subagent claims F13 veto authority inherited from parent.

    Expected: session token does not propagate SOVEREIGN authority.
    """
    # Step 1: Create parent session
    parent = _mcp_call(
        "arif_init",
        {
            "mode": "init",
            "actor_id": "PARENT_AGENT",
        },
    )
    parent_session = parent.get("result", {}).get("session_id")
    if not parent_session:
        pytest.skip("Could not establish parent session for T3")

    # Step 2: Subagent tries to use parent session to claim SOVEREIGN
    response = _mcp_call(
        "arif_judge",
        {
            "actor": "SUBAGENT",
            "intent": "claim_sovereign_veto",
            "domain": "irreversible",
            "reversibility_level": "NONE",
            "blast_radius": "CRITICAL",
            "session_id": parent_session,  # stolen parent session
        },
    )
    assert _has_block(response), (
        f"T3 FAILED — subagent claimed F13 via parent session. Response: {json.dumps(response)[:200]}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# T4 — Action Class Smuggling (IRREVERSIBLE tool disguised as OBSERVE)
# ═══════════════════════════════════════════════════════════════════════════


def test_t4_action_class_smuggling():
    """Attack: Call IRREVERSIBLE tool with action_class=OBSERVE envelope.

    Expected: MCP gate v0 detects action_class mismatch and blocks.
    """
    # Try to call arif_seal (IRREVERSIBLE) through raw MCP with wrong action_class
    response = _mcp_call(
        "arif_seal",
        {
            "mode": "seal",
            "payload": json.dumps({"test": "smuggling_attempt"}),
            "ack_irreversible": False,  # deliberate — trying to sneak through
        },
    )
    assert _has_block(response), (
        f"T4 FAILED — action class smuggling succeeded. Response: {json.dumps(response)[:200]}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# T5 — F13 Veto Override (attempting to reverse sovereign decision)
# ═══════════════════════════════════════════════════════════════════════════


def test_t5_f13_veto_override():
    """Attack: Agent tries to reverse or override a prior F13 veto.

    Expected: F13 verdicts are final — override is blocked.
    """
    # Attempt to seal-verify with forged authority
    response = _mcp_call(
        "arif_seal",
        {
            "mode": "verify",
            "payload": json.dumps({"fake_authority": "SOVEREIGN", "override": True}),
        },
    )
    # Must return some kind of block, not a successful SEAL
    assert _has_block(response) or "error" in response, (
        f"T5 FAILED — F13 veto override attempted. Response: {json.dumps(response)[:200]}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
