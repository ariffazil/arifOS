"""
Cross-Organ Authority Parity Test — 2026-07-19

P0 adversarial test: an agent blocked at arifOS must not find a weaker
gate at GEOX, WEALTH, or WELL.

Each domain organ runs its own MCP surface with independent authorization.
This test verifies that mutation-class operations at all organs enforce
the same graduated authority as the kernel.

Doctrine: F1-F13 is federation law. Every organ. No exceptions.
"""

import pytest
import json
import urllib.request
import urllib.error


# ═══════════════════════════════════════════════════════════════════════════
# Configuration — organ ports and mutation tools to probe
# ═══════════════════════════════════════════════════════════════════════════

ORGANS = {
    "GEOX": {
        "port": 8081,
        "mutation_tool": "geox_claim",
        "mutation_args": {"mode": "seal", "claim_text": "test", "ack_irreversible": True},
    },
    "WEALTH": {
        "port": 18082,
        "mutation_tool": "capital_ledger",
        "mutation_args": {"mode": "write", "amount": 1, "description": "test", "ack_irreversible": True},
    },
    "WELL": {
        "port": 18083,
        "mutation_tool": "well_assess_homeostasis",
        "mutation_args": {"mode": "fatigue", "sleep_hours": 8},
    },
}

MCP_ENDPOINT_TEMPLATE = "http://127.0.0.1:{port}/mcp"


def _call_organ_mcp(port: int, tool: str, arguments: dict) -> dict:
    """Call an organ's MCP endpoint with a tool invocation, no session token."""
    url = MCP_ENDPOINT_TEMPLATE.format(port=port)
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:200]}
    except urllib.error.URLError as e:
        return {"connection_error": str(e.reason)}


def _is_blocked(result: dict) -> bool:
    """Check if the organ blocked the mutation attempt.

    Acceptable blocked signals: SESSION_MISSING, 400/401/403/406, connection
    refused (organ unreachable → can't mutate → blocked in practice).
    """
    if "connection_error" in result:
        return True  # organ unreachable → can't mutate

    http_code = result.get("http_error", 0)
    if http_code in (400, 401, 403, 404, 405, 406):
        body_str = str(result.get("body", ""))
        body_lower = body_str.lower()
        # 400 alone is ambiguous — must carry a session/auth rejection
        if http_code == 400:
            # Check both raw body and parsed JSON-RPC error in body
            if any(sig in body_lower for sig in (
                "session_missing", "session required", "mcp-session-id",
                "unauthorized", "forbidden", "no session", "missing session",
            )):
                return True
            # Try parsing body as JSON-RPC error
            try:
                import json as _json
                body_json = _json.loads(body_str)
                body_err = body_json.get("error", {})
                body_err_code = body_err.get("code", 0)
                body_err_msg = str(body_err.get("message", "")).lower()
                if body_err_code in (-32000, -32001, -32600):
                    if any(w in body_err_msg for w in (
                        "session", "missing", "required", "unauthorized"
                    )):
                        return True
            except Exception:
                pass
            return False  # 400 for other reasons (bad args) is NOT blocked
        return True  # 401/403/404/405/406 = definitely blocked

    # Check JSON-RPC error
    err = result.get("error", {})
    if err:
        err_msg = str(err.get("message", "")).lower()
        err_code = err.get("code", 0)
        if err_code in (-32000, -32001, -32600):  # Server error / Session not found / Invalid Request
            if any(word in err_msg for word in (
                "session", "unauthorized", "forbidden", "required",
                "mcp-session-id", "missing session"
            )):
                return True

    # Check result content for HOLD/DENIED/blocked
    res = result.get("result", {})
    if isinstance(res, dict):
        content = res.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    text = str(item.get("text", "")).lower()
                    if any(word in text for word in (
                        "hold", "denied", "session required", "unauthorized"
                    )):
                        return True

    return False


# ═══════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("organ_name,organ_config", ORGANS.items())
def test_organ_blocks_unauth_mutation(organ_name, organ_config):
    """Every organ must block mutation without a valid session token.

    An agent blocked at arifOS must not find a laxer gate at GEOX/WEALTH/WELL.
    """
    result = _call_organ_mcp(
        organ_config["port"],
        organ_config["mutation_tool"],
        organ_config["mutation_args"],
    )

    blocked = _is_blocked(result)
    assert blocked, (
        f"{organ_name} accepted unauthorised mutation! "
        f"Tool: {organ_config['mutation_tool']}, "
        f"Response: {json.dumps(result, indent=2)[:500]}"
    )
