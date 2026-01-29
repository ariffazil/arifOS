"""
Tests for arifOS Rate Limiter Module (v50.5.17)

Validates:
- Token bucket algorithm
- Per-session rate limits
- Global rate limits
- Thread-safe operations
- Rate limiter singleton
- Cleanup of stale buckets

Constitutional Floor: F11 (Command Auth) - rate limiting is an auth check

DITEMPA BUKAN DIBERI
"""

import pytest
import time
import threading
from unittest.mock import patch

from arifos.mcp.rate_limiter import (
    RateLimiter,
    RateLimitResult,
    TokenBucket,
    get_rate_limiter,
    RATE_LIMIT_ENABLED,
    DEFAULT_LIMITS,
    FALLBACK_LIMIT,
)


class TestTokenBucket:
    """Tests for TokenBucket class."""

    def test_bucket_initial_state(self):
        """Bucket starts with full capacity."""
        bucket = TokenBucket(capacity=10, tokens=10, refill_rate=1.0)
        assert bucket.tokens == 10
        assert bucket.capacity == 10

    def test_bucket_consume_success(self):
        """Bucket allows consumption when tokens available."""
        bucket = TokenBucket(capacity=10, tokens=10, refill_rate=1.0)
        success, remaining = bucket.consume(1)
        assert success is True
        assert remaining == 9

    def test_bucket_consume_multiple(self):
        """Bucket allows multiple token consumption."""
        bucket = TokenBucket(capacity=10, tokens=10, refill_rate=1.0)
        success, remaining = bucket.consume(5)
        assert success is True
        assert remaining == 5

    def test_bucket_consume_insufficient(self):
        """Bucket denies consumption when insufficient tokens."""
        bucket = TokenBucket(capacity=10, tokens=2, refill_rate=1.0)
        success, remaining = bucket.consume(5)
        assert success is False
        assert remaining < 5

    def test_bucket_refill(self):
        """Bucket refills over time."""
        bucket = TokenBucket(capacity=10, tokens=5, refill_rate=10.0)
        # Wait for refill
        time.sleep(0.2)
        success, remaining = bucket.consume(1)
        assert success is True
        assert remaining > 5  # Should have refilled

    def test_bucket_refill_capped(self):
        """Bucket doesn't exceed capacity when refilling."""
        bucket = TokenBucket(capacity=10, tokens=10, refill_rate=100.0)
        time.sleep(0.1)
        success, remaining = bucket.consume(1)
        assert success is True
        # Should not exceed capacity - 1
        assert remaining <= 9


