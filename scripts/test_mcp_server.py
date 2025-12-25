"""
Test script for arifOS MCP Server integration.

Verifies that all 15 tools are registered and demonstrates
the full constitutional pipeline (000->999).
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add arifos_core to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from arifos_core.mcp.server import mcp_server


def test_server_info():
    """Test: Server info shows all 15 tools."""
    print("=" * 80)
    print("TEST 1: Server Info")
    print("=" * 80)

    info = mcp_server.get_info()

    print(f"Server: {info['name']} v{info['version']}")
    print(f"Description: {info['description']}")
    print(f"\nTotal Tools: {info['tool_count']}")

    for phase, tools in info['phases'].items():
        print(f"\n{phase.upper()}:")
        for tool in tools:
            print(f"  - {tool}")

    assert info['tool_count'] == 15, f"Expected 15 tools, got {info['tool_count']}"
    print("\n[OK] Server info test PASSED")
    return True


def test_list_tools():
    """Test: List all tool descriptions."""
    print("\n" + "=" * 80)
    print("TEST 2: List Tool Descriptions")
    print("=" * 80)

    tools = mcp_server.list_tools()

    print(f"\nFound {len(tools)} tools:")

    # Show constitutional pipeline tools
    pipeline_tools = [
        "mcp_000_reset", "mcp_111_sense", "mcp_222_reflect",
        "mcp_444_evidence", "mcp_555_empathize", "mcp_666_align",
        "mcp_777_forge", "mcp_888_judge", "mcp_889_proof", "mcp_999_seal"
    ]

    for tool_name in pipeline_tools:
        if tool_name in tools:
            desc = tools[tool_name]['description']
            # Truncate description for display
            desc_short = desc[:80] + "..." if len(desc) > 80 else desc
            print(f"  [OK] {tool_name}: {desc_short}")
        else:
            print(f"  [X] {tool_name}: MISSING!")

    assert len(tools) == 15, f"Expected 15 tools, got {len(tools)}"
    print("\n[OK] Tool listing test PASSED")
    return True


def test_full_pipeline():
    """Test: Full constitutional pipeline (000->111->222->...->999)."""
    print("\n" + "=" * 80)
    print("TEST 3: Full Constitutional Pipeline")
    print("=" * 80)

    # Step 1: Initialize session (000)
    print("\n[000] RESET - Session initialization")
    r_000 = mcp_server.call_tool("mcp_000_reset", {})
    print(f"  Verdict: {r_000['verdict']}")
    print(f"  Session ID: {r_000['side_data']['session_id']}")
    assert r_000['verdict'] == "PASS"

    # Step 2: Classify query (111)
    print("\n[111] SENSE - Lane classification")
    query = "What is the capital of France?"
    r_111 = mcp_server.call_tool("mcp_111_sense", {"query": query})
    print(f"  Verdict: {r_111['verdict']}")
    print(f"  Lane: {r_111['side_data']['lane']}")
    print(f"  Threshold: {r_111['side_data']['truth_threshold']}")
    assert r_111['verdict'] == "PASS"
    lane = r_111['side_data']['lane']

    # Step 3: Predict Omega0 (222)
    print("\n[222] REFLECT - Omega0 prediction")
    r_222 = mcp_server.call_tool("mcp_222_reflect", {
        "query": query,
        "confidence": 0.95
    })
    print(f"  Verdict: {r_222['verdict']}")
    print(f"  Omega0: {r_222['side_data']['omega_zero']:.4f}")
    print(f"  Quality: {r_222['side_data']['epistemic_quality']}")
    assert r_222['verdict'] == "PASS"
    omega_zero = r_222['side_data']['omega_zero']

    # Step 4: Validate evidence (444)
    print("\n[444] EVIDENCE - Truth grounding")
    r_444 = mcp_server.call_tool("mcp_444_evidence", {
        "claim": "Paris is the capital of France",
        "sources": [
            {"witness": "HUMAN", "id": "s1", "score": 0.96, "text": "Paris is the capital of France"},
            {"witness": "AI", "id": "s2", "score": 0.95, "text": "France's capital is Paris"},
            {"witness": "EARTH", "id": "s3", "score": 0.97, "text": "Capital of France: Paris"}
        ],
        "lane": lane
    })
    print(f"  Verdict: {r_444['verdict']}")
    print(f"  Truth Score: {r_444['side_data']['truth_score']:.2f}")
    print(f"  Convergence: {r_444['side_data']['convergence']:.2f}")
    assert r_444['verdict'] in ["PASS", "PARTIAL"]

    # Step 5: Check tone (555)
    print("\n[555] EMPATHIZE - Tone & power check")
    r_555 = mcp_server.call_tool("mcp_555_empathize", {
        "response_text": "Paris is the capital of France.",
        "recipient_context": {}
    })
    print(f"  Verdict: {r_555['verdict']}")
    print(f"  Peace^2: {r_555['side_data']['peace_score']:.2f}")
    print(f"  kappa_r: {r_555['side_data']['kappa_r']:.2f}")
    assert r_555['verdict'] in ["PASS", "PARTIAL"]

    # Step 6: Veto gate check (666)
    print("\n[666] ALIGN - Veto gates (F1/F8/F9)")
    r_666 = mcp_server.call_tool("mcp_666_align", {
        "query": query,
        "execution_plan": {},
        "metrics": {"G": 0.90, "C_dark": 0.20},
        "draft_text": "Paris is the capital of France"
    })
    print(f"  Verdict: {r_666['verdict']}")
    print(f"  F1: {'PASS' if not r_666['side_data']['f1_violation'] else 'VOID'}")
    print(f"  F8: {'PASS' if not r_666['side_data']['f8_violation'] else 'VOID'}")
    print(f"  F9: {'PASS' if not r_666['side_data']['f9_violation'] else 'VOID'}")
    assert r_666['verdict'] in ["PASS", "VOID"]

    # Step 7: Clarity refinement (777)
    print("\n[777] FORGE - Clarity & humility")
    r_777 = mcp_server.call_tool("mcp_777_forge", {
        "draft_response": "Paris is the capital of France",
        "omega_zero": omega_zero
    })
    print(f"  Verdict: {r_777['verdict']}")
    print(f"  Refined: {r_777['side_data']['refined_response']}")
    print(f"  Clarity: {r_777['side_data']['clarity_score']:.2f}")
    assert r_777['verdict'] == "PASS"

    # Step 8: Aggregate verdicts (888)
    print("\n[888] JUDGE - Verdict aggregation")
    r_888 = mcp_server.call_tool("mcp_888_judge", {
        "verdicts": {
            "222": r_222['verdict'],
            "444": r_444['verdict'],
            "555": r_555['verdict'],
            "666": r_666['verdict'],
            "777": r_777['verdict']
        }
    })
    print(f"  Final Verdict: {r_888['verdict']}")
    print(f"  Confidence: {r_888['side_data']['confidence']:.2f}")
    print(f"  Reason: {r_888['reason']}")
    assert r_888['verdict'] in ["SEAL", "PARTIAL", "VOID"]

    # Step 9: Generate proof (889)
    print("\n[889] PROOF - Cryptographic proof")
    verdict_chain = [
        f"222:{r_222['verdict']}",
        f"444:{r_444['verdict']}",
        f"555:{r_555['verdict']}",
        f"666:{r_666['verdict']}",
        f"777:{r_777['verdict']}",
        f"888:{r_888['verdict']}"
    ]
    r_889 = mcp_server.call_tool("mcp_889_proof", {
        "verdict_chain": verdict_chain,
        "decision_tree": {},
        "claim": "Paris is the capital of France"
    })
    print(f"  Verdict: {r_889['verdict']}")
    print(f"  Proof Hash: {r_889['side_data']['proof_hash'][:16]}...")
    print(f"  Proof Valid: {r_889['side_data']['proof_valid']}")
    print(f"  Nodes Verified: {r_889['side_data']['nodes_verified']}")
    assert r_889['verdict'] == "PASS"
    assert r_889['side_data']['proof_valid'] is True

    # Step 10: Seal verdict (999)
    print("\n[999] SEAL - Final sealing")
    r_999 = mcp_server.call_tool("mcp_999_seal", {
        "verdict": r_888['verdict'],
        "proof_hash": r_889['side_data']['proof_hash'],
        "decision_metadata": {
            "query": query,
            "response": "Paris is the capital of France",
            "floor_verdicts": {
                "222": r_222['verdict'],
                "444": r_444['verdict'],
                "555": r_555['verdict'],
                "666": r_666['verdict'],
                "777": r_777['verdict'],
                "888": r_888['verdict']
            }
        }
    })
    print(f"  Verdict: {r_999['verdict']}")
    print(f"  Audit Log ID: {r_999['side_data']['audit_log_id']}")
    print(f"  Memory Location: {r_999['side_data']['memory_location']}")
    print(f"  Seal Valid: {r_999['side_data']['seal_valid']}")
    assert r_999['verdict'] == "PASS"
    assert r_999['side_data']['seal_valid'] is True

    print("\n[OK] Full pipeline test PASSED")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("arifOS MCP Server - Integration Tests")
    print("=" * 80)

    try:
        test_server_info()
        test_list_tools()
        test_full_pipeline()

        print("\n" + "=" * 80)
        print("ALL TESTS PASSED [OK]")
        print("=" * 80)
        print("\nThe arifOS MCP Server is ready for IDE integration.")
        print("All 15 tools are registered and the constitutional pipeline works end-to-end.")
        print("\nDITEMPA BUKAN DIBERI - The server is forged.\n")

        return 0
    except Exception as e:
        print(f"\n[X] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
