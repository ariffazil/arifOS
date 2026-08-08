#!/usr/bin/env python3
"""
VAULT999 — Corrective receipts for 47 JUDGE_SEAT_DEPUTY entries lacking chain_hash.

APPEND-ONLY: does not mutate existing entries. Appends a CORRECTION_RECEIPT 
that retroactively links the orphaned entries into the chain.

The 47 entries use schema {timestamp, event, tool_origin, role, ...} without
chain_hash or prev_hash. They were emitted by a seat-deputy activation loop
that bypassed the normal seal path.

After correction, verify with:
  python3 /root/arifOS/scripts/verify_vault_chain.py
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


VAULT = Path("/root/arifOS/VAULT999/outcomes.jsonl")
TARGET_EVENT = "JUDGE_SEAT_DEPUTY_ACTIVATED"


def find_orphans() -> list[dict]:
    orphans = []
    noise = 0
    with open(VAULT) as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                noise += 1
                continue
            if entry.get("event") != TARGET_EVENT:
                continue
            # These entries have "timestamp" not "ts", and no chain_hash
            if "chain_hash" in entry and entry["chain_hash"] is not None:
                continue  # already corrected
            orphans.append({"line_no": line_no, **entry})
    if noise:
        print(f"  (skipped {noise} non-dict noise lines)")
    return orphans


def content_hash(entry: dict) -> str:
    """SHA-256 of the entry content as a deterministic string."""
    canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def append_correction(orphans: list[dict]) -> str:
    """Append a single CORRECTION_RECEIPT linking all 47 orphans."""
    orphan_hashes = [content_hash(o) for o in orphans]
    correction = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "CHAIN_CORRECTION_RECEIPT",
        "actor": "hermes-audit",
        "session": "SEAL-bf67c3ff053f41e1",
        "correction_type": "JUDGE_SEAT_DEPUTY_CHAIN_BACKFILL",
        "entries_corrected": len(orphans),
        "entry_line_numbers": [o["line_no"] for o in orphans],
        "entry_content_hashes": orphan_hashes,
        "reason": (
            "47 JUDGE_SEAT_DEPUTY_ACTIVATED entries were emitted with "
            "{timestamp, event, tool_origin, role} schema but lacked chain_hash "
            "and prev_hash. This receipt retroactively links them."
        ),
        "epistemic_tag": "OBS",
        "reversibility": "F1-REVERSIBLE (append-only, does not alter orphans)",
        "prev_hash": "GENESIS",
        "chain_hash": "",  # computed below
    }
    # Compute chain_hash of the correction itself
    correction["chain_hash"] = content_hash(correction)
    return json.dumps(correction, ensure_ascii=False)


def main():
    import sys
    apply_mode = "--apply" in sys.argv

    orphans = find_orphans()
    if not orphans:
        print("✅ No orphaned JUDGE_SEAT_DEPUTY entries found — vault is clean")
        return

    print(f"Found {len(orphans)} orphaned JUDGE_SEAT_DEPUTY entries")
    print(f"Line range: {orphans[0]['line_no']}–{orphans[-1]['line_no']}")
    print(f"Timestamps: {orphans[0].get('timestamp','?')} → {orphans[-1].get('timestamp','?')}")
    print(f"First 3 actors: {[o.get('actor_id','?') for o in orphans[:3]]}")
    print()

    # Build correction receipt
    receipt_line = append_correction(orphans) + "\n"
    import json
    d = json.loads(receipt_line)
    print(f"Receipt SHA-256: {d['chain_hash'][:16]}…")
    print(f"Entries corrected: {d['entries_corrected']}")
    print()

    if not apply_mode:
        print("=== DRY RUN ===")
        print("NOT APPENDING. Run with --apply to write receipt to vault.")
        return

    print("=== APPLYING ===")
    with open(VAULT, "a") as f:
        f.write(receipt_line)

    print("✅ Correction receipt appended to outcomes.jsonl")
    print("   Run verify_vault_chain.py to confirm chain linkage")


if __name__ == "__main__":
    main()
