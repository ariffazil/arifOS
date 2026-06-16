"""
arifosmcp/runtime/sovereign_signer.py

ED25519 SOVEREIGN IDENTITY BRIDGE

Sign messages with Ed25519 sovereign key for arifOS MCP L11 AUTH.

Usage:
    python3 sovereign_signer.py <actor_id> <constitution_hash> <nonce>

Returns base64 Ed25519 signature.

Key: /root/compose/sekrits/arifos_sovereign.key (root-only)
Payload format: "{actor_id}:{constitution_hash}:{nonce}"
    → constitution_hash MUST include "sha256:" prefix
    → e.g. "ariffazil:sha256:c65465c98bc2cfa0:test-nonce"
Signature: base64-encoded raw Ed25519 signature bytes (64 bytes)
"""

from __future__ import annotations

import base64
import sys
from pathlib import Path


def get_constitution_hash() -> str:
    """Get the canonical constitution_hash from FLOOR_SPEC (same as MCP verifier)."""
    import hashlib

    FLOOR_SPEC = (  # noqa: N806
        "F1: Amanah, F2: Truth, F3: Tri-Witness, F4: Clarity, "
        "F5: Peace, F6: Empathy, F7: Humility, F8: Genius, "
        "F9: Anti-Hantu, L10: Ontology, L11: Auth, L12: Injection, L13: Sovereign"
    )
    c_hash = hashlib.sha256(FLOOR_SPEC.encode()).hexdigest()[:16]
    return f"sha256:{c_hash}"  # Include sha256: prefix (MUST match verifier)


def load_private_key() -> bytes:
    """Load raw 32-byte Ed25519 key from PKCS#8, PEM, or raw format."""
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    key_paths = [
        Path("/root/compose/sekrits/arifos_sovereign.key"),
        Path("/run/sekrits/arifos_sovereign.key"),
        Path("/run/secrets/arifos_sovereign.key"),
    ]
    for key_path in key_paths:
        if key_path.exists() and key_path.stat().st_mode & 0o600:
            key_data = key_path.read_bytes()
            # 1. Try PEM
            if b"-----BEGIN" in key_data:
                try:
                    pkey = load_pem_private_key(key_data, password=None)
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

                    if isinstance(pkey, Ed25519PrivateKey):
                        return pkey.private_bytes_raw()
                except Exception:
                    pass
            # 2. Try PKCS#8: 7-byte header + 32-byte raw key
            if len(key_data) == 39 and key_data[0] == 0x30:
                return key_data[7:]  # Skip 7-byte header
            # 3. Try raw 32-byte key
            elif len(key_data) == 32:
                return key_data  # Raw 32-byte key
    raise FileNotFoundError(
        f"Sovereign key not found or format invalid. Tried: {[str(p) for p in key_paths]}"
    )


def sign(actor_id: str, constitution_hash: str, nonce: str) -> str:
    """
    Sign the canonical message with Ed25519 sovereign key.

    Args:
        actor_id: "ariffazil"
        constitution_hash: MUST include sha256: prefix
            e.g. "sha256:c65465c98bc2cfa0"
        nonce: Unique nonce (UUID or timestamp:op_id format)

    Returns:
        base64-encoded Ed25519 signature
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    raw_key = load_private_key()
    private_key = Ed25519PrivateKey.from_private_bytes(raw_key)

    # Message format MUST match verifier: actor_id:constitution_hash:nonce
    # constitution_hash MUST have sha256: prefix (verified against get_constitution_hash())
    message = f"{actor_id}:{constitution_hash}:{nonce}".encode()

    signature = private_key.sign(message)
    return base64.b64encode(signature).decode()


def main() -> str:
    """CLI entry point: returns base64 signature to stdout."""
    if len(sys.argv) != 4:
        # Auto-detect constitution_hash if not provided
        constitution_hash = get_constitution_hash()
        if len(sys.argv) == 3:
            actor_id, nonce = sys.argv[1], sys.argv[2]
        else:
            print(
                "Usage: sovereign_signer.py <actor_id> <nonce> [constitution_hash]", file=sys.stderr
            )
            print(f"Auto-detected constitution_hash: {constitution_hash}", file=sys.stderr)
            sys.exit(1)
    else:
        actor_id, constitution_hash, nonce = sys.argv[1], sys.argv[2], sys.argv[3]

    sig_b64 = sign(actor_id, constitution_hash, nonce)
    print(sig_b64)
    return sig_b64


if __name__ == "__main__":
    main()
