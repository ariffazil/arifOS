"""
arifosmcp/federation/constitution_aggregator.py
══════════════════════════════════════════════════════════════════════════════
Aggregate per-organ constitutions into a single FederationConstitution.

The FederationConstitution is the F2-auditable, hashable artifact that proves
the AGI substrate is bound to a single observable constitution. Every other
organ health JSON, every /federation/constitution REST response, and every
arif_kernel_route(mode="federation_status") call returns the same
FederationConstitution hash for a given state.

This is what closes the "we have 6 separate organs" → "we have 1 federation
with a constitution" gap.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from arifosmcp.federation.organ_constitution import (
    OrganConstitution,
    Tier,
    list_known_organs,
)
from arifosmcp.federation.promotion_gates import (
    aggregate_tier,
    assess_organ,
)

logger = logging.getLogger("arifosmcp.federation.aggregator")


class OrganConstitutionWithTier(OrganConstitution):
    """Organ constitution + computed tier from live attestation.

    The base OrganConstitution.tier defaults to YELLOW (F7 HUMILITY).
    This subclass overrides it with the live-computed tier.
    """

    model_config = ConfigDict(extra="forbid")

    live_health: dict[str, Any] = Field(default_factory=dict)
    live_tool_count: int = 0
    promotion_conditions: list[str] = Field(default_factory=list)


class FederationConstitution(BaseModel):
    """The single hashable, F2-auditable aggregate of all organ constitutions.

    This is what an external auditor hashes to verify federation integrity.
    If federation_constitution_hash changes, the federation constitution
    has changed. If it doesn't change, the federation is stable.
    """

    model_config = ConfigDict(extra="forbid")

    federation_id: str = "arifOS_federation"
    version: str  # ISO date stamp
    as_of: datetime

    # Per-organ
    organs: dict[str, OrganConstitutionWithTier] = Field(default_factory=dict)

    # Aggregate
    aggregate_tier: Tier = "BLACK"
    total_organs: int = 0
    green_organs: int = 0
    yellow_organs: int = 0
    red_organs: int = 0
    black_organs: int = 0

    # Integrity anchor
    federation_constitution_hash: str  # sha256 of the canonical JSON

    # Pending sovereign actions (promote/demote)
    pending_promotions: list[str] = Field(default_factory=list)
    pending_demotions: list[str] = Field(default_factory=list)

    # F1 AMANAH receipt
    note: str = (
        "Hashable, F2-auditable federation constitution. "
        "Stable hash = stable constitution. hash(aggregate) != hash(prev) "
        "means at least one organ's tier or constitution changed."
    )


def _organ_health_probe(organ_id: str) -> tuple[dict[str, Any], int]:
    """Call the existing arifOS organ attestation bridge to get live health
    + tool count for one organ. Pure read-only, no mutation.

    Returns (health_dict, tool_count). If the organ is unreachable, returns
    ({}, 0).
    """
    try:
        from arifosmcp.runtime.organ_attestation import (
            _ORGAN_CONFIG,
            _call_organ_health,
            _list_organ_tools,
        )

        cfg = _ORGAN_CONFIG.get(organ_id)
        if cfg is None:
            return {}, 0

        import asyncio

        async def _gather():
            return await asyncio.gather(
                _call_organ_health(organ_id),
                _list_organ_tools(organ_id),
            )

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Sync fallback — call the synchronous parts
                health = _call_organ_health_sync(organ_id)
                tools = _list_organ_tools_sync(organ_id)
            else:
                health, tools = loop.run_until_complete(_gather())
        except RuntimeError:
            health, tools = asyncio.run(_gather())

        return health or {}, len(tools or [])
    except Exception as e:
        logger.debug(f"Health probe failed for {organ_id}: {e}")
        return {}, 0


def _call_organ_health_sync(organ_id: str) -> dict[str, Any]:
    """Synchronous fallback — call the bridge module's function directly."""
    try:
        import inspect

        from arifosmcp.runtime.organ_attestation import _ORGAN_CONFIG

        cfg = _ORGAN_CONFIG[organ_id]
        mod = __import__(cfg["health_module"], fromlist=[cfg["health_fn"]])
        fn = getattr(mod, cfg["health_fn"])
        if inspect.iscoroutinefunction(fn):
            import asyncio

            return asyncio.run(fn())
        return fn()
    except Exception as e:
        logger.debug(f"Sync health probe failed for {organ_id}: {e}")
        return {}


