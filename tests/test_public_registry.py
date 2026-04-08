from __future__ import annotations

import json
from pathlib import Path

from arifosmcp.runtime.public_registry import (
    build_internal_server_json,
    build_mcp_manifest,
    build_server_json,
    tool_names_for_profile,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC_ROOT = ROOT / "docs" / "reference" / "spec"
CANONICAL_NAMES = {
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_route",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_forge",
    "arifos_vps_monitor",
}


def test_server_json_matches_registry() -> None:
    assert (SPEC_ROOT / "server.json").exists()
    server_json = build_server_json()
    assert {tool["name"] for tool in server_json["tools"]} == CANONICAL_NAMES


def test_mcp_manifest_matches_registry() -> None:
    assert (SPEC_ROOT / "mcp-manifest.json").exists()
    manifest_json = build_mcp_manifest()
    assert {tool["name"] for tool in manifest_json["tools"]} == CANONICAL_NAMES


def test_public_profile_stays_minimal_and_internal_profile_includes_internal_tools() -> None:
    """Canonical 11 tools are public."""
    public_names = tool_names_for_profile("public")
    internal_names = tool_names_for_profile("internal")

    assert "arifos_init" in public_names
    assert "arifos_route" in public_names
    assert "arifos_judge" in public_names
    assert "arifos_vault" in public_names
    assert len(public_names) == 11

    # Internal profile includes all public tools
    assert set(public_names).issubset(set(internal_names))


def test_internal_server_json_declares_internal_capabilities() -> None:
    """Internal server JSON includes all 11 canonical tools."""
    server_json = build_internal_server_json()
    tool_names = {tool["name"] for tool in server_json["tools"]}

    assert "arifos_init" in tool_names
    assert "arifos_mind" in tool_names
    assert "arifos_heart" in tool_names
    assert "arifos_judge" in tool_names
    assert "arifos_vault" in tool_names
    assert len(tool_names) == 11
