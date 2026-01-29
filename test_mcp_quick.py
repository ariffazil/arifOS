#!/usr/bin/env python3
"""Quick 7-Tool Test - arifOS v53.2.9"""
import asyncio
import sys
sys.path.insert(0, "c:/Users/ariff/arifOS")

from codebase.mcp.tools.mcp_trinity import mcp_agi_genius, mcp_asi_act, mcp_apex_judge
from codebase.kernel import mcp_000_init

async def test():
    print("\n" + "="*60)
    print("arifOS v53.2.9 - 7-Tool Quick Test")
    print("="*60 + "\n")

    # Tool 1: _ignite_
    print("[1/7] _ignite_ (Gate)")
    r1 = await mcp_000_init(action="init", query="Test session")
    print(f"  Status: {r1.get('status')}, Session: {r1.get('session_id', 'N/A')[:8]}")
    sid = r1.get('session_id')

    # Tool 2: _logic_
    print("\n[2/7] _logic_ (Mind)")
    r2 = await mcp_agi_genius(action="think", query="What is arifOS?", session_id=sid)
    print(f"  Verdict: {r2.get('verdict')}, Status: {r2.get('status')}")

    # Tool 3: _senses_ (Reality check via full action)
    print("\n[3/7] _senses_ (Reality)")
    r3 = await mcp_agi_genius(action="full", query="External grounding test", session_id=sid)
    print(f"  Verdict: {r3.get('verdict')}, Status: {r3.get('status')}")

    # Tool 4: _atlas_ (via evaluate action)
    print("\n[4/7] _atlas_ (Mapper)")
    r4 = await mcp_agi_genius(action="evaluate", query="codebase/mcp/", session_id=sid)
    print(f"  Verdict: {r4.get('verdict')}, Status: {r4.get('status')}")

    # Tool 5: _forge_ (Builder via ASI full action)
    print("\n[5/7] _forge_ (Builder)")
    r5 = await mcp_asi_act(action="full", query="Simple function", session_id=sid)
    print(f"  Verdict: {r5.get('verdict')}, Status: {r5.get('status')}")

    # Tool 6: _audit_ (Scanner via ASI act)
    print("\n[6/7] _audit_ (Scanner)")
    r6 = await mcp_asi_act(action="act", text="def test(): pass", session_id=sid)
    print(f"  Verdict: {r6.get('verdict')}, Status: {r6.get('status')}")

    # Tool 7: _decree_ (Final judgment)
    print("\n[7/7] _decree_ (Seal)")
    r7 = await mcp_apex_judge(action="full", query="Complete", session_id=sid)
    print(f"  Verdict: {r7.get('verdict')}, Status: {r7.get('status')}")

    print("\n" + "="*60)
    print("SUMMARY:")
    results = [r1, r2, r3, r4, r5, r6, r7]
    seals = sum(1 for r in results if r.get('verdict') == 'SEAL')
    print(f"  SEAL count: {seals}/7")
    print(f"  Session: {sid}")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test())
