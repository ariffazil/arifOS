"""
arifOS Rate Limiter (v51.0.0)
Constitutional Rate Limiting for MCP Tools

Implements:
- Per-session rate limits (prevents single session abuse)
- Global rate limits (prevents system overload)
- Tool-specific limits (different thresholds per tool)
- Burst allowance (short-term spikes OK)

Constitutional Floor: F11 (Command Auth) - rate limiting is an auth check
Law: "I do not think, I only allow."

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment-based configuration
RATE_LIMIT_ENABLED = os.environ.get("ARIFOS_RATE_LIMIT_ENABLED", "true").lower() == "true"

# Default limits (per minute)
DEFAULT_LIMITS = {
    "init_000": {"per_session": 30, "global": 300, "burst": 5},
    "agi_genius": {"per_session": 60, "global": 600, "burst": 10},
    "asi_act": {"per_session": 60, "global": 600, "burst": 10},
    "apex_judge": {"per_session": 60, "global": 600, "burst": 10},
    "vault_999": {"per_session": 30, "global": 300, "burst": 5},
}

# Global fallback
FALLBACK_LIMIT = {"per_session": 60, "global": 600, "burst": 10}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    reason: str = ""
    remaining: int = 0
    reset_in_seconds: float = 0.0
    limit_type: str = ""  # "session", "global", "burst"


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = field(default_factory=time.time)

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens from the bucket.

        Returns:
            (success, remaining_tokens)
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True, self.tokens
        else:
            return False, self.tokens


# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Constitutional Rate Limiter for AAA MCP Tools.

    Thread-safe implementation with:
    - Per-session buckets (identified by session_id)
    - Global buckets (per tool)
    - Automatic bucket cleanup

    Usage:
        limiter = get_rate_limiter()
        result = limiter.check("agi_genius", session_id="abc123")
        if not result.allowed:
            return {"status": "VOID", "reason": result.reason}
    """

    def __init__(self, limits: Optional[Dict] = None):
        """Initialize rate limiter with optional custom limits."""
        self.limits = limits or DEFAULT_LIMITS
        self.enabled = RATE_LIMIT_ENABLED

        # Buckets: {tool_name: {session_id: TokenBucket}}
        self._session_buckets: Dict[str, Dict[str, TokenBucket]] = defaultdict(dict)

        # Global buckets: {tool_name: TokenBucket}
        self._global_buckets: Dict[str, TokenBucket] = {}

        # Lock for thread safety
        self._lock = threading.Lock()

        # Cleanup interval (seconds)
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

        logger.info(f"arifOS RateLimiter initialized (enabled={self.enabled})")

    def check(self, tool_name: str, session_id: str = "") -> RateLimitResult:
        """
        Check if request is allowed under rate limits.

        Args:
            tool_name: Name of the MCP tool being called
            session_id: Optional session identifier for per-session limits

        Returns:
            RateLimitResult with allowed status and details
        """
        if not self.enabled:
            return RateLimitResult(allowed=True, reason="Rate limiting disabled")

        limits = self.limits.get(tool_name, FALLBACK_LIMIT)
        session_limit = limits["per_session"]
        global_limit = limits["global"]

        with self._lock:
            # Periodic cleanup
            self._maybe_cleanup()

            # Check global limit first (more restrictive)
            global_result = self._check_global(tool_name, global_limit)
            if not global_result.allowed:
                logger.warning(f"Rate limit: Global limit exceeded for {tool_name}")
                return global_result

            # Check session limit if session_id provided
            if session_id:
                session_result = self._check_session(tool_name, session_id, session_limit)
                if not session_result.allowed:
                    logger.warning(f"Rate limit: Session limit exceeded for {tool_name}/{session_id}")
                    return session_result

            return RateLimitResult(
                allowed=True,
                remaining=int(global_result.remaining),
                reset_in_seconds=60.0 / (global_limit / 60)  # Approximate
            )

    def _check_global(self, tool_name: str, limit: int) -> RateLimitResult:
        """Check global rate limit for a tool."""
        if tool_name not in self._global_buckets:
            self._global_buckets[tool_name] = TokenBucket(
                capacity=limit,
                tokens=limit,
                refill_rate=limit / 60.0  # Refill over 1 minute
            )

        bucket = self._global_buckets[tool_name]
        allowed, remaining = bucket.consume(1)

        if not allowed:
            return RateLimitResult(
                allowed=False,
                reason=f"Global rate limit exceeded for {tool_name}",
                remaining=0,
                reset_in_seconds=1.0 / bucket.refill_rate,
                limit_type="global"
            )

        return RateLimitResult(allowed=True, remaining=int(remaining))

    def _check_session(self, tool_name: str, session_id: str, limit: int) -> RateLimitResult:
        """Check per-session rate limit."""
        if session_id not in self._session_buckets[tool_name]:
            self._session_buckets[tool_name][session_id] = TokenBucket(
                capacity=limit,
                tokens=limit,
                refill_rate=limit / 60.0
            )

        bucket = self._session_buckets[tool_name][session_id]
        allowed, remaining = bucket.consume(1)

        if not allowed:
            return RateLimitResult(
                allowed=False,
                reason=f"Session rate limit exceeded for {tool_name}",
                remaining=0,
                reset_in_seconds=1.0 / bucket.refill_rate,
                limit_type="session"
            )

        return RateLimitResult(allowed=True, remaining=int(remaining))

    def _maybe_cleanup(self):
        """Clean up stale buckets periodically."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = now
        stale_threshold = 600  # 10 minutes

        # Clean session buckets
        for tool_name in list(self._session_buckets.keys()):
            for session_id in list(self._session_buckets[tool_name].keys()):
                bucket = self._session_buckets[tool_name][session_id]
                if now - bucket.last_refill > stale_threshold:
                    del self._session_buckets[tool_name][session_id]

        logger.debug("Rate limiter cleanup completed")

    def get_stats(self) -> Dict:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "enabled": self.enabled,
                "tools": list(self.limits.keys()),
                "global_buckets": len(self._global_buckets),
                "session_buckets": sum(len(v) for v in self._session_buckets.values()),
                "limits": self.limits
            }


# =============================================================================
# SINGLETON
# =============================================================================

_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get the singleton rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# =============================================================================
# DECORATOR
# =============================================================================

def rate_limited(tool_name: str):
    """
    Decorator to apply rate limiting to a tool function.

    Usage:
        @rate_limited("agi_genius")
        async def mcp_agi_genius(action: str, ...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            session_id = kwargs.get("session_id", "")
            limiter = get_rate_limiter()
            result = limiter.check(tool_name, session_id)

            if not result.allowed:
                return {
                    "status": "VOID",
                    "reason": result.reason,
                    "rate_limit": {
                        "exceeded": True,
                        "limit_type": result.limit_type,
                        "reset_in_seconds": result.reset_in_seconds
                    },
                    "floors_checked": ["F11_CommandAuth"]
                }

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RateLimiter",
    "RateLimitResult",
    "get_rate_limiter",
    "rate_limited",
    "RATE_LIMIT_ENABLED",
]
