"""
arifosmcp/runtime/crypto_auth.py
════════════════════════════════
Cryptographic identity verification for Sovereign + registered agents.

Public key resolution order (first hit wins):
  1. Explicit env ARIFOS_ARIF_PUBLIC_KEY_PATH (arif only)
  2. /root/AAA/IDENTITY/keys/{actor_id}_public.pem
  3. /root/A-FORGE/IDENTITY/keys/{actor_id}/*public*.pem
  4. agent_identities.json identity_proof.public_key_pem
  5. DID registry public_key_hex (did:arif:{actor_id})

Challenge nonces are single-use, TTL default 120s.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

logger = logging.getLogger(__name__)

_CHALLENGE_TTL_SECONDS = int(os.getenv("ARIFOS_AUTH_NONCE_TTL_SECONDS", "120"))
_PUBLIC_KEY_PATH = os.getenv(
    "ARIFOS_ARIF_PUBLIC_KEY_PATH",
    "/root/AAA/IDENTITY/keys/arif_public.pem",
)
_AAA_KEYS = Path("/root/AAA/IDENTITY/keys")
_AFORGE_KEYS = Path("/root/A-FORGE/IDENTITY/keys")
_AGENT_REGISTRY = Path("/root/A-FORGE/data/agent_identities.json")
_DID_REGISTRY_CANDIDATES = (
    Path("/root/secrets/did/registry.json"),
    Path("/root/AAA/secrets/did/registry.json"),
    Path("/root/AAA/auth/did_registry.yaml"),
)

# Actors that may always receive challenges (in addition to registered agents)
_ALWAYS_CHALLENGEABLE = frozenset({"arif", "888", "ariffazil"})


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


def _normalize_actor(actor_id: str) -> str:
    return (actor_id or "").lower().strip()


def _load_pem_public(pem_bytes: bytes) -> ed25519.Ed25519PublicKey | None:
    try:
        key = serialization.load_pem_public_key(pem_bytes)
        if isinstance(key, ed25519.Ed25519PublicKey):
            return key
    except Exception as exc:
        logger.debug("PEM public load failed: %s", exc)
    return None


def _load_hex_public(hex_key: str) -> ed25519.Ed25519PublicKey | None:
    try:
        raw = bytes.fromhex(hex_key.strip())
        return ed25519.Ed25519PublicKey.from_public_bytes(raw)
    except Exception as exc:
        logger.debug("hex public load failed: %s", exc)
        return None


def resolve_actor_public_key(actor_id: str) -> ed25519.Ed25519PublicKey | None:
    """Resolve Ed25519 public key for actor_id from federation registries."""
    aid = _normalize_actor(actor_id)
    if not aid:
        return None

    # arif aliases
    if aid in ("arif", "888", "ariffazil"):
        p = Path(_PUBLIC_KEY_PATH)
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key
        # also try AAA canonical
        p2 = _AAA_KEYS / "arif_public.pem"
        if p2.is_file():
            key = _load_pem_public(p2.read_bytes())
            if key:
                return key

    # AAA/IDENTITY/keys/{actor}_public.pem
    for name in (f"{aid}_public.pem", f"{actor_id}_public.pem", f"{aid}.pem"):
        p = _AAA_KEYS / name
        if p.is_file():
            key = _load_pem_public(p.read_bytes())
            if key:
                return key

    # A-FORGE/IDENTITY/keys/{actor}/
    for base in (_AFORGE_KEYS / aid, _AFORGE_KEYS / actor_id):
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*public*.pem")) + sorted(base.glob("*.pem")):
            if "private" in p.name.lower():
                continue
            key = _load_pem_public(p.read_bytes())
            if key:
                return key

    # agent_identities.json
    if _AGENT_REGISTRY.is_file():
        try:
            reg = json.loads(_AGENT_REGISTRY.read_text(encoding="utf-8"))
            # try exact and lowercase keys
            entry = reg.get(actor_id) or reg.get(aid)
            if entry:
                proof = entry.get("identity_proof") or {}
                if isinstance(proof, dict) and proof.get("type") == "ed25519":
                    pem = proof.get("public_key_pem")
                    if pem:
                        key = _load_pem_public(pem.encode() if isinstance(pem, str) else pem)
                        if key:
                            return key
        except Exception as exc:
            logger.warning("agent_identities load failed: %s", exc)

    # DID registry (json dict or yaml list)
    for reg_path in _DID_REGISTRY_CANDIDATES:
        if not reg_path.is_file():
            continue
        try:
            text = reg_path.read_text(encoding="utf-8")
            if reg_path.suffix in (".yaml", ".yml"):
                import yaml

                data = yaml.safe_load(text) or {}
                dids = data.get("dids") or []
                for item in dids:
                    did = str(item.get("did", ""))
                    if did.endswith(f":{aid}") or did.endswith(f":{actor_id}"):
                        hx = item.get("public_key_hex")
                        if hx:
                            key = _load_hex_public(hx)
                            if key:
                                return key
            else:
                data = json.loads(text)
                dids = data.get("dids") or {}
                if isinstance(dids, dict):
                    for did, meta in dids.items():
                        if did.endswith(f":{aid}") or did.endswith(f":{actor_id}"):
                            hx = (meta or {}).get("public_key_hex")
                            if hx:
                                key = _load_hex_public(hx)
                                if key:
                                    return key
        except Exception as exc:
            logger.debug("DID registry parse %s: %s", reg_path, exc)

    return None


def is_registered_actor(actor_id: str) -> bool:
    """True if actor has a resolvable public key (registered for crypto auth)."""
    return resolve_actor_public_key(actor_id) is not None


def issue_actor_challenge(actor_id: str, ttl_seconds: int | None = None) -> str:
    """Issue a short-lived, single-use nonce for actor signature verification."""
    aid = _normalize_actor(actor_id)
    if aid not in _ALWAYS_CHALLENGEABLE and not is_registered_actor(actor_id):
        raise ValueError(
            f"Actor {actor_id!r} is not registered for crypto auth. "
            "Register public key via agent-onboard.py first."
        )

    ttl = ttl_seconds if ttl_seconds is not None else _CHALLENGE_TTL_SECONDS
    if ttl <= 0:
        raise ValueError("Challenge TTL must be positive")

    now = time.time()
    nonce = secrets.token_urlsafe(32)
    # Store under original actor_id for consume match (session uses same string)
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
        # normalize compare
        if _normalize_actor(challenge.actor_id) != _normalize_actor(actor_id):
            return False, "challenge_actor_mismatch"
        if challenge.expires_at <= now:
            del _issued_challenges[nonce]
            return False, "challenge_expired"

        del _issued_challenges[nonce]
        _used_challenges[nonce] = challenge.expires_at
        return True, "challenge_consumed"


def verify_actor_signature(actor_id: str, nonce: str, signature_b64: str) -> bool:
    """Verify Ed25519 signature over ``{actor_id}:{nonce}`` for any registered actor."""
    if not actor_id:
        return False
    if not nonce:
        logger.warning("Crypto Auth: Missing nonce.")
        return False

    public_key = resolve_actor_public_key(actor_id)
    if public_key is None:
        logger.warning("Crypto Auth: No public key for actor=%s", actor_id)
        return False

    try:
        signature_bytes = base64.b64decode(signature_b64)
        message_bytes = f"{actor_id}:{nonce}".encode()

        public_key.verify(signature_bytes, message_bytes)
        challenge_ok, challenge_reason = _consume_actor_challenge(actor_id, nonce)
        if not challenge_ok:
            logger.warning("Crypto Auth: Nonce rejected — %s.", challenge_reason)
            return False
        return True
    except InvalidSignature:
        logger.warning("Crypto Auth: Invalid signature provided for actor=%s", actor_id)
        return False
    except Exception as e:
        logger.error("Crypto Auth: Verification error - %s", e)
        return False
