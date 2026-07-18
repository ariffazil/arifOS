#!/usr/bin/env python3
"""
sign_seal_json.py — Sign the public seal.json with the Observatory ed25519 key.

Forged 2026-07-18 by kimi-code (FI-008) per sovereign (888) directive.

Per the sovereign ruling:
  "Sign seal.json with snapshot ed25519 key."
  "A signature nobody can fetch proves nothing."

This script:
  1. Reads the unsigned seal.json (issued_by / proof_url are non-cryptographic)
  2. Removes the placeholder `cryptographic_proof` (a self-referential DID string)
  3. Signs the payload using arifOS/runtime/seal_chain_signing.py
  4. Writes the signed payload to a canonical local path
  5. Verifies the signature before declaring success (fail-closed)

The signed seal.json replaces the placeholder cryptographic_proof with a
real signature envelope {alg, value, key_id}, verifiable against the
public key at:
  https://arifos.arif-fazil.com/.well-known/did-arifos-observatory.json

Usage:
  python3 scripts/sign_seal_json.py [--input PATH] [--output PATH]

Defaults:
  --input  /root/ARIF-SITES/sites/arif-fazil.com/public/999/seal.json
  --output <input>.signed  (overwrites with --force)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure the arifOS runtime is importable
# arifOS layout is flat: arifosmcp/ is a sibling of scripts/ — both at repo root.
_ARIFOS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ARIFOS_ROOT))

from arifosmcp.runtime.seal_chain_signing import (  # noqa: E402
    sign_seal_entry,
    verify_seal_entry,
)


def canonical_unsigned(payload: dict) -> dict:
    """Remove fields that should NOT be part of the signature envelope.

    `signature` is what we're adding.
    `cryptographic_proof` was a self-referential DID string; replace it.
    """
    cleaned = {k: v for k, v in payload.items() if k not in ("signature", "cryptographic_proof")}
    return cleaned


def sign_seal(input_path: Path, output_path: Path, force: bool = False) -> int:
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 2

    if output_path.exists() and not force:
        print(
            f"ERROR: output already exists: {output_path} (use --force to overwrite)",
            file=sys.stderr,
        )
        return 3

    raw = json.loads(input_path.read_text(encoding="utf-8"))
    unsigned = canonical_unsigned(raw)

    sig_envelope = sign_seal_entry(unsigned)

    if not sig_envelope.get("value"):
        print(
            f"ERROR: signing failed — {sig_envelope.get('error', 'unknown')}",
            file=sys.stderr,
        )
        return 4

    signed = dict(unsigned)
    signed["signature"] = {
        "alg": sig_envelope["alg"],
        "value": sig_envelope["value"],
        "key_id": sig_envelope["key_id"],
        "canonicalization": "sort_keys+separators+utf8+no_nan",
        "signed_payload_hash_alg": "sha256",
    }
    # Note: the original `cryptographic_proof` was a self-referential DID
    # string (not a real signature). It is intentionally REMOVED — the new
    # `signature` envelope IS the cryptographic proof. Verifier tools that
    # look for `cryptographic_proof` should be updated to look for `signature`.

    # Verify before declaring success (fail-closed)
    if not verify_seal_entry(signed):
        print("ERROR: signature verification failed BEFORE writing — aborting", file=sys.stderr)
        return 5

    output_path.write_text(
        json.dumps(signed, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"SIGNED: {output_path}")
    print(f"  key_id: {sig_envelope['key_id']}")
    print(f"  alg:    {sig_envelope['alg']}")
    print(f"  size:   {output_path.stat().st_size} bytes")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sign seal.json with ed25519.")
    ap.add_argument(
        "--input",
        type=Path,
        default=Path("/root/ARIF-SITES/sites/arif-fazil.com/public/999/seal.json"),
        help="Path to unsigned seal.json",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write signed seal.json (default: <input>.signed)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite output if it exists",
    )
    args = ap.parse_args()
    output = args.output or args.input.with_suffix(args.input.suffix + ".signed")
    return sign_seal(args.input, output, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
