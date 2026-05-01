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

            # Get judge verdict first (required for vault seal)
            res_judge = await session.call_tool(
                "arif_judge_deliberate",
                {
                    "mode": "judge",
                    "candidate": "seal test",
                    "actor_id": "arif",
                },
            )
            judge_payload = json.loads(res_judge.content[0].text)
            cc_id = judge_payload.get("judge_contract", {}).get("constitutional_chain_id")
            state_hash = judge_payload.get("judge_contract", {}).get("state_hash")
            res_seal = await session.call_tool(
                "arif_vault_seal",
                {
                    "mode": "seal",
                    "payload": "E2E Test Evidence for output alignment",
                    "session_id": "e2e-seal-session",
                    "ack_irreversible": True,
                    "actor_id": "arif",
                    "constitutional_chain_id": cc_id,
                    "judge_state_hash": state_hash,
                },
            )

            raw_text = res_seal.content[0].text
            payload = json.loads(raw_text)

            assert (
                payload.get("status") == "OK"
            ), f"Expected OK, got {payload.get('status')}: {raw_text}"
            output = payload.get("output", "")
            assert "Vault" in output
            assert "Verdict:" in output


if __name__ == "__main__":
    asyncio.run(test_seal_e2e())
