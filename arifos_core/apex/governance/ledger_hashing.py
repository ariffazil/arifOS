# arifos_core/ledger_hashing.py
"""
SHA-256 hashing + chain helpers for Cooling Ledger (v36Ω).

- Each entry is a JSON object.
- We compute a canonical JSON string (sorted keys, UTF-8).
- We hash that with SHA-256.
- We maintain a simple hash-chain via `previous_hash`.

This module is designed to be:
- RAG-friendly,
- zkPC-ready,
- Safe to use across platforms.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List


HASH_FIELD = "hash"
PREVIOUS_HASH_FIELD = "previous_hash"
GENESIS_PREVIOUS_HASH = "GENESIS"


def _canonical_json(obj: Any) -> str:
    """
    Produce a canonical JSON string for hashing:
    - sorted keys
    - ensure_ascii=False (keep UTF-8)
    - no trailing spaces
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_hex(data: str) -> str:
    """Return hex-encoded SHA-256 of the given string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_entry_hash(entry: Dict[str, Any]) -> str:
    """
    Compute the SHA-256 hash for a single ledger entry.

    NOTE:
    - HASH_FIELD and PREVIOUS_HASH_FIELD are excluded from the content being hashed.
    - This ensures stable hashing even if we re-run hash computation.
    """
    content = {
        k: v
        for k, v in entry.items()
        if k not in (HASH_FIELD, PREVIOUS_HASH_FIELD)
    }
    canonical = _canonical_json(content)
    return sha256_hex(canonical)


def chain_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Given a list of entries (in chronological order), compute:

    - previous_hash for each entry
    - hash for each entry

    Returns a NEW list of entries with hash fields populated.
    """
    chained: List[Dict[str, Any]] = []
    previous_hash: str = GENESIS_PREVIOUS_HASH

    for entry in entries:
        # Work on a shallow copy to avoid mutating original input.
        e = dict(entry)
        e[PREVIOUS_HASH_FIELD] = previous_hash
        e[HASH_FIELD] = compute_entry_hash(e)
        chained.append(e)
        previous_hash = e[HASH_FIELD]

    return chained


def verify_chain(entries: Iterable[Dict[str, Any]]) -> bool:
    """
    Verify that:
    - each entry's `previous_hash` matches the prior entry's `hash`,
    - each entry's `hash` matches recomputed SHA-256(content-without-hash-fields).

    Returns True if the chain is internally consistent, False otherwise.
    """
    previous_hash: str = GENESIS_PREVIOUS_HASH
    for idx, entry in enumerate(entries):
        expected_prev = previous_hash
        actual_prev = entry.get(PREVIOUS_HASH_FIELD)

        if actual_prev != expected_prev:
            print(
                f"[verify_chain] previous_hash mismatch at index {idx}: "
                f"expected={expected_prev}, got={actual_prev}"
            )
            return False

        expected_hash = compute_entry_hash(entry)
        actual_hash = entry.get(HASH_FIELD)

        if actual_hash != expected_hash:
            print(
                f"[verify_chain] hash mismatch at index {idx}: "
                f"expected={expected_hash}, got={actual_hash}"
            )
            return False

        previous_hash = actual_hash or ""

    return True


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    """Utility: load a JSONL file into a list of dicts."""
    entries: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def dump_jsonl(entries: Iterable[Dict[str, Any]], path: str) -> None:
    """Utility: write entries as JSONL."""
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(_canonical_json(entry))
            f.write("\n")
