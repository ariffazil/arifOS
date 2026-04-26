"""
vault_chain.py — arifOS 999 Immutable Ledger Hash Chain
══════════════════════════════════════════════════════
Append-only hash-chained record layer for VAULT999.

Each entry carries:
  - entry_id       — unique identifier
  - payload_hash   — SHA-256[:16] of the record content
  - prev_hash      — hash of the previous entry (GENESIS for first)
  - timestamp      — UTC ISO-8601
  - permanent      — True (never deletable)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

VAULT_PATH = Path("/root/VAULT999/outcomes.jsonl")


def get_last_hash() -> str:
    """Read last record hash from vault. Return 'GENESIS' if empty or missing."""
    if not VAULT_PATH.exists():
        return "GENESIS"
    text = VAULT_PATH.read_text().strip()
    if not text:
        return "GENESIS"
    lines = text.split("\n")
    if not lines:
        return "GENESIS"
    try:
        last = json.loads(lines[-1])
    except (json.JSONDecodeError, IndexError):
        return "GENESIS"
    return last.get("payload_hash", "GENESIS")


def append_vault_record(record: dict) -> dict:
    """Append a hash-chained record to VAULT999.

    Returns a vault receipt dict with:
      - entry_id
      - payload_hash
      - prev_hash
      - timestamp
      - vault_receipt  (VAULT_<hash>)
      - status ("SEAL")
    """
    prev_hash = get_last_hash()
    entry_id = f"VAULT-{uuid.uuid4().hex[:12]}"
    record_json = json.dumps(record, sort_keys=True)
    payload_hash = hashlib.sha256(record_json.encode()).hexdigest()[:16]
    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "entry_id": entry_id,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
        "timestamp": now,
        "permanent": True,
        **record,
    }

    with open(VAULT_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return {
        "entry_id": entry_id,
        "payload_hash": payload_hash,
        "prev_hash": prev_hash,
        "timestamp": now,
        "vault_receipt": f"VAULT_{payload_hash}",
        "status": "SEAL",
    }
