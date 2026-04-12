import pytest
import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_seal_e2e():
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

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            res_seal = await session.call_tool(
                "arifos_vault",
                {
                    "verdict": "SEAL",
                    "evidence": "E2E Test Evidence for output alignment",
                    "session_id": "e2e-seal-session",
                    "dry_run": True,
                },
            )

            raw_text = res_seal.content[0].text
            payload = json.loads(raw_text)

            assert list(payload.keys()) == ["output"]
            assert "Vault" in payload["output"]
            assert "Context: actor" in payload["output"]
            assert "Verdict:" in payload["output"]

if __name__ == "__main__":
    asyncio.run(test_seal_e2e())
