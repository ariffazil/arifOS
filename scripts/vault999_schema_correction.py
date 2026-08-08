#!/usr/bin/env python3
"""
VAULT999 Schema Correction — retroactive chain-link for legacy entries
══════════════════════════════════════════════════════════════════════════

APPEND-ONLY. Never mutates existing entries. Only appends correction receipts.

Purpose:
  For each entry in outcomes.jsonl that lacks a `chain_hash` key (or has null),
  this script emits a correction receipt that:
  1. Identifies the entry by line_no and event
  2. Computes SHA-256 of the entry content
  3. Links it into a correction chain
  4. Appends a CORRECTION_RECEIPT to outcomes.jsonl

Usage:
  python3 scripts/vault999_schema_correction.py --dry-run   # preview only
  python3 scripts/vault999_schema_correction.py --execute    # append receipts

F1 AMANAH: reversible because we only append — the original entries remain intact.
F2 TRUTH: correction receipts carry OBS epistemic labels.
F11 AUDIT: every receipt is self-attributed and timestamped.
"""

from __future__ import annotations
import hashlib
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

VAULT_FILE = Path("/root/arifOS/VAULT999/outcomes.jsonl")


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def find_broken_entries(path: Path) -> list[dict]:
    """Find entries with missing or null chain_hash, plus non-dict noise."""
    broken = []
    noise = 0
    with open(path) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                broken.append({
                    "line_no": line_no,
                    "event": "PARSE_ERROR",
                    "actor": "?",
                    "ts": "?",
                    "schema": "PARSE_ERROR",
                    "content_hash": sha256_hex(line),
                })
                continue
            if not isinstance(entry, dict):
                # Non-dict JSON (string, list, etc.) — noise in the vault
                noise += 1
                continue
            if "chain_hash" not in entry or entry.get("chain_hash") is None:
                broken.append({
                    "line_no": line_no,
                    "event": entry.get("event", "?"),
                    "actor": entry.get("actor", entry.get("tool_origin", "?")),
                    "ts": entry.get("ts", entry.get("timestamp", "?")),
                    "schema": "LEGACY_FLAT_ROW" if "timestamp" in entry else "MISSING_CHAIN_HASH",
                    "content_hash": sha256_hex(line),
                })
    if noise:
        print(f"  (skipped {noise} non-dict noise lines)")
    return broken


def emit_correction_receipt(
    broken: list[dict],
    prev_correction_hash: str,
    dry_run: bool = True,
) -> str | None:
    """Build and optionally append a correction receipt."""
    receipt = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "VAULT999_SCHEMA_CORRECTION",
        "actor": "hermes-audit",
        "session": "SEAL-bf67c3ff053f41e1",
        "correction_type": "retroactive_chain_link",
        "entries_corrected": len(broken),
        "entry_hashes": [b["content_hash"] for b in broken],
        "entry_lines": [b["line_no"] for b in broken],
        "broken_kinds": list(set(b["schema"] for b in broken)),
        "prev_correction_hash": prev_correction_hash,
        "epistemic_label": "OBS",
        "reversible": True,
        "note": (
            "Append-only correction. Original entries unchanged. "
            "This receipt links legacy chain_hash-missing entries into the correction chain."
        ),
    }
    receipt_str = json.dumps(receipt, ensure_ascii=False)
    receipt_hash = sha256_hex(receipt_str)

    receipt["chain_hash"] = receipt_hash
    receipt_line = json.dumps(receipt, ensure_ascii=False) + "\n"

    if dry_run:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
        return receipt_hash
    else:
        with open(VAULT_FILE, "a") as f:
            f.write(receipt_line)
        print(f"✅ Appended correction receipt: chain_hash={receipt_hash[:16]}…")
        return receipt_hash


def main() -> None:
    dry_run = "--execute" not in sys.argv

    if not VAULT_FILE.exists():
        print("ERROR: outcomes.jsonl not found", file=sys.stderr)
        sys.exit(1)

    broken = find_broken_entries(VAULT_FILE)
    if not broken:
        print("✅ No broken entries found — vault is clean")
        return

    print(f"Found {len(broken)} entries with missing chain_hash")
    print(f"Schema types: {list(set(b['schema'] for b in broken))}")
    print(f"Line range: {broken[0]['line_no']}–{broken[-1]['line_no']}")
    print()

    if dry_run:
        print("=== DRY RUN — no receipts will be appended ===")
        print(f"Would append 1 correction receipt covering {len(broken)} entries")
        emit_correction_receipt(broken, "GENESIS", dry_run=True)
        print()
        print("To execute: python3 scripts/vault999_schema_correction.py --execute")
    else:
        print("=== EXECUTE — appending correction receipt ===")
        receipt_hash = emit_correction_receipt(broken, "GENESIS", dry_run=False)
        print(f"Corrections sealed. Run vault999-verify to confirm.")


if __name__ == "__main__":
    main()
