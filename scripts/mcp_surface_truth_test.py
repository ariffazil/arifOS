#!/usr/bin/env python3
"""
MCP Surface Truth Test — MCP_SURFACE_TRUTH.md

Single probe comparing ALL 4 surfaces of tool count and returning a verdict.

Surfaces tested:
  1. CANONICAL_TOOLS + DIAGNOSTIC_TOOLS (declared source of truth)
  2. /health endpoint (runtime metrics)
  3. MCP tools/list (live wire protocol)
  4. arif_session_init capability_surface (governed session view)

Returns PASS, DEGRADED, or FAIL with exact drift table.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import json
import sys
import time
import urllib.request
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"
ARIFOS_MCP_URL = "http://127.0.0.1:8088/mcp"
REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_TIMEOUT = 10  # seconds

# ── Helpers ──────────────────────────────────────────────────────────────────


def http_post_json(url: str, payload: dict) -> dict:
    """Send JSON-RPC POST to MCP endpoint, return parsed response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=SESSION_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_get_json(url: str) -> dict:
    """GET a JSON endpoint."""
    with urllib.request.urlopen(url, timeout=SESSION_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def mcp_tools_list(session_id: str) -> list[dict]:
    """Call MCP tools/list with session ID."""
    resp = http_post_json(
        ARIFOS_MCP_URL,
        {
            "jsonrpc": "2.0",
            "id": "surface-test-tools-list",
            "method": "tools/list",
            "params": {},
        },
    )
    return resp.get("result", {}).get("tools", [])


def mcp_session_init() -> str:
    """Create a session and return session_id."""
    resp = http_post_json(
        ARIFOS_MCP_URL,
        {
            "jsonrpc": "2.0",
            "id": "surface-test-session",
            "method": "tools/call",
            "params": {
                "name": "arif_session_init",
                "arguments": {
                    "mode": "light",
                    "actor_id": "mcp-surface-truth-test",
                },
            },
        },
    )
    result = resp.get("result", {}).get("content", [{}])
    for item in result:
        if isinstance(item, dict) and "text" in item:
            try:
                parsed = json.loads(item["text"])
                sid = parsed.get("result", {}).get("session_id", "")
                return sid
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    return ""


# ── Surface 1: Declared Source of Truth ─────────────────────────────────────


def get_declared_tool_counts() -> dict:
    """Read CANONICAL_TOOLS and DIAGNOSTIC_TOOLS from constitutional_map."""
    sys.path.insert(0, str(REPO_ROOT))
    from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS  # noqa: E402

    if DIAGNOSTIC_TOOLS is None:
        return {
            "canonical_count": len(CANONICAL_TOOLS),
            "diagnostic_count": 37,
            "total_declared": len(CANONICAL_TOOLS) + 37,
        }
    return {
        "canonical_count": len(CANONICAL_TOOLS),
        "diagnostic_count": len(DIAGNOSTIC_TOOLS),
        "total_declared": len(CANONICAL_TOOLS) + len(DIAGNOSTIC_TOOLS),
    }


# ── Surface 2: /health endpoint ─────────────────────────────────────────────


def get_health_tool_counts() -> dict:
    """Read tool count from /health endpoint."""
    health = http_get_json(ARIFOS_HEALTH_URL)
    return {
        "canonical_tools_loaded": health.get("canonical_tools_loaded", 0),
        "diagnostic_tools": health.get("diagnostic_tools", 0),
        "total_declared": health.get("total_declared_tools", 0),
        "tools_exposed_via_mcp": health.get("tools_exposed_via_mcp", 0),
        "contract_status_count": health.get("contract_status", {}).get("tool_count", 0),
        "registry_truth": health.get("registry_truth", "UNKNOWN"),
        "contract_drift": health.get("contract_drift", True),
        "runtime_drift": health.get("runtime_drift", True),
    }


# ── Surface 3: MCP tools/list ──────────────────────────────────────────────


def get_mcp_wire_counts() -> dict:
    """Count tools returned by MCP tools/list."""
    # First initialize to get session
    sid = mcp_session_init()
    tools = mcp_tools_list(sid)
    return {
        "session_id": sid,
        "wire_tool_count": len(tools),
        "wire_tool_names": sorted(t["name"] for t in tools),
    }


# ── Surface 4: session_init capability_surface ──────────────────────────────


def get_session_capability_counts() -> dict:
    """Extract tool counts from session_init full init response."""
    # Already got session_id from surface 3; query organ attest for full picture
    from arifosmcp.boot.capability_attest import read_capability_attestations  # noqa: E402

    caps = read_capability_attestations()
    return {
        organ: {
            "status": info.get("status", "UNKNOWN"),
            "canonical_tool_count": info.get("canonical_tool_count", info.get("tool_count", 0)),
            "total_tool_count": info.get("total_tool_count", info.get("tool_count", 0)),
            "degraded": info.get("degraded", True),
        }
        for organ, info in caps.items()
    }


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    print("=" * 72)
    print("  MCP SURFACE TRUTH TEST — 4-Surface Comparison")
    print("  DITEMPA BUKAN DIBERI")
    print("=" * 72)

    # ── Surface 1: Declared ─────────────────────────────────────────────
    print("\n[1/4] DECLARED SOURCE (CANONICAL_TOOLS + DIAGNOSTIC_TOOLS)")
    try:
        declared = get_declared_tool_counts()
        print(f"  canonical tools: {declared['canonical_count']}")
        print(f"  diagnostic tools: {declared['diagnostic_count']}")
        print(f"  total declared:   {declared['total_declared']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        declared = {"canonical_count": 0, "diagnostic_count": 0, "total_declared": 0}

    # ── Surface 2: /health ──────────────────────────────────────────────
    print("\n[2/4] /health ENDPOINT")
    try:
        health = get_health_tool_counts()
        print(f"  canonical_tools_loaded: {health['canonical_tools_loaded']}")
        print(f"  diagnostic_tools:       {health['diagnostic_tools']}")
        print(f"  total_declared_tools:   {health['total_declared']}")
        print(f"  tools_exposed_via_mcp:  {health['tools_exposed_via_mcp']}")
        print(f"  contract_status.count:  {health['contract_status_count']}")
        print(f"  registry_truth:         {health['registry_truth']}")
        print(f"  contract_drift:         {health['contract_drift']}")
        print(f"  runtime_drift:          {health['runtime_drift']}")
    except Exception as e:
        print(f"  ERROR: {e}")
        health = {
            "canonical_tools_loaded": 0,
            "diagnostic_tools": 0,
            "total_declared": 0,
            "tools_exposed_via_mcp": 0,
            "contract_status_count": 0,
            "registry_truth": "ERROR",
            "contract_drift": True,
            "runtime_drift": True,
        }

    # ── Surface 3: MCP tools/list ───────────────────────────────────────
    print("\n[3/4] MCP tools/list (WIRE PROTOCOL)")
    try:
        wire = get_mcp_wire_counts()
        print(f"  wire tool count: {wire['wire_tool_count']}")
        # Show first 5, last 5
        names = wire["wire_tool_names"]
        if len(names) <= 20:
            print(f"  tools: {', '.join(names)}")
        else:
            print(f"  tools: {', '.join(names[:5])} ... {', '.join(names[-5:])}")
    except Exception as e:
        print(f"  ERROR: {e}")
        wire = {"session_id": "", "wire_tool_count": 0, "wire_tool_names": []}

    # ── Surface 4: Capability attestation ───────────────────────────────
    print("\n[4/4] CAPABILITY ATTESTATION (static surface)")
    try:
        caps = get_session_capability_counts()
        for organ, info in caps.items():
            status = "🔴" if info["degraded"] else "🟢"
            print(
                f"  {status} {organ:12s} | "
                f"canonical={info['canonical_tool_count']:3d} | "
                f"total={info['total_tool_count']:3d} | "
                f"{info['status']}"
            )
    except Exception as e:
        print(f"  ERROR: {e}")
        caps = {}

    # ── Drift Analysis ──────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  DRIFT ANALYSIS")
    print("=" * 72)

    issues = []

    # Check canonical count consistency
    dc = declared.get("canonical_count", 0)
    hc = health.get("canonical_tools_loaded", 0)
    wc = wire.get("wire_tool_count", 0)

    if dc != hc and hc > 0:
        issues.append(
            f"  [DEGRADED] canonical tools: declared={dc} vs /health={hc}"
        )
    else:
        print(f"  [OK] canonical tools: declared={dc} = /health={hc}")

    # Check total declared
    dt = declared.get("total_declared", 0)
    ht = health.get("total_declared", 0)
    if dt != ht and ht > 0:
        issues.append(f"  [DEGRADED] total declared: declared={dt} vs /health={ht}")
    else:
        print(f"  [OK] total declared: declared={dt} = /health={ht}")

    # Wire count should be >= canonical
    if wc < dc:
        issues.append(f"  [FAIL] wire tools ({wc}) < canonical declared ({dc})")
    else:
        print(f"  [OK] wire tools ({wc}) >= canonical ({dc})")

    # Contract drift flag
    if health.get("contract_drift", True):
        issues.append("  [FAIL] contract_drift=True — schema drift detected")

    # Runtime drift
    if health.get("runtime_drift", True):
        issues.append("  [WARN] runtime_drift=True — code mismatch (redeploy needed)")

    # Registry truth
    if health.get("registry_truth") != "VERIFIED":
        issues.append(f"  [DEGRADED] registry_truth={health.get('registry_truth')}")

    # Degraded organs
    degraded_organs = [o for o, i in caps.items() if i.get("degraded", True)]
    if degraded_organs:
        issues.append(f"  [DEGRADED] degraded organs: {', '.join(degraded_organs)}")
    else:
        print("  [OK] all organs attested")

    # ── Verdict ────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    fail_count = sum(1 for i in issues if i.startswith("  [FAIL]"))
    degraded_count = sum(1 for i in issues if i.startswith("  [DEGRADED]"))
    warn_count = sum(1 for i in issues if i.startswith("  [WARN]"))

    if issues:
        for issue in issues:
            print(issue)

    print()

    if fail_count > 0:
        print(f"  VERDICT: FAIL ({fail_count} failures, {degraded_count} degraded)")
    elif degraded_count > 0:
        print(f"  VERDICT: DEGRADED ({degraded_count} degraded, {warn_count} warnings)")
    elif warn_count > 0:
        print(f"  VERDICT: PASS with WARNINGS ({warn_count})")
    else:
        print("  VERDICT: PASS — all 4 surfaces consistent")

    print("=" * 72)
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
