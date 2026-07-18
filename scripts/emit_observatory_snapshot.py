#!/usr/bin/env python3
"""Emit the canonical signed Observatory snapshot to the public snapshot store.

The API and this scheduled external emitter deliberately share one builder.
The emitter does not invoke tools; durable capability evidence remains the SOT.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from arifosmcp.runtime.capability_drift import PUBLIC_CANONICAL_TOOLS  # noqa: E402
from arifosmcp.runtime.rest_routes.observatory_routes import build_snapshot  # noqa: E402

SNAP_DIR = Path("/root/.arifos/observatory/snapshots")


def build_observatory() -> dict[str, object]:
    """Build from the same SOT used by the live Observatory API.

    The external process has no FastMCP instance, so it supplies the canonical
    public registration set. Invocation and test truth still comes from the
    canonical durable capability cache and event bus.
    """
    return build_snapshot(None, registered_tools=set(PUBLIC_CANONICAL_TOOLS))


def main() -> int:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    print("=== arifOS Observatory Emitter — generating signed snapshot ===", file=sys.stderr)
    snap = build_observatory()
    snap_id = str(snap["snapshot_id"])
    out_path = SNAP_DIR / f"{snap_id}.json"
    latest_path = SNAP_DIR / "snapshot_latest.json"
    encoded = json.dumps(snap, indent=2, default=str)
    out_path.write_text(encoded, encoding="utf-8")
    latest_path.write_text(encoded, encoding="utf-8")
    print(f"  wrote {out_path}", file=sys.stderr)
    print(f"  wrote {latest_path}", file=sys.stderr)
    signature = snap.get("signature") if isinstance(snap.get("signature"), dict) else {}
    print(f"  signature.state: {signature.get('state')}", file=sys.stderr)
    print(f"  signature.key_id: {signature.get('key_id')}", file=sys.stderr)
    findings_block = snap.get("findings") if isinstance(snap.get("findings"), dict) else {}
    findings = findings_block.get("findings") if isinstance(findings_block, dict) else []
    for finding in findings if isinstance(findings, list) else []:
        if not isinstance(finding, dict):
            continue
        print(
            f"    {finding.get('id')} | {finding.get('severity')} | "
            f"{finding.get('status')} | {str(finding.get('evidence'))[:80]}",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
