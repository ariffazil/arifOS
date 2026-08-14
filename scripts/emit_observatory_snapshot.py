#!/usr/bin/env python3
"""Emit the canonical signed Observatory snapshot to the public snapshot store.

The API and this scheduled external emitter deliberately share one builder.
The emitter does not invoke tools; durable capability evidence remains the SOT.

After the snapshot is written and signed, the emitter optionally delegates
publication to ``observatory_publish.publish_latest_snapshot``. Publication
is gated by the ``OBSERVATORY_PUBLISH_TARGET`` environment variable — when
unset (the default), no webroot writes occur. Live publication requires
explicit F13 sovereign opt-in (T3). The helper itself is atomic and
fail-closed: it never touches the private key and re-verifies every
written artifact by SHA-256 before returning.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from observatory_publish import publish_latest_snapshot  # noqa: E402

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


def _maybe_publish() -> None:
    """Publish to ``$OBSERVATORY_PUBLISH_TARGET`` if set. No-op otherwise.

    We deliberately do not raise on publish failure when no target is set —
    the canonical emit must succeed independently of the publication gate.
    """
    target = os.environ.get("OBSERVATORY_PUBLISH_TARGET", "").strip() or None
    try:
        receipt = publish_latest_snapshot(target)
    except Exception as exc:
        print(f"  publish: FAILED {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    if receipt["status"] == "SKIPPED":
        print(
            "  publish: SKIPPED (OBSERVATORY_PUBLISH_TARGET unset — no live webroot writes)",
            file=sys.stderr,
        )
        return
    print(f"  publish: OK target={receipt['target_dir']}", file=sys.stderr)
    for name, info in receipt["files"].items():
        flag = "skipped" if info.get("skipped") else "wrote"
        print(
            f"    {flag:7s} {name} ({info['size_bytes']} bytes, sha256={info['sha256'][:12]})",
            file=sys.stderr,
        )
    print(f"  verification_url: {receipt['verification_url']}", file=sys.stderr)


def _emit_chain_health() -> None:
    """FIX-2 (2026-08-14): measure seal-chain health via the kernel verify
    endpoint and publish it as a companion artifact next to the snapshot.

    The chain file itself is NEVER rewritten (F1 append-only discipline).
    This reads the kernel's own walk (corrupt lines + gaps) and, separately,
    drops a dated quarantine report beside the chain so the damage is
    documented without silent repair.
    """
    import urllib.request

    url = "http://127.0.0.1:8088/api/observatory/v1/seal/verify"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            health = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"  chain-health: FAILED to reach kernel verify ({exc})", file=sys.stderr)
        return
    health["measured_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    (SNAP_DIR / "chain_health_latest.json").write_text(
        json.dumps(health, indent=2, default=str), encoding="utf-8"
    )
    chain_path = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    if chain_path.exists():
        report_path = chain_path.parent / "seal_chain.quarantine-report.json"
        if not report_path.exists():
            report_path.write_text(
                json.dumps(health, indent=2, default=str), encoding="utf-8"
            )
            print(f"  chain-health: wrote one-time quarantine report {report_path}", file=sys.stderr)
    target = os.environ.get("OBSERVATORY_PUBLISH_TARGET", "").strip() or None
    if target:
        out = Path(target) / "observatory-chain-health.json"
        tmp = out.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(health, indent=2, default=str), encoding="utf-8")
        tmp.replace(out)
        print(
            f"  chain-health: {health.get('status')} entries={health.get('entries')} "
            f"corrupt={health.get('corrupt_lines')} gaps={len(health.get('gaps') or [])} -> {out}",
            file=sys.stderr,
        )


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
    _maybe_publish()
    _emit_chain_health()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
