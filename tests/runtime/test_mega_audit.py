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
    # The 7 canonical public handlers are the constitutional core.
    assert CANONICAL_PUBLIC_TOOLS.issubset(set(FINAL_TOOL_IMPLEMENTATIONS))
    assert len(CANONICAL_PUBLIC_TOOLS) == EXPECTED_TOOL_COUNT

    # The full handler map includes internal diagnostics and aliases.
    extra = set(FINAL_TOOL_IMPLEMENTATIONS) - CANONICAL_PUBLIC_TOOLS
    assert extra <= set(DIAGNOSTIC_TOOLS), (
        f"Unexpected non-diagnostic handlers: {extra - set(DIAGNOSTIC_TOOLS)}"
    )

    # The live public surface exposes exactly the canonical 7 (no diagnostics).
    live_names = set(public_tool_names())
    assert live_names == CANONICAL_PUBLIC_TOOLS


@pytest.mark.asyncio
async def test_register_tools_registers_canonical7_plus_diagnostics() -> None:
    mcp = FastMCP("test-canonical7-diagnostics")

    registered = register_tools(mcp)
    listed = await mcp.list_tools()
    listed_names = {tool.name for tool in listed}

    # Canonical 7 must always be present.
    assert CANONICAL_PUBLIC_TOOLS.issubset(set(registered))
    assert CANONICAL_PUBLIC_TOOLS.issubset(listed_names)

    # Diagnostics may be present; no ghost aliases allowed.
    extra = listed_names - CANONICAL_PUBLIC_TOOLS
    assert extra <= set(DIAGNOSTIC_TOOLS), (
        f"Unexpected non-diagnostic tools: {extra - set(DIAGNOSTIC_TOOLS)}"
    )

    # Every listed tool has a valid parameter schema.
    assert all(tool.parameters and "properties" in tool.parameters for tool in listed)


@pytest.mark.asyncio
async def test_canonical7_mode_excludes_all_diagnostics() -> None:
    """canonical7 (profile key canonical13) exposes exactly the 7 canonical verbs; no diagnostics leak."""
    names = set(public_tool_names_for_mode("canonical13"))
    assert names == CANONICAL_PUBLIC_TOOLS, f"canonical7 surface mismatch: {names}"
