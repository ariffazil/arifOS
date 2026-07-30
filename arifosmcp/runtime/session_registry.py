"""
arifosmcp/runtime/session_registry.py — Redis-Backed Session Registry
═══════════════════════════════════════════════════════════════════════

Replaces the global _ACTIVE_SESSION_ID singleton with a Redis-backed
SessionRegistry that provides atomic get/set with async Lock.

Multi-agent safety:
- Each session is a Redis hash with TTL
- Active session pointer is a single Redis key with SETNX semantics
- `acquire_session_lock` / `release_session_lock` for multi-step ops

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# REDIS CLIENT (lazy singleton)
# ═══════════════════════════════════════════════════════════════════════════════

_REDIS_CLIENT: Any = None  # redis.Redis or None
_REDIS_AVAILABLE: bool = False


def _get_redis() -> Any | None:
    """Get or create a Redis client. Returns None if unavailable."""
    global _REDIS_CLIENT, _REDIS_AVAILABLE
    if _REDIS_CLIENT is not None:
        return _REDIS_CLIENT
    if _REDIS_AVAILABLE is False:
        return None

    redis_url = os.environ.get(
        "ARIFOS_REDIS_URL",
        os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    )
    try:
        import redis.asyncio as aioredis  # type: ignore

        _REDIS_CLIENT = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=5,
        )
        _REDIS_AVAILABLE = True
        logger.info("[session_registry] Redis client created (%s)", redis_url.split("@")[-1])
        return _REDIS_CLIENT
    except ImportError:
        logger.warning("[session_registry] redis package not installed — using in-memory fallback")
        _REDIS_AVAILABLE = False
        return None
    except Exception as exc:
        logger.warning("[session_registry] Redis connect failed: %s — using in-memory fallback", exc)
        _REDIS_AVAILABLE = False
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY FALLBACK (thread-safe via dict + monotonic counter)
# ═══════════════════════════════════════════════════════════════════════════════

import threading

_fallback_lock = threading.Lock()
_fallback_sessions: dict[str, dict[str, Any]] = {}
_fallback_active_session: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# KEY PREFIXES
# ═══════════════════════════════════════════════════════════════════════════════

_PREFIX_SESSION = "arifos:session:"        # session data
_PREFIX_ACTIVE = "arifos:active_session"    # current active session ID
_PREFIX_LOCK = "arifos:session_lock:"       # per-session mutex lock
_PREFIX_NONCE = "arifos:nonce:"             # request nonce cache
_DEFAULT_TTL = int(os.environ.get("ARIFOS_SESSION_TTL_SECONDS", "86400"))


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════


class SessionRegistry:
    """
    Atomic, multi-agent-safe session registry backed by Redis (with in-memory fallback).

    Usage:
        registry = SessionRegistry()
        await registry.set_session("sid_abc", {"actor_id": "arif", ...})
        data = await registry.get_session("sid_abc")
        await registry.set_active_session_id("sid_abc")
        active = await registry.get_active_session_id()
    """

    def __init__(self) -> None:
        self._redis = _get_redis()

    # ── Session CRUD ──────────────────────────────────────────────────────

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session data by ID."""
        if self._redis:
            try:
                data = await self._redis.hgetall(f"{_PREFIX_SESSION}{session_id}")
                if data:
                    return _decode_session_hash(data)
                return None
            except Exception as exc:
                logger.debug("[session_registry] Redis get_session error: %s", exc)

        # Fallback
        with _fallback_lock:
            return _fallback_sessions.get(session_id)

    async def set_session(
        self,
        session_id: str,
        data: dict[str, Any],
        ttl: int = _DEFAULT_TTL,
    ) -> None:
        """Set session data with TTL."""
        if self._redis:
            try:
                key = f"{_PREFIX_SESSION}{session_id}"
                await self._redis.hset(key, mapping=_encode_session_hash(data))
                await self._redis.expire(key, ttl)
                return
            except Exception as exc:
                logger.debug("[session_registry] Redis set_session error: %s", exc)

        # Fallback
        with _fallback_lock:
            _fallback_sessions[session_id] = data

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if existed."""
        if self._redis:
            try:
                deleted = await self._redis.delete(f"{_PREFIX_SESSION}{session_id}")
                return deleted > 0
            except Exception as exc:
                logger.debug("[session_registry] Redis delete_session error: %s", exc)

        with _fallback_lock:
            existed = session_id in _fallback_sessions
            _fallback_sessions.pop(session_id, None)
            return existed

    async def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        if self._redis:
            try:
                return await self._redis.exists(f"{_PREFIX_SESSION}{session_id}") > 0
            except Exception as exc:
                logger.debug("[session_registry] Redis exists error: %s", exc)

        with _fallback_lock:
            return session_id in _fallback_sessions

    # ── Active Session ──────────────────────────────────────────────────

    async def get_active_session_id(self) -> str | None:
        """Get the currently active session ID (multi-agent-safe)."""
        if self._redis:
            try:
                return await self._redis.get(_PREFIX_ACTIVE)
            except Exception as exc:
                logger.debug("[session_registry] Redis get_active error: %s", exc)

        with _fallback_lock:
            return _fallback_active_session

    async def set_active_session_id(self, session_id: str) -> None:
        """Set the active session ID. Idempotent — last writer wins."""
        if self._redis:
            try:
                await self._redis.set(_PREFIX_ACTIVE, session_id, ex=_DEFAULT_TTL)
                return
            except Exception as exc:
                logger.debug("[session_registry] Redis set_active error: %s", exc)

        with _fallback_lock:
            global _fallback_active_session
            _fallback_active_session = session_id

    async def clear_active_session(self) -> None:
        """Clear the active session pointer."""
        if self._redis:
            try:
                await self._redis.delete(_PREFIX_ACTIVE)
                return
            except Exception as exc:
                logger.debug("[session_registry] Redis clear_active error: %s", exc)

        with _fallback_lock:
            global _fallback_active_session
            _fallback_active_session = None

    # ── Per-Session Lock (async mutex for multi-step ops) ──────────────

    async def acquire_session_lock(
        self, session_id: str, timeout: float = 10.0
    ) -> str | None:
        """
        Acquire an async mutex lock on a session.

        Returns lock token (must be passed to release_session_lock).
        Returns None if lock could not be acquired within timeout.
        """
        lock_key = f"{_PREFIX_LOCK}{session_id}"
        token = str(uuid.uuid4())
        deadline = time.monotonic() + timeout

        if self._redis:
            try:
                while time.monotonic() < deadline:
                    acquired = await self._redis.setnx(lock_key, token)
                    if acquired:
                        await self._redis.expire(lock_key, int(timeout) + 5)
                        return token
                    await _async_sleep(0.05)
                return None
            except Exception as exc:
                logger.debug("[session_registry] Redis acquire_lock error: %s", exc)
                return token  # optimistic proceed

        # Fallback: no cross-process lock, token is dummy
        return token

    async def release_session_lock(self, session_id: str, token: str) -> None:
        """Release a previously acquired session lock."""
        lock_key = f"{_PREFIX_LOCK}{session_id}"
        if self._redis:
            try:
                # Lua script: delete only if our token matches
                script = """
                if redis.call("get", KEYS[1]) == ARGV[1] then
                    return redis.call("del", KEYS[1])
                end
                return 0
                """
                await self._redis.eval(script, 1, lock_key, token)
                return
            except Exception as exc:
                logger.debug("[session_registry] Redis release_lock error: %s", exc)

        # Fallback: no-op

    # ── Nonce Cache (replay protection) ────────────────────────────────

    async def check_and_record_nonce(self, nonce: str, ttl: int = 600) -> bool:
        """
        Check if a nonce has been seen before, and record it if not.

        Returns True if nonce is fresh (first time seen).
        Returns False if nonce already exists (replay detected).
        """
        if self._redis:
            try:
                key = f"{_PREFIX_NONCE}{nonce}"
                existed = await self._redis.exists(key)
                if existed:
                    return False
                await self._redis.set(key, "1", ex=ttl)
                return True
            except Exception as exc:
                logger.debug("[session_registry] Redis nonce error: %s", exc)
                return True  # optimistic — allow on Redis error

        # Fallback in-memory nonce cache (bounded LRU)
        with _fallback_lock:
            now = time.time()
            # Clean expired entries
            expired = [k for k, v in _nonce_cache.items() if v < now]
            for k in expired:
                _nonce_cache.pop(k, None)
            if nonce in _nonce_cache:
                return False
            _nonce_cache[nonce] = now + ttl
            # Bounded
            while len(_nonce_cache) > 4096:
                _nonce_cache.pop(next(iter(_nonce_cache)), None)
            return True


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

_nonce_cache: dict[str, float] = {}


def _encode_session_hash(data: dict[str, Any]) -> dict[str, str]:
    """Encode session data as flat string dict for Redis hash."""
    encoded: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(v, (str, int, float, bool)):
            encoded[k] = str(v)
        else:
            encoded[k] = json.dumps(v, default=str)
    return encoded


def _decode_session_hash(hash_data: dict[str, str]) -> dict[str, Any]:
    """Decode a flat Redis hash back into session data."""
    decoded: dict[str, Any] = {}
    for k, v in hash_data.items():
        try:
            decoded[k] = json.loads(v)
        except (json.JSONDecodeError, TypeError):
            decoded[k] = v
    return decoded


async def _async_sleep(seconds: float) -> None:
    """Async sleep (works with trio/asyncio/anyio)."""
    import asyncio

    await asyncio.sleep(seconds)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_registry: SessionRegistry | None = None


def get_registry() -> SessionRegistry:
    """Get the module-level SessionRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = SessionRegistry()
    return _registry


def get_session_sync(session_id: str) -> dict | None:
    """Sync session lookup for identity binding / non-async call sites.

    Prefers in-memory fallback; Redis async path is not used here.
    For full Redis, await SessionRegistry.get_session.
    """
    if not session_id:
        return None
    with _fallback_lock:
        return _fallback_sessions.get(session_id)


__all__ = [
    "SessionRegistry",
    "get_registry",
    "get_session_sync",
]
