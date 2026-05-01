"""
geox_mcp_server.py — Hardened GEOX MCP Server for arifOS

This server provides geological intelligence tools anchored in the
arifOS Trinity sovereignty model (F1-F13).
"""

import asyncio
import logging
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.types import (
    TextContent,
    Tool,
)

# arifOS alignment
sys.path.append(r"c:\ariffazil\GEOX")
from arifos.geox.geox_hardened import HardenedGeoxAgent
from arifos.geox.geox_init import GEOXFoundation

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geox_mcp")

# Initialize Hardened Agent
agent = HardenedGeoxAgent(session_id="GEOX_PRODUCTION_SOVEREIGN")

# Create MCP Server
app = Server("geox-hardened")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expose registered geological tools."""
    tools = []
    # registry._tools is the internal dict
    for name, tool_instance in agent.registry._tools.items():
        # Attempt to get schema from tool metadata if it exists
        # Falling back to generic schema for now
        tools.append(Tool(
            name=name,
            description=tool_instance.description,
            inputSchema={"type": "object", "properties": {}}
        ))

    # Add Foundation Health Tool
    tools.append(Tool(
        name="geox_health",
        description="Check GEOX foundation alignment and constitutional health.",
        inputSchema={"type": "object", "properties": {}}
    ))

    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tools with hardening."""
    if name == "geox_health":
        status = GEOXFoundation.ignite()
        return [TextContent(type="text", text=f"GEOX Health: {status['verdict']}\n{status}")]

    # Delegate to hardened agent
    envelope = await agent.execute_tool(name, arguments)

    # Check for 888_HOLD
    if envelope["verdict"] == "888_HOLD":
        text = "WARNING: 888_HOLD [SOVEREIGN APPROVAL REQUIRED]\n"
        text += f"Reason: {envelope['explanation']}\n\n"
        text += f"Result Payload: {envelope['payload']}"
    else:
        text = f"Explanation: {envelope['explanation']}\n\nPayload: {envelope['payload']}"

    # Inject arifOS branding
    text += f"\n\n---\nGEOX v{envelope['version']} | G-Score: {envelope['metrics']['genius_score']} | delta_S: {envelope['metrics']['delta_s']}"

    return [TextContent(type="text", text=text)]

async def main():
    logger.info("Starting sovereign GEOX MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
