#!/usr/bin/env python3
"""
sovereign_signer.py — Ed25519 signing bridge for OpenClaw

Receives: actor_id, constitution_hash, nonce
Returns:  base64 Ed25519 signature over "{actor_id}:{constitution_hash}:{nonce}"

Usage:
  python3 sovereign_signer.py <actor_id> <constitution_hash> <nonce>

Output:
  BASE64_SIGNATURE
  or
  ERROR: <message>

The private key never leaves this process.
OpenClaw (root) can read /root/compose/sekrits/arifos_sovereign.key
"""

from __future__ import annotations

import base64
import sys


def load_private_key() -> "Ed25519PrivateKey":
    """Load Ed25519 private key from standard path."""
    from pathlib import Path

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    key_path = Path("/root/compose/sekrits/arifos_sovereign.key")
    if not key_path.exists():
        # Fallback for container path
        key_path = Path("/run/sekrits/arifos_sovereign.key")

    pem_bytes = key_path.read_bytes()
    private_key = load_pem_private_key(pem_bytes, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError(f"Key is not Ed25519, got {type(private_key).__name__}")
    return private_key


def sign_payload(actor_id: str, constitution_hash: str, nonce: str) -> str:
    """Sign the canonical payload string and return base64 signature."""
    payload = f"{actor_id}:{constitution_hash}:{nonce}"
    payload_bytes = payload.encode("utf-8")

    private_key = load_private_key()
    signature = private_key.sign(payload_bytes)
    # Use standard base64 (verifier uses b64decode which needs padding)
    return base64.b64encode(signature).decode()


def main() -> None:
    if len(sys.argv) != 4:
        print("ERROR: Expected 3 args: <actor_id> <constitution_hash> <nonce>", file=sys.stderr)
        sys.exit(1)

    actor_id, constitution_hash, nonce = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        sig = sign_payload(actor_id, constitution_hash, nonce)
        print(sig)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
