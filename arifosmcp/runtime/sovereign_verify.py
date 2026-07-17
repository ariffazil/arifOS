"""
arifosmcp/runtime/sovereign_verify.py — Ed25519 Sovereign Identity Verification

L11 AUTH: Cryptographic proof of sovereign actor identity.
Delegates signature verification to crypto_auth.verify_init_identity,
which tries multiple payload formats with alias normalization.

Public key path: env ARIFOS_SOVEREIGN_PUBKEY_FILE → /run/sekrits/arifos_sovereign.pub
Payload formats (tried by verify_init_identity):
  1. "{actor_id}:{nonce}"                        — canonical
  2. "{actor_id}:{constitution_hash}:{nonce}"    — kernel compat
Signature: base64-encoded Ed25519 signature over UTF-8 payload bytes

Authority levels:
  SOVEREIGN — Ed25519 signature verified (via verify_init_identity)
  OBSERVER  — No signature provided (read-only access)
  VOID      — Signature provided but verification failed (reject session)
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import time
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

_PUBKEY_CANDIDATES = [
    Path(os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE", ""))
    if os.environ.get("ARIFOS_SOVEREIGN_PUBKEY_FILE")
    else None,
    Path("/run/sekrits/arifos_sovereign.pub"),
    Path("/run/secrets/arifos_sovereign.pub"),
    Path("/root/compose/sekrits/arifos_sovereign.pub"),
    # bridging_seal keypair (canonical did_arifos — must match /opt/arifos/secrets/)
    Path("/opt/arifos/secrets/did_arifos_public.key"),
    # Canonical AAA Arif identity public key (PEM Ed25519)
    Path("/root/AAA/IDENTITY/keys/arif_public.pem"),
    Path("/root/.ssh/operator_did_ed25519.pub"),
]

# Authority level constants
AUTHORITY_SOVEREIGN = "SOVEREIGN"
AUTHORITY_VERIFIED = "VERIFIED"
AUTHORITY_OBSERVER = "OBSERVER"
AUTHORITY_VOID = "VOID"
AUTHORITY_HMAC = "HMAC_VERIFIED"


# HMAC-rootkey verification (for Telegram-native identity)
def verify_hmac_signature(
    actor_id: str,
    challenge: str,
    sig: str,
) -> tuple[bool, str]:
    """
    L11 AUTH via HMAC-rootkey (Telegram-native path).

    Args:
        actor_id: Must be "ariffazil"
        challenge: "timestamp:op_id" format (same as nonce)
        sig: HMAC-SHA256(rootkey, challenge) hex digest

    Returns:
        (verified: bool, reason: str)
    """
    import os

    if actor_id != "ariffazil":
        return False, "hmac_actor_id_mismatch"

    # Canonical vault name is ARIFOS_ROOTKEY; ARIF_ROOTKEY is legacy alias only.
    rootkey = os.getenv("ARIFOS_ROOTKEY", "") or os.getenv("ARIF_ROOTKEY", "")
    if not rootkey:
        return False, "hmac_rootkey_not_configured"

    if not is_challenge_fresh(challenge):
        return False, "hmac_challenge_stale"

    import logging

    logger = logging.getLogger("arifosmcp.sovereign")
    expected = hmac.new(
        rootkey.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    logger.warning(
        "DEBUG-HMAC: actor=%s challenge=%s sig=%s expected=%s",
        actor_id,
        challenge[:30],
        sig[:16] if sig else "None",
        expected[:16],
    )
    if hmac.compare_digest(expected, sig):
        return True, "hmac_signature_verified"
    return False, "hmac_signature_invalid"


def is_challenge_fresh(challenge: str, window_sec: int = 300) -> bool:
    """
    Reject replayed challenges older than window_sec.
    Default 300s (5 min) for HMAC path.

    For timestamped challenges (format: `{timestamp}:{random}`), checks age.
    For plain random tokens (crypto_auth style), returns True — freshness
    is enforced by the crypto_auth challenge store (issue_actor_challenge).
    """
    try:
        ts = int(challenge.split(":")[0])
        return abs(time.time() - ts) <= window_sec
    except (ValueError, IndexError):
        # Plain random token — freshness managed by crypto_auth._issued_challenges
        return True


@lru_cache(maxsize=1)
def _load_public_key():
    """Load and cache the Ed25519 public key. Returns None if not available."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        pubkey_path = next((path for path in _PUBKEY_CANDIDATES if path and path.exists()), None)
        if pubkey_path is None:
            logger.warning(
                "Sovereign public key not found in any candidate path: %s",
                ", ".join(str(path) for path in _PUBKEY_CANDIDATES if path),
            )
            return None

        pem_bytes = pubkey_path.read_bytes()
        pubkey = load_pem_public_key(pem_bytes)
        if not isinstance(pubkey, Ed25519PublicKey):
            logger.error("Sovereign key is not Ed25519 (got %s)", type(pubkey).__name__)
            return None
        logger.info("Sovereign public key loaded from %s", pubkey_path)
        return pubkey
    except FileNotFoundError:
        logger.warning(
            "Sovereign public key not found at %s — identity verification disabled",
            pubkey_path,
        )
        return None
    except Exception as exc:
        logger.error("Failed to load sovereign public key: %s", exc)
        return None


