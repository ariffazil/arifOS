from __future__ import annotations

from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, build_server_json


def test_public_registry_exposes_only_canonical_12() -> None:
    tools = build_server_json()["tools"]
    names = {tool["name"] for tool in tools}

    # ZEN-9 (2026-07-04): canonical wire surface = exactly 9 canonical verbs.
    # arif_critique promoted to standalone (not absorbed into think).
    # Absorbed tools (arif_canary, arif_triage, arif_fetch, arif_bridge_connect)
    # are internal-only aliases.
    assert len(names) == EXPECTED_TOOL_COUNT
    assert EXPECTED_TOOL_COUNT == 9, f"EXPECTED_TOOL_COUNT must be 9, got {EXPECTED_TOOL_COUNT}"
    # All 9 canonical verbs on the wire
    expected_canonical = {
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
    # ZEN-9: arif_seal is canonical (stage 999 — VAULT999 append)
    assert "arif_seal" in names
    # Memory moved to archive (rule 6)
    assert "arif_memory" not in names
