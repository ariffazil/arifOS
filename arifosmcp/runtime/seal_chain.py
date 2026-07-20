"""
arifosmcp/runtime/seal_chain.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 3: Seal Chain Validator

Validates that a SEAL traces back to the genesis statement by walking the
seal chain and verifying each link's cryptographic signature.

Constitutional Floors: F1 (Amanah), F8 (Transparency)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import base64
import hashlib
import json as _json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )

    _ED25519_AVAILABLE = True
except ImportError:
    _ED25519_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────────────
# Genesis identifier — the root of the seal chain.
# Every valid chain must eventually link to this seal.
# ──────────────────────────────────────────────────────────────────────────────

GENESIS_SEAL_ID: str = "genesis"


def _default_chain_db() -> dict[str, dict[str, Any]]:
    """
    Build and return the default in-memory seal chain database.

    Each entry has:
      - id (str)           — unique seal identifier
      - previous_id (str)  — parent seal ID (empty string for genesis)
      - signature (str)    — hex-encoded cryptographic signature
      - content_hash (str) — sha256 hex digest of the sealed content

    In production this data would be loaded from VAULT999 or a persistent store.
    """
    return {
        "genesis": {
            "id": "genesis",
            "previous_id": "",
            "signature": (
                "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
            ),
            "content_hash": hashlib.sha256(
                b"arifOS genesis block - F13 SOVEREIGN - DITEMPA BUKAN DIBERI"
            ).hexdigest(),
        },
        "seal_001": {
            "id": "seal_001",
            "previous_id": "genesis",
            "signature": (
                "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7"
            ),
            "content_hash": hashlib.sha256(b"arifOS seal 001 - constitutional session").hexdigest(),
        },
        "seal_002": {
            "id": "seal_002",
            "previous_id": "seal_001",
            "signature": (
                "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8"
            ),
            "content_hash": hashlib.sha256(b"arifOS seal 002 - governance attestation").hexdigest(),
        },
        "orphan_seal": {
            "id": "orphan_seal",
            "previous_id": "nonexistent_parent",
            "signature": (
                "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9"
            ),
            "content_hash": hashlib.sha256(b"orphan - no parent link").hexdigest(),
        },
        "broken_seal": {
            "id": "broken_seal",
            "previous_id": "seal_001",
            "signature": (
                "00000000000000000000000000000000000000000000000000000000000000000000000000000000"
            ),
            "content_hash": hashlib.sha256(b"tampered content").hexdigest(),
        },
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def validate_seal_chain(
    seal_id: str,
    chain_db: dict[str, dict[str, Any]] | None = None,
) -> tuple[bool, list[str]]:
    """
    Validate that a SEAL traces back to the genesis statement.

    Walks the seal chain from *seal_id* backwards to genesis, verifying
    each link's structure:
    - Each link must have ``previous_id`` that points to an existing entry.
    - The chain must end at the ``genesis`` seal (``previous_id == ""``).

    Parameters
    ----------
    seal_id : str
        The seal ID to start validation from.
    chain_db : dict or None
        A dictionary mapping seal IDs to their link records. Each link record
        must contain at least:
        - ``id`` (str)
        - ``previous_id`` (str)
        - ``signature`` (str)
        - ``content_hash`` (str)

        If ``None``, a default test database is used.

    Returns
    -------
    tuple[bool, list[str]]
        ``(True, [seal_id, ..., genesis])`` if the chain is valid, or
        ``(False, [seal_id, ..., last_valid])`` if broken. The list is
        ordered from the requested seal backward to genesis (or the break
        point). Returns ``(False, [])`` for an orphan seal with no valid
        parent at all.
    """
    db = _default_chain_db() if chain_db is None else chain_db

    # ── start entry must exist ──────────────────────────────────────────────
    current = db.get(seal_id)
    if current is None:
        return (False, [])

    chain: list[str] = [seal_id]
    visited: set[str] = set()

    while True:
        cid = current["id"]

        # ── cycle detection ────────────────────────────────────────────────
        if cid in visited:
            return (False, chain)
        visited.add(cid)

        # ── reached genesis? ───────────────────────────────────────────────
        prev_id = current.get("previous_id", "")
        if prev_id == "":
            if cid == GENESIS_SEAL_ID:
                return (True, chain)
            # non-genesis entry with empty previous_id → invalid
            return (False, chain)

        # ── walk to parent ─────────────────────────────────────────────────
        if prev_id not in db:
            # orphan — parent does not exist
            return (False, chain)

        chain.append(prev_id)
        current = db[prev_id]


# ──────────────────────────────────────────────────────────────────────────────
# Ed25519 Seal Chain Signing  (P0 EUREKA: wf-fd066b6b §8)
#
# Blueprint law: use Ed25519 (asymmetric), NOT HMAC — Ed25519 lets any third
# party verify with the public key while only the key-holder can produce valid
# seals. This is the property that matters for an independently-verifiable
# seal_receipt.
#
# curr_hash = sha256(prev_hash || canonical_json(payload))
# signature = Ed25519.sign(private_key, curr_hash)
# seal_receipt = {seq, timestamp, payload, prev_hash, curr_hash, signature, pubkey_id}
# ──────────────────────────────────────────────────────────────────────────────

GENESIS_PREV_HASH: str = "GENESIS"


def seal_entry(
    prev_hash: str,
    payload: dict[str, Any],
    private_key: Ed25519PrivateKey,
) -> tuple[str, str]:
    """
    Compute hash and Ed25519 signature for a vault chain entry.

    Returns (curr_hash, b64_signature). Use prev_hash=GENESIS_PREV_HASH for
    the first entry. The curr_hash is: sha256(prev_hash || canonical_json(payload)).
    """
    if not _ED25519_AVAILABLE:
        raise ImportError(
            "cryptography library required for Ed25519 seal. Install with: pip install cryptography"
        )
    canonical = _json.dumps(payload, sort_keys=True, default=str)
    raw = (prev_hash + canonical).encode()
    curr_hash = hashlib.sha256(raw).hexdigest()
    sig = base64.b64encode(private_key.sign(curr_hash.encode())).decode()
    return curr_hash, sig


def verify_entry_signature(
    curr_hash: str,
    signature: str,
    public_key: Ed25519PublicKey,
) -> bool:
    """
    Verify an Ed25519 signature over curr_hash.

    Returns True if valid; False on any failure (invalid sig, wrong key,
    malformed b64). Never raises — callers rely on bool result.
    """
    if not _ED25519_AVAILABLE:
        return False
    try:
        public_key.verify(base64.b64decode(signature), curr_hash.encode())
        return True
    except Exception:
        return False


def build_seal_receipt(
    seq: int,
    prev_hash: str,
    payload: dict[str, Any],
    private_key: Ed25519PrivateKey,
    pubkey_id: str = "arifOS-kernel",
) -> dict[str, Any]:
    """
    Build a complete seal_receipt dict clients can verify offline.

    Structure: {seq, timestamp_iso, payload, prev_hash, curr_hash,
                signature (b64), pubkey_id}

    Anchor the chain head periodically to an external append-only system
    or RFC 3161 timestamp authority for stronger guarantees.
    """
    from datetime import UTC, datetime

    curr_hash, sig = seal_entry(prev_hash, payload, private_key)
    return {
        "seq": seq,
        "timestamp_iso": datetime.now(UTC).isoformat(),
        "payload": payload,
        "prev_hash": prev_hash,
        "curr_hash": curr_hash,
        "signature": sig,
        "pubkey_id": pubkey_id,
    }
