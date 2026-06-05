"""F1 AMANAH — VAULT999 append-only seal writer.

Each tool execution produces a seal record appended to
/root/VAULT999/outcomes.jsonl (or the path in VAULT999_OUTCOMES env).
Records are SHA-256 hash-chained via `merkle_leaf` (current_hash +
prev_hash). This is an out-of-band pattern for when the F13 SOVEREIGN
gate on arif_vault_seal is held (unverified actor). The shape is
deliberately close to the canonical Supabase `vault_sealed_events`
schema so a future migration is a straight port.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import threading
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional

DEFAULT_VAULT_PATH = "/root/VAULT999/outcomes.jsonl"


def _vault_path() -> Path:
    p = Path(os.environ.get("VAULT999_OUTCOMES", DEFAULT_VAULT_PATH))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _read_last_leaf(path: Path) -> str:
    """Find the most recent merkle_leaf in the file. Returns 'GENESIS' if empty."""
    if not path.exists() or path.stat().st_size == 0:
        return "GENESIS"
    # Read in reverse chunks; for big files this is O(leaf) not O(file).
    with path.open("rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        if size == 0:
            return "GENESIS"
        chunk = 64 * 1024
        data = b""
        pos = size
        while pos > 0 and data.count(b"\n") < 5:
            read = min(chunk, pos)
            pos -= read
            f.seek(pos)
            data = f.read(read) + data
        # Walk lines from end
        lines = data.split(b"\n")
        for raw in reversed(lines):
            line = raw.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if not isinstance(rec, dict):
                continue
            leaf = rec.get("merkle_leaf")
            if leaf:
                return leaf
    return "GENESIS"


_lock = threading.Lock()


@dataclass
class SealRecord:
    id: str
    actor: str
    tool: str
    action: str
    verdict: str  # SEAL | SABAR | HOLD | VOID
    method: str
    input_hash: str
    result_summary: dict
    effect_size: Optional[float] = None
    p_value: Optional[float] = None
    confidence_interval: Optional[list] = None
    assumptions_check: Optional[dict] = None
    timestamp: str = ""
    session_id: str = ""
    irreversibility: str = "reversible"
    notes: str = ""
    spss_syntax: Optional[str] = None
    prev_leaf: str = "GENESIS"
    merkle_leaf: str = ""
    raw: dict = field(default_factory=dict)

    def to_jsonl(self) -> str:
        d = asdict(self)
        d["raw"] = self.raw
        return json.dumps(d, ensure_ascii=False, default=str)


def _compute_leaf(prev: str, payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    return hashlib.sha256(f"{prev}|{canonical}".encode("utf-8")).hexdigest()


def seal(
    *,
    actor: str,
    tool: str,
    action: str,
    verdict: str,
    method: str,
    input_hash: str,
    result_summary: dict,
    effect_size: Optional[float] = None,
    p_value: Optional[float] = None,
    confidence_interval: Optional[list] = None,
    assumptions_check: Optional[dict] = None,
    irreversibility: str = "reversible",
    notes: str = "",
    spss_syntax: Optional[str] = None,
    session_id: str = "",
) -> SealRecord:
    """Append a seal record. Thread-safe. Returns the record written."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    epoch = int(time.time() * 1000)
    record_id = (
        f"SAF-{epoch}-{hashlib.sha256((tool + action + ts).encode()).hexdigest()[:8]}"
    )

    payload = {
        "actor": actor,
        "tool": tool,
        "action": action,
        "verdict": verdict,
        "method": method,
        "input_hash": input_hash,
        "result_summary": result_summary,
        "effect_size": effect_size,
        "p_value": p_value,
        "confidence_interval": confidence_interval,
        "assumptions_check": assumptions_check,
        "timestamp": ts,
        "session_id": session_id,
        "irreversibility": irreversibility,
        "notes": notes,
    }
    if spss_syntax:
        payload["spss_syntax"] = spss_syntax

    path = _vault_path()
    with _lock:
        prev = _read_last_leaf(path)
        leaf = _compute_leaf(prev, payload)
        rec = SealRecord(
            id=record_id,
            actor=actor,
            tool=tool,
            action=action,
            verdict=verdict,
            method=method,
            input_hash=input_hash,
            result_summary=result_summary,
            effect_size=effect_size,
            p_value=p_value,
            confidence_interval=confidence_interval,
            assumptions_check=assumptions_check,
            timestamp=ts,
            session_id=session_id,
            irreversibility=irreversibility,
            notes=notes,
            spss_syntax=spss_syntax,
            prev_leaf=prev,
            merkle_leaf=leaf,
            raw=payload,
        )
        with path.open("a", encoding="utf-8") as f:
            f.write(rec.to_jsonl() + "\n")
    return rec


def verify_chain(path: str | Path | None = None) -> dict:
    """Walk the chain and confirm every record's merkle_leaf matches.

    Returns a dict with `valid` (bool), `count` (int), and `errors` (list).
    """
    p = Path(path) if path else _vault_path()
    if not p.exists():
        return {"valid": True, "count": 0, "errors": [], "note": "no vault yet"}

    errors: list[str] = []
    count = 0
    prev = "GENESIS"
    with p.open("r", encoding="utf-8") as f:
        for ln, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"line {ln}: JSON parse error: {e}")
                continue
            if not isinstance(rec, dict):
                # Legacy / cross-organ entries may be JSON strings; skip.
                continue
            payload = rec.get("raw", {})
            if not payload:
                # Reconstruct payload from top-level fields
                payload = {
                    k: rec.get(k)
                    for k in [
                        "actor",
                        "tool",
                        "action",
                        "verdict",
                        "method",
                        "input_hash",
                        "result_summary",
                        "effect_size",
                        "p_value",
                        "confidence_interval",
                        "assumptions_check",
                        "timestamp",
                        "session_id",
                        "irreversibility",
                        "notes",
                        "spss_syntax",
                    ]
                    if k in rec
                }
            leaf = _compute_leaf(prev, payload)
            if rec.get("merkle_leaf") != leaf:
                errors.append(
                    f"line {ln}: chain break — expected {leaf[:8]}… got {rec.get('merkle_leaf', '')[:8]}…"
                )
            if rec.get("prev_leaf") != prev:
                errors.append(f"line {ln}: prev_leaf mismatch")
            prev = rec.get("merkle_leaf", prev)
            count += 1
    return {
        "valid": not errors,
        "count": count,
        "errors": errors[:10],
        "tail_leaf": prev,
    }
