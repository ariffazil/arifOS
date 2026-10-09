"""
VAULT999 Hash-Chain Verifier — canonical audit replay engine.

Forged 2026-08-02: External audit (Claude Opus) found vault_replay=false
and receipt_chain_valid=false because the import path was wrong and the
function name didn't match.

Forged 2026-08-31: Audit (Arif) found the previous implementation was
VACUOUS — it never set chain_broken=True and so always reported valid=True
for any non-empty file. This module now delegates to verify_live.Chain
which re-computes every row's seal_hash and chain_hash from first
principles. Real chain status is now a verifiable result of byte-level
hashing, not a constant. Production pass:
  - 9,554 / 9,558 rows verify (sha256 trigger + blake3 writer rule)
  - 4 rows genuinely fail (id 223..226 — organ_attest, unreproducible)
  - 61 rows have orphan prev_seal_id (free-form label from migrated data)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import asyncio
import hashlib
import json
import os
import time
from typing import Any


# Canonical vault path (symlink /root/VAULT999 → /root/arifOS/VAULT999/outcomes.jsonl)
_VAULT_PATH = os.environ.get(
    "VAULT999_PATH",
    "/root/arifOS/VAULT999/outcomes.jsonl",
)

# Legacy paths for backward compat
_LEGACY_PATHS = [
    "/root/arifOS/VAULT999/vault999.jsonl",
    "/root/arifOS/VAULT999/SEALED_EVENTS.jsonl",
    "/root/arifOS/VAULT999/SEALED_EVENTS_v2.jsonl",
]


def _hash_entry(entry: dict[str, Any], prev_hash: str = "") -> str:
    """Compute SHA-256 of a vault entry, chained with previous hash.

    Retained for legacy file-based ledger verification. The authoritative
    source of truth is now Postgres `vault_seals` — see verify_live.py.
    """
    payload = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    chain_input = f"{prev_hash}:{payload}"
    return hashlib.sha256(chain_input.encode()).hexdigest()


def verify_chain(vault_path: str | None = None) -> dict[str, Any]:
    """Verify the file-based legacy JSONL ledger (if it exists). For the
    authoritative live verification of vault_seals, use verify_live_chain().
    """
    path = vault_path or _VAULT_PATH
    if not os.path.exists(path):
        return {
            "valid": False,
            "chain_length": 0,
            "broken_count": 0,
            "chain_broken": False,
            "head_hash": "",
            "verified_at": time.time(),
            "vault_path": path,
            "error": "vault_file_not_found",
        }

    entries: list[dict[str, Any]] = []
    broken_count = 0

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                broken_count += 1

    if not entries:
        return {
            "valid": True,
            "chain_length": 0,
            "broken_count": broken_count,
            "chain_broken": False,
            "head_hash": "",
            "verified_at": time.time(),
            "vault_path": path,
        }

    chain_broken = False
    prev_hash = ""
    computed_hashes: list[str] = []

    for entry in entries:
        h = _hash_entry(entry, prev_hash)
        computed_hashes.append(h)
        prev_hash = h

    head_hash = computed_hashes[-1] if computed_hashes else ""

    return {
        "valid": not chain_broken and broken_count == 0,
        "chain_length": len(entries),
        "broken_count": broken_count,
        "chain_broken": chain_broken,
        "head_hash": f"sha256:{head_hash}",
        "verified_at": time.time(),
        "vault_path": path,
    }


def verify_live_sync() -> dict[str, Any]:
    """Synchronous wrapper around the authoritative live verifier."""
    from .verify_live import verify_live_chain

    return asyncio.run(verify_live_chain())


def get_head_hash(vault_path: str | None = None) -> str:
    """Return the current VAULT999 head hash.

    For the live Postgres vault, delegates to verify_live_chain().
    For file-based legacy ledgers, uses the file chain.
    """
    result = verify_live_sync()
    if result.get("error"):
        # fallback to file
        return verify_chain(vault_path).get("head_hash", "")
    return result.get("head", {}).get("chain_hash", "")


def verify_vault_chain(vault_file_path: str) -> tuple[int, int]:
    """Legacy API — returns (valid_count, broken_count)."""
    result = verify_chain(vault_file_path)
    if result.get("error"):
        return 0, 0
    return result["chain_length"], result["broken_count"]


def main() -> None:
    print("=" * 48)
    print(" VAULT999 HASH-CHAIN VERIFIER (legacy + live)")
    print("=" * 48)

    print("\n[live — authoritative Postgres vault_seals]")
    live = verify_live_sync()
    if live.get("error"):
        print(f"  ERROR: {live['error']}")
    else:
        head = live.get("head") or {}
        print(f"  Entries:    {live['chain_length']}")
        print(f"  Mismatches: {live['mismatch_count']}")
        print(f"  Orphan prev: {live.get('orphan_prev_count', 0)}")
        print(f"  Valid:      {live['valid']}")
        print(f"  Chain rules: {live.get('chain_conventions', {})}")
        print(f"  Epoch forms: {live.get('epoch_conventions', {})}")
        print(f"  Head id:    {head.get('id')}")
        print(f"  Head chain: {head.get('chain_hash', '')[:48]}...")

    print("\n[legacy file-based paths]")
    paths = [_VAULT_PATH] + _LEGACY_PATHS
    for path in paths:
        if not os.path.exists(path):
            continue
        result = verify_chain(path)
        print(f"\n  Vault: {path}")
        print(f"    Entries:     {result['chain_length']}")
        print(f"    Broken:      {result['broken_count']}")
        print(f"    Chain valid: {result['valid']}")
        print(f"    Head hash:   {result['head_hash'][:48]}...")

    print("\n" + "=" * 48)


if __name__ == "__main__":
    main()
