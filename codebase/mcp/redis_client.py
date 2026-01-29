"""
codebase.mcp.redis_client (v53.2.7)

Redis integration for arifOS codebase.
Provides session persistence, metrics caching, and rate limiting.

Falls back gracefully to in-memory storage if Redis unavailable.

DITEMPA BUKAN DIBERI
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Redis client (lazy-loaded)
_redis_client = None
_redis_available = None

# In-memory fallback
_memory_sessions: Dict[str, Dict[str, Any]] = {}
_memory_tokens: Dict[str, str] = {}
_memory_metrics: Dict[str, Any] = {}


def get_redis_url() -> Optional[str]:
    """Get Redis URL from environment."""
    for var in ["REDIS_URL", "REDIS_PRIVATE_URL", "REDISCLOUD_URL"]:
        url = os.getenv(var)
        if url:
            return url
    return None


def get_redis():
    """Get or create Redis client. Returns None if unavailable."""
    global _redis_client, _redis_available

    if _redis_available is False:
        return None
    if _redis_client is not None:
        return _redis_client

    redis_url = get_redis_url()
    if not redis_url:
        logger.info("Redis URL not configured, using in-memory storage")
        _redis_available = False
        return None

    try:
        import redis
        # Use a timeout so we don't hang if Redis is slow
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=2,
            socket_connect_timeout=2
        )
        _redis_client.ping()
        _redis_available = True
        logger.info(f"✅ Redis connected ({redis_url.split('@')[-1]})")
        return _redis_client
    except ImportError:
        logger.warning("redis package not installed")
        _redis_available = False
        return None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        _redis_available = False
        return None


def is_available() -> bool:
    """Check if Redis is available."""
    get_redis()
    return _redis_available is True


# === SESSION MANAGEMENT (Bundles) ===

SESSION_PREFIX = "arifos:bundle:"
SESSION_TTL = 3600  # 1 hour


def save_bundle(session_id: str, data: Dict[str, Any], ttl: int = SESSION_TTL) -> bool:
    """Save session bundle to Redis or memory."""
    r = get_redis()
    data["_updated"] = datetime.utcnow().isoformat()

    if r:
        try:
            r.setex(f"{SESSION_PREFIX}{session_id}", ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Redis bundle save error: {e}")

    _memory_sessions[session_id] = data
    return True


def get_bundle(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session bundle from Redis or memory."""
    r = get_redis()

    if r:
        try:
            data = r.get(f"{SESSION_PREFIX}{session_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis bundle get error: {e}")

    return _memory_sessions.get(session_id)


def delete_bundle(session_id: str) -> bool:
    """Delete session bundle."""
    r = get_redis()

    if r:
        try:
            r.delete(f"{SESSION_PREFIX}{session_id}")
        except Exception as e:
            logger.error(f"Redis bundle delete error: {e}")

    _memory_sessions.pop(session_id, None)
    return True


# === METRICS PERSISTENCE ===

METRICS_PREFIX = "arifos:metric:"

def set_metric(name: str, value: Any):
    """Set a persistent gauge metric."""
    r = get_redis()
    if r:
        try:
            r.set(f"{METRICS_PREFIX}{name}", str(value))
        except Exception as e:
            logger.error(f"Redis metric set error: {e}")

def get_metric(name: str, default: Any = 0) -> Any:
    """Get a persistent gauge metric."""
    r = get_redis()
    if r:
        try:
            val = r.get(f"{METRICS_PREFIX}{name}")
            return val if val is not None else default
        except Exception as e:
            logger.error(f"Redis metric get error: {e}")
    return default

def incr_metric(name: str, amount: int = 1) -> int:
    """Increment a persistent counter metric."""
    r = get_redis()
    if r:
        try:
            return r.incr(f"{METRICS_PREFIX}{name}", amount)
        except Exception as e:
            logger.error(f"Redis metric incr error: {e}")
    return 0


# === RATE LIMITING ===

RATE_PREFIX = "arifos:rate:"


def check_rate_limit(key: str, limit: int, window: int = 60) -> tuple:
    """
    Check rate limit using Redis INCR pattern.
    Returns (allowed, remaining).
    """
    r = get_redis()

    if r:
        try:
            redis_key = f"{RATE_PREFIX}{key}"
            current = r.incr(redis_key)
            if current == 1:
                r.expire(redis_key, window)
            
            remaining = max(0, limit - current)
            return (current <= limit, remaining)
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")

    # Fail open if Redis unavailable (don't block user)
    return (True, limit)


# === HEALTH CHECK ===

def health() -> Dict[str, Any]:
    """Get Redis health status."""
    r = get_redis()

    if not r:
        return {"status": "unavailable", "backend": "memory"}

    try:
        info = r.info("server")
        return {
            "status": "healthy",
            "backend": "redis",
            "version": info.get("redis_version", "?"),
            "uptime_seconds": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        return {"status": "error", "backend": "redis", "error": str(e)}
