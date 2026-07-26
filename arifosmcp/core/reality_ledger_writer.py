"""
arifosmcp/core/reality_ledger_writer.py — Z5 Kernel Integration
═══════════════════════════════════════════════════════════════

Writes standardized governance events to the Reality Ledger
from within the arifOS kernel tools. Called as a post-action
hook by arif_judge, arif_seal, arif_forge, and arif_init.

Design principles (F1-F11 compliant):
- Non-blocking: ledger write failure never blocks the governance verdict
- Hash-chained: every event references the previous event's SHA-256
- Immutable: append-only JSONL, chattr +a on the ledger file
- Rebuildable: all events are self-describing; the chain can be re-verified
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

LEDGER_PATH = Path("/root/reality_ledger/reality_ledger.jsonl")


def _read_last_hash() -> str:
    """Read the hash of the last entry for chain integrity."""
    if not LEDGER_PATH.exists():
        return "0" * 64
    try:
        with open(LEDGER_PATH, "r") as f:
            lines = [l for l in f if l.strip() and not l.strip().startswith('{"_schema"')]
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        return last.get("hash", "0" * 64)
    except Exception:
        return "0" * 64


def _compute_hash(entry: dict) -> str:
    """Compute SHA-256 hash of an entry (excluding hash field)."""
    entry_copy = {k: v for k, v in entry.items() if k != "hash"}
    raw = json.dumps(entry_copy, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def write_reality_event(
    actor: str,
    event_type: str,
    session_id: str,
    verdict: str,
    summary: str,
    action_class: str = "governance",
    evidence: Optional[dict] = None,
    payload: Optional[dict] = None,
) -> Optional[str]:
    """
    Write a governance event to the Reality Ledger.

    This function is designed to be called as a post-action hook
    from arif_judge, arif_seal, arif_forge, and arif_init.

    Returns the event_id on success, None on failure.
    Never raises — ledger write failure must not block governance.
    """
    try:
        prev_hash = _read_last_hash()
        event_id = str(uuid4())[:8]

        entry = {
            "event_id": event_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "event_type": event_type,
            "session_id": session_id,
            "verdict": verdict,
            "action_class": action_class,
            "summary": summary,
            "evidence": evidence or {},
            "payload": payload or {},
            "prev_hash": prev_hash,
            "hash": None,
        }

        entry["hash"] = _compute_hash(entry)

        os.makedirs(LEDGER_PATH.parent, exist_ok=True)
        with open(LEDGER_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

        logger.debug("Reality Ledger event written: %s (%s)", event_id, event_type)
        return event_id

    except Exception as e:
        logger.warning("Reality Ledger write failed (non-blocking): %s", e)
        return None
