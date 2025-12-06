# scripts/compute_merkle_root.py
"""
Compute the Merkle root for the Cooling Ledger (L1) based on entry hashes.

Usage (from repo root):
    python -m scripts.compute_merkle_root

Behavior:
- Loads `cooling_ledger/L1_cooling_ledger.jsonl`.
- Extracts each entry's `hash` field (leaf hashes).
- Builds a Merkle tree and computes the root.
- Writes the root to `cooling_ledger/L1_merkle_root.txt`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arifos_core.ledger_hashing import load_jsonl, HASH_FIELD
from arifos_core.merkle import build_merkle_tree

DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"
DEFAULT_ROOT_PATH = Path("cooling_ledger") / "L1_merkle_root.txt"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute Merkle root from Cooling Ledger (L1) entry hashes."
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default=str(DEFAULT_LEDGER_PATH),
        help="Path to L1 cooling ledger JSONL file.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=str(DEFAULT_ROOT_PATH),
        help="Path to write the Merkle root.",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    out_path = Path(args.out)

    if not ledger_path.exists():
        print(f"[compute_merkle_root] Ledger file not found: {ledger_path}")
        print("[compute_merkle_root] No ledger to process. OK (empty).")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("", encoding="utf-8")
        return 0

    print(f"[compute_merkle_root] Loading ledger from {ledger_path}...")
    entries = load_jsonl(str(ledger_path))

    if not entries:
        print("[compute_merkle_root] Ledger is empty; no Merkle root to compute.")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("", encoding="utf-8")
        return 0

    leaf_hashes = []
    for idx, entry in enumerate(entries):
        h = entry.get(HASH_FIELD)
        if not h:
            print(f"[compute_merkle_root] Missing hash field at index {idx}")
            return 1
        leaf_hashes.append(h)

    print(f"[compute_merkle_root] Building Merkle tree for {len(leaf_hashes)} leaves...")
    tree = build_merkle_tree(leaf_hashes)
    root = tree.root

    if root is None:
        print("[compute_merkle_root] Failed to compute root (no leaves?).")
        return 1

    print(f"[compute_merkle_root] Merkle root: {root}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(root + "\n", encoding="utf-8")
    print(f"[compute_merkle_root] Root written to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
