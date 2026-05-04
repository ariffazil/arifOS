import pytest
import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_arifosmcp_stdio_e2e_protocol():
    """
    E2E test for arifosmcp tools using the MCP stdio protocol.
    This test starts the server as a subprocess and interacts with it using a real MCP client.
    """
    # 1. Setup server parameters
    # Use sys.executable to ensure we use the same Python environment
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "arifosmcp.runtime", "stdio"],
        env={
            **os.environ,
            "ARIFOS_PHYSICS_DISABLED": "1",
            "AAA_MCP_OUTPUT_MODE": "debug",
            "ARIFOS_DEV_MODE": "1",
        },
    )

    # 2. Start the stdio client
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # 3. List tools and verify core tools are present
            tools_response = await session.list_tools()
            tool_names = [t.name for t in tools_response.tools]

            assert "arif_session_init" in tool_names
            assert "arif_kernel_route" in tool_names
            assert "arif_vault_seal" in tool_names

            # 4. Call arif_session_init through the real stdio MCP lane
            result = await session.call_tool(
                "arif_session_init",
                {
                    "actor_id": "protocol-tester",
                },
            )

            assert len(result.content) > 0
            content_text = result.content[0].text
            payload = json.loads(content_text)

            assert payload["status"] == "OK"
            assert payload["tool"] == "arif_session_init"
            assert "session" in payload["result"]
            assert payload["result"]["session"]["actor_id"] == "protocol-tester"


if __name__ == "__main__":
    asyncio.run(test_arifosmcp_stdio_e2e_protocol())
