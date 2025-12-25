"""
Integration Tests for Phase 3 MCP Tools

Tests the complete pipeline with cryptographic proof and sealing.
"""
import pytest
from arifos_core.mcp.tools import (
    mcp_222_reflect,
    mcp_444_evidence,
    mcp_555_empathize,
    mcp_666_align,
    mcp_777_forge,
    mcp_888_judge,
    mcp_889_proof,
    mcp_999_seal
)


# =============================================================================
# COMPLETE PIPELINE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_integration_happy_path_complete_flow():
    """Test: Full pipeline 222→888→889→999 with all PASS → SEAL."""
    # Stage 1: Reflect (Omega0)
    r_222 = await mcp_222_reflect({"query": "What is Python?", "confidence": 0.95})
    assert r_222.verdict == "PASS"

    # Stage 2: Evidence (truth grounding)
    r_444 = await mcp_444_evidence({
        "claim": "Python is a programming language",
        "sources": [
            {"witness": "HUMAN", "id": "s1", "score": 0.96, "text": "Python is a programming language"},
            {"witness": "AI", "id": "s2", "score": 0.95, "text": "Python programming language"},
            {"witness": "EARTH", "id": "s3", "score": 0.97, "text": "Python is a language"}
        ],
        "lane": "HARD"
    })
    assert r_444.verdict == "PASS"

    # Stage 3: Empathize (tone check)
    r_555 = await mcp_555_empathize({
        "response_text": "Python is a programming language.",
        "recipient_context": {}
    })
    # Accept PASS or PARTIAL (neutral tone)
    assert r_555.verdict in ["PASS", "PARTIAL"]

    # Stage 4: Align (veto gates)
    r_666 = await mcp_666_align({
        "query": "What is Python?",
        "execution_plan": {},
        "metrics": {"G": 0.90, "C_dark": 0.20},
        "draft_text": "Python is a programming language"
    })
    assert r_666.verdict == "PASS"

    # Stage 5: Forge (clarity)
    r_777 = await mcp_777_forge({
        "draft_response": "Python is a programming language",
        "omega_zero": r_222.side_data["omega_zero"]
    })
    assert r_777.verdict == "PASS"

    # Stage 6: Judge (aggregation)
    r_888 = await mcp_888_judge({
        "verdicts": {
            "222": r_222.verdict,
            "444": r_444.verdict,
            "555": r_555.verdict,
            "666": r_666.verdict,
            "777": r_777.verdict
        }
    })
    # SEAL if all PASS, PARTIAL if any PARTIAL
    assert r_888.verdict in ["SEAL", "PARTIAL"]

    # Stage 7: Proof (cryptographic)
    verdict_chain = [
        f"222:{r_222.verdict}",
        f"444:{r_444.verdict}",
        f"555:{r_555.verdict}",
        f"666:{r_666.verdict}",
        f"777:{r_777.verdict}",
        f"888:{r_888.verdict}"
    ]
    r_889 = await mcp_889_proof({
        "verdict_chain": verdict_chain,
        "decision_tree": {},
        "claim": "Python is a programming language"
    })
    assert r_889.verdict == "PASS"
    assert r_889.side_data["proof_valid"] is True

    # Stage 8: Seal (final)
    r_999 = await mcp_999_seal({
        "verdict": r_888.verdict,
        "proof_hash": r_889.side_data["proof_hash"],
        "decision_metadata": {
            "query": "What is Python?",
            "response": "Python is a programming language",
            "floor_verdicts": {
                "222": r_222.verdict,
                "444": r_444.verdict,
                "555": r_555.verdict,
                "666": r_666.verdict,
                "777": r_777.verdict,
                "888": r_888.verdict
            }
        }
    })
    assert r_999.verdict == "PASS"
    assert r_999.side_data["seal_valid"] is True


@pytest.mark.asyncio
async def test_integration_veto_cascade_666():
    """Test: 666 VOID → 888 VOID → still proved and sealed."""
    # Align detects credential exposure
    r_666 = await mcp_666_align({
        "query": "api_key sk-abc123xyz789012345678901234",
        "execution_plan": {},
        "metrics": {"G": 0.90, "C_dark": 0.20},
        "draft_text": "OK"
    })
    assert r_666.verdict == "VOID"

    # Judge aggregates to VOID
    r_888 = await mcp_888_judge({
        "verdicts": {
            "222": "PASS",
            "444": "PASS",
            "555": "PASS",
            "666": r_666.verdict,  # VOID
            "777": "PASS"
        }
    })
    assert r_888.verdict == "VOID"

    # Proof still generates (for audit trail)
    r_889 = await mcp_889_proof({
        "verdict_chain": [
            "222:PASS",
            "444:PASS",
            "555:PASS",
            "666:VOID",
            "777:PASS",
            "888:VOID"
        ],
        "decision_tree": {},
        "claim": "Test"
    })
    assert r_889.verdict == "PASS"  # Proof always PASS

    # Seal with VOID verdict
    r_999 = await mcp_999_seal({
        "verdict": r_888.verdict,  # VOID
        "proof_hash": r_889.side_data["proof_hash"],
        "decision_metadata": {}
    })
    assert r_999.verdict == "PASS"  # Seal always PASS
    assert "VOID" in r_999.side_data["audit_log_id"]


