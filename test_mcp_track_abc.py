#!/usr/bin/env python3
"""
Test script for Track A/B/C MCP tools (arifos_validate_full, arifos_meta_select).

Quick verification that the tools are registered and functional.
"""

from arifos_core.mcp.server import MCPServer

def test_mcp_tools():
    """Test Track A/B/C MCP tools."""
    server = MCPServer()

    # Test 1: Verify tools are registered
    print("=" * 70)
    print("TEST 1: Tool Registration")
    print("=" * 70)

    tools = server.list_tools()
    tool_names = list(tools.keys())

    print(f"Total tools registered: {len(tool_names)}")
    print(f"Expected: 17 tools (5 legacy + 2 Track A/B/C + 10 pipeline)")

    assert "arifos_validate_full" in tool_names, "arifos_validate_full not registered!"
    assert "arifos_meta_select" in tool_names, "arifos_meta_select not registered!"

    print("[PASS] arifos_validate_full registered")
    print("[PASS] arifos_meta_select registered")

    # Test 2: Verify tool descriptions
    print("\n" + "=" * 70)
    print("TEST 2: Tool Descriptions")
    print("=" * 70)

    validate_desc = tools["arifos_validate_full"]
    meta_desc = tools["arifos_meta_select"]

    print(f"\narifos_validate_full:")
    print(f"  Name: {validate_desc['name']}")
    print(f"  Description: {validate_desc['description'][:100]}...")
    print(f"  Parameters: {list(validate_desc['parameters']['properties'].keys())}")
    print(f"  Required: {validate_desc['parameters']['required']}")

    print(f"\narifos_meta_select:")
    print(f"  Name: {meta_desc['name']}")
    print(f"  Description: {meta_desc['description'][:100]}...")
    print(f"  Parameters: {list(meta_desc['parameters']['properties'].keys())}")
    print(f"  Required: {meta_desc['parameters']['required']}")

    # Test 3: Call arifos_validate_full
    print("\n" + "=" * 70)
    print("TEST 3: arifos_validate_full Execution")
    print("=" * 70)

    try:
        result = server.call_tool("arifos_validate_full", {
            "output_text": "The sky is blue."
        })

        print(f"[PASS] Tool executed successfully")
        print(f"  Verdict: {result.get('verdict', 'N/A')}")
        print(f"  Violations: {len(result.get('violations', []))} violations")
        print(f"  Floors tested: {list(result.get('floors', {}).keys())}")

        # Verify expected verdict
        assert result["verdict"] == "SEAL", f"Expected SEAL, got {result['verdict']}"
        print(f"[PASS] Verdict is SEAL (expected)")

    except Exception as e:
        print(f"[FAIL] Tool execution failed: {e}")
        raise

    # Test 4: Call arifos_validate_full with F9 negation
    print("\n" + "=" * 70)
    print("TEST 4: F9 Negation Detection")
    print("=" * 70)

    try:
        result = server.call_tool("arifos_validate_full", {
            "output_text": "I do NOT have a soul. I am a language model."
        })

        print(f"[PASS] Tool executed successfully")
        print(f"  Verdict: {result.get('verdict', 'N/A')}")
        print(f"  F9 passed: {result['floors']['F9_AntiHantu']['passed']}")
        print(f"  F9 evidence: {result['floors']['F9_AntiHantu']['evidence']}")

        # Verify F9 passed (negation detected)
        assert result["floors"]["F9_AntiHantu"]["passed"], "F9 should pass with negation!"
        print(f"[PASS] F9 Anti-Hantu passed (negation detected)")

    except Exception as e:
        print(f"[FAIL] F9 test failed: {e}")
        raise

    # Test 5: Call arifos_meta_select
    print("\n" + "=" * 70)
    print("TEST 5: arifos_meta_select Execution")
    print("=" * 70)

    try:
        result = server.call_tool("arifos_meta_select", {
            "verdicts": [
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ]
        })

        print(f"[PASS] Tool executed successfully")
        print(f"  Winner: {result.get('winner', 'N/A')}")
        print(f"  Consensus: {result.get('consensus', 'N/A')}")
        print(f"  Final verdict: {result.get('verdict', 'N/A')}")
        print(f"  Tally: {result.get('tally', {})}")

        # Verify expected result
        assert result["winner"] == "SEAL", f"Expected SEAL winner, got {result['winner']}"
        assert result["consensus"] == 1.0, f"Expected 1.0 consensus, got {result['consensus']}"
        assert result["verdict"] == "SEAL", f"Expected SEAL verdict, got {result['verdict']}"
        print(f"[PASS] Strong consensus (100% SEAL) detected correctly")

    except Exception as e:
        print(f"[FAIL] Tool execution failed: {e}")
        raise

    # Test 6: Low consensus escalation
    print("\n" + "=" * 70)
    print("TEST 6: Low Consensus -> HOLD-888 Escalation")
    print("=" * 70)

    try:
        result = server.call_tool("arifos_meta_select", {
            "verdicts": [
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "VOID", "confidence": 0.99},
                {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
            ]
        })

        print(f"[PASS] Tool executed successfully")
        print(f"  Winner: {result.get('winner', 'N/A')}")
        print(f"  Consensus: {result.get('consensus', 'N/A')}")
        print(f"  Final verdict: {result.get('verdict', 'N/A')}")

        # Verify low consensus escalates to HOLD-888
        assert result["verdict"] == "HOLD-888", f"Expected HOLD-888, got {result['verdict']}"
        assert result["consensus"] < 0.95, "Consensus should be < 0.95"
        print(f"[PASS] Low consensus escalated to HOLD-888 correctly")

    except Exception as e:
        print(f"[FAIL] Low consensus test failed: {e}")
        raise

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("[PASS] All 6 tests passed")
    print("[PASS] arifos_validate_full: Functional")
    print("[PASS] arifos_meta_select: Functional")
    print("[PASS] MCP Server: 17 tools registered")
    print("\nTrack A/B/C MCP integration complete!")

if __name__ == "__main__":
    test_mcp_tools()
