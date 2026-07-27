"""Sovereign Identity Registry — L11/L13 Identity Hardening.

Extracted from archive: _archived/root_runtime_pre_migration/governance_identities.py
DITEMPA BUKAN DIBERI — Forged, Not Given

SECURITY (2026-07-06): SEMANTIC_KEYS removed. Phrase-based auth eliminated.
IMPLEMENTED (2026-07-07): Ed25519 + HMAC verification via sovereign_verify.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# P0: Protected Sovereign IDs (L11 Identity Hardening)
PROTECTED_SOVEREIGN_IDS: set[str] = {
    "arif",
    "ariffazil",
    "sovereign",
    "admin",
    "root",
    "system",
    "arif-fazil",
    "arif_fazil",
    "muhammad_arif",
}

# Identity phrase patterns (English + Malay) — NLP parsing ONLY, NOT auth
IDENTITY_PHRASES: list[tuple[str, str]] = [
    (r"^(i am|im|i'm|saya|aku|hamba)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (
        r"^(hi|hello|hey|yo)\s+(i am|im|i'm|saya|aku)\s+(arif|ariffazil|arif-fazil)$",
        "arif",
    ),
    (r"^it's\s+(arif|ariffazil|arif-fazil)$", "arif"),
]


def canonicalize_identity_claim(text: str | None) -> str | None:
    """Parse raw input for identity claims. Returns canonical actor_id if matched."""
    if not text:
        return None
    clean_text = text.lower().strip().rstrip(".!?")
    for pattern, canonical_id in IDENTITY_PHRASES:
        if re.match(pattern, clean_text):
            return canonical_id
    return None


def is_protected_sovereign_id(actor_id: str | None) -> bool:
    """Check if actor_id is a protected sovereign identity."""
    if not actor_id or actor_id == "anonymous":
        return False
    return actor_id.lower().strip() in PROTECTED_SOVEREIGN_IDS


def validate_sovereign_proof(actor_id: str, proof: dict | str | Any | None) -> bool:
    """Validate cryptographic proof for protected sovereign ID.

    SECURITY (2026-07-06): Semantic key bypass removed. Only cryptographic
    signatures or explicit human approval through verified sessions are accepted.

    IMPLEMENTED (2026-07-07): Ed25519 + HMAC verification via sovereign_verify.
    """
    if not proof:
        return False

    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            return _verify_ed25519_proof(actor_id, proof)

        if "hmac_challenge" in proof and "hmac_sig" in proof:
            return _verify_hmac_proof(actor_id, proof)

    return False


def _verify_ed25519_proof(actor_id: str, proof: dict) -> bool:
    """Verify Ed25519 signature proof. Returns True only on cryptographic success.

    B1 (2026-07-27): Derives the sovereign public key from the signer's private
    key and passes it to the verifier. This ensures the verifier uses the exact
    key that the signer used, rather than independently resolving a public key
    from the actor registry that may not match.
    """
    try:
        from arifosmcp.runtime.sovereign_signer import (
            get_constitution_hash,
            get_sovereign_public_key_pem,
        )
        from arifosmcp.runtime.sovereign_verify import (
            is_challenge_fresh,
            verify_sovereign_signature,
        )
    except ImportError:
        logger.error(
            "sovereign_verify/sovereign_signer not importable — Ed25519 verification unavailable"
        )
        return False

    nonce = proof["nonce"]
    signature = proof["signature"]

    if not is_challenge_fresh(nonce, window_sec=60):
        logger.warning("Ed25519 proof rejected: stale nonce for actor=%s", actor_id)
        return False

    constitution_hash = get_constitution_hash()

    # B1: Derive the matching public key from the signer's private key.
    # Falls back to actor registry resolution if derivation fails (backward compat).
    signer_public_key_pem = get_sovereign_public_key_pem()

    verified, reason = verify_sovereign_signature(
        actor_id=actor_id,
        constitution_hash=constitution_hash,
        nonce=nonce,
        actor_signature=signature,
        public_key_pem=signer_public_key_pem,
    )

    if verified:
        logger.info("Ed25519 proof verified for actor=%s", actor_id)
    else:
        logger.warning("Ed25519 proof FAILED for actor=%s reason=%s", actor_id, reason)

    return verified


def _verify_hmac_proof(actor_id: str, proof: dict) -> bool:
    """Verify HMAC-rootkey proof (Telegram-native path)."""
    try:
        from arifosmcp.runtime.sovereign_verify import verify_hmac_signature
    except ImportError:
        logger.error("sovereign_verify not importable — HMAC verification unavailable")
        return False

    verified, reason = verify_hmac_signature(
        actor_id=actor_id,
        challenge=proof["hmac_challenge"],
        sig=proof["hmac_sig"],
    )

    if verified:
        logger.info("HMAC proof verified for actor=%s", actor_id)
    else:
        logger.warning("HMAC proof FAILED for actor=%s reason=%s", actor_id, reason)

    return verified