class TestRateLimitResult:
    """Tests for RateLimitResult dataclass."""

    def test_result_allowed(self):
        """RateLimitResult with allowed=True."""
        result = RateLimitResult(allowed=True, remaining=10)
        assert result.allowed is True
        assert result.remaining == 10

    def test_result_denied(self):
        """RateLimitResult with allowed=False."""
        result = RateLimitResult(
            allowed=False,
            reason="Rate limit exceeded",
            remaining=0,
            reset_in_seconds=60.0,
            limit_type="global"
        )
        assert result.allowed is False
        assert result.reason == "Rate limit exceeded"
        assert result.limit_type == "global"


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def setup_method(self):
        """Create fresh rate limiter for each test."""
        self.limiter = RateLimiter()

    def test_limiter_init(self):
        """RateLimiter initializes with default limits."""
        assert self.limiter.limits == DEFAULT_LIMITS
        assert self.limiter.enabled == RATE_LIMIT_ENABLED

    def test_limiter_custom_limits(self):
        """RateLimiter accepts custom limits."""
        custom_limits = {"test_tool": {"per_session": 5, "global": 50, "burst": 2}}
        limiter = RateLimiter(limits=custom_limits)
        assert limiter.limits == custom_limits

    def test_limiter_check_allowed(self):
        """RateLimiter allows requests under limit."""
        result = self.limiter.check("agi_genius", session_id="test_session")
        assert result.allowed is True

    def test_limiter_check_no_session(self):
        """RateLimiter works without session_id."""
        result = self.limiter.check("agi_genius")
        assert result.allowed is True

    def test_limiter_fallback_limit(self):
        """RateLimiter uses fallback for unknown tools."""
        result = self.limiter.check("unknown_tool", session_id="test")
        assert result.allowed is True

    def test_limiter_global_limit_exceeded(self):
        """RateLimiter denies when global limit exceeded."""
        # Create limiter with very low global limit
        limiter = RateLimiter(limits={
            "test_tool": {"per_session": 100, "global": 2, "burst": 1}
        })

        # First two should pass
        result1 = limiter.check("test_tool")
        result2 = limiter.check("test_tool")
        assert result1.allowed is True
        assert result2.allowed is True

        # Third should fail (global limit of 2 exceeded)
        result3 = limiter.check("test_tool")
        assert result3.allowed is False
        assert result3.limit_type == "global"

    def test_limiter_session_limit_exceeded(self):
        """RateLimiter denies when session limit exceeded."""
        # Create limiter with very low session limit
        limiter = RateLimiter(limits={
            "test_tool": {"per_session": 2, "global": 100, "burst": 1}
        })

        session_id = "limited_session"

        # First two should pass
        result1 = limiter.check("test_tool", session_id)
        result2 = limiter.check("test_tool", session_id)
        assert result1.allowed is True
        assert result2.allowed is True

        # Third should fail for this session
        result3 = limiter.check("test_tool", session_id)
        assert result3.allowed is False
        assert result3.limit_type == "session"

        # Different session should still work
        result4 = limiter.check("test_tool", "other_session")
        assert result4.allowed is True

    def test_limiter_disabled(self):
        """RateLimiter allows all when disabled."""
        self.limiter.enabled = False

        # Should allow even with limits exceeded
        for _ in range(100):
            result = self.limiter.check("000_init", session_id="test")
            assert result.allowed is True
            assert result.reason == "Rate limiting disabled"

    def test_limiter_get_stats(self):
        """RateLimiter returns stats."""
        self.limiter.check("agi_genius", session_id="test1")
        self.limiter.check("asi_act", session_id="test2")

        stats = self.limiter.get_stats()

        assert "enabled" in stats
        assert "tools" in stats
        assert "global_buckets" in stats
        assert "session_buckets" in stats
        assert "limits" in stats
        assert stats["global_buckets"] >= 2

    def test_limiter_cleanup(self):
        """RateLimiter cleans up stale buckets."""
        # Create a bucket
        self.limiter.check("test_tool", session_id="stale_session")

        # Force bucket to be stale by manipulating last_refill
        bucket = self.limiter._session_buckets["test_tool"]["stale_session"]
        bucket.last_refill = time.time() - 700  # 700 seconds ago (> 600 stale threshold)

        # Force cleanup by setting last_cleanup time
        self.limiter._last_cleanup = time.time() - 400  # > 300 cleanup interval

        # Trigger cleanup via check
        self.limiter.check("other_tool")

        # Stale bucket should be removed
        assert "stale_session" not in self.limiter._session_buckets.get("test_tool", {})


