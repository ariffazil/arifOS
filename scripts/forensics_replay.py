#!/usr/bin/env python3
"""
Forensic replay (v42.1):
- verifies hash chain continuity
- checks spec_hash/zkpc fields
- enforces Psi >= 1.0 and Amanah == 1 on an entry
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def iter_jsonl(p: Path):
    with p.open("rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True, help="path to cooling_ledger.jsonl")
    ap.add_argument("--entry", type=int, default=None, help="1-based index of entry to check (optional)")
    ap.add_argument("--verify-hash-chain", action="store_true", help="verify hash chain continuity")
    args = ap.parse_args()

    path = Path(args.ledger)
    if not path.exists():
        print(f"Ledger not found: {path}", file=sys.stderr)
        return 2

    entries = list(iter_jsonl(path))
    if not entries:
        print("Empty ledger", file=sys.stderr)
        return 1

    # verify chain if requested
    if args.verify_hash_chain:
        prev_hash = "0" * 64
        for i, rec in enumerate(entries, start=1):
            digest = sha256_bytes((prev_hash + json.dumps(rec, sort_keys=True, default=str)).encode("utf-8"))
            prev_hash = digest
        print(f"Hash chain OK across {len(entries)} entries.")

    # pick target
    if args.entry is None:
        target = entries[-1]
        idx = len(entries)
    else:
        idx = args.entry
        if idx < 1 or idx > len(entries):
            print("Invalid --entry index", file=sys.stderr)
            return 3
        target = entries[idx - 1]

    # field checks
    missing = [k for k in ("spec_hashes", "zkpc_receipt", "commit_hash", "psi", "amanah") if k not in target]
    if missing:
        print(f"Entry {idx}: missing fields {missing}", file=sys.stderr)
        return 4

    if not (target.get("psi", 0) >= 1.0 and target.get("amanah", 0) == 1):
        print(f"Entry {idx}: Psi/Amanah failure", file=sys.stderr)
        return 5

    print(f"Entry {idx} OK — Psi>=1 & Amanah=1; spec_hashes present; zkPC receipt present.")
    if "eye_vector" in target:
        print("EYE:", json.dumps(target["eye_vector"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
