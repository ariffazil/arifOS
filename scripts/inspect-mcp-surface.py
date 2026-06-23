#!/usr/bin/env python3
"""
inspect-mcp-surface.py — Machine-checkable arifOS MCP surface inventory.
Read-only. No state mutation.

Usage:
    python scripts/inspect-mcp-surface.py
    python scripts/inspect-mcp-surface.py --json

Exit codes:
    0 = inventory succeeded
    1 = runtime error
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _get_canonical_tools() -> list[str]:
    from arifosmcp.constitutional_map import list_canonical_tools

    return list(list_canonical_tools())


def _get_expanded_tools() -> list[str]:
    from arifosmcp.runtime.public_surface import EXPANDED_45

    return list(EXPANDED_45)


def _get_diagnostic_tools() -> list[str]:
    from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS

    return list(DIAGNOSTIC_TOOLS)


def _get_domain_aliases() -> list[str]:
    from arifosmcp.runtime.public_surface import DOMAIN_ALIASES

    return list(DOMAIN_ALIASES)


def _get_handlers() -> list[str]:
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

    return list(_CANONICAL_HANDLERS.keys())


def _count_decorators(pattern: str, files: list[str]) -> int:
    """Crude but fast decorator count across source files."""
    count = 0
    for rel_path in files:
        path = PROJECT_ROOT / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        count += text.count(pattern)
    return count


def _drift_check_exists() -> bool:
    """Check if mcp_drift_check is importable or defined."""
    try:
        from arifosmcp.tools import drift_check

        return hasattr(drift_check, "mcp_drift_check")
    except Exception:
        return False


def _manifest_exists() -> bool:
    manifest = PROJECT_ROOT / "arifosmcp" / "manifests" / "phoenix72.tools.json"
    return manifest.exists()


def _build_report() -> dict:
    canonical_tools = _get_canonical_tools()
    expanded_tools = _get_expanded_tools()
    diagnostic_tools = _get_diagnostic_tools()
    domain_aliases = _get_domain_aliases()
    handlers = _get_handlers()

    resource_files = [
        "arifosmcp/runtime/fastmcp_ext/resources.py",
        "arifosmcp/runtime/chatgpt_integration/apps_sdk_tools.py",
        "arifosmcp/runtime/mind_mcp.py",
        "arifosmcp/resources/doctrine.py",
        "arifosmcp/resources/session.py",
        "arifosmcp/resources/vitals.py",
        "arifosmcp/resources/schema.py",
        "arifosmcp/resources/forge.py",
        "arifosmcp/resources/tree777.py",
    ]
    prompt_files = [
        "arifosmcp/runtime/fastmcp_ext/prompts.py",
        "arifosmcp/runtime/mind_mcp.py",
        "arifosmcp/prompts/init.py",
        "arifosmcp/prompts/judge.py",
        "arifosmcp/prompts/system.py",
        "arifosmcp/prompts/deliberation.py",
        "arifosmcp/prompts/meta_skills.py",
    ]

    resource_estimate = _count_decorators("@mcp.resource", resource_files) + _count_decorators(
        ".add_resource(", resource_files
    )
    prompt_estimate = _count_decorators("@mcp.prompt", prompt_files)

    # Aliases without handlers = registry inflation
    aliases_without_handlers = sorted(set(expanded_tools) - set(handlers))

    phoenix_ready = True
    phoenix_reasons: list[str] = []

    if len(canonical_tools) < 72:
        phoenix_ready = False
        phoenix_reasons.append(
            f"72-tool manifest not found (canonical={len(canonical_tools)}, expanded={len(expanded_tools)})"
        )
    if not _drift_check_exists():
        phoenix_ready = False
        phoenix_reasons.append("mcp_drift_check not registered")
    if resource_estimate < 18:
        phoenix_ready = False
        phoenix_reasons.append(
            f"resources count not proven (estimated={resource_estimate}, target=18)"
        )
    if prompt_estimate < 9:
        phoenix_ready = False
        phoenix_reasons.append(f"prompts count not proven (estimated={prompt_estimate}, target=9)")

    report = {
        "mode": "canonical13",
        "tools": {
            "canonical_count": len(canonical_tools),
            "expanded_count": len(expanded_tools),
            "handler_count": len(handlers),
            "diagnostic_count": len(diagnostic_tools),
            "domain_alias_count": len(domain_aliases),
            "canonical_names": canonical_tools,
            "expanded_names": expanded_tools,
            "diagnostic_names": diagnostic_tools,
            "domain_alias_names": domain_aliases,
            "aliases_without_handlers": aliases_without_handlers,
            "handler_names": handlers,
        },
        "resources": {
            "estimated_count": resource_estimate,
            "target": 18,
        },
        "prompts": {
            "estimated_count": prompt_estimate,
            "target": 9,
        },
        "phoenix72": {
            "ready": phoenix_ready,
            "manifest_exists": _manifest_exists(),
            "drift_check_exists": _drift_check_exists(),
            "reasons": phoenix_reasons
            if phoenix_reasons
            else ["All gates pass — verify live registry counts"],
        },
        "notes": [
            "Resource/prompt counts are static estimates from source decorators.",
            "Live runtime counts may differ; use MCP tools/list for authoritative data.",
        ],
    }
    return report


def _print_text(report: dict) -> None:
    print("═" * 70)
    print("arifOS MCP Surface Inventory")
    print("═" * 70)
    print(f"Mode: {report['mode']}")
    print()
    print("TOOLS")
    print(f"  Canonical:   {report['tools']['canonical_count']}")
    print(f"  Expanded:    {report['tools']['expanded_count']}")
    print(f"  Handlers:    {report['tools']['handler_count']}")
    print(f"  Diagnostic:  {report['tools']['diagnostic_count']}")
    if report["tools"]["aliases_without_handlers"]:
        print(f"  Aliases w/o handlers: {len(report['tools']['aliases_without_handlers'])}")
    print()
    print("SURFACES")
    print(
        f"  Resources (est): {report['resources']['estimated_count']} / {report['resources']['target']}"
    )
    print(
        f"  Prompts   (est): {report['prompts']['estimated_count']} / {report['prompts']['target']}"
    )
    print()
    print("PHOENIX-72")
    print(f"  Ready:          {report['phoenix72']['ready']}")
    print(f"  Manifest exists: {report['phoenix72']['manifest_exists']}")
    print(f"  Drift check exists: {report['phoenix72']['drift_check_exists']}")
    for reason in report["phoenix72"]["reasons"]:
        print(f"  Reason:         {reason}")
    print()
    print("═" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="arifOS MCP surface inventory")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    try:
        report = _build_report()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
