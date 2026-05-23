#!/usr/bin/env python3
"""
scripts/sign_session.py — Ed25519 Sovereign Session Signing Utility

Usage:
    python3 scripts/sign_session.py \
        --actor-id arif \
        --constitution-hash sha256:c65465c98bc2cfa0 \
        --nonce <nonce-from-server>

    Or generate a nonce automatically:
    python3 scripts/sign_session.py \
        --actor-id arif \
        --constitution-hash sha256:c65465c98bc2cfa0 \
        --auto-nonce

Outputs the base64 actor_signature to pass to arif_session_init.
Private key path: env ARIFOS_SOVEREIGN_PRIVKEY_FILE → /root/compose/sekrits/arifos_sovereign.key
"""

from __future__ import annotations

import argparse
import base64
import os
import secrets
import sys
from pathlib import Path

_KEY_PATH = Path(
    os.environ.get("ARIFOS_SOVEREIGN_PRIVKEY_FILE", "/root/compose/sekrits/arifos_sovereign.key")
)


def load_private_key():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        pem = _KEY_PATH.read_bytes()
        key = load_pem_private_key(pem, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            print(f"ERROR: Key is not Ed25519 (got {type(key).__name__})", file=sys.stderr)
            sys.exit(1)
        return key
    except FileNotFoundError:
        print(f"ERROR: Private key not found at {_KEY_PATH}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Failed to load private key: {exc}", file=sys.stderr)
        sys.exit(1)


def sign_session(actor_id: str, constitution_hash: str, nonce: str) -> str:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    privkey = load_private_key()
    if not isinstance(privkey, Ed25519PrivateKey):
        print("ERROR: loaded key is not Ed25519", file=sys.stderr)
        sys.exit(1)
    payload = f"{actor_id}:{constitution_hash}:{nonce}".encode("utf-8")
    sig_bytes = privkey.sign(payload)
    return base64.b64encode(sig_bytes).decode("ascii")


def main():
    parser = argparse.ArgumentParser(
        description="Sign an arifOS session payload with sovereign Ed25519 key"
    )
    parser.add_argument("--actor-id", default="arif", help="Actor ID (default: arif)")
    parser.add_argument(
        "--constitution-hash", default="sha256:c65465c98bc2cfa0", help="Constitution hash"
    )
    parser.add_argument("--nonce", help="Nonce string (from server or --auto-nonce)")
    parser.add_argument("--auto-nonce", action="store_true", help="Generate a random nonce")
    parser.add_argument("--quiet", action="store_true", help="Print only the signature")
    args = parser.parse_args()

    if args.auto_nonce:
        nonce = secrets.token_hex(16)
    elif args.nonce:
        nonce = args.nonce
    else:
        print("ERROR: Provide --nonce <value> or --auto-nonce", file=sys.stderr)
        sys.exit(1)

    sig = sign_session(args.actor_id, args.constitution_hash, nonce)

    if args.quiet:
        print(sig)
    else:
        print(f"actor_id:          {args.actor_id}")
        print(f"constitution_hash: {args.constitution_hash}")
        print(f"nonce:             {nonce}")
        print(f"actor_signature:   {sig}")
        print()
        print("Pass these fields to arif_session_init:")
        print(f"  actor_id={args.actor_id!r}")
        print(f"  nonce={nonce!r}")
        print(f"  actor_signature={sig!r}")


if __name__ == "__main__":
    main()
