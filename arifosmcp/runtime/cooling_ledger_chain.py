"""
CLRP-1 — Cooling ledger file-chain (local JSONL).

Append-only entropy/RSI ledger with parent_hash linkage and optional
seal_chain_ref. Distinct from the Postgres CoolingLedgerClient substrate
and from VAULT999 seal_chain — this is the session-end cooling surface.

Path (canonical): /root/.local/share/arifos/cooling_ledger.jsonl

Doctrine: DITEMPA BUKAN DIBERI. Never rewrite history.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_LEDGER_PATH = Path(
    os.environ.get(
        "ARIFOS_COOLING_LEDGER_PATH",
        "/root/.local/share/arifos/cooling_ledger.jsonl",
    )
)
SEAL_CHAIN_PATH = Path(
    os.environ.get(
        "ARIFOS_SEAL_CHAIN_PATH",
        "/root/.local/share/arifos/vault999/seal_chain.jsonl",
    )
)

_lock = threading.Lock()


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _line_hash(obj: dict[str, Any]) -> str:
    """Hash of entry without entry_hash field (stable canonical JSON)."""
    payload = {k: v for k, v in obj.items() if k != "entry_hash"}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read_all(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            entries.append({"_parse_error": True, "raw": line[:200]})
    return entries


def _latest_seal_ref() -> dict[str, Any] | None:
    if not SEAL_CHAIN_PATH.exists():
        return None
    last: dict[str, Any] | None = None
    try:
        for line in SEAL_CHAIN_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            last = json.loads(line)
    except Exception:
        return None
    if not last:
        return None
    return {
        "seq": last.get("seq") or last.get("entry_seq") or last.get("id"),
        "hash": last.get("hash")
        or last.get("seal_hash")
        or last.get("entry_hash")
        or last.get("chain_hash"),
    }


def append_cooling_entry(
    *,
    agent: str,
    session_id: str | None = None,
    bottleneck: str | None = None,
    fix_type: str | None = None,
    fix_path: str | None = None,
    delta_S: float | None = None,
    verified: bool | None = None,
    seal_id: str | None = None,
    extra: dict[str, Any] | None = None,
    ledger_path: Path | None = None,
    # P1: Cooling recursion guard — origin, depth, parent tracking
    origin: str = "external_failure",
    cooling_depth: int = 0,
    parent_cooling_id: str | None = None,
) -> dict[str, Any]:
    """Append one cooling-ledger entry with parent_hash + entry_seq.

    P1 invariant: cooling_depth MUST be 0 or 1. Depth > 1 is blocked
    with a HOLD response to prevent runaway recursive cooling.
    Depth=0 = root cooling cycle. Depth=1 = permitted nested cooling
    (one level, parent_cooling_id required).

    Old entries without chain fields remain readable; new entries always chain.
    """
    # ── P1: Cooling recursion guard ──
    if cooling_depth > 1:
        return {
            "status": "HOLD",
            "reason": (
                f"cooling_depth={cooling_depth} exceeds maximum of 1. "
                "Recursive cooling beyond one level is blocked by P1 invariant. "
                "If this is a genuine new failure, start a new root cycle "
                "(cooling_depth=0). If this is a permitted nested correction, "
                "use cooling_depth=1 with a valid parent_cooling_id."
            ),
            "cooling_depth": cooling_depth,
            "max_cooling_depth": 1,
            "invariant": "COOLING_RECURSION_GUARD_P1",
        }
    if cooling_depth < 0:
        return {
            "status": "HOLD",
            "reason": f"cooling_depth={cooling_depth} must be >= 0.",
            "cooling_depth": cooling_depth,
            "invariant": "COOLING_RECURSION_GUARD_P1",
        }
    if cooling_depth == 1 and not parent_cooling_id:
        return {
            "status": "HOLD",
            "reason": "cooling_depth=1 requires parent_cooling_id.",
            "cooling_depth": cooling_depth,
            "invariant": "COOLING_RECURSION_GUARD_P1",
        }

    path = ledger_path or DEFAULT_LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with _lock:
        existing = _read_all(path)
        good = [e for e in existing if not e.get("_parse_error")]
        entry_seq = (good[-1].get("entry_seq") or len(good)) + 1 if good else 1
        if good and isinstance(good[-1].get("entry_seq"), int):
            entry_seq = good[-1]["entry_seq"] + 1
        parent_hash = None
        if good:
            prev = good[-1]
            parent_hash = prev.get("entry_hash") or _line_hash(prev)

        entry: dict[str, Any] = {
            "entry_seq": entry_seq,
            "parent_hash": parent_hash,
            "seal_chain_ref": _latest_seal_ref(),
            "ts": _utc_now(),
            "agent": agent,
            "session_id": session_id,
            "bottleneck": bottleneck,
            "fix_type": fix_type,
            "fix_path": fix_path,
            "delta_S": delta_S,
            "verified": verified,
            "seal_id": seal_id,
            # P1 cooling recursion fields
            "origin": origin,
            "cooling_depth": cooling_depth,
            "parent_cooling_id": parent_cooling_id,
            "schema": "cooling_ledger_entry.v2",
        }
        if extra:
            entry["extra"] = extra
        entry["entry_hash"] = _line_hash(entry)

        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def verify_cooling_ledger(
    ledger_path: Path | None = None,
    *,
    n: int | None = None,
    check_seal_refs: bool = True,
) -> dict[str, Any]:
    """Verify parent_hash chain on last N (or all) entries."""
    path = ledger_path or DEFAULT_LEDGER_PATH
    entries = [e for e in _read_all(path) if not e.get("_parse_error")]
    if n is not None and n > 0:
        entries = entries[-n:]

    broken: list[dict[str, Any]] = []
    if not entries:
        return {
            "entry_count": 0,
            "chain_integrity": "EMPTY",
            "broken_entries": [],
            "cross_ref_integrity": "n/a",
            "ledger_path": str(path),
        }

    # If first retained entry has parent_hash but we truncated, skip first parent check
    for i, e in enumerate(entries):
        seq = e.get("entry_seq")
        eh = e.get("entry_hash")
        if eh:
            recomputed = _line_hash(e)
            if eh != recomputed:
                broken.append(
                    {
                        "entry_seq": seq,
                        "reason": "entry_hash_mismatch",
                        "expected": recomputed,
                        "got": eh,
                    }
                )
        if i == 0:
            continue
        prev = entries[i - 1]
        expected_parent = prev.get("entry_hash") or _line_hash(prev)
        got_parent = e.get("parent_hash")
        if got_parent is None:
            # Legacy entry — not a break if chain not yet hardened
            continue
        if got_parent != expected_parent:
            broken.append(
                {
                    "entry_seq": seq,
                    "reason": "parent_hash_mismatch",
                    "expected": expected_parent,
                    "got": got_parent,
                }
            )
        # monotonic seq when both present
        prev_seq = prev.get("entry_seq")
        if isinstance(seq, int) and isinstance(prev_seq, int) and seq != prev_seq + 1:
            broken.append(
                {
                    "entry_seq": seq,
                    "reason": "seq_gap",
                    "expected": prev_seq + 1,
                    "got": seq,
                }
            )

    seal_ok = 0
    seal_total = 0
    if check_seal_refs and SEAL_CHAIN_PATH.exists():
        seal_seqs: set[Any] = set()
        try:
            for line in SEAL_CHAIN_PATH.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                s = json.loads(line)
                seal_seqs.add(s.get("seq") or s.get("id"))
        except Exception:
            seal_seqs = set()
        for e in entries:
            ref = e.get("seal_chain_ref")
            if not ref:
                continue
            seal_total += 1
            if ref.get("seq") in seal_seqs or ref.get("seq") is None:
                seal_ok += 1

    integrity = "PASS" if not broken else f"BROKEN_AT_{broken[0].get('entry_seq')}"
    return {
        "entry_count": len(entries),
        "chain_integrity": integrity,
        "broken_entries": broken,
        "first_entry": {
            "seq": entries[0].get("entry_seq"),
            "ts": entries[0].get("ts"),
        },
        "last_entry": {
            "seq": entries[-1].get("entry_seq"),
            "ts": entries[-1].get("ts"),
        },
        "cross_ref_integrity": (
            f"{seal_ok}/{seal_total} seal_chain_refs present"
            if seal_total
            else "no seal refs in window"
        ),
        "ledger_path": str(path),
    }
