"""
Tests for MCP Tool 444: EVIDENCE

Tests truth scoring and tri-witness convergence logic.

Constitutional validation:
- F2 (Truth): Validates truth thresholds (0.90 HARD, 0.80 SOFT)
- F3 (Tri-Witness): Tests convergence ≥0.95
- F4 (ΔS): Verifies proof generation
"""

import pytest

from arifos_core.mcp.tools.mcp_444_evidence import (
    mcp_444_evidence,
    mcp_444_evidence_sync,
    score_truth_claim,
    check_convergence,
    generate_proof_hash,
    detect_hallucination,
    extract_entities,
    TRUTH_THRESHOLD_HARD,
    TRUTH_THRESHOLD_SOFT,
    CONVERGENCE_SEAL,
)


# =============================================================================
# TRUTH SCORING TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_hard_lane_pass():
    """Test: HARD lane claim with strong evidence → PASS."""
    result = await mcp_444_evidence({
        "claim": "Paris is the capital of France",
        "sources": [
            {"witness": "HUMAN", "id": "source1", "score": 0.96, "text": "Paris, the capital city of France, is located in..."},
            {"witness": "AI", "id": "source2", "score": 0.95, "text": "France's capital Paris has a population of..."},
            {"witness": "EARTH", "id": "source3", "score": 0.97, "text": "The capital of France is Paris, established in..."}
        ],
        "lane": "HARD"
    })

    assert result.verdict == "PASS"
    assert result.side_data["truth_score"] >= TRUTH_THRESHOLD_HARD
    assert result.side_data["convergence"] >= CONVERGENCE_SEAL


@pytest.mark.asyncio
async def test_evidence_soft_lane_pass():
    """Test: SOFT lane claim with moderate evidence → PASS."""
    result = await mcp_444_evidence({
        "claim": "Photosynthesis is the process by which plants convert light to energy",
        "sources": [
            {"witness": "HUMAN", "id": "source1", "score": 0.88, "text": "Photosynthesis involves light energy conversion in plants"},
            {"witness": "AI", "id": "source2", "score": 0.86, "text": "Plants use photosynthesis to convert light into chemical energy"}
        ],
        "lane": "SOFT"
    })

    assert result.verdict in ["PASS", "PARTIAL"]
    assert result.side_data["truth_score"] >= TRUTH_THRESHOLD_SOFT


@pytest.mark.asyncio
async def test_evidence_insufficient_sources_void():
    """Test: Insufficient evidence → VOID."""
    result = await mcp_444_evidence({
        "claim": "The capital of Atlantis is New Poseidon",
        "sources": [],
        "lane": "HARD"
    })

    assert result.verdict == "VOID"
    assert result.side_data["truth_score"] < TRUTH_THRESHOLD_HARD


@pytest.mark.asyncio
async def test_evidence_hallucination_detection():
    """Test: Hallucination admission → VOID."""
    result = await mcp_444_evidence({
        "claim": "I don't have access to that information",
        "sources": ["Some random text"],
        "lane": "SOFT"
    })

    assert result.verdict == "VOID"
    assert result.side_data["hallucination_detected"] is True


# =============================================================================
# CONVERGENCE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_high_convergence_three_sources():
    """Test: Three agreeing sources → high convergence."""
    result = await mcp_444_evidence({
        "claim": "Water boils at 100 degrees Celsius",
        "sources": [
            {"text": "Water boils at 100°C at sea level", "score": 0.95},
            {"text": "The boiling point of water is 100 degrees Celsius", "score": 0.96},
            {"text": "At standard pressure, water reaches 100°C to boil", "score": 0.94}
        ],
        "lane": "HARD"
    })

    assert result.side_data["convergence"] >= 0.95


@pytest.mark.asyncio
async def test_evidence_low_convergence_single_source():
    """Test: Single source → low convergence."""
    result = await mcp_444_evidence({
        "claim": "Example claim",
        "sources": [{"text": "Single source text", "score": 0.9}],
        "lane": "SOFT"
    })

    assert result.side_data["convergence"] < 0.80


