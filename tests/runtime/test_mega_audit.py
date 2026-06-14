from __future__ import annotations

import pytest
from fastmcp import FastMCP

from arifosmcp.runtime.public_registry import (
    CANONICAL_PUBLIC_TOOLS,
    EXPECTED_TOOL_COUNT,
    public_tool_names,
)
from arifosmcp.runtime.public_surface import DIAGNOSTIC_TOOLS, public_tool_names_for_mode
from arifosmcp.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS, register_tools


def test_canonical_handlers_match_public_registry() -> None:
    # The canonical 13 handlers are the constitutional core.
    assert set(FINAL_TOOL_IMPLEMENTATIONS) == CANONICAL_PUBLIC_TOOLS
    assert len(FINAL_TOOL_IMPLEMENTATIONS) == EXPECTED_TOOL_COUNT

    # The live public surface includes the canonical 13 plus zero-floor diagnostics.
    live_names = set(public_tool_names())
    assert CANONICAL_PUBLIC_TOOLS.issubset(live_names)
    assert live_names - CANONICAL_PUBLIC_TOOLS <= set(DIAGNOSTIC_TOOLS)


@pytest.mark.asyncio
async def test_register_tools_registers_canonical13_plus_diagnostics() -> None:
    mcp = FastMCP("test-canonical13-diagnostics")

    registered = register_tools(mcp)
    listed = await mcp.list_tools()
    listed_names = {tool.name for tool in listed}

    # Canonical 13 must always be present.
    assert CANONICAL_PUBLIC_TOOLS.issubset(set(registered))
    assert CANONICAL_PUBLIC_TOOLS.issubset(listed_names)

    # Diagnostics may be present; no ghost aliases allowed.
    extra = listed_names - CANONICAL_PUBLIC_TOOLS
    assert extra <= set(DIAGNOSTIC_TOOLS), f"Unexpected non-diagnostic tools: {extra - set(DIAGNOSTIC_TOOLS)}"

    # Every listed tool has a valid parameter schema.
    assert all(
        tool.parameters and "properties" in tool.parameters for tool in listed
    )


@pytest.mark.asyncio
async def test_canonical13_mode_excludes_expanded_only_diagnostics() -> None:
    """canonical13 mode exposes only the 5 transport canary diagnostics, not the full expanded set."""
    names = set(public_tool_names_for_mode("canonical13"))
    allowed_diagnostics = {
        "arif_ping",
        "arif_schema_echo",
        "arif_version_echo",
        "arif_transport_echo",
        "arif_initialize_probe",
    }
    extra = names - CANONICAL_PUBLIC_TOOLS
    assert extra == allowed_diagnostics, f"canonical13 diagnostic mismatch: {extra}"
