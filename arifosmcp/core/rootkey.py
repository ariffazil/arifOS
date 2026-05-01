"""
arifOS F11 Rootkey Verification — Domain-Anchored Identity
=========================================================

Replaces JWT with HMAC-rootkey + public witness (arif-fazil.com/#who).
- F3 WITNESS: public page confirms identity (cached 5min)
- F11 AUTH: HMAC-rootkey confirms caller holds the secret

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)

_WHO_CACHE: dict[str, tuple[bool, float]] = {}
_WHO_CACHE_TTL = 300  # 5 minutes


def _is_rootkey_configured() -> bool:
    return bool(os.getenv("ARIF_ROOTKEY"))


async def _verify_who_page() -> bool:
    """F3 WITNESS: verify arif-fazil.com/#who contains identity declarations. Cached."""
    global _WHO_CACHE

    cached_at, cached_val = _WHO_CACHE.get("arif", (0.0, False))
    if time.time() - cached_at < _WHO_CACHE_TTL:
        return cached_val

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://arif-fazil.com",
                headers={"Accept": "text/html"},
                follow_redirects=True,
            )
            text = resp.text
            valid = (
                "Muhammad Arif bin Fazil" in text
                and "arifOS" in text
                and "Sovereign Human Anchor" in text
            )
            _WHO_CACHE["arif"] = (time.time(), valid)
            return valid
    except Exception as e:
        logger.warning(f"F3 WITNESS check failed: {e}")
        # Fail open if page is down — don't block legitimate callers
        _WHO_CACHE["arif"] = (time.time(), True)
        return True


def is_challenge_fresh(challenge: str, window_sec: int = 60) -> bool:
    """Reject replayed challenges older than window_sec."""
    try:
        ts = int(challenge.split(":")[0])
        return abs(time.time() - ts) <= window_sec
    except (ValueError, IndexError):
        return False


def verify_rootkey(actor_id: str, challenge: str, sig: str) -> bool:
    """
    F11 AUTH + F3 WITNESS: Verify actor holds ARIF_ROOTKEY.

    Args:
        actor_id: Must be "ariffazil" (sovereign identity)
        challenge: "timestamp:op_id" format
        sig: HMAC-SHA256(rootkey, challenge) hex digest

    Returns:
        True if rootkey signature is valid AND challenge is fresh
    """
    if not _is_rootkey_configured():
        logger.debug("ARIF_ROOTKEY not set — rootkey verification skipped")
        return False

    if actor_id != "ariffazil":
        return False

    if not is_challenge_fresh(challenge):
        logger.warning(f"F11 rootkey: stale challenge rejected — {challenge[:50]}")
        return False

    rootkey = os.getenv("ARIF_ROOTKEY", "")
    expected = hmac.new(
        rootkey.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, sig)


async def verify_arif_identity(
    actor_id: str,
    challenge: str | None = None,
    sig: str | None = None,
    session_id: str | None = None,
) -> bool:
    """
    Full F3+F11 identity verification for arifOS actor binding.

    Two paths:
    1. Rootkey path: actor_id=ariffazil + valid (challenge, sig) pair
    2. Session path: valid session_id in _SESSION_IDENTITY (already verified)

    Fails open if ARIF_ROOTKEY is not configured.
    """
    if actor_id == "ariffazil" and challenge and sig:
        rootkey_ok = verify_rootkey(actor_id, challenge, sig)
        if rootkey_ok:
            who_ok = await _verify_who_page()
            if who_ok:
                logger.info(f"F3+F11 verified: actor={actor_id} via rootkey+domain")
                return True
            logger.warning("F3 WITNESS failed: arif-fazil.com/#who identity not found")

    if session_id:
        try:
            from arifosmcp.runtime.session import _ensure_active_record

            record = _ensure_active_record(session_id)
            if record and record.get("actor_id") == "ariffazil":
                return True
        except Exception:
            pass

    return False


def make_rootkey_sig(op_id: str) -> tuple[str, str]:
    """
    Generate (challenge, sig) pair for client-side rootkey auth.

    Usage:
        challenge, sig = make_rootkey_sig("memory_store")
        await arif_memory_recall(mode="store", ..., challenge=challenge, sig=sig)
    """
    rootkey = os.getenv("ARIF_ROOTKEY", "")
    if not rootkey:
        raise ValueError("ARIF_ROOTKEY not configured")

    challenge = f"{int(time.time())}:{op_id}"
    sig = hmac.new(
        rootkey.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()
    return challenge, sig
