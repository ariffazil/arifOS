from __future__ import annotations

from arifosmcp.runtime.public_registry import build_server_json


def test_public_registry_exposes_only_capability_tools() -> None:
    tools = build_server_json()["tools"]
    names = {tool["name"] for tool in tools}

    assert len(names) == 13
    assert "arif_ping" not in names
    assert "arif_selftest" not in names
    assert "arif_meaning_witness" not in names
    assert "arif_context_witness" not in names
    assert "arif_ops_measure" in names