class TestRateLimiterThreadSafety:
    """Tests for thread-safe rate limiter operations."""

    def test_concurrent_checks(self):
        """RateLimiter handles concurrent checks safely."""
        limiter = RateLimiter(limits={
            "concurrent_tool": {"per_session": 1000, "global": 10000, "burst": 100}
        })

        results = []

        def do_checks():
            for _ in range(100):
                result = limiter.check("concurrent_tool", session_id="concurrent")
                results.append(result.allowed)

        threads = [threading.Thread(target=do_checks) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All checks should complete without error
        assert len(results) == 1000
        # Most should be allowed (within limit)
        assert sum(results) > 500


class TestGetRateLimiter:
    """Tests for get_rate_limiter singleton."""

    def test_singleton(self):
        """get_rate_limiter returns same instance."""
        import arifos.mcp.rate_limiter as module

        # Clear singleton
        module._rate_limiter = None

        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()

        assert limiter1 is limiter2


class TestDefaultLimits:
    """Tests for default limit configurations."""

    def test_all_tools_have_limits(self):
        """All Trinity tools have default limits."""
        expected_tools = ["000_init", "agi_genius", "asi_act", "apex_judge", "999_vault"]
        for tool in expected_tools:
            assert tool in DEFAULT_LIMITS
            assert "per_session" in DEFAULT_LIMITS[tool]
            assert "global" in DEFAULT_LIMITS[tool]
            assert "burst" in DEFAULT_LIMITS[tool]

    def test_fallback_limit_complete(self):
        """Fallback limit has all required fields."""
        assert "per_session" in FALLBACK_LIMIT
        assert "global" in FALLBACK_LIMIT
        assert "burst" in FALLBACK_LIMIT

    def test_limits_are_positive(self):
        """All limits are positive integers."""
        for tool, limits in DEFAULT_LIMITS.items():
            assert limits["per_session"] > 0
            assert limits["global"] > 0
            assert limits["burst"] > 0


class TestRateLimiterIntegration:
    """Integration tests for rate limiter with MCP tools."""

    def test_rate_limit_response_format(self):
        """Rate limit exceeded response has correct format."""
        limiter = RateLimiter(limits={
            "test_tool": {"per_session": 1, "global": 1, "burst": 1}
        })

        # Exhaust limit
        limiter.check("test_tool")

        # Get denied response
        result = limiter.check("test_tool")

        assert result.allowed is False
        assert len(result.reason) > 0
        assert result.reset_in_seconds > 0
        assert result.limit_type in ("global", "session", "burst")


class TestRateLimitedDecorator:
    """Tests for @rate_limited decorator."""

    
    async def test_decorator_allows_request(self):
        """Decorator allows request when under limit."""
        from arifos.mcp.rate_limiter import rate_limited
        import arifos.mcp.rate_limiter as module

        # Reset singleton and create fresh limiter with high limits
        module._rate_limiter = RateLimiter(limits={
            "decorated_tool": {"per_session": 100, "global": 1000, "burst": 10}
        })

        @rate_limited("decorated_tool")
        async def test_tool(value: str, session_id: str = ""):
            return {"status": "SEAL", "value": value}

        result = await test_tool("test_value", session_id="test_session")

        assert result["status"] == "SEAL"
        assert result["value"] == "test_value"

    
    async def test_decorator_blocks_when_exceeded(self):
        """Decorator blocks request when rate limit exceeded."""
        from arifos.mcp.rate_limiter import rate_limited
        import arifos.mcp.rate_limiter as module

        # Create limiter with very low limits
        module._rate_limiter = RateLimiter(limits={
            "limited_tool": {"per_session": 1, "global": 1, "burst": 1}
        })

        @rate_limited("limited_tool")
        async def test_tool(session_id: str = ""):
            return {"status": "SEAL"}

        # First call should succeed
        result1 = await test_tool(session_id="test")
        assert result1["status"] == "SEAL"

        # Second call should be rate limited
        result2 = await test_tool(session_id="test")
        assert result2["status"] == "VOID"
        assert "rate_limit" in result2
        assert result2["rate_limit"]["exceeded"] is True

    
    async def test_decorator_extracts_session_id(self):
        """Decorator extracts session_id from kwargs."""
        from arifos.mcp.rate_limiter import rate_limited
        import arifos.mcp.rate_limiter as module

        module._rate_limiter = RateLimiter(limits={
            "session_tool": {"per_session": 2, "global": 100, "burst": 10}
        })

        @rate_limited("session_tool")
        async def test_tool(session_id: str = ""):
            return {"status": "SEAL", "session_id": session_id}

        # Two calls to same session
        await test_tool(session_id="session_a")
        await test_tool(session_id="session_a")

        # Third call to same session should be limited
        result = await test_tool(session_id="session_a")
        assert result["status"] == "VOID"

        # But different session should work
        result = await test_tool(session_id="session_b")
        assert result["status"] == "SEAL"

    
    async def test_decorator_no_session_id(self):
        """Decorator works without session_id kwarg."""
        from arifos.mcp.rate_limiter import rate_limited
        import arifos.mcp.rate_limiter as module

        module._rate_limiter = RateLimiter(limits={
            "no_session_tool": {"per_session": 100, "global": 100, "burst": 10}
        })

        @rate_limited("no_session_tool")
        async def test_tool():
            return {"status": "SEAL"}

        result = await test_tool()
        assert result["status"] == "SEAL"
