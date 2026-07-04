"""
arifosmcp/runtime/did_resolver.py — Decentralized Identifier (DID) resolver.
Resolves did:key and did:arifos identifiers to standard W3C DID Documents.
"""

from __future__ import annotations

import os
from typing import Any, Optional

logger = os.getenv("ARIFOS_LOG_LEVEL", "INFO")

# Base58BTC Alphabet
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def base58_decode(s: str) -> bytes:
    """Decode a Base58 encoded string to bytes."""
    num = 0
    for char in s:
        if char not in BASE58_ALPHABET:
            raise ValueError(f"Invalid Base58 character: {char}")
        num = num * 58 + BASE58_ALPHABET.index(char)
    combined = num.to_bytes((num.bit_length() + 7) // 8, byteorder="big")
    # Add leading zeros
    num_zeros = len(s) - len(s.lstrip(BASE58_ALPHABET[0]))
    return b"\x00" * num_zeros + combined


def resolve_did(did: str) -> Optional[dict[str, Any]]:
    """
    Resolve a DID identifier to a standard W3C DID Document.
    Supports did:key (Ed25519) and did:arifos custom methods.
    """
    if not did or not isinstance(did, str):
        return None

    if did.startswith("did:key:"):
        return _resolve_did_key(did)
    elif did.startswith("did:arifos:"):
        return _resolve_did_arifos(did)

    return None


def _resolve_did_key(did: str) -> Optional[dict[str, Any]]:
    """Resolve did:key to a DID Document."""
    # Format: did:key:z<base58btc-multicodec>
    method_specific = did[8:]
    if not method_specific.startswith("z"):
        return None  # Only base58btc (z) is supported

    try:
        raw_bytes = base58_decode(method_specific[1:])
    except Exception:
        return None

    # Check multicodec prefix. Ed25519 is represented by z6M in base58btc
    if method_specific.startswith("z6M"):
        # Ed25519 key type
        return {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1",
            ],
            "id": did,
            "verificationMethod": [
                {
                    "id": f"{did}#key-1",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                    "publicKeyMultibase": method_specific,
                }
            ],
            "authentication": [f"{did}#key-1"],
            "assertionMethod": [f"{did}#key-1"],
        }

    # If it is another algorithm, we can return a basic representation
    return {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "JsonWebKey2020",
                "controller": did,
                "publicKeyMultibase": method_specific,
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
    }


def _resolve_did_arifos(did: str) -> Optional[dict[str, Any]]:
    """Resolve did:arifos:<actor_id> using local keys/registry."""
    actor_id = did[11:]
    if not actor_id:
        return None

    # Normalize actor name
    if actor_id in ("arif", "000-SALAM", "sovereign"):
        key_path = "/root/AAA/IDENTITY/keys/arif_public.pem"
    else:
        key_path = f"/root/AAA/IDENTITY/keys/{actor_id}_public.pem"

    if os.path.exists(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                pem_data = f.read()

            return {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/suites/jws-2020/v1",
                ],
                "id": did,
                "verificationMethod": [
                    {
                        "id": f"{did}#key-1",
                        "type": "JsonWebKey2020",
                        "controller": did,
                        "publicKeyPem": pem_data,
                    }
                ],
                "authentication": [f"{did}#key-1"],
                "assertionMethod": [f"{did}#key-1"],
            }
        except Exception:
            return None

    # Default fallback for registered actors without dedicated files
    return {
        "@context": ["https://www.w3.org/ns/did/v1"],
        "id": did,
        "verificationMethod": [
            {
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": "z6MkpTHR8VNsBxRzAgPbdJu2efx4L6cxDuh5gG6H6T4L",
            }
        ],
        "authentication": [f"{did}#key-1"],
        "assertionMethod": [f"{did}#key-1"],
    }
