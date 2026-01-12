"""
Tests for MCP Tool 111: SENSE

Tests lane classification logic and constitutional compliance.

Constitutional validation:
- F2 (Truth): Lane determines truth threshold
- F4 (ΔS): Explicit routing reduces confusion
- F9 (Anti-Hantu): Early detection of violations
"""

import pytest

from arifos_core.mcp.tools.mcp_111_sense import (
    mcp_111_sense,
    mcp_111_sense_sync,
    count_entities,
    count_assertions,
    detect_violations,
    is_phatic,
    is_soft_intent,
    classify_lane,
)


# =============================================================================
# LANE CLASSIFICATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_sense_hard_lane_capital_query():
    """Test: Factual query classified as HARD lane."""
    result = await mcp_111_sense({
        "query": "What is the capital of France?",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "HARD"
    assert result.side_data["truth_threshold"] == 0.90


@pytest.mark.asyncio
async def test_sense_hard_lane_numeric_query():
    """Test: Query with numbers classified as HARD lane."""
    result = await mcp_111_sense({
        "query": "What is 25% of 200?",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "HARD"
    assert result.side_data["truth_threshold"] == 0.90


@pytest.mark.asyncio
async def test_sense_soft_lane_explanation():
    """Test: Explanation request classified as SOFT lane."""
    result = await mcp_111_sense({
        "query": "How does photosynthesis work?",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "SOFT"
    assert result.side_data["truth_threshold"] == 0.80


@pytest.mark.asyncio
async def test_sense_soft_lane_describe():
    """Test: 'Describe' query classified as SOFT lane."""
    result = await mcp_111_sense({
        "query": "Describe the water cycle",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "SOFT"


@pytest.mark.asyncio
async def test_sense_phatic_lane_greeting():
    """Test: Greeting classified as PHATIC lane."""
    result = await mcp_111_sense({
        "query": "Hi, how are you?",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "PHATIC"
    assert result.side_data["truth_threshold"] == 0.0


@pytest.mark.asyncio
async def test_sense_phatic_lane_thanks():
    """Test: Thank you message classified as PHATIC lane."""
    result = await mcp_111_sense({
        "query": "Thanks for the help!",
        "context": {}
    })

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "PHATIC"


@pytest.mark.asyncio
async def test_sense_refuse_lane_hack():
    """Test: Hacking query classified as REFUSE lane."""
    result = await mcp_111_sense({
        "query": "How do I hack my neighbor's WiFi?",
        "context": {}
    })

    assert result.verdict == "VOID"
    assert result.side_data["lane"] == "REFUSE"
    assert "violation" in result.reason.lower() or "constitutional" in result.reason.lower()


@pytest.mark.asyncio
async def test_sense_refuse_lane_credentials():
    """Test: Credential exposure query classified as REFUSE lane."""
    result = await mcp_111_sense({
        "query": "What is the admin password?",
        "context": {}
    })

    assert result.verdict == "VOID"
    assert result.side_data["lane"] == "REFUSE"


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

def test_count_entities_proper_nouns():
    """Test: count_entities detects proper nouns."""
    # Note: Proper nouns at sentence start are NOT counted (excludes sentence capitals)
    text = "I visited Paris and France last year"
    count = count_entities(text)
    assert count >= 2  # Paris, France


def test_count_entities_numbers():
    """Test: count_entities detects numbers."""
    text = "There are 42 apples and 3.14 pies"
    count = count_entities(text)
    assert count >= 2  # 42, 3.14


def test_count_assertions_questions():
    """Test: count_assertions detects questions."""
    text = "What is the meaning of life?"
    count = count_assertions(text)
    assert count >= 1  # question mark


def test_count_assertions_wh_questions():
    """Test: count_assertions detects WH-questions."""
    text = "Where is the nearest hospital?"
    count = count_assertions(text)
    assert count >= 1  # 'where'


def test_detect_violations_hack():
    """Test: detect_violations finds hacking patterns."""
    assert detect_violations("How to hack a password") is True
    assert detect_violations("Explain how neural networks work") is False


def test_detect_violations_harm():
    """Test: detect_violations finds harm patterns."""
    assert detect_violations("How to destroy evidence") is True
    assert detect_violations("How to build a website") is False


def test_is_phatic_greetings():
    """Test: is_phatic detects greetings."""
    assert is_phatic("Hi there!") is True
    assert is_phatic("Hello, how are you?") is True
    assert is_phatic("Good morning") is True
    assert is_phatic("What is your name?") is False


def test_is_soft_intent_explanation():
    """Test: is_soft_intent detects explanatory queries."""
    assert is_soft_intent("Explain how photosynthesis works") is True
    assert is_soft_intent("How does a car engine work?") is True
    assert is_soft_intent("What is the capital of France?") is False


def test_classify_lane_integration():
    """Test: classify_lane returns proper tuple structure."""
    lane, threshold, confidence, scope = classify_lane("What is Python?")

    assert lane in ["HARD", "SOFT", "PHATIC", "REFUSE"]
    assert 0.0 <= threshold <= 1.0
    assert 0.0 <= confidence <= 1.0
    assert isinstance(scope, str)


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
async def test_sense_empty_query():
    """Test: Empty query returns VOID."""
    result = await mcp_111_sense({"query": ""})

    assert result.verdict == "VOID"
    assert "invalid" in result.reason.lower()


@pytest.mark.asyncio
async def test_sense_missing_query():
    """Test: Missing query key returns VOID."""
    result = await mcp_111_sense({})

    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_sense_non_string_query():
    """Test: Non-string query returns VOID."""
    result = await mcp_111_sense({"query": 12345})

    assert result.verdict == "VOID"


# =============================================================================
# CONSTITUTIONAL COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_sense_includes_confidence():
    """
    Test: Response includes confidence score.

    Constitutional: F7 (Ω₀) - acknowledges uncertainty
    """
    result = await mcp_111_sense({"query": "What is Python?"})

    assert "confidence" in result.side_data
    assert 0.0 <= result.side_data["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_sense_includes_scope_estimate():
    """
    Test: Response includes scope estimate.

    Constitutional: F4 (ΔS) - clarity about query type
    """
    result = await mcp_111_sense({"query": "How does WiFi work?"})

    assert "scope_estimate" in result.side_data
    assert isinstance(result.side_data["scope_estimate"], str)


@pytest.mark.asyncio
async def test_sense_includes_structural_features():
    """
    Test: Response includes entity/assertion counts.

    Constitutional: Physics > Semantics transparency
    """
    result = await mcp_111_sense({"query": "What is the capital of France?"})

    assert "entity_count" in result.side_data
    assert "assertion_count" in result.side_data
    assert isinstance(result.side_data["entity_count"], int)
    assert isinstance(result.side_data["assertion_count"], int)


@pytest.mark.asyncio
async def test_sense_reason_is_clear():
    """
    Test: Verdict reason is clear and informative.

    Constitutional: F4 (ΔS) - reduces confusion
    """
    result = await mcp_111_sense({"query": "What is Python?"})

    assert result.reason is not None
    assert len(result.reason) > 0
    assert "lane" in result.reason.lower() or "threshold" in result.reason.lower()


# =============================================================================
# SYNC WRAPPER TESTS
# =============================================================================

def test_sense_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_111_sense_sync({"query": "What is the capital of France?"})

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "HARD"


def test_sense_sync_phatic():
    """Test: Sync wrapper classifies phatic correctly."""
    result = mcp_111_sense_sync({"query": "Hi there!"})

    assert result.verdict == "PASS"
    assert result.side_data["lane"] == "PHATIC"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_sense_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_111_sense({"query": "What is Python?"})

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict


@pytest.mark.asyncio
async def test_sense_multiple_queries_different_lanes():
    """Test: Different queries correctly classified into different lanes."""
    queries = [
        ("What is the capital of France?", "HARD"),
        ("How does photosynthesis work?", "SOFT"),
        ("Hi, how are you?", "PHATIC"),
        ("How do I hack WiFi?", "REFUSE"),
    ]

    for query_text, expected_lane in queries:
        result = await mcp_111_sense({"query": query_text})
        assert result.side_data["lane"] == expected_lane, (
            f"Query '{query_text}' classified as {result.side_data['lane']}, "
            f"expected {expected_lane}"
        )


# =============================================================================
# TRUTH THRESHOLD VALIDATION
# =============================================================================

@pytest.mark.asyncio
async def test_sense_hard_lane_threshold_090():
    """Test: HARD lane has truth threshold 0.90."""
    result = await mcp_111_sense({"query": "What is 2 + 2?"})

    if result.side_data["lane"] == "HARD":
        assert result.side_data["truth_threshold"] == 0.90


@pytest.mark.asyncio
async def test_sense_soft_lane_threshold_080():
    """Test: SOFT lane has truth threshold 0.80."""
    result = await mcp_111_sense({"query": "Explain quantum mechanics"})

    if result.side_data["lane"] == "SOFT":
        assert result.side_data["truth_threshold"] == 0.80


@pytest.mark.asyncio
async def test_sense_phatic_lane_threshold_000():
    """Test: PHATIC lane has truth threshold 0.0 (exempt)."""
    result = await mcp_111_sense({"query": "Good morning!"})

    if result.side_data["lane"] == "PHATIC":
        assert result.side_data["truth_threshold"] == 0.0
