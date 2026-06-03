from __future__ import annotations

from arifosmcp.runtime.public_registry import (
    CANONICAL_PUBLIC_TOOLS,
    EXPECTED_TOOL_COUNT,
    build_internal_server_json,
    build_mcp_manifest,
    build_server_json,
    contract_status_summary,
    public_tool_names,
    tool_names_for_profile,
    verify_no_drift,
)
from arifosmcp.runtime.public_surface import BLOCKED_PUBLIC_PREFIXES


def test_server_json_matches_canonical13_registry() -> None:
    server_json = build_server_json()
    tool_names = {tool["name"] for tool in server_json["tools"]}

    assert tool_names == CANONICAL_PUBLIC_TOOLS
    assert server_json["capabilities"]["public_surface"] == "canonical13"


def test_mcp_manifest_matches_canonical13_registry() -> None:
    manifest_json = build_mcp_manifest()
    tool_names = {tool["name"] for tool in manifest_json["tools"]}

    assert tool_names == CANONICAL_PUBLIC_TOOLS


def test_public_profile_stays_canonical13() -> None:
    public_names = tool_names_for_profile("public")

    assert len(public_names) == EXPECTED_TOOL_COUNT
    assert set(public_names) == CANONICAL_PUBLIC_TOOLS
    assert not [name for name in public_names if name.startswith(BLOCKED_PUBLIC_PREFIXES)]


def test_internal_profile_contains_public_surface_without_leaking_into_public() -> None:
    public_names = set(public_tool_names())
    internal_names = {tool["name"] for tool in build_internal_server_json()["tools"]}

    assert public_names.issubset(internal_names)
    assert len(internal_names) >= len(public_names)


def test_public_registry_has_no_drift() -> None:
    drift = verify_no_drift()

    assert drift["ok"], drift
    assert drift["actual_count"] == EXPECTED_TOOL_COUNT


def test_public_registry_publishes_input_and_output_schemas() -> None:
    server_json = build_server_json()
    tools = {tool["name"]: tool for tool in server_json["tools"]}

    assert contract_status_summary()["schemas_complete"] is True
    assert all("properties" in tool["inputSchema"] for tool in tools.values())
    assert all(tool.get("outputSchema", {}).get("properties") for tool in tools.values())
    assert "preserve" in tools["arif_evidence_fetch"]["description"]
    assert "health" in tools["arif_ops_measure"]["description"]
