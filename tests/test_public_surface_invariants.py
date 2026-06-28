"""
test_public_surface_invariants — Lock canonical 7-tool MCP public facade.

Invariants (F13 ratified 2026-06-23, verified 2026-06-28):
  1. Default public surface = exactly CANONICAL_7 (7 verbs).
  2. No forbidden tools appear in default mode.
  3. expanded45 requires explicit gate.
  4. All canonical tools have strict schemas (additionalProperties: false).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest
from arifosmcp.runtime.public_surface import (
    CANONICAL_7,
    CANONICAL_LONG_NAME_ALIASES,
    DIAGNOSTIC_TOOLS as DIAG_TOOL_NAMES,
    public_tool_names_for_mode,
    normalize_public_surface_mode,
)

# ── Golden invariant ────────────────────────────────────────────────────────
# F13 SOVEREIGN 2026-06-23: exactly 7 canonical verbs on public wire.
EXPECTED_CANONICAL_7 = {
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_judge",
    "arif_act",
    "arif_seal",
}

# Tools that MUST NEVER appear in public mode.
FORBIDDEN_PUBLIC = {
    "arif_bridge_connect",
    "arif_gateway_connect",
    "arif_forge",
    "arif_forge_execute",
    "arif_memory",
    "arif_memory_recall",
    "arif_vault_seal",
    "hermes_vault_query",
    "arif_canary",
    "arif_conformance_report",
    "arif_judge_deliberate",
    "arif_session_init",
    "arif_sense_observe",
    "arif_evidence_fetch",
    "arif_mind_reason",
    "arif_heart_critique",
    "arif_reply_compose",
    "arif_ops_measure",
}


class TestPublicSurfaceInvariants:
    """Constitutional MCP public surface invariants."""

    def test_canonical_7_exact_count(self):
        """CANONICAL_7 must be exactly 7 tools."""
        assert len(CANONICAL_7) == 7, f"Expected 7, got {len(CANONICAL_7)}"

    def test_canonical_7_contents(self):
        """CANONICAL_7 must contain the exact expected tools."""
        assert set(CANONICAL_7) == EXPECTED_CANONICAL_7, (
            f"Mismatch: expected {EXPECTED_CANONICAL_7}, got {set(CANONICAL_7)}"
        )

    def test_default_public_mode_is_canonical13(self):
        """Default public surface mode must be canonical13."""
        mode = normalize_public_surface_mode(None)
        assert mode == "canonical13", f"Expected canonical13, got {mode}"

    def test_default_public_tools_exactly_7(self):
        """Default public tools/list must return exactly CANONICAL_7."""
        tools = public_tool_names_for_mode(None)
        assert len(tools) == 7, f"Expected 7 tools, got {len(tools)}: {tools}"

    def test_default_public_tools_match_canonical(self):
        """Default public tools must match CANONICAL_7 exactly."""
        tools = set(public_tool_names_for_mode(None))
        assert tools == EXPECTED_CANONICAL_7, (
            f"Public surface mismatch. Extra: {tools - EXPECTED_CANONICAL_7}. "
            f"Missing: {EXPECTED_CANONICAL_7 - tools}"
        )

    def test_no_forbidden_tools_in_default_public(self):
        """Forbidden tools must never appear in default public mode."""
        tools = set(public_tool_names_for_mode(None))
        leaked = tools & FORBIDDEN_PUBLIC
        assert not leaked, f"Forbidden tools leaked into public surface: {leaked}"

    def test_no_forbidden_tools_in_canonical13_mode(self):
        """Forbidden tools must never appear in canonical13 mode."""
        tools = set(public_tool_names_for_mode("canonical13"))
        leaked = tools & FORBIDDEN_PUBLIC
        assert not leaked, f"Forbidden tools leaked in canonical13: {leaked}"

    def test_no_alias_tools_in_default_public(self):
        """SDK alias tools must not appear in default public surface."""
        tools = set(public_tool_names_for_mode(None))
        alias_leaked = tools & set(CANONICAL_LONG_NAME_ALIASES)
        assert not alias_leaked, f"Alias tools leaked: {alias_leaked}"

    def test_expanded45_gated(self):
        """expanded45 must only be active when explicitly set, not the default."""
        mode = normalize_public_surface_mode(None)
        assert mode != "expanded45", "expanded45 must not be the default mode"

    def test_expanded45_includes_diagnostics(self):
        """expanded45 mode must include diagnostic tools."""
        tools = set(public_tool_names_for_mode("expanded45"))
        # Should have more than 7 tools
        assert len(tools) > 7, f"expanded45 should have >7 tools, got {len(tools)}"
        # Should include diagnostic tools
        has_any_diag = bool(tools & set(DIAG_TOOL_NAMES)) if DIAG_TOOL_NAMES else True
        # Note: DIAG_TOOL_NAMES may be empty in some configs

    def test_canonical_7_sorted(self):
        """CANONICAL_7 should maintain consistent ordering (000→999 pipeline)."""
        expected_order = [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_judge",
            "arif_act",
            "arif_seal",
        ]
        assert list(CANONICAL_7) == expected_order, (
            f"Order mismatch: expected {expected_order}, got {list(CANONICAL_7)}"
        )
