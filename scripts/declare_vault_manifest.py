#!/usr/bin/env python3
"""declare_vault_manifest.py — VAULT999 stable identity declaration (Stage-0.2).

Creates/refreshes vault_manifest.json + identity_anchor.json in the canonical
vault dir (DEFAULT_VAULT_DIR per arifosmcp/runtime/canonical_vault_chain.py:
/root/.local/share/arifos/vault999). Completes the Stage-0.2 organ-attestation
design documented in organ_attestation.py: the manifest is the vault's stable
self-declared identity (first anchor candidate); identity_anchor.json pins it
explicitly (second candidate); the seal chain remains audit material that
mutates on every seal and is NOT identity.

Idempotent: re-running refreshes the declaration (chain stats recorded at
declaration time). Do NOT wire this into seal events — the whole point is a
stable anchor.

Usage: python3 scripts/declare_vault_manifest.py [--vault-dir PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_VAULT_DIR = Path("/root/.local/share/arifos/vault999")
GENESIS_PREV_HASH = "genesis"


def _sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vault-dir", type=Path, default=DEFAULT_VAULT_DIR)
    args = ap.parse_args()

    vault = args.vault_dir
    chain_path = vault / "seal_chain.jsonl"
    if not chain_path.exists():
        print(f"ERROR: canonical chain not found: {chain_path}")
        return 1

    now = datetime.now(timezone.utc).isoformat()
    chain_bytes = chain_path.read_bytes()
    lines = [l for l in chain_bytes.decode("utf-8", errors="replace").splitlines() if l.strip()]
    head = {}
    try:
        head = json.loads(lines[-1]) if lines else {}
    except json.JSONDecodeError:
        head = {}

    manifest = {
        "manifest_type": "vault_manifest",
        "manifest_version": 1,
        "organ": "VAULT999",
        "role": "immutable_ledger",
        "domain_law": "IMMUTABLE_LEDGER",
        "canonical_dir": str(vault),
        "declared_by": "arifOS canonical_vault_chain.py DEFAULT_VAULT_DIR",
        "declared_at": now,
        "chain": {
            "file": "seal_chain.jsonl",
            "genesis_prev_hash": GENESIS_PREV_HASH,
            "entries_at_declaration": len(lines),
            "head_sequence_at_declaration": head.get("sequence"),
            "head_prev_hash_at_declaration": head.get("prev_hash"),
            "file_sha256_at_declaration": _sha256_bytes(chain_bytes),
            "note": (
                "live chain head mutates on every seal — audit material, "
                "not identity; refresh this declaration deliberately, "
                "never on seal events"
            ),
        },
        "laws": ["append-only", "no-unseal", "accepted entries are permanent"],
        "legacy_twin": {
            "path": "/root/arifOS/VAULT999/seal_chain.jsonl",
            "status": "closed-2026-09-25",
            "closure_record": "CHAIN_REDIRECT tombstone (final line)",
            "follows": "canonical chain declared by this manifest",
        },
        "identity_note": (
            "This file is the vault's stable self-declared identity anchor "
            "(organ_attestation Stage-0.2, completed 2026-09-25). "
        ),
    }

    manifest_path = vault / "vault_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    anchor = {
        "anchor_kind": "identity_anchor",
        "organ": "VAULT999",
        "pinned_at": now,
        "pins": {
            "vault_manifest.json": _sha256_file(manifest_path),
        },
        "chain_head_at_pin": {
            "entries": len(lines),
            "head_sequence": head.get("sequence"),
            "file_sha256": _sha256_bytes(chain_bytes),
        },
        "note": (
            "explicit pin of the stable manifest (organ_attestation second "
            "anchor candidate); consumed only if vault_manifest.json is absent"
        ),
    }
    anchor_path = vault / "identity_anchor.json"
    anchor_path.write_text(json.dumps(anchor, indent=2) + "\n", encoding="utf-8")

    # match vault dir ownership (arifos service account writes here)
    for p in (manifest_path, anchor_path):
        try:
            shutil.chown(p, user="arifos", group="arifos")
        except (LookupError, PermissionError, OSError) as e:
            print(f"WARN: chown {p} failed: {e}")

    print(f"[manifest] {manifest_path}")
    print(f"[manifest]   entries={len(lines)} head_seq={head.get('sequence')} "
          f"chain={manifest['chain']['file_sha256_at_declaration'][:19]}…")
    print(f"[anchor]   {anchor_path}")
    print(f"[anchor]   pins manifest {anchor['pins']['vault_manifest.json'][:19]}…")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
