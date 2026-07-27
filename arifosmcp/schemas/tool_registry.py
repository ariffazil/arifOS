"""
arifOS Canonical Tool Registry — Single Source of Truth
═══════════════════════════════════════════════════════════

This module owns the canonical tool registry for the arifOS MCP kernel.
It is THE authoritative source that everything else must derive from:

  1. MCP tools/list response      (tools_list_manifest)
  2. Plugin/tool metadata          (plugin_metadata)
  3. SDK alias resolution          (resolve_alias, sdk_alias_map)
  4. Documentation generation      (markdown_tool_table, doc_manifest)
  5. Conformance expectations      (conformance_profile_def)

Drift detection:
  surface_conformance_check() probes the live runtime and compares
  advertised_public_tools == runtime_callable_public_tools.
  If not equal → returns 888_HOLD verdict.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent
_DEFAULT_REGISTRY_PATH = SCHEMA_DIR / "arifos_tool_registry.json"

# ── Public API ───────────────────────────────────────────────────────────────


@cache
def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    """Load the canonical tool registry from JSON.

    Args:
        path: Optional explicit path. Defaults to arifos_tool_registry.json
              in the schemas directory.

    Returns:
        The full registry dict.
    """
    p = Path(path) if path else _DEFAULT_REGISTRY_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def public_tool_names() -> list[str]:
    """Return ordered list of public canonical tool names."""
    return list(load_registry()["public_tools"].keys())


def public_tool_spec(name: str) -> dict[str, Any] | None:
    """Return the spec dict for a public tool, or None."""
    return load_registry()["public_tools"].get(name)


def internal_tool_names() -> list[str]:
    """Return ordered list of internal-only tool names."""
    return list(load_registry()["internal_tools"].keys())


def all_tool_names() -> list[str]:
    """Return ALL known tool names (public + internal)."""
    reg = load_registry()
    return list(reg["public_tools"].keys()) + list(reg["internal_tools"].keys())


def sdk_alias_map() -> dict[str, dict[str, Any]]:
    """Return the SDK alias map: alias_name -> {target, status, migration, conformance}."""
    return dict(load_registry()["sdk_aliases"])


def resolve_alias(name: str) -> dict[str, Any] | None:
    """Resolve an SDK alias to its canonical target.

    Returns None if the name is not a known alias.
    Returns dict with target, status, migration, conformance.
    """
    return load_registry()["sdk_aliases"].get(name)


def diagnostic_tool_names() -> list[str]:
    """Return list of diagnostic tool names."""
    return list(load_registry()["diagnostic_tools"].keys())


# ── Auto-generation: MCP tools/list response ────────────────────────────


def tools_list_manifest(profile: str = "sovereign", expose_dev_tools: bool = False) -> list[dict[str, Any]]:
    """Generate a tools/list-compatible manifest for a given profile.

    This is the canonical function for producing what the MCP tools/list
    endpoint returns. Every tool in the response MUST be callable.

    Args:
        profile: One of "public_agent", "trusted_agent", "executor",
                 "sovereign", "operator".
        expose_dev_tools: If True, include gated diagnostic tools.

    Returns:
        List of tool descriptors suitable for tools/list response.
    """
    reg = load_registry()
    conformance = reg["conformance_expectations"]["profiles"]
    profile_key = _resolve_profile(profile, conformance)
    expected = set(conformance[profile_key]["exposed_tools"])
    diagnostics_enabled = conformance[profile_key].get("diagnostics", False)

    result: list[dict[str, Any]] = []
    public = reg["public_tools"]

    for name in public_tool_names():
        if name in expected:
            spec = public[name]
            result.append({
                "name": name,
                "description": spec["description"],
                "stage": spec["stage"],
                "lane": spec["lane"],
                "floors": spec["floors"],
                "irreversible": spec["irreversible"],
                "risk_tier": spec["risk_tier"],
                "conformance_profile": profile_key,
                "inputSchema": {"type": "object", "properties": spec.get("input_schema", {}).get("properties", {})},
            })

    # Add diagnostic tools if enabled
    if expose_dev_tools and diagnostics_enabled:
        diag = reg["diagnostic_tools"]
        for name in diagnostic_tool_names():
            spec = diag[name]
            result.append({
                "name": name,
                "description": f"DIAGNOSTIC: {name} ({spec['tier']})",
                "access": spec["access"],
                "conformance_profile": profile_key,
            })

    return result


def _resolve_profile(profile: str, conformance: dict[str, Any]) -> str:
    """Resolve a profile name to a known key, with fallback."""
    aliases = {
        "public": "public_agent",
        "chatgpt": "public_agent",
        "agnostic": "public_agent",
        "trusted": "trusted_agent",
        "exec": "executor",
        "sovereign": "sovereign",
        "operator": "operator",
        "full": "operator",
        "internal": "operator",
    }
    key = profile.strip().lower()
    if key in aliases:
        key = aliases[key]
    if key in conformance:
        return key
    return "sovereign"  # safest default


# ── Auto-generation: Plugin/tool metadata ────────────────────────────────


def plugin_metadata() -> dict[str, Any]:
    """Generate plugin discovery metadata from the canonical registry.

    This is what MCP gateway / plugin registries consume to understand
    arifOS capabilities without hitting the live kernel.
    """
    reg = load_registry()
    public = reg["public_tools"]
    return {
        "protocol": "arifos-tool-registry/v1",
        "registry_version": reg["registry_version"],
        "canonical_count": len(public),
        "internal_count": len(reg["internal_tools"]),
        "alias_count": len(reg["sdk_aliases"]),
        "diagnostic_count": len(reg["diagnostic_tools"]),
        "public_tools": [
            {
                "name": name,
                "stage": spec["stage"],
                "lane": spec["lane"],
                "modes": spec["modes"],
                "floors": spec["floors"],
                "irreversible": spec["irreversible"],
                "risk_tier": spec["risk_tier"],
            }
            for name, spec in public.items()
        ],
        "profiles": {
            name: {
                "tool_count": len(cfg["exposed_tools"]),
                "tools": cfg["exposed_tools"],
                "diagnostics": cfg.get("diagnostics", False),
            }
            for name, cfg in reg["conformance_expectations"]["profiles"].items()
        },
        "semantic_abi": reg["conformance_expectations"]["semantic_abi"],
    }


# ── Auto-generation: SDK alias map ──────────────────────────────────────


def sdk_alias_redirect_map() -> dict[str, str]:
    """Return a flat alias -> target map for SDK routing."""
    return {alias: info["target"] for alias, info in load_registry()["sdk_aliases"].items()}


# ── Auto-generation: Documentation ──────────────────────────────────────


def markdown_tool_table() -> str:
    """Generate a markdown table of all canonical tools for docs."""
    reg = load_registry()
    lines = [
        "| Tool | Stage | Lane | Access | Floors | Irreversible | Risk Tier |",
        "| :--- | :---- | :--- | :----- | :----- | :------------ | :-------- |",
    ]
    for name, spec in reg["public_tools"].items():
        floors = ", ".join(spec["floors"])
        lines.append(
            f"| `{name}` | {spec['stage']} | {spec['lane']} | public | {floors} "
            f"| {'YES' if spec['irreversible'] else 'no'} | {spec['risk_tier']} |"
        )
    for name, spec in reg["internal_tools"].items():
        target = spec.get("redirect_to") or "−"
        lines.append(
            f"| `{name}` | − | − | internal ({spec['access_reason'][:50]}…) "
            f"| − | − | → {target} |"
        )
    return "\n".join(lines)


def doc_manifest() -> dict[str, Any]:
    """Generate a machine-readable documentation manifest."""
    reg = load_registry()
    public = reg["public_tools"]
    return {
        "title": "arifOS MCP Canonical Tool Registry",
        "version": reg["registry_version"],
        "public_tool_count": len(public),
        "surface_rules": reg["surface_doctrine"]["rules"],
        "888_hold_triggers": reg["surface_doctrine"]["888_hold_triggers"],
        "tools": {
            name: {
                "description": spec["description"],
                "modes": spec["modes"],
                "constitutional_floors": spec["floors"],
                "risk_tier": spec["risk_tier"],
            }
            for name, spec in public.items()
        },
    }


# ── Conformance expectations per profile ─────────────────────────────────


def conformance_profile_def(profile: str = "sovereign") -> dict[str, Any]:
    """Return the conformance expectations for a given profile.

    Includes expected tool set, max tools on wire, and doctrine notes.
    """
    reg = load_registry()
    key = _resolve_profile(profile, reg["conformance_expectations"]["profiles"])
    return dict(reg["conformance_expectations"]["profiles"][key])


# ── SURFACE CONFORMANCE GATE ────────────────────────────────────────────
# This is THE gate that verifies:
#   advertised_public_tools == runtime_callable_public_tools
# If not equal → deployment fails / enters 888_HOLD.


def surface_conformance_check(
    runtime_tool_names: list[str],
    profile: str = "sovereign",
    expose_dev_tools: bool = False,
) -> dict[str, Any]:
    """Compare advertised registry tools against actual runtime exposure.

    This is the canonical surface-conformance gate. Every deployment MUST
    pass this check. If it doesn't → 888_HOLD is the verdict.

    Args:
        runtime_tool_names: The tool names reported by the live kernel's
                            tools/list or /health endpoint.
        profile: Which conformance profile to validate against.
        expose_dev_tools: Whether diagnostic tools were expected (gated).

    Returns:
        A verdict dict with:
          - ok: bool — overall pass/fail
          - verdict: str — "SEAL" (pass), "888_HOLD" (fail)
          - expected_tools: list[str]
          - runtime_tools: list[str]
          - missing: list[str] — tools in registry but not runtime
          - unexpected: list[str] — tools in runtime but not registry
          - drift_report: str — human-readable summary
          - details: list[dict] — per-tool breakdown
    """
    reg = load_registry()
    conformance = reg["conformance_expectations"]["profiles"]
    profile_key = _resolve_profile(profile, conformance)
    profile_cfg = conformance[profile_key]

    # Expected public tools from the registry
    expected_public: set[str] = set(profile_cfg["exposed_tools"])

    # Add diagnostic tools if they were expected to be on the wire
    diagnostics_enabled = profile_cfg.get("diagnostics", False) and expose_dev_tools
    if diagnostics_enabled:
        expected_public.update(reg["diagnostic_tools"].keys())

    # The internal tools and SDK aliases that should NOT be on the wire
    known_internal: set[str] = set(reg["internal_tools"].keys())
    known_aliases: set[str] = set(reg["sdk_aliases"].keys())

    runtime_set = set(runtime_tool_names)

    # Missing: expected in registry but not found at runtime
    missing = sorted(expected_public - runtime_set)

    # Unexpected: found at runtime but NOT in expected set
    # Internal tools and aliases appearing on wire = unexpected
    unexpected = sorted(runtime_set - expected_public)

    # But diagnostic tools ARE allowed when gated — tag them separately
    unexpected_public = sorted(
        t for t in unexpected
        if t not in reg["diagnostic_tools"] or not diagnostics_enabled
    )

    # Detailed per-tool breakdown
    details: list[dict[str, Any]] = []
    for name in sorted(expected_public):
        in_runtime = name in runtime_set
        # Determine if expected but missing
        if not in_runtime:
            details.append({
                "tool": name,
                "expected": True,
                "found": False,
                "anomaly": "MISSING",
                "message": f"Tool '{name}' is in registry but NOT on runtime wire.",
            })
        else:
            details.append({
                "tool": name,
                "expected": True,
                "found": True,
                "anomaly": None,
                "message": None,
            })

    for name in unexpected:
        in_registry = name in expected_public or name in known_internal or name in known_aliases
        if name in known_internal:
            details.append({
                "tool": name,
                "expected": False,
                "found": True,
                "anomaly": "INTERNAL_LEAK",
                "message": f"INTERNAL tool '{name}' leaked to public wire! Must be removed.",
            })
        elif name in known_aliases:
            details.append({
                "tool": name,
                "expected": False,
                "found": True,
                "anomaly": "ALIAS_ON_WIRE",
                "message": f"SDK alias '{name}' appears on wire as standalone tool instead of redirecting.",
            })
        elif name not in expected_public:
            details.append({
                "tool": name,
                "expected": False,
                "found": True,
                "anomaly": "UNREGISTERED",
                "message": f"Tool '{name}' on runtime wire but NOT in registry.",
            })

    ok = len(missing) == 0 and len(unexpected_public) == 0

    # Build drift report
    drift_parts: list[str] = []
    if missing:
        drift_parts.append(f"MISSING ({len(missing)}): {', '.join(missing)}")
    if unexpected_public:
        drift_parts.append(f"UNEXPECTED ({len(unexpected_public)}): {', '.join(unexpected_public)}")
    internal_leaks = [d["tool"] for d in details if d.get("anomaly") == "INTERNAL_LEAK"]
    if internal_leaks:
        drift_parts.append(f"INTERNAL_LEAK ({len(internal_leaks)}): {', '.join(internal_leaks)}")
    alias_leaks = [d["tool"] for d in details if d.get("anomaly") == "ALIAS_ON_WIRE"]
    if alias_leaks:
        drift_parts.append(f"ALIAS_ON_WIRE ({len(alias_leaks)}): {', '.join(alias_leaks)}")

    drift_report = (
        "SURFACE CONFORMANCE: "
        + ("PASS" if ok else "888_HOLD")
        + ". "
        + (" | ".join(drift_parts) if drift_parts else "Registry contract === runtime exposure.")
    )

    return {
        "ok": ok,
        "verdict": "SEAL" if ok else "888_HOLD",
        "expected_tools": sorted(expected_public),
        "runtime_tools": sorted(runtime_set),
        "missing": missing,
        "unexpected": unexpected_public,
        "unexpected_all": unexpected,
        "internal_leaks": internal_leaks,
        "alias_leaks": alias_leaks,
        "profile": profile_key,
        "expose_dev_tools": expose_dev_tools,
        "drift_report": drift_report,
        "details": details,
    }


def validate_tool_registry() -> dict[str, Any]:
    """Validate the internal consistency of the canonical tool registry.

    Checks:
      - No tool appears in both public and internal
      - All SDK aliases point to valid targets
      - Conformance profiles only reference existing public tools
      - Semantic ABI count matches expected
    """
    reg = load_registry()
    errors: list[str] = []

    public = set(reg["public_tools"].keys())
    internal = set(reg["internal_tools"].keys())
    aliases = reg["sdk_aliases"]
    profiles = reg["conformance_expectations"]["profiles"]
    abi = reg["conformance_expectations"]["semantic_abi"]

    # No overlap
    overlap = public & internal
    if overlap:
        errors.append(f"Tools in both public and internal: {sorted(overlap)}")

    # All alias targets are valid tools
    for alias, info in aliases.items():
        target = info.get("target", "")
        if target and target not in public:
            # Allow internal tool targets too
            if target not in internal:
                errors.append(f"Alias '{alias}' points to unknown target '{target}'")

    # Profile tool references are valid
    for profile_name, cfg in profiles.items():
        for tool_name in cfg["exposed_tools"]:
            if tool_name not in public:
                errors.append(
                    f"Profile '{profile_name}' references unknown tool '{tool_name}'"
                )

    # Semantic ABI count
    expected_count = abi.get("expected_capabilities", 8)
    if len(public) != expected_count:
        errors.append(
            f"Public tool count {len(public)} != expected {expected_count}"
        )

    return {
        "ok": not errors,
        "errors": errors,
        "public_count": len(public),
        "internal_count": len(internal),
        "alias_count": len(aliases),
        "profile_count": len(profiles),
    }


# ── CLI Entry Point ──────────────────────────────────────────────────────


def main() -> None:
    """Run all registry validations and surface conformance checks."""
    import sys

    print("═══ arifOS Canonical Tool Registry Validation ═══")
    print()

    # Validate internal consistency
    result = validate_tool_registry()
    if result["ok"]:
        print("✓ Registry self-consistency: PASS")
    else:
        for err in result["errors"]:
            print(f"✗ {err}")

    print(f"  Public tools:       {result['public_count']}")
    print(f"  Internal tools:     {result['internal_count']}")
    print(f"  SDK aliases:        {result['alias_count']}")
    print(f"  Profiles:           {result['profile_count']}")
    print()

    # Print markdown table
    print("═══ Canonical Tool Surface ═══")
    print(markdown_tool_table())
    print()

    # Print alias summary
    print("═══ SDK Alias Summary ═══")
    aliases = sdk_alias_map()
    for alias, info in sorted(aliases.items()):
        status = info["status"]
        target = info["target"]
        print(f"  {alias:30s} → {target:20s} [{status}]")
    print()

    # Profile summary
    print("═══ Conformance Profiles ═══")
    reg = load_registry()
    for name, cfg in reg["conformance_expectations"]["profiles"].items():
        tools = ", ".join(cfg["exposed_tools"])
        print(f"  {name:20s}: {len(cfg['exposed_tools'])} tools → {tools}")
    print()

    # Check if runtime is live and probe
    try:
        import urllib.request

        resp = urllib.request.urlopen("http://127.0.0.1:8088/health", timeout=5)
        health = json.loads(resp.read().decode())
        runtime_tools = []
        if "tools_loaded" in health:
            runtime_tools = health["tools_loaded"]
        elif "contract_status" in health:
            runtime_tools = health["contract_status"].get("tool_names", [])

        print("═══ Live Surface Conformance Check ═══")
        if runtime_tools:
            print(f"  Runtime reports {len(runtime_tools)} tools")
            check = surface_conformance_check(runtime_tools, profile="sovereign")
            print(f"  Verdict: {check['verdict']}")
            if not check["ok"]:
                print(f"  DRIFT: {check['drift_report']}")
                for detail in check["details"]:
                    if detail.get("anomaly"):
                        print(f"    {detail['anomaly']}: {detail['tool']} — {detail['message']}")
            else:
                print("  ✓ No drift detected. Registry contract === runtime exposure.")
        else:
            print("  ⚠ Kernel alive but no tool list found in /health response")
            print(f"  Health payload keys: {list(health.keys())}")
    except Exception as e:
        print(f"  ⚠ Cannot probe live kernel: {e}")
        print("  (This is expected during CI if the kernel isn't running.)")


if __name__ == "__main__":
    main()
