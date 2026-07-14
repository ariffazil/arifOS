from __future__ import annotations

from arifosmcp.runtime.public_registry import EXPECTED_TOOL_COUNT, build_server_json


def test_public_registry_exposes_public_agent_profile() -> None:
    tools = build_server_json(surface_mode="public_agent")["tools"]
    names = {tool["name"] for tool in tools}

    assert EXPECTED_TOOL_COUNT == 6
    assert len(names) == EXPECTED_TOOL_COUNT
    assert names == {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
    }
    assert "arif_forge" not in names
    assert "arif_seal" not in names
    assert "arif_session_init" not in names
