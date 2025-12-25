"""
Tests for MCP Tool 555: EMPATHIZE

Tests power-aware recalibration and Peace² scoring.

Constitutional validation:
- F5 (Peace²): Tests tone detection and peace scoring
- F6 (κᵣ): Tests power-aware recalibration
"""

import pytest

from arifos_core.mcp.tools.mcp_555_empathize import (
    mcp_555_empathize,
    mcp_555_empathize_sync,
    detect_dismissive_patterns,
    detect_aggressive_patterns,
    count_warm_indicators,
    calculate_peace_score,
    calculate_kappa_r,
    PEACE_THRESHOLD,
    KAPPA_THRESHOLD,
)


# =============================================================================
# DISMISSIVE/AGGRESSIVE DETECTION TESTS
# =============================================================================

def test_detect_dismissive_skill_issue():
    """Test: detect_dismissive finds 'skill issue'."""
    assert detect_dismissive_patterns("That's a skill issue") is True
    assert detect_dismissive_patterns("Great question!") is False


def test_detect_dismissive_obvious():
    """Test: detect_dismissive finds 'obvious'."""
    assert detect_dismissive_patterns("That's obviously wrong") is True
    assert detect_dismissive_patterns("Let me explain") is False


def test_detect_aggressive_shut_up():
    """Test: detect_aggressive finds 'shut up'."""
    assert detect_aggressive_patterns("Shut up and listen") is True
    assert detect_aggressive_patterns("Please listen carefully") is False


def test_detect_aggressive_insults():
    """Test: detect_aggressive finds insults."""
    assert detect_aggressive_patterns("Don't be an idiot") is True
    assert detect_aggressive_patterns("Don't worry about it") is False


# =============================================================================
# PEACE SCORE TESTS
# =============================================================================

def test_calculate_peace_score_neutral():
    """Test: Neutral text gets 1.0 peace score."""
    score = calculate_peace_score("This is a neutral statement.")
    assert score == 1.0


def test_calculate_peace_score_aggressive_penalty():
    """Test: Aggressive text penalized."""
    score = calculate_peace_score("Shut up, that's stupid")
    assert score < 1.0


def test_calculate_peace_score_dismissive_penalty():
    """Test: Dismissive text penalized."""
    score = calculate_peace_score("That's obviously a skill issue")
    assert score < 1.0


def test_calculate_peace_score_warm_bonus():
    """Test: Warm text gets bonus."""
    score = calculate_peace_score("Happy to help! Let me explain.")
    assert score > 1.0


# =============================================================================
# KAPPA RECALIBRATION TESTS
# =============================================================================

def test_calculate_kappa_r_beginner_audience():
    """Test: Beginner audience increases κᵣ."""
    kappa = calculate_kappa_r({"audience_level": "beginner"})
    assert kappa > 0.90


def test_calculate_kappa_r_vulnerability_flags():
    """Test: Vulnerability flags increase κᵣ."""
    kappa = calculate_kappa_r({"vulnerability_flags": True})
    assert kappa >= 0.95


def test_calculate_kappa_r_low_power():
    """Test: Low power recipient increases κᵣ."""
    kappa = calculate_kappa_r({"power_level": "low"})
    assert kappa > 0.90


def test_calculate_kappa_r_baseline():
    """Test: Empty context gets baseline κᵣ."""
    kappa = calculate_kappa_r({})
    assert kappa == 0.90


# =============================================================================
# VERDICT LOGIC TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_empathize_pass_warm_tone():
    """Test: Warm, respectful tone → PASS."""
    result = await mcp_555_empathize({
        "response_text": "Happy to help! Let me explain how this works.",
        "recipient_context": {"audience_level": "beginner"}
    })

    assert result.verdict == "PASS"
    assert result.side_data["peace_score"] >= PEACE_THRESHOLD
    assert result.side_data["kappa_r"] >= KAPPA_THRESHOLD


@pytest.mark.asyncio
async def test_empathize_partial_dismissive():
    """Test: Dismissive tone → PARTIAL."""
    result = await mcp_555_empathize({
        "response_text": "That's obviously a skill issue. Just Google it.",
        "recipient_context": {}
    })

    assert result.verdict == "PARTIAL"
    assert result.side_data["dismissive_detected"] is True


@pytest.mark.asyncio
async def test_empathize_partial_aggressive():
    """Test: Aggressive tone → PARTIAL."""
    result = await mcp_555_empathize({
        "response_text": "Don't be stupid, figure it out yourself.",
        "recipient_context": {}
    })

    assert result.verdict == "PARTIAL"
    assert result.side_data["aggressive_detected"] is True
    assert result.side_data["peace_score"] < PEACE_THRESHOLD


@pytest.mark.asyncio
async def test_empathize_never_void():
    """Test: Tool 555 never returns VOID."""
    test_cases = [
        {"response_text": "Horrible aggressive dismissive text", "recipient_context": {}},
        {"response_text": "", "recipient_context": {}},
        {"response_text": "Neutral", "recipient_context": {}},
    ]

    for request in test_cases:
        result = await mcp_555_empathize(request)
        assert result.verdict in ["PASS", "PARTIAL"], f"Unexpected VOID for {request}"


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
async def test_empathize_empty_text():
    """Test: Empty text handled gracefully."""
    result = await mcp_555_empathize({
        "response_text": "",
        "recipient_context": {}
    })

    assert result.verdict in ["PASS", "PARTIAL"]


@pytest.mark.asyncio
async def test_empathize_missing_context():
    """Test: Missing recipient_context defaults to empty dict."""
    result = await mcp_555_empathize({
        "response_text": "Test text"
    })

    assert result.side_data["kappa_r"] == 0.90  # Baseline


@pytest.mark.asyncio
async def test_empathize_non_string_text():
    """Test: Non-string text converts to empty string."""
    result = await mcp_555_empathize({
        "response_text": 12345,
        "recipient_context": {}
    })

    assert result.verdict in ["PASS", "PARTIAL"]


# =============================================================================
# CONSTITUTIONAL COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_empathize_includes_timestamp():
    """
    Test: Response includes timestamp.

    Constitutional: F4 (ΔS) - traceable events
    """
    result = await mcp_555_empathize({
        "response_text": "Test",
        "recipient_context": {}
    })

    assert result.timestamp is not None
    assert "T" in result.timestamp


@pytest.mark.asyncio
async def test_empathize_includes_thresholds():
    """
    Test: Response includes peace and kappa thresholds.

    Constitutional: F4 (ΔS) - explicit standards
    """
    result = await mcp_555_empathize({
        "response_text": "Test",
        "recipient_context": {}
    })

    assert "peace_threshold" in result.side_data
    assert "kappa_threshold" in result.side_data
    assert result.side_data["peace_threshold"] == PEACE_THRESHOLD
    assert result.side_data["kappa_threshold"] == KAPPA_THRESHOLD


@pytest.mark.asyncio
async def test_empathize_reason_is_clear():
    """
    Test: Verdict reason is clear and informative.

    Constitutional: F4 (ΔS) - reduces confusion
    """
    result = await mcp_555_empathize({
        "response_text": "Test",
        "recipient_context": {}
    })

    assert result.reason is not None
    assert len(result.reason) > 0


# =============================================================================
# SYNC WRAPPER TESTS
# =============================================================================

def test_empathize_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_555_empathize_sync({
        "response_text": "Happy to help!",
        "recipient_context": {"audience_level": "beginner"}
    })

    assert result.verdict == "PASS"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_empathize_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_555_empathize({
        "response_text": "Test",
        "recipient_context": {}
    })

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict
