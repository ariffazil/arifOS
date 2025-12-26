# scripts/show_merkle_proof.py
"""
Show Merkle membership proof for a given ledger entry index.

Usage (from repo root):
    python -m scripts.show_merkle_proof --index 0

Options:
    --ledger PATH
    --index N
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from arifos_core.governance.ledger_hashing import load_jsonl, HASH_FIELD
from arifos_core.governance.merkle import build_merkle_tree, get_merkle_proof, verify_merkle_proof


DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show Merkle proof for a given Cooling Ledger entry index."
    )
    parser.add_argument(
        "--ledger",
        type=str,
        default=str(DEFAULT_LEDGER_PATH),
        help="Path to L1 cooling ledger JSONL file.",
    )
    parser.add_argument(
        "--index",
        type=int,
        required=True,
        help="Zero-based index of the ledger entry to prove.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Also verify the proof against the computed root.",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger)

    if not ledger_path.exists():
        print(f"[show_merkle_proof] Ledger file not found: {ledger_path}")
        return 1

    entries = load_jsonl(str(ledger_path))
    if not entries:
        print("[show_merkle_proof] Ledger is empty.")
        return 1

    idx = args.index
    if idx < 0 or idx >= len(entries):
        print(f"[show_merkle_proof] Index {idx} out of range (0..{len(entries)-1})")
        return 1

    leaf_hashes = []
    for entry in entries:
        h = entry.get(HASH_FIELD)
        if not h:
            print("[show_merkle_proof] Missing hash field in an entry.")
            return 1
        leaf_hashes.append(h)

    tree = build_merkle_tree(leaf_hashes)
    root = tree.root
    proof = get_merkle_proof(tree, idx)

    print(f"Entry index: {idx}")
    print(f"Leaf hash : {leaf_hashes[idx]}")
    print(f"Root hash : {root}")
    print(f"Proof steps ({len(proof)} from leaf to root):")
    for i, step in enumerate(proof):
        print(f"  [{i}] sibling={step.sibling} position={step.position}")

    if args.verify:
        print("\nVerifying proof...")
        valid = verify_merkle_proof(leaf_hashes[idx], proof, root)
        if valid:
            print("Proof VALID")
        else:
            print("Proof INVALID")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
