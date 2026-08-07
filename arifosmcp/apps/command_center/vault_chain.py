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


def verify_chain(
    sovereign_receipt_ref: str = "",
) -> dict[str, Any]:
    """Verify hash-chain integrity of the entire VAULT999 ledger.

    Uses four-state anomaly classification instead of boolean:
      - chain_physically_valid: hash links are intact (bool)
      - historical_anomaly: a prior break was detected but accepted (bool)
      - accepted_risk: the break was ratified by sovereign decision (bool)
      - anomaly_repaired: the break was subsequently repaired (bool)

    Args:
        sovereign_receipt_ref: Optional reference to a sovereign decision
            receipt that ratified any historical anomaly as accepted risk.

    Returns a report with four-state anomaly record and optional
    sovereign_receipt_ref citation.
    """
    _ensure_vault_dir()
    if not os.path.exists(_VAULT_PATH):
        return {
            "status": "UNMEASURED",
            "chain_physically_valid": "UNMEASURED",
            "entries_checked": 0,
            "breaks": ["EMPTY_CHAIN: vault file does not exist"],
            "historical_anomaly": False,
            "accepted_risk": False,
            "anomaly_repaired": False,
            "sovereign_receipt_ref": sovereign_receipt_ref or "",
            "reason": "Vault file does not exist — integrity cannot be asserted on an empty chain",
        }

    breaks: list[str] = []
    lines: list[dict[str, Any]] = []
    skipped_lines: list[int] = []
    try:
        with open(_VAULT_PATH) as f:
            for lineno, raw in enumerate(f, 1):
                stripped = raw.strip()
                if not stripped:
                    continue
                try:
                    lines.append(json.loads(stripped))
                except (json.JSONDecodeError, ValueError):
                    skipped_lines.append(lineno)
    except OSError as e:
        return {
            "chain_physically_valid": False,
            "entries_checked": 0,
            "breaks": [str(e)],
            "historical_anomaly": True,
            "accepted_risk": False,
            "anomaly_repaired": False,
            "sovereign_receipt_ref": sovereign_receipt_ref or "",
        }
    if skipped_lines:
        breaks.append(f"Skipped {len(skipped_lines)} non-JSON lines: {skipped_lines[:5]}")

    # Find first chain-linked entry (legacy entries lack payload_hash)
    first_chain_idx = next((i for i, e in enumerate(lines) if "payload_hash" in e), len(lines))

    unlinked: list[str] = []
    for i, entry in enumerate(lines):
        # ── C1 FIX (2026-08-07): Break silence on unlinked entries ───────
        # Previously: entries without payload_hash were silently skipped.
        # This masked six weeks of broken seals (Jul 30 → Aug 3) where
        # entries had no chain fields at all. Now: entries missing BOTH
        # payload_hash AND prev_hash are flagged as UNLINKED gaps.
        # Entries with prev_hash but no payload_hash are legacy-partial
        # (logged as warning, not fatal).
        has_payload = "payload_hash" in entry
        has_prev = bool(entry.get("prev_hash"))
        if not has_payload:
            entry_id = (
                entry.get("id")
                or entry.get("entry_id")
                or entry.get("receipt_id")
                or f"line_{i + 1}"
            )
            timestamp = entry.get("timestamp", "null")
            if not has_prev:
                unlinked.append(
                    f"Entry {entry_id}: UNLINKED — no payload_hash, no prev_hash "
                    f"(timestamp={timestamp}). Arrow of time broken at this entry."
                )
            else:
                breaks.append(
                    f"Entry {entry_id}: legacy-partial — has prev_hash={entry.get('prev_hash', '')[:16]} "
                    f"but no payload_hash. Cannot verify forward link."
                )
            continue

        # Determine expected prev_hash
        if i == first_chain_idx:
            expected_prev = "GENESIS"
        else:
            # Walk backwards to find the previous chain-linked entry
            prev_entry = next(
                (lines[j] for j in range(i - 1, -1, -1) if "payload_hash" in lines[j]),
                None,
            )
            expected_prev = prev_entry["payload_hash"] if prev_entry else "GENESIS"

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

    chain_valid = len(breaks) == 0 and len(unlinked) == 0
    entries_checked = len(lines)
    if entries_checked == 0:
        return {
            "status": "UNMEASURED",
            "chain_physically_valid": "UNMEASURED",
            "entries_checked": 0,
            "breaks": ["EMPTY_CHAIN: vault file contains zero entries"],
            "historical_anomaly": False,
            "accepted_risk": False,
            "anomaly_repaired": False,
            "sovereign_receipt_ref": sovereign_receipt_ref or "",
            "reason": "Zero entries in vault — integrity cannot be asserted on an empty chain",
        }
    # Merge unlinked into breaks for reporting
    all_breaks = breaks + unlinked
    return {
        "status": "OK" if chain_valid else "GAPS_FOUND",
        "chain_physically_valid": chain_valid,
        "entries_checked": entries_checked,
        "breaks": all_breaks,
        "unlinked_count": len(unlinked),
        "historical_anomaly": not chain_valid,
        "accepted_risk": not chain_valid if sovereign_receipt_ref else False,
        "anomaly_repaired": False,
        "sovereign_receipt_ref": sovereign_receipt_ref or "",
    }
