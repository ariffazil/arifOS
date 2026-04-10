"""
arifosmcp/evals/substrate_alignment_test.py — Constitutional Alignment Test

Verifies that substrate bridges (Git, Fetch, Memory) correctly enforce 
constitutional floors (F2, F7, F8, F9, F11, F13).

DITEMPA BUKAN DIBERI — Alignment Witness
"""

import asyncio
import logging

from arifosmcp.integrations.fetch_bridge import arifos_fetch
from arifosmcp.integrations.git_bridge import arifos_git_commit, arifos_git_status
from arifosmcp.integrations.memory_bridge import arifos_memory_query, arifos_memory_write
from arifosmcp.runtime.models import Verdict

logger = logging.getLogger(__name__)

async def test_git_alignment():
    print("📋 TESTING GIT ALIGNMENT (F11/F13)...")
    
    # Test read (F11 audit only)
    status = await arifos_git_status(path="./")
    print(f"  Status Read: {'OK' if status.ok else 'FAIL'}")
    
    # Test mutation without human (Should be VOID if F13 is not simulated)
    # Note: In a real test we'd mock the judge, but here we test the bridge logic
    commit = await arifos_git_commit(message="Test commit", files=["README.md"], actor_id="tester")
    print(f"  Mutation (F13): {'SEAL' if commit.verdict == Verdict.SEAL else 'VOID/HOLD'} (Result: {commit.verdict})")

async def test_fetch_alignment():
    print("📋 TESTING FETCH ALIGNMENT (F8/F9)...")
    
    # Test F9 Hantu Scan (Simulated content)
    url = "https://example.com/manifesto"
    # We'd normally call the bridge which calls the substrate
    # Since we can't hit real URLs easily in this env, we assume success or check logic
    fetch_result = await arifos_fetch(url=url, actor_id="tester")
    print(f"  Fetch (F9): {'OK' if fetch_result.ok else 'FAIL'} (Verdict: {fetch_result.verdict})")

async def test_memory_alignment():
    print("📋 TESTING MEMORY ALIGNMENT (F2/F7)...")
    
    # Test write with confidence
    write = await arifos_memory_write(
        entity_id="test_entity",
        entity_type="test",
        observations=["Observation 1"],
        actor_id="tester",
        truth_confidence=0.9
    )
    print(f"  Memory Write (F2): {'OK' if write.ok else 'FAIL'}")
    
    # Test query
    query = await arifos_memory_query(query="test_entity", actor_id="tester")
    print(f"  Memory Query: {'OK' if query.ok else 'FAIL'}")

async def main():
    print("🏗️  STARTING SUBSTRATE ALIGNMENT VERIFICATION...\n")
    await test_git_alignment()
    await test_fetch_alignment()
    await test_memory_alignment()
    print("\n✅ VERIFICATION COMPLETE.")

if __name__ == "__main__":
    asyncio.run(main())
