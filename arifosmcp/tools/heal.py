"""arif_heal — read-only repair diagnosis (E2, 2026-10-17).

WAL query + strategy lookup. This tool never mutates: it reads receipt/WAL
files, classifies failure signatures, and returns the registered repair
strategy for each. Execution remains with arif_forge under a SEAL verdict.

Registered as a diagnostic tool (outside the sovereign-ratified 8-verb
facade). Enable/disable with ARIFOS_ENABLE_HEAL_GUARD.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_WAL_CANDIDATES: tuple[str, ...] = (
    "/var/lib/arifflow/receipts.jsonl",
    "/var/lib/arifos/receipts.jsonl",
    "/root/AAA/state/receipts.jsonl",
    "/root/.agent-workbench/mcp-audit.jsonl",
)

# Failure signature -> bounded, reversible repair strategy.
_STRATEGIES: dict[str, dict[str, Any]] = {
    "UNAUTHORIZED_VERB": {
        "owner": "identity",
        "action": "re-init with a signed ACT or use an allowed verb",
        "reversible": True,
        "gate": "arif_init(actor_signature=...)",
    },
    "MCPError": {
        "owner": "wire",
        "action": "check SDK signature drift (mcp 1.x vs 2.x) in the handler",
        "reversible": True,
        "gate": "unit test that exercises the error path",
    },
    "circuit_open": {
        "owner": "transport",
        "action": "probe the target organ /health, then restart its unit",
        "reversible": True,
        "gate": "organ health 200",
    },
    "FQ_GATED": {
        "owner": "metabolism",
        "action": "emit a Verify receipt; FQ floor is 0.5",
        "reversible": True,
        "gate": "arifFlow :7073/health quotient >= 0.5",
    },
    "drift": {
        "owner": "deploy",
        "action": "rebuild wheel from the reviewed commit and restart",
        "reversible": True,
        "gate": "deployed_commit == built_commit",
    },
    "timeout": {
        "owner": "latency",
        "action": "reduce context or route to a faster lane",
        "reversible": True,
        "gate": "p95 latency under budget",
    },
}


def _wal_paths() -> list[Path]:
    override = os.environ.get("ARIFOS_WAL_PATH")
    if override:
        return [Path(override)]
    return [Path(p) for p in _WAL_CANDIDATES if Path(p).exists()]


def _tail_jsonl(path: Path, limit: int) -> list[dict]:
    rows: list[dict] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh.readlines()[-limit:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    obj = {"raw": line[:300]}
                if isinstance(obj, dict):
                    rows.append(obj)
    except Exception:
        return []
    return rows


def _classify(row: dict) -> list[str]:
    blob = json.dumps(row, ensure_ascii=False).lower()
    hits = []
    for sig in _STRATEGIES:
        if sig.lower() in blob:
            hits.append(sig)
    for sig, words in (
        ("UNAUTHORIZED_VERB", ("not allowed", "unauthorized_verb", "forbidden")),
        ("timeout", ("timed out", "timeout")),
        ("circuit_open", ("circuit", "connection refused", "unreachable")),
    ):
        if any(w in blob for w in words) and sig not in hits:
            hits.append(sig)
    return hits


async def arif_heal(
    mode: str = "diagnose",
    query: str = "",
    limit: int = 50,
    actor_id: str = "unknown",
    session_id: str = "",
    session_token: str = "",
) -> dict[str, Any]:
    """Diagnose recent failures and return the repair strategy (read-only).

    Modes:
      diagnose — tail WAL/receipt files, classify signatures, map strategies
      strategy — return the strategy table (optionally filtered by query)
      wal      — return the raw tail of the newest WAL file
    """
    limit = max(1, min(int(limit or 50), 500))
    paths = _wal_paths()

    if mode == "strategy":
        table = _STRATEGIES
        if query:
            q = query.lower()
            table = {k: v for k, v in table.items() if q in k.lower()}
        return {
            "status": "ok",
            "tool": "arif_heal",
            "mode": mode,
            "strategies": table,
            "mutation": False,
        }

    if not paths:
        return {
            "status": "ok",
            "tool": "arif_heal",
            "mode": mode,
            "found": False,
            "wals": [],
            "note": "No WAL/receipt file present; nothing to diagnose.",
            "mutation": False,
        }

    newest = max(paths, key=lambda p: p.stat().st_mtime)
    rows = _tail_jsonl(newest, limit)

    if mode == "wal":
        return {
            "status": "ok",
            "tool": "arif_heal",
            "mode": mode,
            "wal": str(newest),
            "rows": rows[-limit:],
            "mutation": False,
        }

    findings: dict[str, dict[str, Any]] = {}
    for row in rows:
        for sig in _classify(row):
            entry = findings.setdefault(
                sig,
                {"count": 0, "strategy": _STRATEGIES.get(sig, {}), "sample": None},
            )
            entry["count"] += 1
            if entry["sample"] is None:
                entry["sample"] = str(row)[:300]

    return {
        "status": "ok",
        "tool": "arif_heal",
        "mode": "diagnose",
        "wal": str(newest),
        "scanned": len(rows),
        "findings": findings,
        "healthy": not findings,
        "mutation": False,
        "actor_id": actor_id,
        "session_id": session_id,
    }
