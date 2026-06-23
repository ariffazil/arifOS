from __future__ import annotations

from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, build_server_json
from arifosmcp.runtime.public_surface import CANARY_PROBES


def test_public_registry_exposes_only_capability_tools() -> None:
    tools = build_server_json()["tools"]
    names = {tool["name"] for tool in tools}

    # Default canonical13 wire surface = canonical + SDK aliases + canary probe
    assert len(names) == EXPECTED_TOOL_COUNT
    # Canary probe is part of the default public surface
    assert "arif_canary" in names
    # Internal-only / legacy diagnostics must NOT leak to public surface
    assert "arif_selftest" not in names
    assert "arif_meaning_witness" not in names
    assert "arif_context_witness" not in names
    assert "arif_ops_measure" in names
