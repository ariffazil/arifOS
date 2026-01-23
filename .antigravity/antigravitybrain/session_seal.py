import asyncio
import json
import os
from arifos.mcp.tools.mcp_trinity import mcp_apex_judge, mcp_999_vault

async def seal_session():
    session_id = 'f5a293c3-ae8a-4676-9556-46e340404a31'
    summary = 'Harmonized agent brain directories across .antigravity, .claude, and .codex. Updated agent adapters (GEMINI.md, CLAUDE.md) and pushed changes to GitHub (commit 7e0ce5c).'
    
    # 1. Apex Judge
    judge_res = await mcp_apex_judge(
        action='full',
        response=summary,
        session_id=session_id
    )
    
    # 2. Vault Seal
    vault_res = await mcp_999_vault(
        action='seal',
        verdict=judge_res.get('status', 'SEAL'),
        session_id=session_id,
        apex_result=judge_res,
        query=summary
    )
    
    # Output result
    print("--- SESSION SEALED ---")
    print(f"Verdict: {vault_res.get('verdict')}")
    print(f"Merkle Root: {vault_res.get('merkle_root')}")
    print(f"Audit Hash: {vault_res.get('audit_hash')}")
    print(f"Memory: {vault_res.get('memory_location')}")
    print("----------------------")

if __name__ == "__main__":
    asyncio.run(seal_session())
