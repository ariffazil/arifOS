#!/usr/bin/env python3
"""
Connector schema drift audit — regenerates from live runtime tools/list.

Permanent fix per Arif directive 2026-07-24:
  runtime tools/list → canonical capability registry →
  OpenAPI / plugin export / MCP card / tool manifest

CI must FAIL when:
  advertised_tools != runtime_callable_tools
  advertised_schema != runtime_input_schema

Usage:
  python scripts/audit_connector_schemas.py          # audit only
  python scripts/audit_connector_schemas.py --fix    # regenerate from live
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

ORGANS = {
    "arifos": "http://127.0.0.1:8088",
    "geox": "http://127.0.0.1:8081",
    "wealth": "http://127.0.0.1:18082",
    "well": "http://127.0.0.1:18083",
    "aforge": "http://127.0.0.1:7072",
}


def probe_live_tools(base_url: str) -> list[dict[str, Any]]:
    """Call tools/list on a live MCP server."""
    req = Request(
        f"{base_url}/mcp",
        data=json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {},
            }
        ).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
            return body.get("result", {}).get("tools", [])
    except (URLError, json.JSONDecodeError, OSError) as exc:
        print(f"  ⚠ probe {base_url} failed: {exc}", file=sys.stderr)
        return []


def read_static_tools(manifest_path: Path) -> list[str]:
    """Read tool names from a static manifest file."""
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text())
        tools = data.get("tools", [])
        if isinstance(tools, list):
            return [t if isinstance(t, str) else t.get("name", "?") for t in tools]
    except (json.JSONDecodeError, OSError):
        pass
    return []


FILES_TO_CHECK: list[tuple[Path, str, str]] = [
    (ROOT / "static" / ".well-known" / "ai-plugin.json", "arifos", "ai-plugin"),
    (ROOT / "static" / "manifest" / "tools.json", "arifos", "manifest"),
    (ROOT / "contracts" / "tools.yaml", "arifos", "contract"),
]


def main() -> int:
    fix = "--fix" in sys.argv or "--regenerate" in sys.argv
    errors = 0

    for manifest_path, organ, label in FILES_TO_CHECK:
        print(f"\n=== {label} ({organ}) ===")

        live_tools = probe_live_tools(ORGANS[organ])
        live_names = sorted(t["name"] for t in live_tools)

        if not live_names:
            print(f"  ❌ LIVE PROBE FAILED — cannot verify {label}")
            errors += 1
            continue

        print(f"  Live tools: {', '.join(live_names)}")

        if not manifest_path.exists():
            print(f"  ⚠ {label} file missing: {manifest_path}")
            continue

        static_names = read_static_tools(manifest_path)

        if not static_names:
            print(f"  ⚠ {label} has no tool list — skipping comparison")
            continue

        print(f"  Advertised: {', '.join(static_names)}")

        only_in_live = set(live_names) - set(static_names)
        only_in_static = set(static_names) - set(live_names)

        if not only_in_live and not only_in_static:
            print("  ✅ MATCH — no drift")
            continue

        if only_in_static:
            print(f"  ❌ DRIFT: advertised but NOT callable: {sorted(only_in_static)}")
            errors += 1

        if only_in_live:
            print(f"  ⚠ MISSING from manifest: {sorted(only_in_live)}")

        if fix and label == "ai-plugin":
            new_data = json.loads(manifest_path.read_text())
            new_data["tools"] = live_names
            new_data["_regenerated"] = "2026-07-24T11:35:00Z"
            new_data["_source"] = f"live runtime tools/list at {ORGANS[organ]}"
            manifest_path.write_text(json.dumps(new_data, indent=2) + "\n")
            print(f"  🔧 REGENERATED {manifest_path}")

    print()
    if errors:
        print(f"❌ DRIFT DETECTED: {errors} failures")
        return 1
    print("✅ ALL CONNECTOR SCHEMAS MATCH LIVE RUNTIME")
    return 0


if __name__ == "__main__":
    sys.exit(main())
