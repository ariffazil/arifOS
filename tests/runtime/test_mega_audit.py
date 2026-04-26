from __future__ import annotations

import pytest
from fastmcp import FastMCP

from arifosmcp.runtime.public_registry import CANONICAL_PUBLIC_TOOLS, EXPECTED_TOOL_COUNT, public_tool_names
from arifosmcp.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS, register_tools


def test_canonical_handlers_match_public_registry() -> None:
    assert set(public_tool_names()) == CANONICAL_PUBLIC_TOOLS
    assert set(FINAL_TOOL_IMPLEMENTATIONS) == CANONICAL_PUBLIC_TOOLS
    assert len(FINAL_TOOL_IMPLEMENTATIONS) == EXPECTED_TOOL_COUNT


@pytest.mark.asyncio
async def test_register_tools_registers_only_canonical13() -> None:
    mcp = FastMCP("test-canonical13")

    registered = register_tools(mcp)
    listed = await mcp.list_tools()

    assert set(registered) == CANONICAL_PUBLIC_TOOLS
    assert {tool.name for tool in listed} == CANONICAL_PUBLIC_TOOLS
