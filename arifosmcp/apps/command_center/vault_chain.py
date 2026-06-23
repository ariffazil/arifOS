"""VAULT999 Hash-Chain Ledger — arifOS Command Center v0.3.

Provides real append-only hash-chained records to /root/VAULT999/outcomes.jsonl.
Every entry links to the previous entry's payload_hash via prev_hash.
 GENESIS is the anchor for the first entry.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

_VAULT_PATH = os.getenv(
    "VAULT999_PATH", os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"
)
_VAULT_DIR = str(Path(_VAULT_PATH).parent)
_ledger_lock = RLock()


def _ensure_vault_dir() -> None:
    """Ensure VAULT999 directory exists."""
    os.makedirs(_VAULT_DIR, exist_ok=True)


def _read_last_entry() -> dict[str, Any] | None:
    """Read the last entry from the ledger."""
    _ensure_vault_dir()
    if not os.path.exists(_VAULT_PATH):
        return None
    try:
        with open(_VAULT_PATH) as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            return None
        return json.loads(lines[-1])
    except (json.JSONDecodeError, OSError):
        return None


def _hash_payload(payload: dict[str, Any]) -> str:
    """Compute a short deterministic hash of a payload dict."""
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def append_vault_record(
    entry_type: str,
    payload: dict[str, Any],
    permanent: bool = False,
    note: str = "",
    actor_id: str = "arif",
    app: str = "command_center",
) -> dict[str, Any]:
    """Append a hash-chained record to the VAULT999 ledger.

    Each record contains:
      - entry_id: VAULT-<8hex>
      - payload_hash: sha256[:16] of the canonical payload
      - prev_hash: previous entry's payload_hash (or GENESIS)
      - chain_hash: sha256(payload_hash + prev_hash)[:16]
      - timestamp: ISO-8601 UTC
      - permanent: whether this is a permanent seal
      - type: event classification
      - note: human-readable description
      - app: source application

    Returns the created record dict.
    """
    with _ledger_lock:
        _ensure_vault_dir()

        last = _read_last_entry()
        prev_hash = last.get("payload_hash", "GENESIS") if last else "GENESIS"

        canonical = {
            "entry_type": entry_type,
            "actor_id": actor_id,
            "app": app,
            **payload,
        }
        payload_hash = _hash_payload(canonical)
        chain_input = f"{payload_hash}:{prev_hash}"
        chain_hash = hashlib.sha256(chain_input.encode()).hexdigest()[:16]

        entry_id = f"VAULT-{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC).isoformat()

        record: dict[str, Any] = {
            "entry_id": entry_id,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
            "chain_hash": chain_hash,
            "timestamp": now,
            "permanent": permanent,
            "type": entry_type,
            "note": note,
            "app": app,
            "actor_id": actor_id,
            "payload": canonical,
        }

        with open(_VAULT_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")

        # Return without the full payload to keep the return value lean
        return {
            "entry_id": entry_id,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
            "chain_hash": chain_hash,
            "timestamp": now,
            "permanent": permanent,
            "type": entry_type,
            "note": note,
        }


def read_vault_entries(limit: int = 20) -> list[dict[str, Any]]:
    """Read the last N entries from the VAULT999 ledger.

    Returns entries newest-first.
    """
    _ensure_vault_dir()
    if not os.path.exists(_VAULT_PATH):
        return []

    try:
        with open(_VAULT_PATH) as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]
        entries = []
        for line in lines[-limit:]:
            # Strip payload to keep response lean
            lean = {k: v for k, v in line.items() if k != "payload"}
            entries.append(lean)
        return entries
    except (json.JSONDecodeError, OSError):
        return []


def verify_chain() -> dict[str, Any]:
    """Verify hash-chain integrity of the entire VAULT999 ledger.

    Returns a report: {"valid": bool, "entries_checked": int, "breaks": list[str]}.
    """
    _ensure_vault_dir()
    if not os.path.exists(_VAULT_PATH):
        return {"valid": True, "entries_checked": 0, "breaks": []}

    breaks: list[str] = []
    try:
        with open(_VAULT_PATH) as f:
            lines = [json.loads(line.strip()) for line in f if line.strip()]
    except (json.JSONDecodeError, OSError) as e:
        return {"valid": False, "entries_checked": 0, "breaks": [str(e)]}

    for i, entry in enumerate(lines):
        if i == 0:
            expected_prev = "GENESIS"
        else:
            expected_prev = lines[i - 1]["payload_hash"]

        actual_prev = entry.get("prev_hash", "")
        if actual_prev != expected_prev:
            breaks.append(
                f"Entry {entry.get('entry_id', '?')}: prev_hash={actual_prev[:16]} "
                f"!= expected={expected_prev[:16]}"
            )

        # Verify chain_hash
        chain_input = f"{entry['payload_hash']}:{actual_prev}"
        expected_chain = hashlib.sha256(chain_input.encode()).hexdigest()[:16]
        if entry.get("chain_hash", "") != expected_chain:
            breaks.append(f"Entry {entry.get('entry_id', '?')}: chain_hash mismatch")

    return {
        "valid": len(breaks) == 0,
        "entries_checked": len(lines),
        "breaks": breaks,
    }
