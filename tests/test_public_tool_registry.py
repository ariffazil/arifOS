from __future__ import annotations

from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, build_server_json


def test_public_registry_exposes_only_canonical_12() -> None:
    tools = build_server_json()["tools"]
    names = {tool["name"] for tool in tools}

    # FROZEN 2026-07-04: canonical12 wire surface = exactly 12 canonical verbs.
    # SDK aliases and individual canary children removed from wire surface — one
    # name per function. arif_forge replaces arif_act as the canonical execution
    # tool; arif_act is now an internal alias only.
    assert len(names) == EXPECTED_TOOL_COUNT
    assert EXPECTED_TOOL_COUNT == 12, f"EXPECTED_TOOL_COUNT must be 12, got {EXPECTED_TOOL_COUNT}"
    # All 12 canonical verbs on the wire
    expected_canonical = {
        "arif_init",
        "arif_canary",
        "arif_triage",
        "arif_observe",
        "arif_fetch",
        "arif_think",
        "arif_route",
        "arif_critique",
        "arif_bridge_connect",
        "arif_judge",
        "arif_forge",
        "arif_compose",
    }
    assert expected_canonical.issubset(names), (
        f"Missing canonical tools: {expected_canonical - names}"
    )
    # Internal-only / legacy diagnostics must NOT leak to public surface
    assert "arif_selftest" not in names
    assert "arif_meaning_witness" not in names
    assert "arif_context_witness" not in names
    # Canonical names only — no SDK aliases on wire
    assert "arif_observe" in names
    assert "arif_init" in names
    assert "arif_session_init" not in names  # alias removed from wire
    # Trim 2026-07-04: arif_forge is the canonical public name; arif_act is internal alias
    assert "arif_forge" in names
    assert "arif_act" not in names  # internal alias now
    # Fake seal verb removed from public wire (VAULT999 owns)
    assert "arif_seal" not in names
    # Memory moved to archive (rule 6)
    assert "arif_memory" not in names
