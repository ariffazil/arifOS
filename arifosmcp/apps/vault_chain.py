"""
vault_chain.py — arifOS 999 Immutable Ledger Hash Chain
══════════════════════════════════════════════════════
Append-only hash-chained record layer for VAULT999.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

VAULT_PATH = Path(os.environ.get("VAULT999_PATH", "/root/VAULT999/outcomes.jsonl"))


def _compute_hash(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def get_last_hash() -> str:
    """Read last record hash from vault. Return 'GENESIS' if empty or missing."""
    if not VAULT_PATH.exists():
        return "GENESIS"
    try:
        text = VAULT_PATH.read_text().strip()
        if not text:
            return "GENESIS"
        last_line = text.split("\n")[-1]
        record = json.loads(last_line)
        return record.get("payload_hash", "GENESIS")
    except Exception:
        return "GENESIS"


def append_vault_record(record: dict) -> dict:
    """Append a hash-chained record to VAULT999.

    Record format:
      - entry_id     — VAULT-xxxxxx (unique)
      - payload_hash — SHA-256[:16] of the record content
      - prev_hash    — hash of the previous entry (GENESIS for first)
      - timestamp    — UTC ISO-8601
      - permanent    — True (never deletable)

    DITEMPA BUKAN DIBERI — Forged, Not Given
    """
    entry_id = f"VAULT-{uuid.uuid4().hex[:6]}"
    prev_hash = get_last_hash()

    # Timestamped payload
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    record["entry_id"] = entry_id
    record["prev_hash"] = prev_hash

    # Compute content hash (stable — excludes entry_id and self hash)
    content_for_hash = {
        k: v for k, v in record.items() if k not in ("entry_id", "payload_hash")
    }
    payload_hash = _compute_hash(
        json.dumps(content_for_hash, sort_keys=True, default=str)
    )
    record["payload_hash"] = payload_hash

    # Ensure vault directory exists
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Append-only write
    line = json.dumps(record, default=str) + "\n"
    with open(VAULT_PATH, "a") as f:
        f.write(line)

    return {
        "vault_receipt": record,
        "entry_id": entry_id,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
        "timestamp": record["timestamp"],
        "chain_status": "APPENDED",
    }
