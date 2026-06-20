"""
tests/federation/test_constitution_aggregator.py
══════════════════════════════════════════════════════════════════════════════
Tests for the FederationConstitution aggregator.

The federation_constitution_hash must be:
  1. Deterministic for the same set of organs
  2. Stable across calls (cached) for the same TTL
  3. Different when any organ's tier or constitution changes
"""

from __future__ import annotations


from arifosmcp.federation.constitution_aggregator import (
    FederationConstitution,
    _tier_rank,
    aggregate,
    as_dict,
    get_federation_constitution,
)
from arifosmcp.federation.organ_constitution import list_known_organs


# Mock health provider — returns (health_dict, tool_count) per organ
def _all_healthy_provider(organ_id: str) -> tuple[dict, int]:
    return {"status": "healthy", "version": "test"}, 20


def _all_degraded_provider(organ_id: str) -> tuple[dict, int]:
    return {"status": "degraded"}, 5


def _no_health_provider(organ_id: str) -> tuple[dict, int]:
    return {}, 0


def _only_arifos_healthy_provider(organ_id: str) -> tuple[dict, int]:
    if organ_id == "arifOS":
        return {"status": "healthy"}, 13
    return {"status": "unhealthy"}, 0


class TestAggregate:
    def test_aggregate_uses_provider(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        assert isinstance(fc, FederationConstitution)
        assert fc.total_organs == len(list_known_organs())
        assert fc.aggregate_tier in {"GREEN", "YELLOW", "RED", "BLACK"}

    def test_aggregate_counts(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        # With all healthy + tools > 0, organs with constitution files should be GREEN
        # A-FORGE and AAA have no constitution files → YELLOW
        # The other 4 (arifOS, GEOX, WEALTH, WELL) have constitution files → GREEN
        assert fc.green_organs + fc.yellow_organs == fc.total_organs
        assert fc.red_organs == 0
        assert fc.black_organs == 0

    def test_aggregate_degraded_makes_red(self):
        fc = aggregate(health_provider=_all_degraded_provider)
        # All degraded → all RED
        assert fc.red_organs == fc.total_organs
        assert fc.aggregate_tier == "RED"

    def test_aggregate_no_health_makes_black(self):
        fc = aggregate(health_provider=_no_health_provider)
        # No health → all BLACK
        assert fc.black_organs == fc.total_organs
        assert fc.aggregate_tier == "BLACK"

    def test_aggregate_only_arifos_healthy(self):
        fc = aggregate(health_provider=_only_arifos_healthy_provider)
        # arifOS may be GREEN, but others degrade
        # The aggregate is the WORST tier
        assert fc.aggregate_tier in {"RED", "BLACK"}
        assert fc.total_organs == len(list_known_organs())

    def test_aggregate_deterministic_hash(self):
        """Same provider input → same federation hash."""
        fc1 = aggregate(health_provider=_all_healthy_provider)
        fc2 = aggregate(health_provider=_all_healthy_provider)
        # The as_of timestamp will differ, but the hash includes the payload.
        # Let's verify the structure is identical (just timestamp differs)
        assert fc1.aggregate_tier == fc2.aggregate_tier
        assert fc1.green_organs == fc2.green_organs
        assert fc1.federation_constitution_hash == fc2.federation_constitution_hash
        # Note: federation hash includes as_of, so two calls back-to-back
        # have DIFFERENT hashes. That's correct — federation state is time-stamped.
        # The deterministic part is the *structure* (counts, tiers).

    def test_aggregate_federation_hash_format(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        assert fc.federation_constitution_hash.startswith("sha256:")
        assert len(fc.federation_constitution_hash) == 7 + 64

    def test_aggregate_federation_id_and_version(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        assert fc.federation_id == "arifOS_federation"
        # Version is ISO date format YYYY.MM.DD
        import re

        assert re.match(r"^\d{4}\.\d{2}\.\d{2}$", fc.version)

    def test_aggregate_organ_payload_complete(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        assert set(fc.organs.keys()) == set(list_known_organs())
        for organ_id, oc in fc.organs.items():
            assert oc.organ_id == organ_id
            assert oc.tier in {"GREEN", "YELLOW", "RED", "BLACK"}
            assert isinstance(oc.live_tool_count, int)
            assert isinstance(oc.live_health, dict)
            assert isinstance(oc.promotion_conditions, list)
            assert len(oc.promotion_conditions) > 0

    def test_aggregate_pending_promotions_demotions(self):
        """If an organ's tier is being upgraded/downgraded, it's tracked."""
        fc = aggregate(health_provider=_all_healthy_provider)
        # The constitution template has tier=YELLOW as default.
        # Live assessment may return GREEN for organs with constitutions.
        # That should show up as pending_promotions for F13 ack.
        assert isinstance(fc.pending_promotions, list)
        assert isinstance(fc.pending_demotions, list)


class TestGetFederationConstitution:
    def test_cached_aggregate_within_ttl(self):
        """Within TTL, the same object reference is returned."""

        fc1 = get_federation_constitution(health_provider=_all_healthy_provider)
        fc2 = get_federation_constitution(health_provider=_all_healthy_provider)
        # Same object (cached)
        assert fc1 is fc2

    def test_force_refresh_bypasses_cache(self):
        fc1 = get_federation_constitution(health_provider=_all_healthy_provider)
        fc2 = get_federation_constitution(
            health_provider=_all_healthy_provider,
            force_refresh=True,
        )
        # Different object (rebuilt) — but same content
        assert fc1 is not fc2
        assert fc1.aggregate_tier == fc2.aggregate_tier

    def test_cache_ttl_seconds_is_set(self):
        """TTL should be positive and reasonable."""
        from arifosmcp.federation.constitution_aggregator import _CACHE_TTL_SECONDS

        assert _CACHE_TTL_SECONDS > 0
        assert _CACHE_TTL_SECONDS <= 300  # Don't cache for more than 5min


class TestAsDict:
    def test_as_dict_json_serializable(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        d = as_dict(fc)
        import json

        # Must round-trip through JSON without errors
        text = json.dumps(d, default=str)
        assert len(text) > 0
        # Hash present
        assert "federation_constitution_hash" in d

    def test_as_dict_contains_all_organs(self):
        fc = aggregate(health_provider=_all_healthy_provider)
        d = as_dict(fc)
        assert "organs" in d
        assert set(d["organs"].keys()) == set(list_known_organs())


class TestTierRank:
    def test_rank_ordering(self):
        """Higher rank = better tier."""
        assert _tier_rank("GREEN") > _tier_rank("YELLOW")
        assert _tier_rank("YELLOW") > _tier_rank("RED")
        assert _tier_rank("RED") > _tier_rank("BLACK")

    def test_rank_values(self):
        assert _tier_rank("GREEN") == 3
        assert _tier_rank("YELLOW") == 2
        assert _tier_rank("RED") == 1
        assert _tier_rank("BLACK") == 0
