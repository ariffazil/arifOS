#!/usr/bin/env python3
"""
sync_manifest.py — Sync WEALTH live tool count into arifOS federation manifests.

Queries the WEALTH MCP server's tools/list endpoint, verifies the live count,
then updates the three federation manifest files that track WEALTH's surface:

  - registry/federation_registry.json
  - arifosmcp/sites/apex-dashboard/federation.charter.json
  - static/mcp-discovery-index.json

Safety guard: aborts if live_count == 0 (possible import failure in WEALTH).

Usage:
    python scripts/sync_manifest.py [--dry-run] [--wealth-url URL]

Exit codes:
    0 = manifests updated (or dry-run passed)
    1 = SYNC_ABORT: zero tools returned or unreachable
    2 = manifest parse/write error
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

WEALTH_DEFAULT_URL = "http://localhost:18082/mcp"
WEALTH_BRIDGE_PORT_ENV = "WEALTH_BRIDGE_PORT"

MANIFEST_FILES = {
    "federation_registry": PROJECT_ROOT / "registry" / "federation_registry.json",
    "federation_charter": (
        PROJECT_ROOT
        / "arifosmcp"
        / "sites"
        / "apex-dashboard"
        / "federation.charter.json"
    ),
    "mcp_discovery": PROJECT_ROOT / "static" / "mcp-discovery-index.json",
}


def _build_url(base: str) -> str:
    import os

    port = os.environ.get(WEALTH_BRIDGE_PORT_ENV)
    if port:
        return f"http://localhost:{port}/mcp"
    return base


def _fetch_live_count(wealth_url: str) -> int:
    """Call WEALTH MCP tools/list and return the number of live tools."""
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
    ).encode()

    req = urllib.request.Request(
        wealth_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
    except urllib.error.URLError as exc:
        print(f"SYNC_ABORT: Cannot reach WEALTH at {wealth_url} — {exc}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"SYNC_ABORT: Invalid JSON from WEALTH — {exc}", file=sys.stderr)
        sys.exit(1)

    tools = body.get("result", {}).get("tools", [])
    return len(tools)


def _update_federation_registry(path: Path, live_count: int, dry_run: bool) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR reading {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    data["tool_count"]["WEALTH"] = live_count
    # Recalculate total from all organ counts
    data["tool_count"]["total"] = sum(
        v for k, v in data["tool_count"].items() if k != "total"
    )

    for server in data.get("servers", []):
        if server.get("organ") == "WEALTH":
            server["tools"] = live_count
            # Remove stale split-count fields if present
            server.pop("public_surface", None)
            server.pop("runtime_surface", None)
            server.pop("hidden_aliases", None)

    if not dry_run:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    prefix = "[dry-run] " if dry_run else ""
    total = data["tool_count"]["total"]
    print(f"  {prefix}federation_registry.json → WEALTH tools={live_count}, total={total}")


def _update_federation_charter(path: Path, live_count: int, dry_run: bool) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR reading {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    organs = data.get("organs", {})
    # organs is a dict keyed by lowercase organ id (e.g. "wealth")
    wealth = organs.get("wealth") if isinstance(organs, dict) else None
    if wealth is None:
        print(f"  WARNING: WEALTH organ not found in {path.name} — skipping")
        return

    old = wealth.get("tool_count")
    wealth["tool_count"] = live_count
    # Keep discovery_note count token in sync
    note = wealth.get("discovery_note", "")
    if note and old is not None and str(old) in note:
        wealth["discovery_note"] = note.replace(str(old), str(live_count), 1)

    if not dry_run:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    prefix = "[dry-run] " if dry_run else ""
    print(f"  {prefix}federation.charter.json → WEALTH tool_count={live_count}")


def _update_mcp_discovery(path: Path, live_count: int, dry_run: bool) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR reading {path}: {exc}", file=sys.stderr)
        sys.exit(2)

    wealth_organ = data.get("organs", {}).get("wealth")
    if wealth_organ is None:
        print(f"  WARNING: wealth organ not found in {path.name} — skipping")
        return

    wealth_organ["verified_mcp_tool_count"] = live_count
    wealth_organ["rest_registry_tool_count"] = live_count

    if not dry_run:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    prefix = "[dry-run] " if dry_run else ""
    print(f"  {prefix}mcp-discovery-index.json → WEALTH verified_mcp_tool_count={live_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing files")
    parser.add_argument("--wealth-url", default=None, help=f"WEALTH MCP endpoint (default: {WEALTH_DEFAULT_URL})")
    args = parser.parse_args()

    wealth_url = args.wealth_url or _build_url(WEALTH_DEFAULT_URL)

    print(f"sync_manifest: querying WEALTH at {wealth_url} ...")
    live_count = _fetch_live_count(wealth_url)

    if live_count == 0:
        print(
            "SYNC_ABORT: runtime returned 0 tools — possible import failure, monolith.py not updated",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"sync_manifest: live_count={live_count}")
    print("sync_manifest: updating manifests ...")

    _update_federation_registry(MANIFEST_FILES["federation_registry"], live_count, args.dry_run)
    _update_federation_charter(MANIFEST_FILES["federation_charter"], live_count, args.dry_run)
    _update_mcp_discovery(MANIFEST_FILES["mcp_discovery"], live_count, args.dry_run)

    print(f"sync_manifest: {'dry-run complete' if args.dry_run else 'done'} — WEALTH={live_count} tools")


if __name__ == "__main__":
    main()