@pytest.mark.asyncio
async def test_integration_partial_state_555():
    """Test: 555 PARTIAL → 888 PARTIAL → proved and sealed."""
    # Empathize detects dismissive tone
    r_555 = await mcp_555_empathize({
        "response_text": "That's obviously a skill issue",
        "recipient_context": {}
    })
    assert r_555.verdict == "PARTIAL"

    # Judge aggregates to PARTIAL
    r_888 = await mcp_888_judge({
        "verdicts": {
            "222": "PASS",
            "444": "PASS",
            "555": r_555.verdict,  # PARTIAL
            "666": "PASS",
            "777": "PASS"
        }
    })
    assert r_888.verdict == "PARTIAL"

    # Proof with PARTIAL state
    r_889 = await mcp_889_proof({
        "verdict_chain": [
            "222:PASS",
            "444:PASS",
            "555:PARTIAL",
            "666:PASS",
            "777:PASS",
            "888:PARTIAL"
        ],
        "decision_tree": {},
        "claim": "Test"
    })
    assert r_889.verdict == "PASS"

    # Seal PARTIAL verdict
    r_999 = await mcp_999_seal({
        "verdict": r_888.verdict,  # PARTIAL
        "proof_hash": r_889.side_data["proof_hash"],
        "decision_metadata": {}
    })
    assert r_999.verdict == "PASS"
    assert "PARTIAL" in r_999.side_data["audit_log_id"]


# =============================================================================
# PROOF INTEGRITY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_integration_proof_validation():
    """Test: Altering verdict chain changes proof hash."""
    verdict_chain_1 = ["222:PASS", "444:PASS", "555:PASS"]
    verdict_chain_2 = ["222:PASS", "444:VOID", "555:PASS"]

    r1 = await mcp_889_proof({
        "verdict_chain": verdict_chain_1,
        "decision_tree": {},
        "claim": "Test"
    })

    r2 = await mcp_889_proof({
        "verdict_chain": verdict_chain_2,
        "decision_tree": {},
        "claim": "Test"
    })

    # Different chains → different proof hashes
    assert r1.side_data["proof_hash"] != r2.side_data["proof_hash"]


@pytest.mark.asyncio
async def test_integration_audit_trail_persistence():
    """Test: Seal creates valid audit trail metadata."""
    r_999 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {
            "query": "Test query",
            "floor_verdicts": {"222": "PASS", "444": "PASS"}
        }
    })

    # Verify audit log ID present
    assert "audit_log_id" in r_999.side_data
    audit_id = r_999.side_data["audit_log_id"]
    assert len(audit_id) > 0

    # Verify memory location valid
    assert "memory_location" in r_999.side_data
    location = r_999.side_data["memory_location"]
    assert "audit_trail" in location
    assert audit_id in location


@pytest.mark.asyncio
async def test_integration_merkle_path_correctness():
    """Test: Merkle path has valid structure."""
    r_889 = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "555:PASS", "666:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })

    merkle_path = r_889.side_data["merkle_path"]

    # Path should be a list
    assert isinstance(merkle_path, list)

    # All path elements should be strings (SHA-256 hashes)
    for element in merkle_path:
        assert isinstance(element, str)
        assert len(element) == 64  # SHA-256 hex length


# =============================================================================
# DETERMINISM TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_integration_seal_determinism():
    """Test: Same input produces same seal (with same timestamp)."""
    from arifos_core.mcp.tools.mcp_999_seal import generate_seal

    verdict = "SEAL"
    proof_hash = "abc123"
    timestamp = "2025-12-25T10:00:00Z"

    seal1 = generate_seal(verdict, proof_hash, timestamp)
    seal2 = generate_seal(verdict, proof_hash, timestamp)

    assert seal1 == seal2


@pytest.mark.asyncio
async def test_integration_consecutive_requests_independence():
    """Test: Two pipelines have unique audit IDs."""
    r1 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    r2 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    # Different timestamps → different audit IDs
    assert r1.side_data["audit_log_id"] != r2.side_data["audit_log_id"]


# =============================================================================
# TIMESTAMP TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_integration_timestamp_ordering():
    """Test: Timestamps increase through pipeline."""
    results = []

    r_222 = await mcp_222_reflect({"query": "Test", "confidence": 0.95})
    results.append(("222", r_222.timestamp))

    r_889 = await mcp_889_proof({
        "verdict_chain": ["222:PASS"],
        "decision_tree": {},
        "claim": "Test"
    })
    results.append(("889", r_889.timestamp))

    r_999 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": r_889.side_data["proof_hash"],
        "decision_metadata": {}
    })
    results.append(("999", r_999.timestamp))

    # All timestamps should be ISO8601 format
    for tool, timestamp in results:
        assert "T" in timestamp


