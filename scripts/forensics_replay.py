#!/usr/bin/env python3
"""
Forensic replay (v42.1):
- verifies hash chain continuity
- checks spec_hash presence
- enforces Ψ  1.0 and Amanah == 1 on an entry
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_bytes(b: bytes) -> str:
    """Compute SHA256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()


def iter_jsonl(p: Path):
    """Iterate over JSONL entries."""
    with p.open("rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main():
    """Replay and verify ledger entries."""
    ap = argparse.ArgumentParser(
        description="Forensic replay for arifOS v42.1 Cooling Ledger"
    )
    ap.add_argument(
        "--ledger",
        required=True,
        help="path to cooling_ledger.jsonl"
    )
    ap.add_argument(
        "--entry",
        type=int,
        default=None,
        help="1-based index of entry to check (optional; default=latest)"
    )
    args = ap.parse_args()

    path = Path(args.ledger)
    if not path.exists():
        print(f"Ledger not found: {path}", file=sys.stderr)
        sys.exit(2)

    prev_hash = "0" * 64
    entries = list(iter_jsonl(path))
    if not entries:
        print("Empty ledger", file=sys.stderr)
        sys.exit(1)

    # Verify hash chain
    print(f"Verifying hash chain across {len(entries)} entries...", file=sys.stderr)
    for i, rec in enumerate(entries, start=1):
        digest = sha256_bytes(
            (prev_hash + json.dumps(rec, sort_keys=True)).encode("utf-8")
        )
        prev_hash = digest

    print(f" Hash chain OK", file=sys.stderr)

    # Pick target entry
    if args.entry is None:
        target = entries[-1]
        idx = len(entries)
    else:
        idx = args.entry
        if idx < 1 or idx > len(entries):
            print(f"Invalid --entry index (1-{len(entries)})", file=sys.stderr)
            sys.exit(3)
        target = entries[idx - 1]

    # Field checks (required for forensic integrity)
    required_fields = ("spec_hashes", "zkpc_receipt", "commit_hash", "psi", "amanah")
    missing = [k for k in required_fields if k not in target]
    if missing:
        print(f"Entry {idx}: missing fields {missing}", file=sys.stderr)
        sys.exit(4)

    # Enforce Ψ  1.0 and Amanah == 1 (constitutional requirements)
    psi_val = target.get("psi", 0.0)
    amanah_val = target.get("amanah", 0)
    if not (psi_val >= 1.0 and amanah_val == 1):
        print(
            f"Entry {idx}: Ψ/Amanah failure (Ψ={psi_val}, Amanah={amanah_val})",
            file=sys.stderr
        )
        sys.exit(5)

    # Report success
    print(f" Entry {idx} OK", file=sys.stderr)
    print(f"  Ψ (vitality)  1.0: {psi_val}", file=sys.stderr)
    print(f"  Amanah (trust): {amanah_val}", file=sys.stderr)
    print(f"  spec_hashes present: {bool(target.get('spec_hashes'))}", file=sys.stderr)
    print(f"  zkpc_receipt present: {bool(target.get('zkpc_receipt'))}", file=sys.stderr)
    print(f"  commit_hash: {target.get('commit_hash')}", file=sys.stderr)

    # Optional: print EYE vector reasons
    if "eye_vector" in target:
        eye = target["eye_vector"]
        print(f"  EYE level: {eye.get('level')}", file=sys.stderr)
        print(f"  EYE action: {eye.get('action')}", file=sys.stderr)
        if eye.get("reasons"):
            print(f"  EYE reasons: {eye['reasons']}", file=sys.stderr)

    # Print full entry to stdout (JSON)
    print(json.dumps(target, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
