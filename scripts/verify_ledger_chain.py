# scripts/verify_ledger_chain.py
"""
Verify the SHA-256 hash-chain integrity of the Cooling Ledger (L1).

Usage (from repo root):
    python -m scripts.verify_ledger_chain

This is CI-friendly: exit code 0 = OK, 1 = chain broken.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arifos_core.governance.ledger_hashing import load_jsonl, verify_chain

DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify SHA-256 hash-chain integrity of Cooling Ledger (L1)."
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default=str(DEFAULT_LEDGER_PATH),
        help="Path to L1 cooling ledger JSONL file.",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger)

    if not ledger_path.exists():
        print(f"[verify_ledger_chain] Ledger file not found: {ledger_path}")
        print("[verify_ledger_chain] No ledger to verify. OK (empty).")
        return 0

    print(f"[verify_ledger_chain] Loading ledger from {ledger_path}...")
    entries = load_jsonl(str(ledger_path))

    if not entries:
        print("[verify_ledger_chain] Ledger is empty. OK.")
        return 0

    print("[verify_ledger_chain] Verifying chain...")
    ok = verify_chain(entries)

    if ok:
        print(f"[verify_ledger_chain] Chain OK - {len(entries)} entries verified.")
        return 0
    else:
        print("[verify_ledger_chain] Chain BROKEN!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
