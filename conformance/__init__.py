"""
conformance/ — arifOS Negative Conformance Suite
═══════════════════════════════════════════════════

WAJIB 1: Every "must never happen" statement becomes a test.
Each test runs against the live kernel at ARIFOS_URL (default localhost:8088).

Run: pytest conformance/ -q --tb=short
Requires: arifOS kernel running, no session token needed for OBSERVE_ONLY tests.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import os
import pytest

ARIFOS_URL = os.environ.get("ARIFOS_URL", "http://localhost:8088")
MCP_URL = f"{ARIFOS_URL}/mcp"


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _call_tool(tool_name: str, arguments: dict, session_id: str | None = None) -> dict:
    """Call an MCP tool on the kernel. Returns parsed result dict."""
    import json
    import urllib.request

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
        },
    }
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["mcp-session-id"] = session_id

    req = urllib.request.Request(
        MCP_URL, data=json.dumps(payload).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"_error": str(e)}


def _init_session(actor_id: str = "conformance-test") -> dict:
    """Initialize a session and return the parsed result."""
    response = _call_tool("arif_init", {"mode": "init", "actor_id": actor_id})
    content = response.get("result", {}).get("content", [])
    for item in content:
        text = item.get("text", "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return response
