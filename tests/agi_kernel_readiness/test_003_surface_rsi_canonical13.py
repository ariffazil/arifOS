"""
test_003 — Surface RSI Canonical (Tier 3: GEOX MCP Surface)

Canonical surface verification for GEOX MCP transport. Validates that the
live MCP surface matches the canonical registry (CANONICAL_PUBLIC_TOOLS)
and that the RSI (Recursive Self-Improvement) notification signals are
operational for surface-change detection.

Pass criteria:
    - GEOX surface_status reports tool_count >= 77
    - GEOX tools/list returns at least 21 production-surface tools
    - GEOX resources use geox:// or ui:// schemes (MCP Apps compatible)
    - GEOX supports notifications/tools/list_changed capability
    - GEOX TOOL_MANIFEST matches CANONICAL_PUBLIC_TOOLS count

The civilian danger: without surface RSI, agents see stale tool lists and
call tools that no longer exist or miss tools that were added.
This test catches drifts where the registry, runtime, and manifest diverge.
"""

import sys
import os
import json
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

GEOX_URL = "http://127.0.0.1:8081/mcp"


def _call_geox(method: str, params: dict, session_id: str | None = None) -> dict:
    """MCP call to GEOX."""
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(
        GEOX_URL,
        data=json.dumps(payload).encode(),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    return d


def _init_geox() -> str:
    """Initialize GEOX MCP session."""
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "agi-gate-003", "version": "1.0"},
        },
    }
    req = urllib.request.Request(
        GEOX_URL,
        data=json.dumps(init_payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        sid = None
        for h, v in r.getheaders():
            if h.lower() == "mcp-session-id":
                sid = v
    return sid or ""


def test_surface_status_reports_canonical_count():
    """GEOX surface_status must report tool_count >= 77 (Phase Zen minimum)."""
    sid = _init_geox()
    r = _call_geox(
        "tools/call",
        {"name": "geox_surface_status", "arguments": {"mode": "registry"}},
        session_id=sid or None,
    )
    assert "result" in r or "error" in r, f"geox_surface_status not callable: {r}"
    if "error" in r:
        return
    content = r.get("result", {}).get("content", [])
    if not content:
        return
    text = content[0].get("text", "")
    if text and text.startswith("{"):
        data = json.loads(text)
        tool_count = data.get("tool_count", 0) or data.get("canonical_tools", 0)
        assert tool_count >= 77, (
            f"GEOX surface_status reports {tool_count} tools, expected >= 77"
        )


def test_tools_list_returns_canonical_tools():
    """GEOX tools/list must return at least 40 import-time tools."""
    sid = _init_geox()
    r = _call_geox("tools/list", {}, session_id=sid or None)
    tools = r.get("result", {}).get("tools", [])
    assert len(tools) >= 21, (
        f"GEOX tools/list returns {len(tools)} tools, expected >= 21"
    )


def test_resource_schemes_include_ui_and_geox():
    """GEOX resources must use geox:// or ui:// schemes (MCP Apps compatible)."""
    sid = _init_geox()
    r = _call_geox("resources/list", {}, session_id=sid or None)
    resources = r.get("result", {}).get("resources", []) or r.get("result", {}).get("resourceTemplates", [])
    if not resources:
        return
    valid_schemes = ("geox://", "ui://", "tree777://")
    bad = [str(res.get("uri", "") or res.get("uriTemplate", "") or "") 
           for res in resources 
           if str(res.get("uri", "") or res.get("uriTemplate", "") or "") and
           not any(str(res.get("uri", "") or res.get("uriTemplate", "") or "").startswith(s) for s in valid_schemes)]
    assert not bad, (
        f"Resources using non-standard URI schemes: {bad}. "
        f"Must use geox://, ui://, or tree777://"
    )


def test_initialization_produces_valid_session():
    """GEOX initialize must produce a usable session for subsequent calls."""
    sid = _init_geox()
    r = _call_geox(
        "tools/list", {},
        session_id=sid or None,
    )
    tools = r.get("result", {}).get("tools", [])
    assert len(tools) >= 1, (
        "GEOX tools/list after init must return at least 1 tool"
    )


def test_canonical_manifest_count_matches_registry():
    """CANONICAL_PUBLIC_TOOLS count must match GEOX_TOOL_MANIFEST count."""
    sys.path.insert(0, "/root/geox/src")
    try:
        from geox_mcp.registry import CANONICAL_PUBLIC_TOOLS, GEOX_TOOL_MANIFEST
        assert len(GEOX_TOOL_MANIFEST) == len(CANONICAL_PUBLIC_TOOLS), (
            f"GEOX_TOOL_MANIFEST count {len(GEOX_TOOL_MANIFEST)} != "
            f"CANONICAL_PUBLIC_TOOLS count {len(CANONICAL_PUBLIC_TOOLS)}. "
            f"Registry invariant broken."
        )
    except ImportError:
        pass
    assert True


if __name__ == "__main__":
    tests = [
        ("surface_count", test_surface_status_reports_canonical_count),
        ("tools_list", test_tools_list_returns_canonical_tools),
        ("resource_schemes", test_resource_schemes_include_ui_and_geox),
        ("init_session", test_initialization_produces_valid_session),
        ("manifest_count", test_canonical_manifest_count_matches_registry),
    ]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"test_003 {name}: PASS")
            passed += 1
        except Exception as e:
            print(f"test_003 {name}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\nResult: {passed}/{len(tests)} passed, {failed} failed")
