"""
arifOS Enforcement Governance Module
v51.0.0 - Constitutional Authority & Rate Limiting

DITEMPA BUKAN DIBERI
"""

from arifos.core.enforcement.governance.rate_limiter import (
    RateLimiter,
    RateLimitResult,
    get_rate_limiter,
    rate_limited,
    RATE_LIMIT_ENABLED,
)

__all__ = [
    "RateLimiter",
    "RateLimitResult",
    "get_rate_limiter",
    "rate_limited",
    "RATE_LIMIT_ENABLED",
]
