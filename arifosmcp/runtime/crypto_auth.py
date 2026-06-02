"""
arifosmcp/runtime/crypto_auth.py
════════════════════════════════
Cryptographic identity verification for Sovereign actors.
"""
import base64
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)


_CHALLENGE_TTL_SECONDS = int(os.getenv("ARIFOS_AUTH_NONCE_TTL_SECONDS", "120"))
_PUBLIC_KEY_PATH = os.getenv(
    "ARIFOS_ARIF_PUBLIC_KEY_PATH",
    "/root/AAA/IDENTITY/keys/arif_public.pem",
)


@dataclass
class _Challenge:
    actor_id: str
    expires_at: float


_challenge_lock = threading.Lock()
_issued_challenges: dict[str, _Challenge] = {}
_used_challenges: dict[str, float] = {}


def _purge_challenges(now: float) -> None:
    expired = [
        nonce for nonce, challenge in _issued_challenges.items() if challenge.expires_at <= now
    ]
    for nonce in expired:
        del _issued_challenges[nonce]

    expired_used = [nonce for nonce, expires_at in _used_challenges.items() if expires_at <= now]
    for nonce in expired_used:
        del _used_challenges[nonce]


def issue_actor_challenge(actor_id: str, ttl_seconds: int | None = None) -> str:
    """Issue a short-lived, single-use nonce for actor signature verification."""
    if actor_id != "arif":
        raise ValueError("Only the Sovereign root actor can receive a crypto auth challenge")

    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")

    now = time.time()
    nonce = secrets.token_urlsafe(32)
    with _challenge_lock:
        _purge_challenges(now)
        _issued_challenges[nonce] = _Challenge(actor_id=actor_id, expires_at=now + ttl)
    return nonce


def _consume_actor_challenge(actor_id: str, nonce: str) -> tuple[bool, str]:
    now = time.time()
    with _challenge_lock:
        _purge_challenges(now)

        if nonce in _used_challenges:
            return False, "challenge_replayed"

        challenge = _issued_challenges.get(nonce)
        if challenge is None:
            return False, "challenge_not_issued"
        if challenge.actor_id != actor_id:
            return False, "challenge_actor_mismatch"
        if challenge.expires_at <= now:
            del _issued_challenges[nonce]
            return False, "challenge_expired"

        del _issued_challenges[nonce]
        _used_challenges[nonce] = challenge.expires_at
        return True, "challenge_consumed"


def verify_actor_signature(actor_id: str, nonce: str, signature_b64: str) -> bool:
    if actor_id != "arif":
        # Currently only the Sovereign root actor has a required public key anchor.
        return False

    if not nonce:
        logger.warning("Crypto Auth: Missing nonce.")
        return False

    pub_key_path = _PUBLIC_KEY_PATH
    if not os.path.exists(pub_key_path):
        logger.warning(f"Crypto Auth: Public key not found at {pub_key_path}")
        return False

    try:
        with open(pub_key_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())

        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            logger.error("Crypto Auth: Expected Ed25519 public key.")
            return False

        signature_bytes = base64.b64decode(signature_b64)
        message_bytes = f"{actor_id}:{nonce}".encode()

        public_key.verify(signature_bytes, message_bytes)
        challenge_ok, challenge_reason = _consume_actor_challenge(actor_id, nonce)
        if not challenge_ok:
            logger.warning("Crypto Auth: Nonce rejected — %s.", challenge_reason)
            return False
        return True
    except InvalidSignature:
        logger.warning("Crypto Auth: Invalid signature provided.")
        return False
    except Exception as e:
        logger.error(f"Crypto Auth: Verification error - {e}")
        return False
