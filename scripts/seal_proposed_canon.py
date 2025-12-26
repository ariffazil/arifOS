# scripts/seal_proposed_canon.py
"""
Seal a proposed canon into the Cooling Ledger (L1) as 999_SEAL (v36Ω).

This script is the 888 Judge's tool for turning a human-edited
PROPOSED_CANON file into a sealed constitutional canon entry.

Usage (from repo root):

    # Seal by file path:
    python -m scripts.seal_proposed_canon --file cooling_ledger/proposed/PROPOSED_CANON_...json

    # Or seal by proposed canon id:
    python -m scripts.seal_proposed_canon --id PROPOSED_CANON_ZKPC-20251207-abcd1234

    # Skip confirmation prompt:
    python -m scripts.seal_proposed_canon --file ... --yes

Behavior:

1. Loads the proposed canon JSON from `cooling_ledger/proposed/`.
2. Prompts (lightly) to confirm sealing (unless --yes is passed).
3. Constructs a new ledger entry:
    - type: "999_SEAL"
    - source: "seal_proposed_canon"
    - canon: proposed["canon"]
    - from_receipt_id: proposed["from_receipt_id"]
4. Appends it to `cooling_ledger/L1_cooling_ledger.jsonl` with:
    - previous_hash
    - hash (SHA-256)
5. Recomputes Merkle root over all ledger entries and writes to:
    - `cooling_ledger/L1_merkle_root.txt`
6. Moves the original proposed file to:
    - `cooling_ledger/proposed/archived/`

This script does NOT auto-edit or "fix" the canon text. It assumes
the 888 Judge has already reviewed and edited the proposed canon file.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from arifos_core.governance.ledger_hashing import (
    load_jsonl,
    dump_jsonl,
    compute_entry_hash,
    HASH_FIELD,
    PREVIOUS_HASH_FIELD,
    GENESIS_PREVIOUS_HASH,
)
from arifos_core.governance.merkle import build_merkle_tree


LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"
MERKLE_ROOT_PATH = Path("cooling_ledger") / "L1_merkle_root.txt"
PROPOSED_DIR = Path("cooling_ledger") / "proposed"
ARCHIVE_DIR = PROPOSED_DIR / "archived"


def _load_ledger() -> List[Dict[str, Any]]:
    if not LEDGER_PATH.exists():
        return []
    return load_jsonl(str(LEDGER_PATH))


def _find_proposed_file_by_id(pid: str) -> Optional[Path]:
    """
    Find a proposed canon file by its id (e.g. PROPOSED_CANON_xxx).

    We expect filenames like: PROPOSED_CANON_<receipt_id>.json
    """
    if not PROPOSED_DIR.exists():
        return None
    for p in PROPOSED_DIR.glob("*.json"):
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("id") == pid:
                return p
        except Exception:
            continue
    return None


def _load_proposed(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _ask_confirm(prompt: str) -> bool:
    ans = input(f"{prompt} [y/N]: ").strip().lower()
    return ans in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal a proposed canon into the Cooling Ledger as 999_SEAL."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file",
        type=str,
        help="Path to a PROPOSED_CANON_*.json file.",
    )
    group.add_argument(
        "--id",
        type=str,
        help="ID of the proposed canon (e.g. PROPOSED_CANON_...).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Seal without interactive confirmation.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all proposed canon files in the proposed directory.",
    )
    args = parser.parse_args()

    # If --list, show proposed files and exit
    if args.list:
        print("[seal_proposed_canon] Proposed canon files:")
        if not PROPOSED_DIR.exists():
            print("  (no proposed directory)")
            return 0
        for p in PROPOSED_DIR.glob("*.json"):
            try:
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                pid = data.get("id", p.stem)
                print(f"  {p.name} -> id={pid}")
            except Exception:
                print(f"  {p.name} -> (error reading)")
        return 0

    # Resolve proposed file path
    if args.file:
        proposed_path = Path(args.file)
        if not proposed_path.exists():
            print(f"[seal_proposed_canon] Proposed file not found: {proposed_path}")
            return 1
    else:
        pid = args.id
        proposed_path = _find_proposed_file_by_id(pid)
        if not proposed_path:
            print(f"[seal_proposed_canon] No proposed canon with id={pid} found in {PROPOSED_DIR}")
            return 1

    print(f"[seal_proposed_canon] Loading proposed canon from {proposed_path}...")
    proposed = _load_proposed(proposed_path)

    # Basic sanity checks
    if proposed.get("type") != "PROPOSED_CANON":
        print(
            f"[seal_proposed_canon] WARNING: proposed file type is {proposed.get('type')}, "
            "expected PROPOSED_CANON."
        )

    canon = proposed.get("canon")
    if not isinstance(canon, dict):
        print("[seal_proposed_canon] ERROR: proposed['canon'] missing or not a dict.")
        return 1

    from_receipt_id = proposed.get("from_receipt_id", "UNKNOWN")
    pid = proposed.get("id", proposed_path.stem)

    print("\n[seal_proposed_canon] === PROPOSED CANON SUMMARY ===")
    print(f"ID              : {pid}")
    print(f"From receipt_id : {from_receipt_id}")
    print(f"Principle       : {canon.get('principle')}")
    print(f"Law (first 200) : {str(canon.get('law', ''))[:200]!r}")
    print("==================================================")

    if not args.yes:
        if not _ask_confirm("Seal this proposed canon as 999_SEAL into L1_cooling_ledger.jsonl?"):
            print("[seal_proposed_canon] Aborted by user.")
            return 0

    # Load current ledger
    entries = _load_ledger()
    previous_hash = entries[-1].get(HASH_FIELD) if entries else GENESIS_PREVIOUS_HASH

    # Build new sealed entry
    sealed_entry: Dict[str, Any] = {
        "id": pid.replace("PROPOSED_", "CANON_"),
        "timestamp": proposed.get("timestamp"),
        "type": "999_SEAL",
        "source": "seal_proposed_canon",
        "from_receipt_id": from_receipt_id,
        PREVIOUS_HASH_FIELD: previous_hash,
        "canon": canon,
        # Optionally propagate tags from proposed canon
        "tags": canon.get("tags", []),
    }
    sealed_entry[HASH_FIELD] = compute_entry_hash(sealed_entry)
    entries.append(sealed_entry)

    # Write updated ledger
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    dump_jsonl(entries, str(LEDGER_PATH))

    # Recompute Merkle root
    leaf_hashes = [e[HASH_FIELD] for e in entries if HASH_FIELD in e]
    if leaf_hashes:
        tree = build_merkle_tree(leaf_hashes)
        root = tree.root or ""
    else:
        root = ""

    MERKLE_ROOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MERKLE_ROOT_PATH.write_text(root + "\n", encoding="utf-8")

    print("\n[seal_proposed_canon] === SEALED ENTRY ===")
    print(f"Sealed id      : {sealed_entry['id']}")
    print(f"Type           : {sealed_entry['type']}")
    print(f"hash           : {sealed_entry[HASH_FIELD]}")
    print(f"previous_hash  : {sealed_entry[PREVIOUS_HASH_FIELD]}")
    print(f"Merkle root    : {root}")
    print("==================================================")

    # Archive the proposed file
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    archived_path = ARCHIVE_DIR / proposed_path.name
    shutil.move(str(proposed_path), str(archived_path))
    print(f"[seal_proposed_canon] Proposed file archived to: {archived_path}")

    print("[seal_proposed_canon] DONE. Canon is now sealed into L1_cooling_ledger.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
