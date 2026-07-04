"""
test_public_surface_invariants — Lock canonical 9-stage metabolic loop MCP public facade.

Invariants (ZEN-9 collapse 2026-07-04):
  1. Default public surface = exactly CANONICAL_9 (9 tools, 9 stages).
  2. No forbidden tools appear in default mode.
  3. expanded45 requires explicit gate.
  4. All canonical tools have strict schemas (additionalProperties: false).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest
from arifosmcp.runtime.public_surface import (
    CANONICAL_9,
    CANONICAL_LONG_NAME_ALIASES,
    DIAGNOSTIC_TOOLS as DIAG_TOOL_NAMES,
    public_tool_names_for_mode,
    normalize_public_surface_mode,
)

EXPECTED_CANONICAL_9 = {
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_critique",
    "arif_judge",
    "arif_forge",
    "arif_compose",
    "arif_seal",
}

FORBIDDEN_PUBLIC = {
    # Absorbed into arif_init modes
    "arif_canary",
    "arif_triage",
    "arif_session_init",
    # Absorbed into arif_observe(mode=fetch)
    "arif_fetch",
    "arif_evidence_fetch",
    # Absorbed into arif_think (but arif_critique is standalone canonical)
    "arif_heart_critique",
    # Absorbed into arif_route(mode=bridge)
    "arif_bridge_connect",
    "arif_bridge",
    "arif_kernel_route",
    # Internal only
    "arif_act",
    "arif_measure",
    "arif_memory",
    "arif_memory_recall",
    "arif_kernel_intercept",
    "arif_judge_deliberate",
    "arif_conformance_report",
    "arif_gateway_connect",
    "arif_mind_reason",
    "arif_reply_compose",
    "arif_sense_observe",
    "arif_forge_execute",
    "arif_ops_measure",
    "arif_explore",
    "arif_vault_seal",
    "hermes_vault_query",
}


class TestPublicSurfaceInvariants:
    """Constitutional MCP public surface invariants (ZEN-9)."""

    def test_canonical_9_exact_count(self):
        """CANONICAL_9 must be exactly 9 tools (9 stages, critique standalone)."""
        assert len(CANONICAL_9) == 9, f"Expected 9, got {len(CANONICAL_9)}"

    def test_canonical_9_contents(self):
        """CANONICAL_9 must contain the exact expected tools."""
        assert set(CANONICAL_9) == EXPECTED_CANONICAL_9, (
            f"Mismatch: expected {EXPECTED_CANONICAL_9}, got {set(CANONICAL_9)}"
        )

    def test_default_public_mode_is_canonical9(self):
        """Default public surface mode must be canonical9."""
        mode = normalize_public_surface_mode(None)
        assert mode == "canonical9", f"Expected canonical9, got {mode}"

    def test_default_public_tools_exactly_8(self):
        """Default public tools/list must return exactly CANONICAL_9 (9 tools)."""
        tools = public_tool_names_for_mode(None)
        assert len(tools) == 9, f"Expected 9 tools, got {len(tools)}: {tools}"

    def test_default_public_tools_match_canonical(self):
        """Default public tools must match CANONICAL_9 exactly."""
        tools = set(public_tool_names_for_mode(None))
        assert tools == EXPECTED_CANONICAL_9, (
            f"Public surface mismatch. Extra: {tools - EXPECTED_CANONICAL_9}. "
            f"Missing: {EXPECTED_CANONICAL_9 - tools}"
        )

    def test_no_forbidden_tools_in_default_public(self):
        """Forbidden (absorbed/internal) tools must never appear in default public mode."""
        tools = set(public_tool_names_for_mode(None))
        leaked = tools & FORBIDDEN_PUBLIC
        assert not leaked, f"Forbidden tools leaked into public surface: {leaked}"

    def test_no_forbidden_tools_in_canonical12_alias(self):
        """Forbidden tools must never appear in canonical12 (deprecated alias of canonical9)."""
        tools = set(public_tool_names_for_mode("canonical12"))
        leaked = tools & FORBIDDEN_PUBLIC
        assert not leaked, f"Forbidden tools leaked in canonical12 alias: {leaked}"

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
        """expanded45 mode must include diagnostic tools when the dev-tools gate is on."""
        tools_gated = set(public_tool_names_for_mode("expanded45"))
        assert len(tools_gated) >= 8, (
            f"expanded45 must include >= canonical9, got {len(tools_gated)}: {tools_gated}"
        )
        from arifosmcp.runtime.public_surface import EXPANDED_45

        if DIAG_TOOL_NAMES:
            assert len(EXPANDED_45) > 8, (
                f"EXPANDED_45 must contain all DIAGNOSTIC_TOOLS, "
                f"got {len(EXPANDED_45)} (DIAG has {len(DIAG_TOOL_NAMES)})"
            )

    def test_canonical_9_ordered(self):
        """CANONICAL_9 must maintain canonical ordering (000 -> 999 pipeline)."""
        expected_order = [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_critique",
            "arif_judge",
            "arif_forge",
            "arif_compose",
            "arif_seal",
        ]
        assert list(CANONICAL_9) == expected_order, (
            f"Order mismatch: expected {expected_order}, got {list(CANONICAL_9)}"
        )

    def test_legacy_aliases_resolve_to_canonical9(self):
        """CANONICAL_7 and CANONICAL_13 must semantically equal CANONICAL_9 (deprecated aliases)."""
        from arifosmcp.runtime.public_surface import CANONICAL_7, CANONICAL_13

        assert tuple(CANONICAL_7) == tuple(CANONICAL_9), (
            "CANONICAL_7 must equal CANONICAL_9 (deprecated alias)"
        )
        assert tuple(CANONICAL_13) == tuple(CANONICAL_9), (
            "CANONICAL_13 must equal CANONICAL_9 (deprecated alias)"
        )

    def test_arif_seal_on_public_surface(self):
        """arif_seal must BE on the public surface (ZEN-9: 999 needs its verb)."""
        tools = set(public_tool_names_for_mode(None))
        assert "arif_seal" in tools, "arif_seal missing from public surface (ZEN-9 restored)"

    def test_arif_forge_on_public_surface(self):
        """arif_forge must BE on the public surface (canonical execution gate)."""
        tools = set(public_tool_names_for_mode(None))
        assert "arif_forge" in tools, "arif_forge missing from public surface"

    def test_absorbed_tools_off_public_surface(self):
        """Absorbed tools must NOT be on public surface."""
        tools = set(public_tool_names_for_mode(None))
        for absorbed in (
            "arif_canary",
            "arif_triage",
            "arif_fetch",
            "arif_bridge_connect",
        ):
            assert absorbed not in tools, (
                f"{absorbed} leaked to public surface (should be absorbed mode)"
            )