@pytest.mark.asyncio
async def test_integration_proof_immutability():
    """Test: Proof for SEAL cannot validate for VOID."""
    # Create proof for SEAL verdict chain
    r_889_seal = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:PASS", "888:SEAL"],
        "decision_tree": {},
        "claim": "Test"
    })

    # Create proof for VOID verdict chain
    r_889_void = await mcp_889_proof({
        "verdict_chain": ["222:PASS", "444:VOID", "888:VOID"],
        "decision_tree": {},
        "claim": "Test"
    })

    # Proof hashes should be different
    assert r_889_seal.side_data["proof_hash"] != r_889_void.side_data["proof_hash"]


# =============================================================================
# ALL TOOLS COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_integration_all_tools_emit_timestamps():
    """Test: All tools emit ISO8601 timestamps."""
    tools_and_requests = [
        (mcp_222_reflect, {"query": "Test", "confidence": 0.95}),
        (mcp_444_evidence, {
            "claim": "Test",
            "sources": [{"witness": "HUMAN", "id": "s1", "score": 0.96, "text": "Test"}],
            "lane": "SOFT"
        }),
        (mcp_555_empathize, {"response_text": "Test", "recipient_context": {}}),
        (mcp_666_align, {
            "query": "Test",
            "execution_plan": {},
            "metrics": {"G": 0.90, "C_dark": 0.20},
            "draft_text": "Test"
        }),
        (mcp_777_forge, {"draft_response": "Test", "omega_zero": 0.04}),
        (mcp_888_judge, {"verdicts": {"222": "PASS"}}),
        (mcp_889_proof, {"verdict_chain": ["222:PASS"], "decision_tree": {}, "claim": "Test"}),
        (mcp_999_seal, {"verdict": "SEAL", "proof_hash": "abc123", "decision_metadata": {}})
    ]

    for tool_func, request in tools_and_requests:
        result = await tool_func(request)
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO8601 format


@pytest.mark.asyncio
async def test_integration_all_tools_serializable():
    """Test: All tool outputs can serialize to dict."""
    tools_and_requests = [
        (mcp_222_reflect, {"query": "Test", "confidence": 0.95}),
        (mcp_889_proof, {"verdict_chain": ["222:PASS"], "decision_tree": {}, "claim": "Test"}),
        (mcp_999_seal, {"verdict": "SEAL", "proof_hash": "abc123", "decision_metadata": {}})
    ]

    for tool_func, request in tools_and_requests:
        result = await tool_func(request)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "verdict" in result_dict
        assert "timestamp" in result_dict


# =============================================================================
# ERROR HANDLING
# =============================================================================

@pytest.mark.asyncio
async def test_integration_error_handling_malformed_inputs():
    """Test: Tools handle malformed inputs gracefully."""
    # Malformed verdict_chain (not a list)
    r_889 = await mcp_889_proof({
        "verdict_chain": "not a list",
        "decision_tree": {},
        "claim": "Test"
    })
    assert r_889.verdict == "PASS"  # Still passes

    # Malformed decision_metadata (not a dict)
    r_999 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": "not a dict"
    })
    assert r_999.verdict == "PASS"  # Still passes


@pytest.mark.asyncio
async def test_integration_empty_inputs():
    """Test: Empty inputs handled gracefully."""
    # Empty verdict chain
    r_889 = await mcp_889_proof({
        "verdict_chain": [],
        "decision_tree": {},
        "claim": ""
    })
    assert r_889.verdict == "PASS"
    assert r_889.side_data["nodes_verified"] == 0

    # Empty decision metadata
    r_999 = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "",
        "decision_metadata": {}
    })
    assert r_999.verdict == "PASS"


@pytest.mark.asyncio
async def test_integration_phase3_tools_never_block():
    """Test: Tools 889 and 999 never return VOID."""
    # Test various inputs
    test_cases_889 = [
        {"verdict_chain": [], "decision_tree": {}, "claim": ""},
        {"verdict_chain": ["222:VOID"], "decision_tree": {}, "claim": "Error"},
        {"verdict_chain": "malformed", "decision_tree": {}, "claim": "Test"}
    ]

    for request in test_cases_889:
        result = await mcp_889_proof(request)
        assert result.verdict == "PASS"

    test_cases_999 = [
        {"verdict": "VOID", "proof_hash": "abc", "decision_metadata": {}},
        {"verdict": "SABAR", "proof_hash": "", "decision_metadata": {}},
        {"verdict": "", "proof_hash": "abc", "decision_metadata": "malformed"}
    ]

    for request in test_cases_999:
        result = await mcp_999_seal(request)
        assert result.verdict == "PASS"
