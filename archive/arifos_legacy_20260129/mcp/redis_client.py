"""
arifos.mcp.redis_client (v53.0.1)

Redis integration for arifOS MCP server.
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
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5
        )
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis connected")
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


# === SESSION MANAGEMENT ===

SESSION_PREFIX = "arifos:session:"
SESSION_TTL = 3600


def save_session(session_id: str, data: Dict[str, Any], ttl: int = SESSION_TTL) -> bool:
    """Save session to Redis or memory."""
    r = get_redis()
    data["_updated"] = datetime.utcnow().isoformat()

    if r:
        try:
            r.setex(f"{SESSION_PREFIX}{session_id}", ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Redis save error: {e}")

    _memory_sessions[session_id] = data
    return True


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session from Redis or memory."""
    r = get_redis()

    if r:
        try:
            data = r.get(f"{SESSION_PREFIX}{session_id}")
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")

    return _memory_sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """Delete session from Redis and memory."""
    r = get_redis()

    if r:
        try:
            r.delete(f"{SESSION_PREFIX}{session_id}")
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    _memory_sessions.pop(session_id, None)
    return True


def list_sessions() -> List[str]:
    """List all session IDs."""
    r = get_redis()

    if r:
        try:
            keys = r.keys(f"{SESSION_PREFIX}*")
            return [k.replace(SESSION_PREFIX, "") for k in keys]
        except Exception as e:
            logger.error(f"Redis list error: {e}")

    return list(_memory_sessions.keys())


# === TOKEN MANAGEMENT ===

TOKEN_PREFIX = "arifos:token:"
TOKEN_TTL = 3600


def save_token(session_id: str, token: str) -> bool:
    """Save session token."""
    r = get_redis()

    if r:
        try:
            r.setex(f"{TOKEN_PREFIX}{session_id}", TOKEN_TTL, token)
            return True
        except Exception as e:
            logger.error(f"Redis token save error: {e}")

    _memory_tokens[session_id] = token
    return True


def get_token(session_id: str) -> Optional[str]:
    """Get session token."""
    r = get_redis()

    if r:
        try:
            return r.get(f"{TOKEN_PREFIX}{session_id}")
        except Exception as e:
            logger.error(f"Redis token get error: {e}")

    return _memory_tokens.get(session_id)


def delete_token(session_id: str) -> bool:
    """Delete session token."""
    r = get_redis()

    if r:
        try:
            r.delete(f"{TOKEN_PREFIX}{session_id}")
        except Exception as e:
            logger.error(f"Redis token delete error: {e}")

    _memory_tokens.pop(session_id, None)
    return True


def count_tokens() -> int:
    """Count active tokens."""
    r = get_redis()

    if r:
        try:
            return len(r.keys(f"{TOKEN_PREFIX}*"))
        except Exception as e:
            logger.error(f"Redis count error: {e}")

    return len(_memory_tokens)


# === METRICS CACHE ===

METRICS_KEY = "arifos:metrics"
METRICS_TTL = 5


def cache_metrics(metrics: Dict[str, Any]) -> bool:
    """Cache metrics with 5s TTL."""
    r = get_redis()

    if r:
        try:
            r.setex(METRICS_KEY, METRICS_TTL, json.dumps(metrics))
            return True
        except Exception as e:
            logger.error(f"Redis metrics cache error: {e}")

    _memory_metrics["data"] = metrics
    _memory_metrics["expires"] = datetime.utcnow() + timedelta(seconds=METRICS_TTL)
    return True


def get_cached_metrics() -> Optional[Dict[str, Any]]:
    """Get cached metrics if valid."""
    r = get_redis()

    if r:
        try:
            data = r.get(METRICS_KEY)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Redis metrics get error: {e}")

    if "data" in _memory_metrics:
        if _memory_metrics.get("expires", datetime.min) > datetime.utcnow():
            return _memory_metrics["data"]

    return None


# === RATE LIMITING ===

RATE_PREFIX = "arifos:rate:"


def check_rate_limit(key: str, limit: int, window: int) -> tuple:
    """
    Check rate limit. Returns (allowed, remaining).
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

    return (True, limit)  # Allow if Redis unavailable


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
            "uptime": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        return {"status": "error", "backend": "redis", "error": str(e)}
