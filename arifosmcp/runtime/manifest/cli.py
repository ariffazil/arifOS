"""
PR4 — manifest CLI.

`python -m arifosmcp.runtime.manifest.cli --emit-mcp > /var/www/html/arifos/.well-known/mcp/server.json`
"""

from __future__ import annotations

import argparse
import json
import sys

from arifosmcp.runtime.manifest.diff import exit_with_drift, manifest_drift
from arifosmcp.runtime.manifest.generator import compose_manifest


def emit_mcp() -> dict:
    """Format the manifest as `/.well-known/mcp/server.json` shape."""
    m = compose_manifest()
    return {
        "schema": "agent-manifest/v1",
        "name": "arifOS MCP surface",
        "url": "https://mcp.arif-fazil.com/mcp",
        "version": "1.0.0",
        "tools": m["tools"],
        "totals": m["totals"],
        "manifest_drift": m["manifest_drift"],
        "issued_at": m["issued_at"],
    }


def emit_agent_card() -> dict:
    return compose_manifest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="arifosmcp.runtime.manifest.cli")
    parser.add_argument("--emit-mcp", action="store_true", help="emit /server.json shape")
    parser.add_argument("--emit-agent-card", action="store_true", help="emit agent-card shape")
    parser.add_argument(
        "--check-drift-against", type=str, help="path to a published manifest; exit 1 on drift"
    )
    args = parser.parse_args(argv)
    if args.emit_mcp:
        print(json.dumps(emit_mcp(), indent=2))
        return 0
    if args.emit_agent_card:
        print(json.dumps(emit_agent_card(), indent=2))
        return 0
    if args.check_drift_against:
        with open(args.check_drift_against, encoding="utf-8") as fh:
            published = json.load(fh)
        generated = compose_manifest()
        findings = manifest_drift(generated, published)
        exit_with_drift(findings)
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