def _list_organ_tools_sync(organ_id: str) -> list[dict[str, Any]]:
    """Synchronous fallback — list the organ's tool surface."""
    try:
        import inspect

        from arifosmcp.runtime.organ_attestation import _ORGAN_CONFIG

        cfg = _ORGAN_CONFIG[organ_id]
        list_fn = cfg.get("list_fn")
        if not list_fn:
            return []
        mod = __import__(cfg["health_module"], fromlist=[list_fn])
        fn = getattr(mod, list_fn)
        if inspect.iscoroutinefunction(fn):
            import asyncio

            return asyncio.run(fn())
        return fn()
    except Exception as e:
        logger.debug(f"Sync tool list failed for {organ_id}: {e}")
        return []


def aggregate(health_provider: Any | None = None) -> FederationConstitution:
    """Build the FederationConstitution by aggregating all known organs.

    If health_provider is None, uses the live arifOS bridges.
    If health_provider is a callable (organ_id) -> (health_dict, tool_count),
    uses that instead (for tests).
    """
    organs_with_tier: dict[str, OrganConstitutionWithTier] = {}
    tiers: list[Tier] = []
    pending_promotions: list[str] = []
    pending_demotions: list[str] = []

    known = list_known_organs()
    for organ_id in known:
        # Get health
        if health_provider is not None:
            health, tool_count = health_provider(organ_id)
        else:
            health, tool_count = _organ_health_probe(organ_id)

        # Load constitution
        constitution, tier, conditions = assess_organ(organ_id, health, tool_count)
        tiers.append(tier)

        # Build per-organ artifact
        oc = OrganConstitutionWithTier(
            **constitution.model_dump(),
            live_health=health,
            live_tool_count=tool_count,
            promotion_conditions=conditions,
        )
        oc.tier = tier
        organs_with_tier[organ_id] = oc

        # Check for promotion/demotion vs current tier
        if constitution.tier != tier:
            if _tier_rank(tier) > _tier_rank(constitution.tier):
                pending_promotions.append(
                    f"{organ_id}: {constitution.tier} → {tier} (auto-detected, awaiting sovereign ack)"
                )
            else:
                pending_demotions.append(
                    f"{organ_id}: {constitution.tier} → {tier} (auto-detected, awaiting sovereign ack)"
                )

    # Counts
    counts = {"GREEN": 0, "YELLOW": 0, "RED": 0, "BLACK": 0}
    for t in tiers:
        counts[t] += 1

    # Build aggregate
    version = datetime.now(UTC).strftime("%Y.%m.%d")
    as_of = datetime.now(UTC)
    aggregate_t = aggregate_tier(tiers)

    # Federation hash — canonical JSON of (organs sorted by id, all fields)
    canonical_payload = {
        "federation_id": "arifOS_federation",
        "version": version,
        "as_of": as_of.isoformat(),
        "organs": {oid: oc.model_dump(mode="json") for oid, oc in sorted(organs_with_tier.items())},
        "aggregate_tier": aggregate_t,
    }
    canonical_text = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"))
    federation_hash = f"sha256:{hashlib.sha256(canonical_text.encode()).hexdigest()}"

    return FederationConstitution(
        federation_id="arifOS_federation",
        version=version,
        as_of=as_of,
        organs=organs_with_tier,
        aggregate_tier=aggregate_t,
        total_organs=len(known),
        green_organs=counts["GREEN"],
        yellow_organs=counts["YELLOW"],
        red_organs=counts["RED"],
        black_organs=counts["BLACK"],
        federation_constitution_hash=federation_hash,
        pending_promotions=pending_promotions,
        pending_demotions=pending_demotions,
    )


def _tier_rank(tier: Tier) -> int:
    """Higher rank = better tier. GREEN=3, YELLOW=2, RED=1, BLACK=0."""
    return {"GREEN": 3, "YELLOW": 2, "RED": 1, "BLACK": 0}[tier]


# Module-level cached aggregate (rebuilt per call — no global state mutation)
_CACHED_AGGREGATE: FederationConstitution | None = None
_CACHED_AT: datetime | None = None
_CACHE_TTL_SECONDS = 30  # F4 CLARITY: don't probe every call


def get_federation_constitution(
    health_provider: Any | None = None,
    force_refresh: bool = False,
) -> FederationConstitution:
    """Cached aggregate accessor. TTL = 30 seconds by default.

    For F2 truth, the cached aggregate is rebuilt (not the previous one) when
    the TTL expires. Pass force_refresh=True to bypass the cache.
    """
    global _CACHED_AGGREGATE, _CACHED_AT

    now = datetime.now(UTC)
    if (
        force_refresh
        or _CACHED_AGGREGATE is None
        or _CACHED_AT is None
        or (now - _CACHED_AT).total_seconds() > _CACHE_TTL_SECONDS
    ):
        _CACHED_AGGREGATE = aggregate(health_provider=health_provider)
        _CACHED_AT = now

    return _CACHED_AGGREGATE


def as_dict(fc: FederationConstitution) -> dict[str, Any]:
    """JSON-serializable dict for REST responses and MCP resources."""
    return fc.model_dump(mode="json")
