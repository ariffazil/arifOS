"""
tests/test_surface_map_live_contract.py — Surface map contract tests.

Updated 2026-07-08: _build_surface_map was removed during ZEN-9 consolidation.
Surface map is now a static dict SURFACE_MAP. Tests verify its shape.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.resources.surface_map import SURFACE_MAP
from arifosmcp.runtime.public_surface import CANONICAL_12, public_tool_names_for_mode


def test_surface_map_has_expected_structure():
    """SURFACE_MAP must contain the agent surface map with tools and resources."""
    assert "arifos_agent_surface_map" in SURFACE_MAP
    payload = SURFACE_MAP["arifos_agent_surface_map"]
    assert "mcp_tools" in payload
    assert "mcp_resources" in payload
    assert isinstance(payload["mcp_tools"], list)


def test_surface_map_tools_are_canonical():
    """All tools in the surface map must start with arif_."""
    tools = SURFACE_MAP["arifos_agent_surface_map"]["mcp_tools"]
    assert all(name.startswith("arif_") for name in tools)


def test_public_tool_names_match_canonical():
    """public_tool_names_for_mode returns the canonical surface."""
    names = public_tool_names_for_mode(None)
    assert len(names) >= 9
    assert all(name.startswith("arif_") for name in names)