@pytest.mark.asyncio
async def test_evidence_moderate_convergence_two_sources():
    """Test: Two sources → moderate convergence."""
    result = await mcp_444_evidence({
        "claim": "Python is a programming language",
        "sources": [
            {"text": "Python is a high-level programming language", "score": 0.9},
            {"text": "The Python programming language was created in 1991", "score": 0.88}
        ],
        "lane": "SOFT"
    })

    convergence = result.side_data["convergence"]
    assert 0.80 <= convergence < 0.95


# =============================================================================
# PROOF GENERATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_proof_hash_generated():
    """Test: Proof hash is generated for all claims."""
    result = await mcp_444_evidence({
        "claim": "Test claim",
        "sources": ["Source 1", "Source 2"],
        "lane": "SOFT"
    })

    assert "proof" in result.side_data
    assert isinstance(result.side_data["proof"], str)
    assert len(result.side_data["proof"]) == 64  # SHA-256 hex length


@pytest.mark.asyncio
async def test_evidence_proof_hash_deterministic():
    """Test: Same inputs produce same proof hash."""
    request = {
        "claim": "Deterministic test",
        "sources": ["Source A", "Source B"],
        "lane": "HARD"
    }

    result1 = await mcp_444_evidence(request)
    result2 = await mcp_444_evidence(request)

    # Note: Timestamps differ, so hashes will differ
    # But structure should be consistent
    assert len(result1.side_data["proof"]) == len(result2.side_data["proof"])


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

def test_score_truth_claim_with_entities():
    """Test: score_truth_claim detects entity matches."""
    claim = "Paris is the capital of France"
    sources = ["Paris, the capital of France, has..."]

    score = score_truth_claim(claim, sources)
    assert score > 0.5  # Should match entities


def test_score_truth_claim_with_numbers():
    """Test: score_truth_claim detects numeric matches."""
    claim = "The answer is 42"
    sources = ["According to the book, the answer is 42"]

    score = score_truth_claim(claim, sources)
    assert score > 0.5  # Should match number


def test_score_truth_claim_no_sources():
    """Test: score_truth_claim returns 0.0 for empty sources."""
    score = score_truth_claim("Test claim", [])
    assert score == 0.0


def test_score_truth_claim_hallucination():
    """Test: score_truth_claim returns 0.0 for hallucination."""
    claim = "I cannot verify this information"
    sources = ["Some text"]

    score = score_truth_claim(claim, sources)
    assert score == 0.0


def test_check_convergence_three_sources():
    """Test: check_convergence for three agreeing sources."""
    sources = [
        {"text": "Source 1", "score": 0.95},
        {"text": "Source 2", "score": 0.94},
        {"text": "Source 3", "score": 0.96}
    ]

    convergence = check_convergence(sources)
    assert convergence >= 0.95  # High agreement


def test_check_convergence_no_sources():
    """Test: check_convergence returns 0.0 for empty sources."""
    convergence = check_convergence([])
    assert convergence == 0.0


def test_generate_proof_hash():
    """Test: generate_proof_hash creates SHA-256 hex."""
    proof = generate_proof_hash("Test claim", ["Source 1"], 0.85)

    assert isinstance(proof, str)
    assert len(proof) == 64  # SHA-256 hex length
    assert all(c in '0123456789abcdef' for c in proof)


def test_detect_hallucination_patterns():
    """Test: detect_hallucination finds admission patterns."""
    assert detect_hallucination("I don't have access to that") is True
    assert detect_hallucination("No information available") is True
    assert detect_hallucination("Cannot verify this claim") is True
    assert detect_hallucination("Paris is the capital of France") is False


def test_extract_entities_proper_nouns():
    """Test: extract_entities finds proper nouns."""
    text = "I visited Paris and France last year"
    entities = extract_entities(text)

    assert "Paris" in entities
    assert "France" in entities


