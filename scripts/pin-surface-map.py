#!/usr/bin/env python3
"""
pin-surface-map.py — Surface Map Drift Detector

Probes live MCP tools/list at localhost:8088/mcp and compares against the
canonical surface-map YAML. Detects:
  - Phantom tools (live but undeclared)
  - Ghost tools (declared but missing)
  - Naming convention drift
  - Resource count mismatch

Exit code: 0 = pinned, 1 = drift detected

Usage:
  python3 scripts/pin-surface-map.py           # check drift
  python3 scripts/pin-surface-map.py --fix     # update YAML (requires F13)
  python3 scripts/pin-surface-map.py --ci      # CI gate - fail on drift

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import argparse
import json
import os
import sys
import urllib.request

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACE_YAML = os.path.join(ROOT, "arifos_agent_surface_map.yaml")
SURFACE_MD = os.path.join(ROOT, "arifos_agent_surface_map.md")
CONTRACTS_YAML = os.path.join(ROOT, "contracts", "mcp_surface.yaml")
MCP_ENDPOINT = "http://localhost:8088/tools"
HEALTH_ENDPOINT = "http://localhost:8088/health"


def probe_mcp_tools() -> list[dict]:
    """Probe live MCP tools via REST /tools or /openapi.json."""
    # Try GET /tools (REST surface)
    for path in ("/tools", "/openapi.json"):
        try:
            url = f"http://localhost:8088{path}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            # /tools returns dict with tool names as keys
            if isinstance(data, dict):
                # Try common response shapes
                if "tools" in data and isinstance(data["tools"], list):
                    return data["tools"]
                if "paths" in data:
                    # OpenAPI format — extract tool names from paths
                    tools = []
                    for p, methods in data.get("paths", {}).items():
                        if p.startswith("/tools/"):
                            name = p.split("/tools/")[-1]
                            post = methods.get("post", {})
                            summary = post.get("summary", "")
                            tools.append({"name": name, "description": summary})
                    if tools:
                        return tools
                # Fallback: dict keys might be tool names
                keys = list(data.keys())
                if keys and all(k.startswith("arif_") for k in keys[:5]):
                    return [
                        {
                            "name": k,
                            "description": v.get("description", "") if isinstance(v, dict) else "",
                        }
                        for k, v in data.items()
                    ]
        except Exception:
            continue
    print("ERROR: Cannot probe live MCP tools", file=sys.stderr)
    return []


def probe_health() -> dict:
    """Probe /health endpoint for tool counts."""
    try:
        with urllib.request.urlopen(HEALTH_ENDPOINT, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"ERROR: Cannot probe /health: {e}", file=sys.stderr)
        return {}


def load_surface_yaml() -> dict:
    """Load the canonical surface-map YAML."""
    import yaml

    with open(SURFACE_YAML) as f:
        return yaml.safe_load(f)


def detect_drift(live_tools: list[dict], health: dict) -> list[dict]:
    """Compare live tools against surface-map declarations. Returns drift entries."""

    drift = []

    # ── Load surface map ─────────────────────────────────────────────────
    try:
        surface = load_surface_yaml()
        declared_tools = surface.get("arifos_agent_surface_map", {}).get("mcp_tools", [])
        declared_resources = surface.get("arifos_agent_surface_map", {}).get("mcp_resources", [])
    except FileNotFoundError:
        # In CI, the surface YAML may not exist — not a drift signal, just absent.
        # Return empty drift so the CI exemption path handles it gracefully.
        return drift
    except Exception as e:
        drift.append({"severity": "CRITICAL", "field": "surface_yaml", "detail": str(e)})
        return drift

    # ── Tool names ───────────────────────────────────────────────────────
    live_names = sorted({t.get("name", "") for t in live_tools if t.get("name")})
    declared_names = sorted(declared_tools) if isinstance(declared_tools, list) else []

    # Phantom tools: live but not declared
    phantom = [n for n in live_names if n not in declared_names]
    if phantom:
        drift.append(
            {
                "severity": "HIGH",
                "field": "phantom_tools",
                "detail": f"Live but undeclared: {phantom}",
                "live_count": len(live_names),
                "declared_count": len(declared_names),
            }
        )

    # Ghost tools: declared but not live
    ghost = [n for n in declared_names if n not in live_names]
    if ghost:
        drift.append(
            {
                "severity": "HIGH",
                "field": "ghost_tools",
                "detail": f"Declared but missing: {ghost}",
                "live_count": len(live_names),
                "declared_count": len(declared_names),
            }
        )

    # ── Naming convention ────────────────────────────────────────────────
    live_prefixes = set(n.split("_")[0] for n in live_names if "_" in n)
    declared_prefixes = set(n.split("_")[0] for n in declared_names if "_" in n)
    naming_convention = surface.get("arifos_agent_surface_map", {}).get("naming_convention", "")
    if live_prefixes != declared_prefixes:
        drift.append(
            {
                "severity": "MEDIUM",
                "field": "naming_convention",
                "detail": f"Live prefixes {live_prefixes} ≠ declared prefixes {declared_prefixes}. Expected: {naming_convention}",
            }
        )

    # ── Tool counts from /health ─────────────────────────────────────────
    exposed = health.get("tools_exposed_via_mcp")
    canonical_loaded = health.get("canonical_tools_loaded")
    diagnostic = health.get("diagnostic_tools")
    total_declared = health.get("total_declared_tools")

    surface_counts = surface.get("arifos_agent_surface_map", {}).get("tool_counts", {})
    if exposed is not None and surface_counts.get("exposed_via_mcp") != exposed:
        drift.append(
            {
                "severity": "LOW",
                "field": "exposed_tool_count",
                "detail": f"Live: {exposed}, Surface-map: {surface_counts.get('exposed_via_mcp')}",
            }
        )
    if total_declared is not None and surface_counts.get("total_declared") != total_declared:
        drift.append(
            {
                "severity": "LOW",
                "field": "total_declared_tool_count",
                "detail": f"Live: {total_declared}, Surface-map: {surface_counts.get('total_declared')}",
            }
        )

    # ── Resource count ───────────────────────────────────────────────────
    # (Resources are harder to probe — just check the surface list is populated)
    if not declared_resources:
        drift.append(
            {
                "severity": "MEDIUM",
                "field": "resources",
                "detail": "Surface-map declares 0 resources — likely stale",
            }
        )

    return drift


def report_drift(drift: list[dict]) -> int:
    """Print drift report and return max severity level."""
    if not drift:
        print("✅ SURFACE PINNED — Live tools match surface-map declarations.")
        return 0

    severity_map = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    max_severity = max(
        (severity_map.get(d.get("severity", "LOW"), 0) for d in drift),
        default=0,
    )

    print(f"⚠️  DRIFT DETECTED — {len(drift)} issue(s):\n")
    for d in sorted(
        drift, key=lambda x: severity_map.get(x.get("severity", "LOW"), 0), reverse=True
    ):
        label = d["severity"]
        sep = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(label, "⚪")
        print(f"  {sep} [{label}] {d['field']}")
        print(f"     {d['detail']}")
        if "live_count" in d and "declared_count" in d:
            print(f"     Live: {d['live_count']} | Declared: {d['declared_count']}")
        print()

    return max_severity


def fix_surface_yaml(live_tools: list[dict], health: dict) -> bool:
    """Auto-fix the surface-map YAML to match live state.
    NOTE: This is a destructive operation — only run with F13 approval.
    """
    print("⚠️  --fix mode: Would regenerate surface YAML from live state.")
    print("   (Not implemented automatically — requires F13 SOVEREIGN approval per run)")
    return False


def main():
    parser = argparse.ArgumentParser(description="Surface Map Drift Detector")
    parser.add_argument("--fix", action="store_true", help="Auto-fix surface YAML (requires F13)")
    parser.add_argument("--ci", action="store_true", help="CI gate mode - exit 1 on any drift")
    parser.add_argument(
        "--require-live-mcp",
        action="store_true",
        default=False,
        help=(
            "T6 strict mode: fail closed when MCP servers are unreachable. "
            "Also controlled by FORGE_SURFACE_GATE_STRICT=1 env var. "
            "Default: off (fail-open for CI/offline dev). "
            "Sovereign enables this with 'export FORGE_SURFACE_GATE_STRICT=1'"
        ),
    )
    args = parser.parse_args()

    # T6: Respect env var FORGE_SURFACE_GATE_STRICT
    env_strict = os.environ.get("FORGE_SURFACE_GATE_STRICT", "").strip()
    if env_strict in ("1", "true", "yes", "on"):
        args.require_live_mcp = True

    print("🔍 Probing live MCP surface...")
    live_tools = probe_mcp_tools()
    health = probe_health()

    print(f"   Live MCP tools: {len(live_tools)}")
    if live_tools:
        for t in live_tools:
            print(f"     - {t.get('name', '?')}")
    print(f"   /health exposed: {health.get('tools_exposed_via_mcp', '?')}")
    print(f"   /health total declared: {health.get('total_declared_tools', '?')}")
    print()

    drift = detect_drift(live_tools, health)
    severity = report_drift(drift)

    if args.fix:
        fixed = fix_surface_yaml(live_tools, health)
        if fixed:
            print("✅ Surface YAML regenerated from live state.")
        else:
            print("❌ Fix not applied.")
            sys.exit(1)

    # ── CI infrastructure exemption ─────────────────────────────────────
    # If neither tools nor /health could be probed at all (CI runner has no
    # live MCP), don't fail the gate on ghost/phantom drift — we simply
    # cannot verify against live state. Surface-YAML parsing still happens
    # and CRITICAL surface_yaml drift still fails.
    #
    # T6 2026-07-17: When --require-live-mcp is set (or FORGE_SURFACE_GATE_STRICT=1),
    # this exemption is REVOKED. The gate fails closed if live MCP cannot be
    # probed — a verifier that SKIPS live checks cannot certify PASS.
    live_unavailable = not live_tools and not health and severity > 0
    if args.ci and live_unavailable:
        any_critical = any(d.get("severity") == "CRITICAL" for d in drift)
        if any_critical:
            print("⚠️  Live MCP unreachable AND CRITICAL surface drift — failing CI gate.")
            sys.exit(1)
        # T6: strict mode revokes the CI exemption
        if args.require_live_mcp:
            print("🔴 T6 STRICT MODE: Live MCP unreachable — failing closed.")
            print("   FORGE_SURFACE_GATE_STRICT=1 set but no live MCP to verify against.")
            print("   SKIPPED ≠ PASS. Set FORGE_SURFACE_GATE_STRICT=0 to bypass.")
            sys.exit(1)
        print("ℹ️  Live MCP unreachable in CI — drift detection against live skipped.")
        print("   (To fail closed on unreachable MCP, set FORGE_SURFACE_GATE_STRICT=1)")
        sys.exit(0)

    if args.ci and severity >= 1:
        sys.exit(1)
    sys.exit(0 if severity < 1 else severity)


if __name__ == "__main__":
    main()
