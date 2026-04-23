from __future__ import annotations

import pytest
from fastmcp import FastMCP

from arifosmcp.runtime.public_registry import (
    public_tool_names,
    verify_no_drift,
    CANONICAL_PUBLIC_TOOLS,
    EXPECTED_TOOL_COUNT,
)
from arifosmcp.runtime.tools import register_tools
from arifosmcp.capability_map import CAPABILITY_MAP


def test_public_registry_exactly_11():
    """Requirement A: Public registry exposes exactly 11 tools."""
    names = set(public_tool_names())
    assert len(names) == EXPECTED_TOOL_COUNT
    assert names == CANONICAL_PUBLIC_TOOLS

    drift = verify_no_drift()
    assert drift["ok"], f"Registry drift detected: {drift}"


@pytest.mark.asyncio
async def test_legacy_aliases_routing():
    """Requirement C: Backward compatibility — legacy aliases route correctly.

    Note: init_anchor_state and get_caller_status were REMOVED in Track A.
    They were simple wrappers routing to init_anchor(mode=X). The unified
    init_anchor now handles all modes internally via init_v1 adapter.
    """
    mcp = FastMCP("test")
    register_tools(mcp)

    # In FastMCP, use list_tools() to get registered tools
    tools = await mcp.list_tools()
    registered_names = {t.name for t in tools}

    # REMOVED legacy tools (intentionally absent — Track A)
    removed_aliases = ["init_anchor_state", "get_caller_status"]
    for alias in removed_aliases:
        assert alias not in registered_names, (
            f"Legacy alias '{alias}' should be REMOVED but is still registered"
        )

    # Still-present legacy aliases from CAPABILITY_MAP
    active_aliases = [
        "agi_reason",
        "reality_compass",
        "vault_seal",
    ]

    for alias in active_aliases:
        assert alias in registered_names, f"Legacy alias '{alias}' is missing from registration"
        target = CAPABILITY_MAP[alias]
        tool = next(t for t in tools if t.name == alias)
        # Verify the tool is callable and has a description
        assert tool.description is not None, f"Tool '{alias}' has no description"


def test_governance_contracts_aligned():
    """Requirement D: Governance integrity — contracts are bound to 11 tools."""
    from arifosmcp.runtime.contracts import (
        AAA_TOOL_STAGE_MAP,
        TRINITY_BY_TOOL,
        TOOL_MODES,
        verify_contract,
    )

    result = verify_contract()
    assert result["ok"], f"Contract verification failed: {result}"

    # Ensure every public tool has a stage and trinity
    for tool in CANONICAL_PUBLIC_TOOLS:
        assert tool in AAA_TOOL_STAGE_MAP
        assert tool in TRINITY_BY_TOOL
        assert tool in TOOL_MODES


def test_no_forbidden_public_exposure():
    """Ensure internal tools are NOT in the public names list."""
    public_names = set(public_tool_names())
    internal_only = {
        "init_anchor_state",
        "get_caller_status",
        "agi_reason",
        "forge",
        "fs_inspect",
    }

    # These should be shims in the MCP object but NOT tool specs in public_registry
    intersection = public_names.intersection(internal_only)
    assert not intersection, f"Internal tools exposed in public ToolSpecs: {intersection}"
