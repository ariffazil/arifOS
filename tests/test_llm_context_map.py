import json

import pytest
from arifosmcp.capability_map import build_llm_context_map
from arifosmcp.runtime.public_registry import build_mcp_discovery_json
from arifosmcp.runtime import resources as runtime_resources
from arifosmcp.runtime.resources import register_resources
from arifosmcp.runtime.tools_internal import architect_registry_dispatch_impl
from fastmcp import FastMCP


def test_build_llm_context_map_exposes_canonical_surface():
    payload = build_llm_context_map()

    assert payload["schema"] == "arifos-llm-context/v1"
    assert "init_anchor" in payload["canonical_tools"]
    assert "agi_mind" in payload["canonical_tools"]
    assert payload["continuity_contract"]["contract_version"] == "0.1.0"
    assert "authorization may not widen without authority_transition" in payload["continuity_contract"]["invariants"]


def test_discovery_manifest_points_to_llm_context_resource():
    manifest = build_mcp_discovery_json()
    assert manifest["llm_context_resource"] == "arifos://mcp/context"
    assert manifest["continuity_contract_version"] == "0.1.0"
    assert manifest["llm_context"]["schema"] == "arifos-llm-context/v1"


def test_resources_register_llm_context_resource():
    mcp = FastMCP("test")
    register_resources(mcp)

    assert "arifos://mcp/context" in runtime_resources._resource_content_functions
    payload = json.loads(runtime_resources._resource_content_functions["arifos://mcp/context"]())
    assert payload["schema"] == "arifos-llm-context/v1"
    assert payload["discovery"]["tool_contracts_resource"] == "arifos://contracts/tools"


@pytest.mark.asyncio
async def test_architect_registry_context_mode_returns_llm_context():
    envelope = await architect_registry_dispatch_impl(
        mode="context",
        payload={"session_id": "ctx-001"},
        auth_context=None,
        risk_tier="low",
        dry_run=True,
        ctx=None,
    )
    assert envelope.payload["context"]["schema"] == "arifos-llm-context/v1"
    assert envelope.payload["resource_uri"] == "arifos://mcp/context"
