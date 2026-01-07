# scripts/propose_canon_from_receipt.py
"""
Propose canon entries from zkPC receipts for 888 Judge review (v36Ω).

Usage (from repo root):
    python -m scripts.propose_canon_from_receipt --index 0
    python -m scripts.propose_canon_from_receipt --id ZKPC-20251207-abcd1234

This script:
- Reads `cooling_ledger/L1_cooling_ledger.jsonl`,
- Selects a zkpc_receipt entry (by index or id),
- Builds a proposed canon entry (EUREKA-style),
- Writes it to `cooling_ledger/proposed/PROPOSED_CANON_<receipt_id>.json`.

The 888 Judge (you) can then:
- Inspect the proposed file,
- Edit/comment if needed,
- Decide whether to SEAL it into main canon.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from arifos_core.apex.governance.ledger_hashing import load_jsonl

LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"
PROPOSED_DIR = Path("cooling_ledger") / "proposed"


def _load_ledger() -> List[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        print(f"[propose_canon_from_receipt] Ledger not found: {LEDGER_PATH}")
        return []
    return load_jsonl(str(LEDGER_PATH))


def _find_receipt_by_index(entries: List[Dict[str, Any]], index: int) -> Optional[Dict[str, Any]]:
    if index < 0 or index >= len(entries):
        print(f"[propose_canon_from_receipt] Index {index} out of range (0..{len(entries)-1})")
        return None
    entry = entries[index]
    if entry.get("type") != "zkpc_receipt":
        print(
            f"[propose_canon_from_receipt] Entry at index {index} is not a zkpc_receipt "
            f"(type={entry.get('type')})"
        )
        return None
    return entry


def _find_receipt_by_id(entries: List[Dict[str, Any]], rid: str) -> Optional[Dict[str, Any]]:
    for e in entries:
        if e.get("type") == "zkpc_receipt":
            r = e.get("receipt", {})
            if isinstance(r, dict) and r.get("receipt_id") == rid:
                return e
        # Also check top-level id field
        if e.get("id") == rid and e.get("type") == "zkpc_receipt":
            return e
    print(f"[propose_canon_from_receipt] No zkpc_receipt with receipt_id={rid} found.")
    return None


def _build_proposed_canon(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a proposed canon entry skeleton from a zkpc_receipt ledger entry.

    This does NOT write to the main ledger; it is for 888 Judge review.
    """
    receipt = entry.get("receipt", {}) or {}
    rid = receipt.get("receipt_id") or entry.get("id", "UNKNOWN")
    ts = receipt.get("timestamp") or entry.get("timestamp")

    care_scope = receipt.get("care_scope", {})
    metrics = receipt.get("metrics", {})
    verdict = receipt.get("verdict", "UNKNOWN")

    # Try to guess a principle/law text from the receipt.
    # In practice, you may want to edit this manually before SEAL.
    principle = f"EUREKA derived from zkPC receipt {rid}"
    law_text = (
        "This proposed canon is derived from a zkPC-governed event. "
        "It should be edited and SEALED by the 888 Judge before becoming binding law."
    )

    proposed = {
        "id": f"PROPOSED_CANON_{rid}",
        "timestamp": ts,
        "type": "PROPOSED_CANON",
        "source": "propose_canon_from_receipt",
        "from_receipt_id": rid,
        "verdict": verdict,
        "care_scope": care_scope,
        "metrics_snapshot": metrics,
        "canon": {
            "principle": principle,
            "law": law_text,
            "checks": [
                # These are suggestions; edit as needed in the file.
                "Describe the core EUREKA insight in one or two sentences.",
                "Define explicit checks/floors this canon enforces.",
                "State how this canon protects maruah and the weakest stakeholder.",
            ],
            "tags": [
                "proposed",
                "zkpc",
                "eureka_candidate",
            ],
        },
    }
    return proposed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Propose canon from a zkPC receipt (for 888 Judge review)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--index",
        type=int,
        help="Index in L1 ledger to use (must be a zkpc_receipt).",
    )
    group.add_argument(
        "--id",
        type=str,
        help="zkpc_receipt receipt_id to use.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all zkpc_receipt entries in the ledger.",
    )
    args = parser.parse_args()

    entries = _load_ledger()
    if not entries:
        print("[propose_canon_from_receipt] Ledger is empty or not found; nothing to propose.")
        return 1

    # If --list flag, show available receipts
    if args.list:
        print("[propose_canon_from_receipt] zkpc_receipt entries in ledger:")
        for i, e in enumerate(entries):
            if e.get("type") == "zkpc_receipt":
                rid = e.get("id") or (e.get("receipt", {}) or {}).get("receipt_id", "?")
                ts = e.get("timestamp", "?")
                print(f"  [{i}] {rid} @ {ts}")
        return 0

    if args.index is not None:
        entry = _find_receipt_by_index(entries, args.index)
    else:
        entry = _find_receipt_by_id(entries, args.id)

    if entry is None:
        return 1

    proposed = _build_proposed_canon(entry)

    PROPOSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROPOSED_DIR / f"{proposed['id']}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(proposed, f, ensure_ascii=False, indent=2)

    print(f"[propose_canon_from_receipt] Proposed canon written to: {out_path}")
    print("You (888 Judge) should edit and SEAL this before merging into main canon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
