#!/usr/bin/env python3
"""
verify_tool_surface.py — Phase 1V Verification Harness.
8 checks to confirm tool surface integrity after schema + manifest changes.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from typing import Any

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭️ SKIP"

checks: list[dict[str, Any]] = []
_errors: list[str] = []


def check(name: str, result: bool, detail: str = "") -> None:
    icon = PASS if result else FAIL
    checks.append({"name": name, "passed": result, "detail": detail})
    print(f"  {icon} {name}")
    if detail and not result:
        print(f"       {detail}")


def get_mcp_tools() -> list[dict[str, Any]]:
    """Call tools/list on the running MCP server."""
    import http.client
    
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
    
    try:
        conn = http.client.HTTPConnection("127.0.0.1", 8088, timeout=5)
        conn.request("POST", "/mcp", body=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "mcp-session-id": "SEAL-verify-harness",
        })
        resp = conn.getresponse()
        body = resp.read().decode()
        data = json.loads(body)
        if "result" in data:
            return data["result"].get("tools", [])
        else:
            _errors.append(f"tools/list error: {data.get('error', body[:200])}")
            return []
    except Exception as e:
        _errors.append(f"tools/list HTTP error: {e}")
        return []


def get_health() -> dict[str, Any]:
    """Call /health endpoint."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:8088/health", timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        _errors.append(f"/health error: {e}")
        return {}


def verify_all() -> bool:
    """Run all 8 verification checks."""
    print("\n🔍 Verification Harness — arifOS Tool Surface Integrity")
    print("=" * 60)

    # C1: Live tools/list
    tools = get_mcp_tools()
    tool_names = [t["name"] for t in tools]
    check("C1: MCP server reachable", len(tools) > 0,
          f"Got {len(tools)} tools")

    if not tools:
        print("\n⚠️  MCP server unreachable. Running offline checks only.\n")
        # Still do declaration-based checks

    # C2: Canonical tools registered (core subset >= 13)
    canonical_core = [
        "arif_session_init", "arif_sense_observe", "arif_evidence_fetch",
        "arif_mind_reason", "arif_heart_critique", "arif_kernel_route",
        "arif_reply_compose", "arif_memory_recall", "arif_gateway_connect",
        "arif_judge_deliberate", "arif_vault_seal", "arif_forge_execute",
        "arif_ops_measure",
    ]
    if tools:
        found_canonical = sum(1 for n in canonical_core if n in tool_names)
        check("C2: Canonical tools registered (>= 13)", found_canonical >= 13,
              f"Found {found_canonical}/13+ canonical tools")

    # C3: Mode parameters have enum values
    if tools:
        enum_issues = []
        for t in tools:
            props = t.get("inputSchema", {}).get("properties", {})
            mode_schema = props.get("mode", {})
            if "enum" not in mode_schema:
                # Only flag if the tool has a mode parameter
                if "mode" in props:
                    enum_issues.append(t["name"])
        
        check("C3: Mode params have enum values", len(enum_issues) == 0,
              f"Tools missing enum: {', '.join(enum_issues[:5])}" if enum_issues else "")

    # C4: /health has split fields
    health = get_health()
    has_split = all(k in health for k in [
        "canonical_tools_loaded", "tools_exposed_via_mcp",
        "diagnostic_tools", "total_declared_tools",
    ])
    if health and has_split:
        check("C4: /health has canonical/diagnostic split", True,
              f"canonical_tools_loaded={health.get('canonical_tools_loaded')} "
              f"tools_exposed_via_mcp={health.get('tools_exposed_via_mcp')} "
              f"diagnostic_tools={health.get('diagnostic_tools')} "
              f"total_declared_tools={health.get('total_declared_tools')}")
    elif health:
        check("C4: /health has canonical/diagnostic split", False,
              f"Missing fields. Have: {list(health.keys())[:10]}...")
    else:
        check("C4: /health has canonical/diagnostic split", False,
              "/health unreachable")

    # C5: total_declared_tools >= tools_exposed_via_mcp
    if health and has_split:
        declared_total = health.get("total_declared_tools", 0)
        exposed = health.get("tools_exposed_via_mcp", 0)
        check("C5: total_declared >= exposed", declared_total >= exposed,
              f"declared={declared_total} vs exposed={exposed}")

    # C6: llms.txt hash matches manifest
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from scripts.generate_tool_manifest import manifest_hash, _canonical_tool_list, _operational_tool_list
        declared_canonical = len(_canonical_tool_list())
        declared_operational = len(_operational_tool_list())
        mhash = manifest_hash()
        
        # Check llms.txt exists
        llms_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llms.txt")
        if os.path.exists(llms_path):
            with open(llms_path) as f:
                content = f.read()
            has_hash_in_content = mhash in content
            check("C6: llms.txt contains manifest hash", has_hash_in_content,
                  f"Hash {mhash} {'found' if has_hash_in_content else 'NOT FOUND'} in llms.txt")
        else:
            check("C6: llms.txt exists", False, "File not found")
    except Exception as e:
        check("C6: llms.txt manifest check", False, str(e))
        declared_canonical = 19
        declared_operational = 37  # Fallback from constitutional_map.py DIAGNOSTIC_TOOLS

    # C7: Declaration counts are consistent
    check("C7: Registry counts sane",
          declared_canonical >= 13 and declared_operational > 0,
          f"Canonical: {declared_canonical} (expect >=13), Operational: {declared_operational} (expect >0)")

    # C8: tools/list count vs /health tools_exposed_via_mcp
    if tools and health and has_split:
        mcp_count = len(tools)
        health_count = health.get("tools_exposed_via_mcp", 0)
        check("C8: tools/list count == /health count", mcp_count == health_count,
              f"tools/list: {mcp_count}, /health: {health_count}")

    print("=" * 60)
    passed = sum(1 for c in checks if c["passed"])
    total_checks = len(checks)
    print(f"\n📊 Result: {passed}/{total_checks} checks passed")
    
    if _errors:
        print(f"\n⚠️  Errors: {len(_errors)}")
        for e in _errors:
            print(f"  • {e}")
    
    print()
    return passed == total_checks


if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