def verify_sovereign_signature(
    actor_id: str,
    constitution_hash: str,
    nonce: str,
    actor_signature: str,
) -> tuple[bool, str]:
    """
    Verify Ed25519 signature — delegates to crypto_auth.verify_init_identity.

    verify_init_identity tries multiple payload formats:
      1. "{actor_id}:{nonce}"                        — canonical
      2. "{actor_id}:{constitution_hash}:{nonce}"    — kernel compat
    with actor-alias normalization and challenge replay protection.

    Returns:
        (verified: bool, reason: str)
    """
    from arifosmcp.runtime.crypto_auth import verify_init_identity

    return verify_init_identity(
        actor_id=actor_id,
        nonce=nonce,
        signature_b64=actor_signature,
        constitution_hash=constitution_hash or None,
    )


def resolve_authority_level(
    actor_id: str | None,
    identity_verified: bool,
    signature_provided: bool,
) -> str:
    """
    Resolve authority level based on verification result.

    SOVEREIGN — Ed25519 verified sovereign actor
    VERIFIED  — Ed25519 verified bounded non-sovereign actor
    OBSERVER  — No signature (anonymous read-only access)
    VOID      — Signature provided but failed (reject)
    """
    if identity_verified:
        from arifosmcp.runtime.governance_identity import is_protected_sovereign_id
        if is_protected_sovereign_id(actor_id):
            return AUTHORITY_SOVEREIGN
        return AUTHORITY_VERIFIED
    if signature_provided and not identity_verified:
        return AUTHORITY_VOID
    return AUTHORITY_OBSERVER


def purge_expired_nonces(nonce_store: dict[str, float], ttl_seconds: int = 300) -> int:
    """Remove expired nonces from the store. Returns count of purged entries."""
    cutoff = time.time() - ttl_seconds
    expired = [k for k, ts in list(nonce_store.items()) if ts < cutoff]
    for k in expired:
        del nonce_store[k]
    return len(expired)


def pubkey_status() -> dict:
    """Return public key availability status for health checks."""
    pubkey = _load_public_key()
    pubkey_path = next((path for path in _PUBKEY_CANDIDATES if path and path.exists()), None)
    return {
        "sovereign_pubkey_loaded": pubkey is not None,
        "sovereign_pubkey_path": str(pubkey_path) if pubkey_path else None,
        "sovereign_pubkey_exists": pubkey_path is not None,
        "ed25519_verification": "enabled" if pubkey is not None else "disabled",
    }
