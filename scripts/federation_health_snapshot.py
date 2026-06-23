#!/usr/bin/env python3
"""
federation_health_snapshot.py — Live organ health snapshot for arifOS Federation.

Usage:
    python scripts/federation_health_snapshot.py [--format json|markdown] [--save]

Outputs a structured health snapshot of all federation organs.
If --save is passed, appends a receipt to VAULT999 local ledger.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

ORGANS = [
    {"name": "arifOS", "port": 8088, "path": "/health"},
    {"name": "arifosd", "port": 18081, "path": "/health"},
    {"name": "GEOX", "port": 8081, "path": "/health"},
    {"name": "WEALTH", "port": 18082, "path": "/health"},
    {"name": "WELL", "port": 18083, "path": "/health"},
    {"name": "A-FORGE", "port": 7071, "path": "/health"},
    {"name": "AAA", "port": 3001, "path": "/health"},
    {"name": "APEX", "port": 3002, "path": "/health"},
    {"name": "OpenClaw", "port": 18789, "path": "/health"},
    {"name": "vault999-api", "port": 8100, "path": "/health"},
    {"name": "vault999-writer", "port": 5001, "path": "/health"},
]

TIMEOUT = 5.0


@dataclass
class OrganProbe:
    name: str
    url: str
    status_code: int | None
    ok: bool
    latency_ms: float
    payload: dict[str, Any]
    error: str | None


async def probe_one(client: httpx.AsyncClient, organ: dict[str, Any]) -> OrganProbe:
    url = f"http://127.0.0.1:{organ['port']}{organ['path']}"
    started = datetime.now(timezone.utc)
    try:
        response = await client.get(url, timeout=TIMEOUT)
        latency = (datetime.now(timezone.utc) - started).total_seconds() * 1000
        try:
            payload = response.json()
        except Exception:
            payload = {"raw": response.text[:200]}
        return OrganProbe(
            name=organ["name"],
            url=url,
            status_code=response.status_code,
            ok=response.status_code == 200,
            latency_ms=round(latency, 2),
            payload=payload,
            error=None,
        )
    except Exception as exc:
        latency = (datetime.now(timezone.utc) - started).total_seconds() * 1000
        return OrganProbe(
            name=organ["name"],
            url=url,
            status_code=None,
            ok=False,
            latency_ms=round(latency, 2),
            payload={},
            error=f"{type(exc).__name__}: {exc}",
        )


async def run_snapshot() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        probes = await asyncio.gather(*[probe_one(client, o) for o in ORGANS])

    healthy = sum(1 for p in probes if p.ok)
    snapshot = {
        "snapshot_id": f"health-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": "af-forge",
        "organs_total": len(ORGANS),
        "organs_healthy": healthy,
        "organs_unhealthy": len(ORGANS) - healthy,
        "overall_status": "healthy"
        if healthy == len(ORGANS)
        else "degraded"
        if healthy > len(ORGANS) // 2
        else "critical",
        "organs": [asdict(p) for p in probes],
    }
    return snapshot


def to_markdown(snapshot: dict[str, Any]) -> str:
    lines = [
        f"# Federation Health Snapshot — {snapshot['snapshot_id']}",
        f"**Host:** {snapshot['host']}  ",
        f"**Timestamp:** {snapshot['timestamp']}  ",
        f"**Overall:** {snapshot['overall_status'].upper()} ({snapshot['organs_healthy']}/{snapshot['organs_total']} healthy)",
        "",
        "| Organ | Status | HTTP | Latency (ms) | Error |",
        "|-------|--------|------|-------------:|-------|",
    ]
    for organ in snapshot["organs"]:
        status = "✅ healthy" if organ["ok"] else "❌ unhealthy"
        error = organ["error"] or ""
        lines.append(
            f"| {organ['name']} | {status} | {organ['status_code'] or '-'} | {organ['latency_ms']} | {error} |"
        )
    lines.append("")
    lines.append("## Payloads")
    for organ in snapshot["organs"]:
        lines.append(f"### {organ['name']}")
        lines.append("```json")
        lines.append(json.dumps(organ["payload"], indent=2, default=str))
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def save_to_vault(snapshot: dict[str, Any]) -> None:
    """Append a minimal receipt to the local VAULT999 outcomes ledger."""
    vault_path = "/root/.agent-workbench/vault999.jsonl"
    receipt = {
        "type": "federation_health_snapshot",
        "snapshot_id": snapshot["snapshot_id"],
        "timestamp": snapshot["timestamp"],
        "overall_status": snapshot["overall_status"],
        "organs_healthy": snapshot["organs_healthy"],
        "organs_total": snapshot["organs_total"],
    }
    with open(vault_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, default=str) + "\n")
    print(f"Receipt appended to {vault_path}", file=sys.stderr)


async def main() -> int:
    parser = argparse.ArgumentParser(description="Federation health snapshot")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown")
    parser.add_argument("--save", action="store_true", help="Append receipt to VAULT999")
    args = parser.parse_args()

    snapshot = await run_snapshot()

    if args.format == "json":
        print(json.dumps(snapshot, indent=2, default=str))
    else:
        print(to_markdown(snapshot))

    if args.save:
        save_to_vault(snapshot)

    return 0 if snapshot["overall_status"] == "healthy" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
