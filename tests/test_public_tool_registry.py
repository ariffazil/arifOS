from __future__ import annotations

from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, build_server_json
from arifosmcp.runtime.public_surface import CANARY_PROBES


def test_public_registry_exposes_only_capability_tools() -> None:
    tools = build_server_json()["tools"]
    names = {tool["name"] for tool in tools}

    # FROZEN 2026-06-23: canonical13 wire surface = 15 canonical + 1 canary = 16 tools
    # SDK aliases removed from wire surface — one name per function.
    assert len(names) == EXPECTED_TOOL_COUNT
    # Canary probe is part of the default public surface
    assert "arif_canary" in names
    # Internal-only / legacy diagnostics must NOT leak to public surface
    assert "arif_selftest" not in names
    assert "arif_meaning_witness" not in names
    assert "arif_context_witness" not in names
    # Canonical names only — no SDK aliases on wire
    assert "arif_measure" in names
    assert "arif_ops_measure" not in names  # alias removed from wire
    assert "arif_init" in names
    assert "arif_session_init" not in names  # alias removed from wire
