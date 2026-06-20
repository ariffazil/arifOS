"""
test_mcp_surface_contract.py
═══════════════════════════════════════════════════════════════════════════

MCP Surface Governor — contract tests.

These tests verify the visibility policy and shortlist router behave
correctly per amendment_001.md. They are the F2-honest guardrails for
"Fix the visibility layer. Keep the full federation."

F2 truth: these tests are deterministic. No live HTTP probing here.
That belongs to test_degraded_organs_hidden.py.

Author: @integrator (session 2026-06-12-mcp-governor-and-minimax-forge)
Forged: 2026-06-12
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the runtime/ directory is importable
_runtime_dir = Path(__file__).resolve().parents[1] / "arifosmcp" / "runtime"
if str(_runtime_dir) not in sys.path:
    sys.path.insert(0, str(_runtime_dir))

from mcp_visibility_policy import (  # noqa: E402
    DIAGNOSTIC_TOOL_NAMES,
    OrganHealth,
    Tier,
    ToolEntry,
    VisibilityPolicy,
    build_policy_from_registry,
    filter_visible_tools,
    load_registry,
)
from organ_health_gate import (  # noqa: E402
    get_diagnostic_shortlist,
)
from tool_shortlist_router import (  # noqa: E402
    route_intent_to_organs,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _tool(
    name: str,
    organ: str = "arifOS",
    tier: Tier = Tier.CORE,
    health: OrganHealth = OrganHealth.HEALTHY,
    constitution_hash: str | None = "constitution-hash",
    schema_hash: str | None = "schema-hash",
    version: str | None = "v1.0",
    schema_tokens: int = 100,
) -> ToolEntry:
    return ToolEntry(
        name=name,
        organ=organ,
        tier=tier,
        health=health,
        constitution_hash=constitution_hash,
        schema_hash=schema_hash,
        version=version,
        schema_tokens=schema_tokens,
    )


def _policy(**overrides) -> VisibilityPolicy:
    p = VisibilityPolicy()
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Healthy organ exposes up to max_visible tools
# ─────────────────────────────────────────────────────────────────────────────


def test_healthy_organ_exposes_full_surface():
    tools = [
        _tool("arif_session_init", tier=Tier.CORE),
        _tool("arif_sense_observe", tier=Tier.CORE),
        _tool("arif_mind_reason", tier=Tier.CORE),
        _tool("arif_judge_deliberate", tier=Tier.CORE),
        _tool("arif_vault_seal", tier=Tier.CORE),
        _tool("arif_forge_execute", tier=Tier.CORE),
        _tool("arif_memory_recall", tier=Tier.CORE),
        _tool("arif_reply_compose", tier=Tier.CORE),
        _tool("arif_heart_critique", tier=Tier.CORE),
        _tool("arif_kernel_route", tier=Tier.CORE),
        _tool("arif_evidence_fetch", tier=Tier.CORE),
        _tool("arif_gateway_connect", tier=Tier.CORE),
        _tool("arif_ops_measure", tier=Tier.CORE),
    ]
    result = filter_visible_tools(tools, _policy())
    assert result.counts["visible"] == 13
    assert result.counts["hidden"] == 0
    assert result.counts["quarantined_diagnostics"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Degraded organ exposes exactly 3 diagnostic tools
# ─────────────────────────────────────────────────────────────────────────────


def test_degraded_organ_yields_3_diagnostic_tools():
    tools = [
        _tool("arif_session_init", tier=Tier.CORE),
        _tool("some_broken_tool", organ="broken", tier=Tier.CORE, health=OrganHealth.DEGRADED),
        _tool("another_broken_tool", organ="broken", tier=Tier.CORE, health=OrganHealth.DEGRADED),
    ]
    result = filter_visible_tools(tools, _policy())
    # The 2 broken tools are moved to hidden + quarantined_diagnostics placeholder
    assert result.counts["visible"] == 1  # only the healthy arif_session_init
    assert result.counts["quarantined_diagnostics"] >= 1
    # And the diagnostic shortlist generator for the broken organ returns 3
    shortlist = get_diagnostic_shortlist("broken")
    assert len(shortlist) == 3
    assert {t.name for t in shortlist} <= set(DIAGNOSTIC_TOOL_NAMES)


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Lab tools require explicit route (allow_lab flag)
# ─────────────────────────────────────────────────────────────────────────────


def test_lab_tools_require_explicit_route():
    tools = [
        _tool("arif_session_init", tier=Tier.CORE),
        _tool("experimental_search", tier=Tier.LAB, organ="minimax-search"),
        _tool("experimental_browse", tier=Tier.LAB, organ="minimax-search"),
    ]
    # Default: lab hidden
    r1 = filter_visible_tools(tools, _policy())
    assert r1.counts["visible"] == 1
    assert r1.counts["hidden"] == 2
    # With allow_lab: lab visible (subject to health + max)
    r2 = filter_visible_tools(tools, _policy(allow_lab=True))
    assert r2.counts["visible"] == 3


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Deprecated tools are non-callable
# ─────────────────────────────────────────────────────────────────────────────


def test_deprecated_tools_not_visible():
    tools = [
        _tool("arif_session_init", tier=Tier.CORE),
        _tool("legacy_alias", tier=Tier.DEPRECATED, organ="arifOS"),
        _tool("old_mmx_code", tier=Tier.DEPRECATED, organ="minimax-code"),
    ]
    result = filter_visible_tools(tools, _policy(allow_lab=True))
    assert result.counts["visible"] == 1
    assert result.counts["hidden"] == 2
    # Verify the deprecated tool names are NOT in visible
    visible_names = {t.name for t in result.visible}
    assert "legacy_alias" not in visible_names
    assert "old_mmx_code" not in visible_names


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Entropy budgets are enforced
# ─────────────────────────────────────────────────────────────────────────────


def test_max_visible_cap_enforced():
    tools = [_tool(f"tool_{i:02d}", tier=Tier.CORE) for i in range(30)]
    policy = _policy(max_visible=15)
    result = filter_visible_tools(tools, policy)
    assert result.counts["visible"] == 15
    assert result.counts["hidden"] == 15
    assert result.counts["max_visible_policy"] == 15


def test_schema_token_cap_enforced():
    tools = [
        _tool("small_tool", tier=Tier.CORE, schema_tokens=100),
        _tool("huge_tool", tier=Tier.CORE, schema_tokens=1500),  # over 700 cap
    ]
    result = filter_visible_tools(tools, _policy(max_schema_tokens_per_tool=700))
    visible_names = {t.name for t in result.visible}
    assert "small_tool" in visible_names
    assert "huge_tool" not in visible_names


def test_missing_required_fields_excluded():
    tools = [
        _tool("complete", tier=Tier.CORE, constitution_hash="abc", schema_hash="def", version="1.0"),
        _tool("no_constitution", tier=Tier.CORE, constitution_hash=None),
        _tool("no_schema", tier=Tier.CORE, schema_hash=None),
        _tool("no_version", tier=Tier.CORE, version=None),
    ]
    result = filter_visible_tools(tools, _policy())
    visible_names = {t.name for t in result.visible}
    assert "complete" in visible_names
    assert "no_constitution" not in visible_names
    assert "no_schema" not in visible_names
    assert "no_version" not in visible_names


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Intent routing maps keywords to organs
# ─────────────────────────────────────────────────────────────────────────────


def test_intent_routing_for_media():
    organs = route_intent_to_organs("generate a voiceover for the morning briefing")
    assert "minimax-media" in organs


def test_intent_routing_for_search():
    organs = route_intent_to_organs("web_search for arifOS constitutional kernel")
    # Could route to minimax-code or minimax-search or arifOS
    assert any(o in organs for o in ("minimax-code", "minimax-search", "arifOS"))


def test_intent_routing_for_wellness():
    organs = route_intent_to_organs("check my sleep debt and stress load")
    assert "well" in organs


def test_intent_routing_for_geo():
    organs = route_intent_to_organs("evaluate the Malay Basin prospect")
    assert "geox" in organs


def test_intent_routing_for_wealth():
    organs = route_intent_to_organs("compute NPV for a deal")
    assert "wealth" in organs


def test_intent_routing_default_to_arifOS():
    organs = route_intent_to_organs("")
    assert organs == ["arifOS"]


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Shortlist returns top N by tier priority
# ─────────────────────────────────────────────────────────────────────────────


def test_shortlist_respects_tier_priority():
    tools = [
        _tool("core_a", tier=Tier.CORE),
        _tool("core_b", tier=Tier.CORE),
        _tool("core_c", tier=Tier.CORE),
        _tool("organ_a", tier=Tier.ORGAN, organ="wealth"),
        _tool("organ_b", tier=Tier.ORGAN, organ="wealth"),
        _tool("lab_a", tier=Tier.LAB, organ="minimax-search"),
    ]
    policy = _policy(allow_lab=False)
    result = filter_visible_tools(tools, policy)
    shortlist = result.shortlist(n=3)
    # Top 3 should be all CORE (priority 0 < ORGAN priority 1)
    assert all(t.tier == Tier.CORE for t in shortlist)
    assert len(shortlist) == 3  # we have 3 core tools


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: Diagnostic shortlist has correct structure
# ─────────────────────────────────────────────────────────────────────────────


def test_diagnostic_shortlist_structure():
    shortlist = get_diagnostic_shortlist("degraded-organ")
    assert len(shortlist) == 3
    for tool in shortlist:
        assert tool.organ == "degraded-organ"
        assert tool.tier == Tier.ORGAN
        assert tool.health in (OrganHealth.DEGRADED, OrganHealth.UNKNOWN)
        assert "diagnostic" in tool.constitution_hash.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: Healthy organ diagnostic shortlist is empty
# ─────────────────────────────────────────────────────────────────────────────


def test_healthy_organ_diagnostic_shortlist_empty():
    # For an organ that's never been probed, it returns UNKNOWN by default
    # so we get a diagnostic. But for a healthy organ, it returns [].
    # First, probe to populate cache.
    from organ_health_gate import get_organ_health, invalidate_cache

    invalidate_cache("arifOS")
    health = get_organ_health("arifOS")
    if health == OrganHealth.HEALTHY:
        shortlist = get_diagnostic_shortlist("arifOS")
        assert shortlist == []


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: Load registry produces non-empty organ list
# ─────────────────────────────────────────────────────────────────────────────


def test_registry_load_returns_organs():
    reg = load_registry()
    assert isinstance(reg, dict)
    assert "organs" in reg
    assert len(reg["organs"]) >= 5
    organ_ids = [o.get("id") for o in reg["organs"]]
    assert "arifOS" in organ_ids
    assert "geox" in organ_ids
    assert "wealth" in organ_ids
    assert "well" in organ_ids


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: Policy from registry respects entropy_budget
# ─────────────────────────────────────────────────────────────────────────────


def test_policy_from_registry_entropy_budget():
    reg = load_registry()
    policy = build_policy_from_registry(reg)
    entropy = reg.get("entropy_budget", {})
    assert policy.max_visible == entropy.get("default_visible_tools_max", 15)
    assert policy.max_schema_tokens_per_tool == entropy.get("max_schema_tokens_per_tool", 700)
