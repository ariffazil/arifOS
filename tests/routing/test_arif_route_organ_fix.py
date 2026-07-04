"""
test_arif_route_organ_fix.py — Regression tests for G14 routing fix (2026-07-04).

The directive: "WELL organ health" and "GEOX organ earth/geoscience evidence"
were being routed to arifOS instead of their organs because the kernel guard
contained the greedy patterns "organ health" and "organ attestation".

This test verifies that:
  1. Organ-qualified phrases route to the named organ.
  2. The original kernel-guard cases (unqualified MCP/constitutional queries)
     still route to arifOS.
  3. The YAML keyword map produces the longest-keyword match.
  4. A-FORGE organ-qualified intents route to A-FORGE.

Run with:
  cd /root/arifOS && python -m pytest tests/routing/test_arif_route_organ_fix.py -v
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Ensure arifosmcp is importable
ARIFOS_ROOT = Path("/root/arifOS")
if str(ARIFOS_ROOT) not in sys.path:
    sys.path.insert(0, str(ARIFOS_ROOT))

from arifosmcp.tools import kernel_canonical  # noqa: E402


# ── Routing regression tests ────────────────────────────────────────────────


def _route(intent: str) -> str:
    """Call _route_intent_to_organ and clear cache to pick up YAML changes."""
    kernel_canonical._intent_map_cache = None  # clear cache
    return kernel_canonical._route_intent_to_organ(intent)


class TestOrganQualifiedRouting:
    """G14 FIX — organ-qualified phrases MUST route to the named organ."""

    def test_well_organ_health_routes_to_well(self):
        # The directive's exact failing case
        assert _route("WELL organ health and cooling bridge status check") == "well"

    def test_well_cooling_bridge_routes_to_well(self):
        assert _route("cooling bridge status") == "well"

    def test_well_biometric_readiness_routes_to_well(self):
        assert _route("biometric readiness") == "well"

    def test_well_state_json_routes_to_well(self):
        assert _route("well state.json") == "well"

    def test_geox_organ_earth_routes_to_geox(self):
        # The directive's exact failing case
        assert _route("GEOX organ earth/geoscience evidence status check") == "geox"

    def test_geox_geology_interpretation_routes_to_geox(self):
        assert _route("geology interpretation") == "geox"

    def test_geox_seismic_section_routes_to_geox(self):
        assert _route("seismic section") == "geox"

    def test_geox_earth_evidence_routes_to_geox(self):
        assert _route("earth evidence") == "geox"

    def test_wealth_capital_intelligence_routes_to_wealth(self):
        assert _route("capital intelligence") == "wealth"

    def test_aaa_state_governance_routes_to_aaa(self):
        assert _route("AAA state and governance") == "aaa"

    def test_aaa_seal_chain_routes_to_aaa(self):
        assert _route("seal chain") == "aaa"

    def test_aforge_status_routes_to_a_forge(self):
        assert _route("forge status") == "a-forge"

    def test_aforge_health_routes_to_a_forge(self):
        assert _route("forge health") == "a-forge"


class TestKernelGuardStillWorks:
    """The kernel guard must STILL catch unqualified MCP/constitutional queries."""

    def test_arifos_kernel_health_routes_to_arifos(self):
        assert _route("kernel health") == "arifos"

    def test_arifos_kernel_status_routes_to_arifos(self):
        assert _route("kernel status") == "arifos"

    def test_mcp_tool_registry_routes_to_arifos(self):
        assert _route("tool registry") == "arifos"

    def test_constitutional_floor_check_routes_to_arifos(self):
        assert _route("constitutional floor check") == "arifos"

    def test_chatgpt_connector_routes_to_arifos(self):
        assert _route("ChatGPT connector status") == "arifos"

    def test_unqualified_organ_health_routes_to_arifos(self):
        # The original failing pattern — but UNQUALIFIED should still go to arifOS
        assert _route("organ health") == "arifos"

    def test_unqualified_organ_attestation_routes_to_arifos(self):
        # Org-qualified case is handled in Step 1. Unqualified stays in arifOS.
        assert _route("organ attestation") == "arifos"


class TestYAMLKeywordLongestMatch:
    """The YAML map must produce longest-keyword match per organ."""

    def test_longer_keyword_wins_organ_qualified(self):
        # "WELL organ health" (3 tokens) should beat "WELL organ" (2 tokens)
        # because both exist as keywords. The kernel logic uses prefix-match
        # in Step 1, which is binary, but Step 3's longest-match should
        # also produce WELL.
        result = _route("WELL organ health check")
        assert result == "well"

    def test_geox_earth_intelligence_routes_to_geox(self):
        assert _route("earth intelligence") == "geox"

    def test_geox_geoscience_routes_to_geox(self):
        assert _route("geoscience") == "geox"


class TestEdgeCases:
    """Edge cases that should not crash."""

    def test_empty_intent_routes_to_arifos(self):
        assert _route("") == "arifos"

    def test_unknown_intent_routes_to_arifos(self):
        assert _route("xyzzy plugh foobar") == "arifos"

    def test_explicit_organ_overrides_keyword(self):
        # When caller explicitly passes organ="GEOX", that wins
        assert (
            kernel_canonical._route_intent_to_organ(
                "WELL organ health", explicit_organ="GEOX"
            )
            == "geox"
        )


class TestAForgeRoute:
    """A-FORGE keywords."""

    def test_aforge_docker_routes_to_a_forge(self):
        assert _route("docker compose up") == "a-forge"

    def test_aforge_build_routes_to_a_forge(self):
        assert _route("build the package") == "a-forge"

    def test_aforge_rollback_routes_to_a_forge(self):
        assert _route("rollback") == "a-forge"


if __name__ == "__main__":
    # Manual smoke run
    import json

    cases = [
        ("WELL organ health and cooling bridge status check", "well"),
        ("GEOX organ earth/geoscience evidence status check", "geox"),
        ("cooling bridge status", "well"),
        ("seismic section", "geox"),
        ("capital intelligence", "wealth"),
        ("seal chain", "aaa"),
        ("forge status", "a-forge"),
        ("kernel health", "arifos"),
        ("ChatGPT connector", "arifos"),
        ("organ attestation", "arifos"),
        ("WELL biometric readiness", "well"),
    ]
    fail = 0
    for intent, expected in cases:
        actual = _route(intent)
        ok = "✓" if actual.lower() == expected.lower() else "✗"
        if ok == "✗":
            fail += 1
        print(f"{ok}  '{intent}' → {actual}  (expected {expected})")
    print(f"\n{len(cases) - fail}/{len(cases)} passed")
    sys.exit(0 if fail == 0 else 1)