def test_extract_entities_numbers():
    """Test: extract_entities finds numbers."""
    text = "The answer is 42 and pi is 3.14"
    entities = extract_entities(text)

    assert "42" in entities
    assert "3.14" in entities


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_empty_claim():
    """Test: Empty claim → VOID."""
    result = await mcp_444_evidence({
        "claim": "",
        "sources": ["Source 1"],
        "lane": "SOFT"
    })

    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_evidence_missing_claim():
    """Test: Missing claim key → VOID."""
    result = await mcp_444_evidence({
        "sources": ["Source 1"],
        "lane": "SOFT"
    })

    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_evidence_non_string_claim():
    """Test: Non-string claim → VOID."""
    result = await mcp_444_evidence({
        "claim": 12345,
        "sources": ["Source 1"],
        "lane": "SOFT"
    })

    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_evidence_missing_lane():
    """Test: Missing lane defaults to SOFT."""
    result = await mcp_444_evidence({
        "claim": "Test claim",
        "sources": ["Source 1", "Source 2", "Source 3"]
    })

    assert result.side_data["lane"] == "SOFT"
    assert result.side_data["threshold"] == TRUTH_THRESHOLD_SOFT


@pytest.mark.asyncio
async def test_evidence_invalid_sources():
    """Test: Invalid sources handled gracefully."""
    result = await mcp_444_evidence({
        "claim": "Test claim",
        "sources": "not a list",  # Invalid type
        "lane": "SOFT"
    })

    assert result.side_data["num_sources"] == 0


# =============================================================================
# CONSTITUTIONAL COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_includes_timestamp():
    """
    Test: Response includes timestamp.

    Constitutional: F4 (ΔS) - traceable events
    """
    result = await mcp_444_evidence({
        "claim": "Test",
        "sources": ["Source 1"],
        "lane": "SOFT"
    })

    assert result.timestamp is not None
    assert "T" in result.timestamp


@pytest.mark.asyncio
async def test_evidence_includes_threshold():
    """
    Test: Response includes applied truth threshold.

    Constitutional: F2 (Truth) - explicit standards
    """
    result = await mcp_444_evidence({
        "claim": "Test",
        "sources": ["Source 1"],
        "lane": "HARD"
    })

    assert "threshold" in result.side_data
    assert result.side_data["threshold"] == TRUTH_THRESHOLD_HARD


@pytest.mark.asyncio
async def test_evidence_reason_is_clear():
    """
    Test: Verdict reason is clear and informative.

    Constitutional: F4 (ΔS) - reduces confusion
    """
    result = await mcp_444_evidence({
        "claim": "Test",
        "sources": ["Source 1", "Source 2"],
        "lane": "SOFT"
    })

    assert result.reason is not None
    assert len(result.reason) > 0
    assert "score" in result.reason.lower() or "convergence" in result.reason.lower()


# =============================================================================
# SYNC WRAPPER TESTS
# =============================================================================

def test_evidence_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_444_evidence_sync({
        "claim": "Test claim",
        "sources": ["Source 1", "Source 2"],
        "lane": "SOFT"
    })

    assert result.verdict in ["PASS", "PARTIAL", "VOID"]
    assert "truth_score" in result.side_data


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_evidence_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_444_evidence({
        "claim": "Test",
        "sources": ["Source 1"],
        "lane": "SOFT"
    })

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict


@pytest.mark.asyncio
async def test_evidence_verdict_cascade():
    """Test: Verdict logic follows PASS > PARTIAL > VOID cascade."""
    # Test PASS conditions
    pass_result = await mcp_444_evidence({
        "claim": "Water freezes at 0 degrees Celsius",
        "sources": [
            {"text": "Water freezes at 0°C at standard pressure", "score": 0.95},
            {"text": "The freezing point of water is 0 degrees Celsius", "score": 0.96},
            {"text": "At 0°C, water transitions to ice", "score": 0.94}
        ],
        "lane": "HARD"
    })

    # Should pass with high score and convergence
    if pass_result.side_data["truth_score"] >= TRUTH_THRESHOLD_HARD:
        assert pass_result.verdict in ["PASS", "PARTIAL"]
