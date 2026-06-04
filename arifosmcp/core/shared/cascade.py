"""
cascade.py — Thermodynamic Compute Tiering (Reusable Cascade Module)

Constitutional anchor: /root/arifOS/COMPUTE_TIERING.md
Floors enforced: F10 ELEGANCE, F13 SOVEREIGN, F1 AMANAH

This module provides a reusable 3-tier cascade pattern for any compute-bound
substrate (LLM, vector search, storage, external APIs).

Usage:
    from arifosmcp.core.shared.cascade import tiered_call, TierConfig, SovereigntyFloorBreach

    tiers = [
        TierConfig(name="minimax", call=call_minimax, timeout=2.0),
        TierConfig(name="ilmu", call=call_ilmu, timeout=50.0),
        TierConfig(name="ollama", call=call_ollama, timeout=120.0, sovereign=True),
    ]

    result = await tiered_call(tiers, request_payload)

All tiers are tried in order. If a tier fails, cascade falls through to next tier.
Tier 3 (sovereign=True) MUST succeed — failure raises SovereigntyFloorBreach (F13 violation).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Prometheus instrumentation (optional — only if prometheus_client installed)
try:
    from prometheus_client import Counter

    TIER_CALLS = Counter(
        "arifos_tier_calls_total",
        "Total number of tier calls",
        ["substrate", "tier", "provider"],
    )
    TIER_FAILURES = Counter(
        "arifos_tier_failures_total",
        "Total number of tier failures",
        ["substrate", "tier", "provider", "reason"],
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TierFailureReason(str, Enum):
    """Classification of tier failure reasons for observability."""

    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"  # Network error, 503, connection refused
    INVALID_RESPONSE = "invalid_response"  # Malformed JSON, unexpected schema
    UNKNOWN = "unknown"  # Catch-all for unexpected errors


@dataclass
class TierConfig:
    """
    Configuration for a single tier in the cascade.

    Args:
        name: Human-readable tier name (e.g., "minimax", "ilmu", "ollama")
        call: Async callable that performs the tier operation.
              Signature: async def call(request: Any) -> Any
        timeout: Max seconds to wait for this tier before falling through
        sovereign: If True, this is Tier 3 (sovereignty floor). Failure here
                   raises SovereigntyFloorBreach exception (F13 violation).
        substrate: Optional substrate name for metrics (e.g., "llm", "vector")
    """

    name: str
    call: Callable[[Any], Any]  # async callable
    timeout: float
    sovereign: bool = False
    substrate: str = "unknown"


class SovereigntyFloorBreach(Exception):
    """
    Raised when Tier 3 (sovereign tier) fails.

    This is a CONSTITUTIONAL VIOLATION (F13 SOVEREIGN).
    System cannot degrade further. Human escalation required.
    """

    pass


async def tiered_call(
    tiers: list[TierConfig],
    request: Any,
    on_fallback: Callable[[int, str, Exception], None] | None = None,
) -> Any:
    """
    Execute a tiered cascade call across compute substrates.

    Tiers are tried in order. If a tier fails (timeout, unavailable, invalid response),
    cascade falls through to the next tier. The final tier (sovereign=True) MUST succeed.

    Args:
        tiers: List of TierConfig objects (ordered by priority: fastest → most reliable → sovereign)
        request: Request payload to pass to each tier's call function
        on_fallback: Optional callback invoked on tier failure. Signature:
                     (tier_index: int, tier_name: str, exception: Exception) -> None

    Returns:
        Result from the first tier that succeeds

    Raises:
        SovereigntyFloorBreach: If the sovereign tier (tier 3) fails. This is F13 violation.
        ValueError: If no tiers provided, or no sovereign tier defined, or multiple sovereign tiers

    Example:
        tiers = [
            TierConfig(name="fast", call=call_fast, timeout=2.0),
            TierConfig(name="reliable", call=call_reliable, timeout=50.0),
            TierConfig(name="local", call=call_local, timeout=120.0, sovereign=True),
        ]
        result = await tiered_call(tiers, my_request)
    """

    # Validation: Ensure exactly one sovereign tier exists (Tier 3)
    if not tiers:
        raise ValueError("No tiers provided. Cascade requires at least 1 tier.")

    sovereign_count = sum(1 for t in tiers if t.sovereign)
    if sovereign_count == 0:
        raise ValueError(
            "No sovereign tier defined. F13 SOVEREIGN requires exactly one tier with sovereign=True."
        )
    if sovereign_count > 1:
        raise ValueError(
            f"Multiple sovereign tiers defined ({sovereign_count}). "
            "F13 SOVEREIGN requires exactly ONE sovereignty floor."
        )

    # Iterate through tiers
    for idx, tier in enumerate(tiers):
        tier_num = idx + 1
        logger.debug(
            f"[Cascade] Attempting Tier {tier_num}/{len(tiers)}: {tier.name} "
            f"(timeout={tier.timeout}s, sovereign={tier.sovereign})"
        )

        # Instrument metrics (if prometheus_client available)
        if METRICS_AVAILABLE:
            TIER_CALLS.labels(
                substrate=tier.substrate, tier=f"tier{tier_num}", provider=tier.name
            ).inc()

        try:
            # Execute tier call with timeout
            result = await asyncio.wait_for(tier.call(request), timeout=tier.timeout)

            logger.info(
                f"[Cascade] Tier {tier_num} ({tier.name}) succeeded in <{tier.timeout}s"
            )
            return result

        except TimeoutError as e:
            reason = TierFailureReason.TIMEOUT
            logger.warning(
                f"[Cascade] Tier {tier_num} ({tier.name}) timeout after {tier.timeout}s"
            )

            # Instrument failure
            if METRICS_AVAILABLE:
                TIER_FAILURES.labels(
                    substrate=tier.substrate,
                    tier=f"tier{tier_num}",
                    provider=tier.name,
                    reason=reason,
                ).inc()

            # If this is the sovereign tier, CANNOT fall through — raise F13 violation
            if tier.sovereign:
                raise SovereigntyFloorBreach(
                    f"[F13 SOVEREIGN VIOLATION] Tier {tier_num} ({tier.name}) is the sovereignty floor "
                    f"and MUST succeed. Timeout after {tier.timeout}s is a constitutional breach. "
                    "System cannot degrade further. Human escalation required."
                ) from e

            # Otherwise, invoke fallback callback and continue to next tier
            if on_fallback:
                on_fallback(idx, tier.name, e)

        except (ConnectionError, OSError) as e:
            # Network-level failure (connection refused, DNS failure, etc.)
            reason = TierFailureReason.UNAVAILABLE
            logger.warning(
                f"[Cascade] Tier {tier_num} ({tier.name}) unavailable: {type(e).__name__}: {e}"
            )

            if METRICS_AVAILABLE:
                TIER_FAILURES.labels(
                    substrate=tier.substrate,
                    tier=f"tier{tier_num}",
                    provider=tier.name,
                    reason=reason,
                ).inc()

            if tier.sovereign:
                raise SovereigntyFloorBreach(
                    f"[F13 SOVEREIGN VIOLATION] Tier {tier_num} ({tier.name}) is the sovereignty floor "
                    f"and MUST succeed. Unavailable ({type(e).__name__}: {e}) is a constitutional breach. "
                    "System cannot degrade further. Human escalation required."
                ) from e

            if on_fallback:
                on_fallback(idx, tier.name, e)

        except Exception as e:
            # Catch-all for unexpected errors (invalid response, schema mismatch, etc.)
            reason = (
                TierFailureReason.INVALID_RESPONSE
                if "json" in str(e).lower() or "schema" in str(e).lower()
                else TierFailureReason.UNKNOWN
            )
            logger.error(
                f"[Cascade] Tier {tier_num} ({tier.name}) failed: {type(e).__name__}: {e}"
            )

            if METRICS_AVAILABLE:
                TIER_FAILURES.labels(
                    substrate=tier.substrate,
                    tier=f"tier{tier_num}",
                    provider=tier.name,
                    reason=reason,
                ).inc()

            if tier.sovereign:
                raise SovereigntyFloorBreach(
                    f"[F13 SOVEREIGN VIOLATION] Tier {tier_num} ({tier.name}) is the sovereignty floor "
                    f"and MUST succeed. Failure ({type(e).__name__}: {e}) is a constitutional breach. "
                    "System cannot degrade further. Human escalation required."
                ) from e

            if on_fallback:
                on_fallback(idx, tier.name, e)

    # Should never reach here (sovereign tier should have raised SovereigntyFloorBreach)
    raise RuntimeError(
        "[Cascade Logic Error] All tiers exhausted without sovereign tier raising exception. "
        "This indicates a bug in cascade.py validation logic."
    )
