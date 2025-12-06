# scripts/build_ledger_hashes.py
"""
Rebuild SHA-256 hash-chain for the Cooling Ledger (L1).

Usage (from repo root):
    python -m scripts.build_ledger_hashes

Behavior:
- Loads `cooling_ledger/L1_cooling_ledger.jsonl` (if exists).
- Recomputes `hash` and `previous_hash` for each entry in order.
- Writes back to the same file.
- Optionally writes a backup copy before overwriting.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from arifos_core.ledger_hashing import (
    chain_entries,
    dump_jsonl,
    load_jsonl,
    verify_chain,
)


DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"
BACKUP_SUFFIX = ".bak"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rebuild SHA-256 hash-chain for Cooling Ledger (L1)."
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default=str(DEFAULT_LEDGER_PATH),
        help="Path to L1 cooling ledger JSONL file.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not write a backup file before overwriting.",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger)

    if not ledger_path.exists():
        print(f"[build_ledger_hashes] Ledger file not found: {ledger_path}")
        return

    print(f"[build_ledger_hashes] Loading ledger from {ledger_path}...")
    entries = load_jsonl(str(ledger_path))

    if not entries:
        print("[build_ledger_hashes] Ledger is empty. Nothing to do.")
        return

    if not args.no_backup:
        backup_path = ledger_path.with_suffix(ledger_path.suffix + BACKUP_SUFFIX)
        print(f"[build_ledger_hashes] Creating backup at {backup_path}...")
        shutil.copy2(ledger_path, backup_path)

    print("[build_ledger_hashes] Recomputing chain hashes...")
    chained = chain_entries(entries)

    print("[build_ledger_hashes] Verifying chain consistency...")
    if not verify_chain(chained):
        print("[build_ledger_hashes] ERROR: Chain inconsistent after recompute. Aborting.")
        return

    print(f"[build_ledger_hashes] Writing updated ledger to {ledger_path}...")
    dump_jsonl(chained, str(ledger_path))
    print("[build_ledger_hashes] Done.")


if __name__ == "__main__":
    main()
