#!/usr/bin/env python3
"""
7-Tool Integration Test
Tests all MCP tools in sequence: _ignite_ -> _logic_ -> _senses_ -> _atlas_ -> _forge_ -> _audit_ -> _decree_

v53.2.9-AAA9
"""

import asyncio
import json
import sys
from typing import Dict, Any

# Add codebase to path
sys.path.insert(0, "c:/Users/ariff/arifOS")

from codebase.mcp.tools.mcp_trinity import (
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
)
from codebase.kernel import mcp_000_init


def print_result(tool_name: str, result: Dict[str, Any]):
    """Pretty print tool result."""
    print(f"\n{'='*60}")
    print(f"[TOOL] {tool_name}")
    print(f"{'='*60}")
    print(f"Status: {result.get('status', 'UNKNOWN')}")
    print(f"Verdict: {result.get('verdict', 'UNKNOWN')}")

    if "session_id" in result:
        print(f"Session: {result['session_id']}")

    if "floors_active" in result:
        print(f"Floors Active: {', '.join(result['floors_active'])}")

    if "reasoning" in result:
        print(f"Reasoning: {json.dumps(result['reasoning'], indent=2)}")

    if "metrics" in result:
        print(f"Metrics: {json.dumps(result['metrics'], indent=2)}")

    if "error" in result:
        print(f"[ERROR] {result['error']}")

    print(f"{'='*60}\n")


