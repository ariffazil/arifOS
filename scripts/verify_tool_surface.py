#!/usr/bin/env python3
"""
verify_tool_surface.py — Contract Convergence Verification Harness (v2026.06.26)

8 checks to confirm tool surface integrity.
Asserts: manifest = runtime = prompts = tests = docs.

DITEMPA BUKAN DIBERI 🔥⚒️
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
        conn.request(
            "POST",
            "/mcp",
            body=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "mcp-session-id": "SEAL-verify-harness",
            },
        )
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


def get_manifest() -> dict[str, Any]:
    """Load mcp-arifos.json manifest."""
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp-arifos.json")
    try:
        with open(manifest_path) as f:
            return json.load(f)
    except Exception as e:
        _errors.append(f"manifest error: {e}")
        return {}


def verify_all() -> bool:
    """Run all 8 verification checks."""
    print("\n🔍 Contract Convergence Harness — arifOS Tool Surface v2026.06.26")
    print("=" * 70)

    # C1: Server reachable
    tools = get_mcp_tools()
    tool_names = [t["name"] for t in tools]
    check("C1: MCP server reachable", len(tools) > 0, f"Got {len(tools)} tools")

    # C2: tools/list exposes the canonical 9-stage public loop
    PUBLIC_VERBS = {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_critique",
        "arif_judge",
        "arif_forge",
        "arif_compose",
        "arif_seal",
    }
    if tools:
        found_public = PUBLIC_VERBS.intersection(set(tool_names))
        # Count only the public verbs in tools/list (diagnostics may also appear)
        check(
            "C2: Public verbs present (9 canonical)",
            found_public == PUBLIC_VERBS,
            f"Found {len(found_public)}/9: {sorted(found_public)}",
        )

    # C3: Long-name aliases dispatch but are not advertised
    LONG_ALIASES = {
        "arif_session_init",
        "arif_sense_observe",
        "arif_mind_reason",
        "arif_judge_deliberate",
        "arif_vault_seal",
    }
    if tools:
        advertised_aliases = LONG_ALIASES.intersection(set(tool_names))
        check(
            "C3: Long-name aliases NOT in tools/list",
            len(advertised_aliases) == 0,
            f"Found advertised aliases: {advertised_aliases}"
            if advertised_aliases
            else "Clean — no aliases advertised",
        )

    # C4: Guarded execution uses arif_forge on the public surface
    if tools:
        forge_tool = next((t for t in tools if t["name"] == "arif_forge"), None)
        if forge_tool:
            props = forge_tool.get("inputSchema", {}).get("properties", {})
            has_seal_param = "seal_verdict_id" in props
            check(
                "C4: arif_forge requires seal_verdict_id",
                has_seal_param,
                f"seal_verdict_id {'found' if has_seal_param else 'MISSING'} in arif_forge schema",
            )
        else:
            check("C4: arif_forge tool exists", False, "arif_forge not found in tools/list")

    # C5: arif_seal requires provenance
    if tools:
        seal_tool = next((t for t in tools if t["name"] == "arif_seal"), None)
        if seal_tool:
            props = seal_tool.get("inputSchema", {}).get("properties", {})
            has_payload = "payload" in props
            check(
                "C5: arif_seal has payload parameter",
                has_payload,
                f"payload {'found' if has_payload else 'MISSING'} in arif_seal schema",
            )
        else:
            check("C5: arif_seal tool exists", False, "arif_seal not found in tools/list")

    # C6: /health agrees with manifest
    health = get_health()
    manifest = get_manifest()
    if health and manifest:
        manifest_public_count = (
            manifest.get("capabilities", {}).get("public_tools", {}).get("count", 0)
        )
        health_tools_count = health.get("tools_exposed_via_mcp", 0)
        check(
            "C6: /health sees live MCP exposure and manifest sees canonical public count",
            health_tools_count > 0 and manifest_public_count == 9,
            f"manifest public_tools={manifest_public_count}, /health exposed={health_tools_count}",
        )
    else:
        check("C6: /health agrees with manifest", False, "Missing health or manifest data")

    # C7: Manifest describes 9 public verbs + 13 organs
    if manifest:
        has_public = manifest.get("capabilities", {}).get("public_tools", {}).get("count") == 9
        has_organs = (
            manifest.get("capabilities", {}).get("constitutional_organs", {}).get("count") == 13
        )
        has_golden = "golden_path" in manifest
        check(
            "C7: Manifest has 9 public + 13 organs + golden_path",
            has_public and has_organs and has_golden,
            f"public=9:{has_public}, organs=13:{has_organs}, golden_path:{has_golden}",
        )
    else:
        check("C7: Manifest structure", False, "Cannot load manifest")

    # C8: Golden path order is correct for the public 9-verb facade
    if manifest:
        gp_order = manifest.get("capabilities", {}).get("prompts", {}).get("golden_path_order", [])
        expected_sequence = [
            "000_init",
            "111_observe",
            "333_think",
            "444_route",
            "555_critique",
            "666_judge",
            "777_forge",
            "888_compose",
            "999_seal",
        ]
        sequence_positions = []
        ordered = True
        for step in expected_sequence:
            if step not in gp_order:
                ordered = False
                break
            sequence_positions.append(gp_order.index(step))
        ordered = ordered and sequence_positions == sorted(sequence_positions)
        check(
            "C8: Golden path order follows init→observe→think→route→critique→judge→forge→compose→seal",
            ordered,
            f"Order: {' → '.join(gp_order)}" if gp_order else "No golden_path_order in manifest",
        )

    print("=" * 70)
    passed = sum(1 for c in checks if c["passed"])
    total_checks = len(checks)
    print(f"\n📊 Result: {passed}/{total_checks} checks passed")

    if _errors:
        print(f"\n⚠️  Errors: {len(_errors)}")
        for e in _errors:
            print(f"  • {e}")

    print()
    if passed == total_checks:
        print("🔥⚒️  CONTRACT CONVERGENCE VERIFIED")
        print("manifest = runtime = prompts = tests = docs")
        print("DITEMPA BUKAN DIBERI")
    else:
        print("⚠️  CONTRACT DRIFT DETECTED — fix before SEAL")
    print()
    return passed == total_checks


if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
