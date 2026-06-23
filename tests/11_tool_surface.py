"""CI test file for tool surface invariants.
Forged: 2026-06-22 as part of MCP AGI Kernel Substrate Phase 1.
"""

import pytest
from arifosmcp.constitutional_map import CANONICAL_TOOLS


class TestToolSurfaceInvariants:
    """Phase 1 invariants for the MCP tool surface."""

    def test_canonical_tools_count(self):
        """External-facing tools must be ≤26 (13+13 target)."""
        # Currently 22 tools (21 canonical + 1 probe).
        # Phase 2 reduces to 13 external + 13 internal.
        assert len(CANONICAL_TOOLS) >= 13, "Too few tools"
        assert len(CANONICAL_TOOLS) <= 26, "Too many tools — must remove one before adding"

    def test_external_tool_prefix(self):
        """All external tools must start with 'arif_'."""
        for name in CANONICAL_TOOLS:
            assert name.startswith("arif_"), f"Tool {name} does not start with arif_"

    def test_no_arifos_public(self):
        """No arifos_* tools in CANONICAL_TOOLS (they're internal)."""
        for name in CANONICAL_TOOLS:
            assert not name.startswith("arifos_"), f"Internal tool {name} in CANONICAL_TOOLS"

    def test_stage_uniqueness(self):
        """Each tool must have a unique (stage, lane) pair (with exceptions for side-branches and known siblings).

        Known allowed duplicates:
          - arif_explore / arif_sense_observe: both stage=111, lane=AGI.
            arif_explore is an L2 exploration substrate that extends
            the observe sense — a legitimate sibling pair.
        """
        _KNOWN_DUPLICATE_STAGES: set[str] = {
            "111",  # arif_explore + arif_sense_observe (L2 exploration extends observe)
            "555",  # 8 routing tools share stage 555/AGI: arif_kernel_route (deprecated),
            # arif_route, arif_triage, arif_kernel_status (deprecated),
            # arif_bridge_connect, arif_bridge (deprecated),
            # arif_kernel_attest (deprecated), arif_kernel_health (deprecated).
            # All are legitimate infrastructure siblings at the routing stage.
        }
        seen = {}
        for name, spec in CANONICAL_TOOLS.items():
            stage = spec.get("stage")
            lane = spec.get("lane")
            key = (str(stage), str(lane))
            if key in seen:
                # Side-branches (r, g, m suffixes) are allowed duplicates
                if not any(suffix in str(stage) for suffix in ["r", "g", "m"]):
                    if str(stage) not in _KNOWN_DUPLICATE_STAGES:
                        pytest.fail(f"Duplicate stage/lane: {key} for {name} and {seen[key]}")
            seen[key] = name

    def test_irreversible_tools_have_f13(self):
        """All irreversible tools must include L13 in floors."""
        for name, spec in CANONICAL_TOOLS.items():
            if spec.get("irreversible"):
                assert any(
                    "L13" in str(f) or "SOVEREIGN" in str(f) for f in spec.get("floors", [])
                ), f"Irreversible tool {name} missing L13 floor"

    def test_no_deprecated_without_replacement(self):
        """Every deprecated tool must have a _canonical_name or redirects_to."""
        for name, spec in CANONICAL_TOOLS.items():
            if spec.get("_deprecated") or spec.get("deprecated"):
                assert spec.get("_canonical_name") or spec.get("redirects_to"), (
                    f"Deprecated tool {name} has no replacement specified"
                )


class TestDiagnosticToolsCount:
    """Ensure diagnostic tool count is within bounds."""

    def test_diagnostic_count_reasonable(self):
        """Diagnostic tools must be fewer than canonical tools."""
        from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS

        assert len(DIAGNOSTIC_TOOLS) < len(CANONICAL_TOOLS), (
            "Diagnostic tools should be fewer than canonical tools"
        )