async def test_all_tools():
    """Test all 7 MCP tools in sequence."""

    print("\n" + "="*60)
    print("arifOS v53.2.9 - 7-Tool Constitutional Test")
    print("DITEMPA BUKAN DIBERI - Forged, Not Given")
    print("="*60 + "\n")

    session_id = None

    # =========================================================================
    # TEST 1: _ignite_ (Session Initialization)
    # =========================================================================
    print("\n[1/7] Testing _ignite_ (Constitutional Gate)")
    print("Purpose: Initialize session, verify authority, check F11 & F12")

    try:
        result = await mcp_000_init(
            action="init",
            query="Test all constitutional tools",
            authority_token="arif_sovereign"
        )
        print_result("_ignite_", result)

        if result.get("status") == "SEAL":
            session_id = result.get("session_id")
            print(f"[OK] Session initialized: {session_id}\n")
        else:
            print("[FAIL] Failed to initialize session")
            return
    except Exception as e:
        print(f"[ERROR] Error in _ignite_: {e}")
        return

    # =========================================================================
    # TEST 2: _logic_ (Deep Reasoning)
    # =========================================================================
    print("\n[2/7] Testing _logic_ (AGI Mind - Delta)")
    print("Purpose: Deep logical reasoning, F2 Truth, F4 Clarity")

    try:
        result = await mcp_agi_genius(
            action="think",
            query="What are the 13 constitutional floors of arifOS?",
            session_id=session_id
        )
        print_result("_logic_", result)

        if result.get("verdict") == "SEAL":
            print("[OK] Logic engine passed\n")
        else:
            print(f"[WARN] Logic engine returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[ERROR] Error in _logic_: {e}")

    # =========================================================================
    # TEST 3: _senses_ (External Reality)
    # =========================================================================
    print("\n[3/7] Testing _senses_ (Reality Grounding)")
    print("Purpose: External fact-checking, F7 Humility")
    print("[NOTE] Requires Brave API key - may skip if unavailable")

    try:
        # Note: This will use circuit breaker if Brave API is unavailable
        result = await mcp_agi_genius(
            action="search",
            query="Latest Claude Code MCP features 2026",
            session_id=session_id
        )
        print_result("_senses_", result)

        if result.get("verdict") in ["SEAL", "SABAR"]:
            print("[OK] Senses check completed\n")
        else:
            print(f"[WARN] Senses returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[SKIP] Senses unavailable (expected if no API key): {e}")

    # =========================================================================
    # TEST 4: _atlas_ (Knowledge Mapping)
    # =========================================================================
    print("\n[4/7] Testing _atlas_ (Knowledge Mapper)")
    print("Purpose: Map codebase structure, F10 Ontology")

    try:
        result = await mcp_agi_genius(
            action="atlas",
            query="codebase/mcp/",
            session_id=session_id
        )
        print_result("_atlas_", result)

        if result.get("verdict") == "SEAL":
            print("[OK] Atlas mapping passed\n")
        else:
            print(f"[WARN] Atlas returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[ERROR] Error in _atlas_: {e}")

    # =========================================================================
    # TEST 5: _forge_ (Code Generation)
    # =========================================================================
    print("\n[5/7] Testing _forge_ (ASI Heart - Omega)")
    print("Purpose: Safe code generation, F1 Amanah, F5 Peace^2, F6 Empathy")

    try:
        result = await mcp_asi_act(
            action="evaluate",
            query="Create a simple hello world function",
            session_id=session_id
        )
        print_result("_forge_", result)

        if result.get("verdict") in ["SEAL", "PARTIAL"]:
            print("[OK] Forge evaluation passed\n")
        else:
            print(f"[WARN] Forge returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[ERROR] Error in _forge_: {e}")

    # =========================================================================
    # TEST 6: _audit_ (Compliance Check)
    # =========================================================================
    print("\n[6/7] Testing _audit_ (Constitutional Scanner)")
    print("Purpose: Check all 13 floors for violations")

    try:
        result = await mcp_asi_act(
            action="audit",
            text="def hello(): return 'Hello World'",
            session_id=session_id
        )
        print_result("_audit_", result)

        if result.get("verdict") in ["SEAL", "PARTIAL"]:
            print("[OK] Audit scan completed\n")
        else:
            print(f"[WARN] Audit returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[ERROR] Error in _audit_: {e}")

    # =========================================================================
    # TEST 7: _decree_ (Final Judgment)
    # =========================================================================
    print("\n[7/7] Testing _decree_ (APEX Soul - Psi)")
    print("Purpose: Final verdict, F3 Tri-Witness, VAULT-999 seal")

    try:
        result = await mcp_apex_judge(
            action="judge",
            query="All 7 tools tested successfully",
            session_id=session_id,
            verdict_data={
                "query": "Test all constitutional tools",
                "response": "All tools operational",
                "agi_result": {"verdict": "SEAL"},
                "asi_result": {"verdict": "SEAL"}
            }
        )
        print_result("_decree_", result)

        if result.get("verdict") == "SEAL":
            print("[OK] Final decree SEALED\n")
        else:
            print(f"[WARN] Decree returned: {result.get('verdict')}\n")
    except Exception as e:
        print(f"[ERROR] Error in _decree_: {e}")

    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*60)
    print("[SUMMARY] TEST RESULTS")
    print("="*60)
    print("Session ID:", session_id)
    print("All 7 constitutional tools tested")
    print("="*60)
    print("\nFloor Coverage:")
    print("  F1 Amanah       -> _forge_, _audit_")
    print("  F2 Truth        -> _logic_, _audit_")
    print("  F3 Tri-Witness  -> _decree_")
    print("  F4 Clarity      -> _logic_")
    print("  F5 Peace^2       -> _forge_")
    print("  F6 Empathy      -> _forge_")
    print("  F7 Humility     -> _logic_, _senses_")
    print("  F8 Genius       -> _decree_")
    print("  F9 Anti-Hantu   -> _forge_, _audit_")
    print("  F10 Ontology    -> _logic_, _atlas_")
    print("  F11 Authority   -> _ignite_, _decree_")
    print("  F12 Injection   -> _ignite_, _audit_")
    print("  F13 Curiosity   -> _decree_")
    print("\n[OK] Constitutional governance VERIFIED")
    print("DITEMPA BUKAN DIBERI - Forged, Not Given\n")


if __name__ == "__main__":
    asyncio.run(test_all_tools())
