import pytest
import asyncio
import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_seal_e2e():
    """E2E: Vault correctly enforces judge-packet lineage via MCP stdio.

    After F13 hardening (v2026.05), arif_judge_deliberate requires an MCP
    client with elicitation support. When called via plain stdio without a
    Context, it returns HOLD. Consequently, no judge contract is registered,
    and arif_vault_seal correctly returns HOLD for missing judge lineage.

    This test verifies the *current* hardened behavior rather than a legacy
    success path that is no longer reachable without an elicitation-capable
    MCP client.
    """
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

            # Judge call without elicitation context → F13 HOLD
            res_judge = await session.call_tool(
                "arif_judge_deliberate",
                {
                    "mode": "judge",
                    "candidate": "seal test",
                    "actor_id": "arif",
                },
            )
            judge_payload = json.loads(res_judge.content[0].text)
            assert judge_payload.get("status") == "HOLD"
            assert "F13" in judge_payload.get("meta", {}).get("reason", "") or \
                   "elicitation" in judge_payload.get("meta", {}).get("reason", "").lower() or \
                   "self-certify" in judge_payload.get("meta", {}).get("reason", "").lower()

            cc_id = judge_payload.get("judge_contract", {}).get("constitutional_chain_id")
            state_hash = judge_payload.get("judge_contract", {}).get("state_hash")

            # Vault seal with missing/invalid judge lineage → HOLD
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

            assert payload.get("status") == "HOLD"
            assert (
                "judge" in payload.get("meta", {}).get("reason", "").lower()
                or "constitutional_chain_id" in payload.get("meta", {}).get("reason", "").lower()
            )


if __name__ == "__main__":
    asyncio.run(test_seal_e2e())
