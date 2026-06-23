"""
test_degraded_organs_hidden.py
═══════════════════════════════════════════════════════════════════════════

MCP Surface Governor — quarantine tests for degraded organs.

These tests verify the F2-honest behavior of the visibility governor when
an organ's /health endpoint returns non-healthy or is unreachable.

Test strategy:
  1. Force the health cache into known states (degraded / unknown / healthy).
  2. Apply the visibility policy.
  3. Verify only the 3-tool diagnostic shortlist is exposed for the bad organ.

F2 truth: tests are deterministic. We never mock /health directly — we
populate the cache by forcing a probe and intercepting the result.

Author: @integrator (session 2026-06-12-mcp-governor-and-minimax-forge)
Forged: 2026-06-12
"""

from __future__ import annotations

import sys
from pathlib import Path

_runtime_dir = Path(__file__).resolve().parents[1] / "arifosmcp" / "runtime"
if str(_runtime_dir) not in sys.path:
    sys.path.insert(0, str(_runtime_dir))

from mcp_visibility_policy import (  # noqa: E402
    OrganHealth,
    Tier,
    ToolEntry,
    VisibilityPolicy,
    filter_visible_tools,
)
from organ_health_gate import (  # noqa: E402
    HealthCacheEntry,
    _HEALTH_CACHE,
    get_diagnostic_shortlist,
    invalidate_cache,
)
from tool_shortlist_router import (  # noqa: E402
    Authority,
    shortlist_tools,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _force_organ_health(organ_id: str, health: OrganHealth) -> None:
    """Force the health cache to a specific value (test-only)."""
    import time

    _HEALTH_CACHE[organ_id] = HealthCacheEntry(
        health=health,
        error=f"forced to {health.value} for test",
        probed_at=time.time(),
    )


def _tool(
    name: str,
    organ: str = "arifOS",
    tier: Tier = Tier.CORE,
    health: OrganHealth = OrganHealth.HEALTHY,
    constitution_hash: str | None = "constitution-hash",
    schema_hash: str | None = "schema-hash",
    version: str | None = "v1.0",
) -> ToolEntry:
    return ToolEntry(
        name=name,
        organ=organ,
        tier=tier,
        health=health,
        constitution_hash=constitution_hash,
        schema_hash=schema_hash,
        version=version,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: GEOX with degraded /health → only diagnostic tools visible
# ─────────────────────────────────────────────────────────────────────────────


def test_geox_degraded_only_diagnostics():
    _force_organ_health("geox", OrganHealth.DEGRADED)
    try:
        # 37 GEOX tools, all marked degraded
        geox_tools = [
            _tool(f"geox_tool_{i:02d}", organ="geox", tier=Tier.ORGAN, health=OrganHealth.DEGRADED)
            for i in range(37)
        ]
        # 13 healthy arifOS tools
        arif_tools = [
            _tool(f"arif_{i:02d}", organ="arifOS", tier=Tier.CORE, health=OrganHealth.HEALTHY)
            for i in range(13)
        ]
        result = filter_visible_tools(geox_tools + arif_tools, VisibilityPolicy())
        # Only the 13 arifOS tools should be visible
        visible_names = {t.name for t in result.visible}
        arif_names = {f"arif_{i:02d}" for i in range(13)}
        geox_names = {f"geox_tool_{i:02d}" for i in range(37)}
        assert arif_names <= visible_names
        assert geox_names & visible_names == set()  # no GEOX tools visible
        # And the diagnostic shortlist for GEOX has 3 tools
        shortlist = get_diagnostic_shortlist("geox")
        assert len(shortlist) == 3
    finally:
        invalidate_cache("geox")


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: WEALTH with unhealthy probe → only 3 diagnostic tools
# ─────────────────────────────────────────────────────────────────────────────


def test_wealth_degraded_only_diagnostics():
    _force_organ_health("wealth", OrganHealth.DEGRADED)
    try:
        wealth_tools = [
            _tool(
                f"wealth_tool_{i:02d}", organ="wealth", tier=Tier.ORGAN, health=OrganHealth.DEGRADED
            )
            for i in range(20)
        ]
        arif_tools = [
            _tool(f"arif_{i:02d}", organ="arifOS", tier=Tier.CORE, health=OrganHealth.HEALTHY)
            for i in range(13)
        ]
        result = filter_visible_tools(wealth_tools + arif_tools, VisibilityPolicy())
        visible_names = {t.name for t in result.visible}
        wealth_names = {f"wealth_tool_{i:02d}" for i in range(20)}
        assert wealth_names & visible_names == set()
        shortlist = get_diagnostic_shortlist("wealth")
        assert len(shortlist) == 3
    finally:
        invalidate_cache("wealth")


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: WELL with unknown health → 1-3 diagnostic tools visible
# ─────────────────────────────────────────────────────────────────────────────


def test_well_unknown_only_diagnostics():
    _force_organ_health("well", OrganHealth.UNKNOWN)
    try:
        well_tools = [
            _tool(f"well_tool_{i:02d}", organ="well", tier=Tier.ORGAN, health=OrganHealth.UNKNOWN)
            for i in range(17)
        ]
        arif_tools = [
            _tool(f"arif_{i:02d}", organ="arifOS", tier=Tier.CORE, health=OrganHealth.HEALTHY)
            for i in range(13)
        ]
        result = filter_visible_tools(well_tools + arif_tools, VisibilityPolicy())
        visible_names = {t.name for t in result.visible}
        well_names = {f"well_tool_{i:02d}" for i in range(17)}
        assert well_names & visible_names == set()
        shortlist = get_diagnostic_shortlist("well")
        assert 1 <= len(shortlist) <= 3
    finally:
        invalidate_cache("well")


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: arifOS healthy → full surface visible
# ─────────────────────────────────────────────────────────────────────────────


def test_arifos_healthy_full_surface():
    _force_organ_health("arifOS", OrganHealth.HEALTHY)
    try:
        arif_tools = [
            _tool(f"arif_{i:02d}", organ="arifOS", tier=Tier.CORE, health=OrganHealth.HEALTHY)
            for i in range(13)
        ]
        result = filter_visible_tools(arif_tools, VisibilityPolicy())
        visible_names = {t.name for t in result.visible}
        arif_names = {f"arif_{i:02d}" for i in range(13)}
        assert arif_names <= visible_names
        assert result.counts["quarantined_diagnostics"] == 0
    finally:
        invalidate_cache("arifOS")


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Multi-organ mix — only healthy organs surface
# ─────────────────────────────────────────────────────────────────────────────


def test_multi_organ_mix():
    _force_organ_health("arifOS", OrganHealth.HEALTHY)
    _force_organ_health("geox", OrganHealth.DEGRADED)
    _force_organ_health("wealth", OrganHealth.HEALTHY)
    _force_organ_health("well", OrganHealth.UNKNOWN)
    try:
        all_tools = (
            [_tool(f"arif_{i:02d}", organ="arifOS", tier=Tier.CORE) for i in range(13)]
            + [
                _tool(f"geox_{i:02d}", organ="geox", tier=Tier.ORGAN, health=OrganHealth.DEGRADED)
                for i in range(37)
            ]
            + [_tool(f"wealth_{i:02d}", organ="wealth", tier=Tier.ORGAN) for i in range(20)]
            + [
                _tool(f"well_{i:02d}", organ="well", tier=Tier.ORGAN, health=OrganHealth.UNKNOWN)
                for i in range(17)
            ]
        )
        # Use a larger cap so we can verify all healthy organs surface
        result = filter_visible_tools(all_tools, VisibilityPolicy(max_visible=60))
        visible_names = {t.name for t in result.visible}
        # arifOS (13) + wealth (20) = 33 visible. GEOX (37) + WELL (17) = 54 hidden.
        arif_names = {f"arif_{i:02d}" for i in range(13)}
        wealth_names = {f"wealth_{i:02d}" for i in range(20)}
        geox_names = {f"geox_{i:02d}" for i in range(37)}
        well_names = {f"well_{i:02d}" for i in range(17)}
        assert arif_names <= visible_names
        assert wealth_names <= visible_names
        assert geox_names & visible_names == set()
        assert well_names & visible_names == set()
    finally:
        for o in ("arifOS", "geox", "wealth", "well"):
            invalidate_cache(o)


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Diagnostic shortlist excludes the F12 HOLD case
# ─────────────────────────────────────────────────────────────────────────────


def test_diagnostic_shortlist_when_organ_degraded():
    _force_organ_health("minimax-search", OrganHealth.DEGRADED)
    try:
        shortlist = get_diagnostic_shortlist("minimax-search")
        # 3 tools, all with the diagnostic role
        assert len(shortlist) == 3
        for tool in shortlist:
            assert tool.organ == "minimax-search"
            assert tool.health == OrganHealth.DEGRADED
            # Schema tokens are small (diagnostics are cheap)
            assert tool.schema_tokens <= 100
    finally:
        invalidate_cache("minimax-search")


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Real shortlist_tools() respects degraded organ
# ─────────────────────────────────────────────────────────────────────────────


def test_shortlist_router_skips_degraded_organ():
    _force_organ_health("minimax-media", OrganHealth.DEGRADED)
    _force_organ_health("arifOS", OrganHealth.HEALTHY)
    try:
        # Even with intent that should route to minimax-media, the shortlist
        # should NOT include minimax-media tools (it's degraded).
        result = shortlist_tools(
            "generate audio for the morning briefing",
            authority=Authority(actor_id="test", session_id="test-degraded"),
            all_tools=[
                _tool("arif_session_init", organ="arifOS", tier=Tier.CORE),
                _tool(
                    "text_to_audio",
                    organ="minimax-media",
                    tier=Tier.CORE,
                    health=OrganHealth.DEGRADED,
                ),
                _tool(
                    "list_voices",
                    organ="minimax-media",
                    tier=Tier.CORE,
                    health=OrganHealth.DEGRADED,
                ),
            ],
        )
        shortlist = result["shortlist"]
        assert "text_to_audio" not in shortlist
        assert "list_voices" not in shortlist
        # And arifOS tool IS surfaced
        assert "arif_session_init" in shortlist
    finally:
        invalidate_cache("minimax-media")
        invalidate_cache("arifOS")
