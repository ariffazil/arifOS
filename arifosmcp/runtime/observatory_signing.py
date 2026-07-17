"""Ed25519 signing for the public Observatory snapshot.

The private key stays in the local Observatory runtime directory.  This
module only loads the established key; it never creates or rotates identity
material as a side effect of a read-only snapshot emit.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

KEY_DIR = Path("/root/.arifos/observatory/keys")
PRIVATE_KEY_PATH = KEY_DIR / "observatory_signing_key.pem"
PUBLIC_KEY_PATH = KEY_DIR / "observatory_signing_key.pub.pem"


def _canonical_json(payload: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in payload.items() if key != "signature"}
    return json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _load_or_generate_key() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Load the established key pair; generation is deliberately forbidden."""
    if not PRIVATE_KEY_PATH.is_file():
        raise FileNotFoundError(f"Observatory signing key missing: {PRIVATE_KEY_PATH}")
    key = serialization.load_pem_private_key(PRIVATE_KEY_PATH.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("Observatory signing key is not Ed25519")
    public = key.public_key()
    if PUBLIC_KEY_PATH.is_file():
        stored = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
        if not isinstance(stored, Ed25519PublicKey):
            raise TypeError("Observatory public key is not Ed25519")
        raw_public = public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        raw_stored = stored.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        if raw_public != raw_stored:
            raise ValueError("Observatory public/private key mismatch")
    return key, public


def get_public_key_fingerprint() -> str:
    _, public = _load_or_generate_key()
    raw = public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return f"ed25519:sha256:{hashlib.sha256(raw).hexdigest()[:16]}"


def sign_snapshot_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key, _ = _load_or_generate_key()
    canonical = _canonical_json(payload)
    signature = key.sign(canonical)
    observed_at = str(payload.get("observed_at") or "")
    fingerprint = get_public_key_fingerprint()
    return {
        "value": base64.b64encode(signature).decode("ascii"),
        "state": "signed",
        "source": f"ed25519 over canonicaljson(payload_without_signature) — key {fingerprint}",
        "observed_at": observed_at,
        "signed_at": observed_at,
        "age_seconds": 0,
        "confidence": 1.0,
        "observation_method": "ed25519_signing",
        "independent_or_self_reported": "independent",
        "key_id": fingerprint,
        "algorithm": "ed25519",
        "key_algorithm": "ed25519",
        "key_namespace": "arifos-observatory",
        "payload_hash": hashlib.sha256(canonical).hexdigest(),
        "payload_hash_sha256": hashlib.sha256(canonical).hexdigest(),
        "canonicalization": "sort_keys+separators+utf8+no_nan",
        "verification_url": "https://arifos.arif-fazil.com/.well-known/did-arifos-observatory.json",
    }
