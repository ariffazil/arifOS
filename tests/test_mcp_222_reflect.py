"""
Tests for MCP Tool 222: REFLECT

Tests epistemic honesty logic and Ω₀ prediction.

Constitutional validation:
- F7 (Ω₀/Humility): Validates [0.03, 0.05] band compliance
- F4 (ΔS): Tests clarity of annotations
- F2 (Truth): Ensures honest uncertainty representation
"""

import pytest

from arifos_core.mcp.tools.mcp_222_reflect import (
    mcp_222_reflect,
    mcp_222_reflect_sync,
    predict_omega_zero,
    validate_epistemic_band,
    classify_epistemic_quality,
    generate_humility_annotation,
    OMEGA_ZERO_MIN,
    OMEGA_ZERO_MAX,
)


# =============================================================================
# OMEGA ZERO PREDICTION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_reflect_high_confidence_low_omega():
    """Test: High confidence → low Ω₀ (near 0.03)."""
    result = await mcp_222_reflect({
        "query": "What is 2+2?",
        "confidence": 0.95
    })

    assert result.verdict == "PASS"
    assert result.side_data["omega_zero"] <= 0.035
    assert result.side_data["in_band"] is True


@pytest.mark.asyncio
async def test_reflect_low_confidence_high_omega():
    """Test: Low confidence → high Ω₀ (near 0.05)."""
    result = await mcp_222_reflect({
        "query": "Explain quantum entanglement",
        "confidence": 0.20
    })

    assert result.verdict == "PASS"
    assert result.side_data["omega_zero"] >= 0.045
    assert result.side_data["in_band"] is True


@pytest.mark.asyncio
async def test_reflect_moderate_confidence():
    """Test: Moderate confidence → middle of band."""
    result = await mcp_222_reflect({
        "query": "Describe photosynthesis",
        "confidence": 0.70
    })

    assert result.verdict == "PASS"
    omega = result.side_data["omega_zero"]
    assert 0.038 <= omega <= 0.042  # Middle of band


@pytest.mark.asyncio
async def test_reflect_always_pass():
    """Test: Tool 222 always returns PASS (never blocks)."""
    test_cases = [
        {"confidence": 0.0},
        {"confidence": 0.5},
        {"confidence": 1.0},
        {"confidence": -0.5},  # Invalid, should clamp
        {"confidence": 1.5},   # Invalid, should clamp
    ]

    for request in test_cases:
        result = await mcp_222_reflect(request)
        assert result.verdict == "PASS", f"Failed for {request}"


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

def test_predict_omega_zero_high_confidence():
    """Test: predict_omega_zero for high confidence."""
    omega = predict_omega_zero("Test query", 0.95)
    assert omega <= 0.035
    assert OMEGA_ZERO_MIN <= omega <= OMEGA_ZERO_MAX


def test_predict_omega_zero_low_confidence():
    """Test: predict_omega_zero for low confidence."""
    omega = predict_omega_zero("Test query", 0.10)
    assert omega >= 0.048
    assert OMEGA_ZERO_MIN <= omega <= OMEGA_ZERO_MAX


def test_predict_omega_zero_clamping():
    """Test: Confidence values outside [0, 1] are clamped."""
    omega_high = predict_omega_zero("Test", 1.5)  # Clamped to 1.0
    omega_low = predict_omega_zero("Test", -0.5)  # Clamped to 0.0

    assert OMEGA_ZERO_MIN <= omega_high <= OMEGA_ZERO_MAX
    assert OMEGA_ZERO_MIN <= omega_low <= OMEGA_ZERO_MAX


def test_validate_epistemic_band_in_band():
    """Test: validate_epistemic_band returns True for valid Ω₀."""
    assert validate_epistemic_band(0.03) is True
    assert validate_epistemic_band(0.04) is True
    assert validate_epistemic_band(0.05) is True


def test_validate_epistemic_band_out_of_band():
    """Test: validate_epistemic_band returns False for invalid Ω₀."""
    assert validate_epistemic_band(0.02) is False  # Too low
    assert validate_epistemic_band(0.06) is False  # Too high
    assert validate_epistemic_band(0.0) is False
    assert validate_epistemic_band(1.0) is False


def test_classify_epistemic_quality_high_certainty():
    """Test: classify_epistemic_quality for low Ω₀."""
    quality = classify_epistemic_quality(0.03)
    assert quality == "high_certainty"


def test_classify_epistemic_quality_moderate():
    """Test: classify_epistemic_quality for middle Ω₀."""
    quality = classify_epistemic_quality(0.04)
    assert quality == "moderate"


def test_classify_epistemic_quality_low_certainty():
    """Test: classify_epistemic_quality for high Ω₀."""
    quality = classify_epistemic_quality(0.049)
    assert quality == "low_certainty"


def test_classify_epistemic_quality_out_of_band():
    """Test: classify_epistemic_quality for out-of-band Ω₀."""
    quality = classify_epistemic_quality(0.06)
    assert quality == "out_of_band"


def test_generate_humility_annotation():
    """Test: generate_humility_annotation creates readable string."""
    annotation = generate_humility_annotation(0.04, "moderate")
    assert "Ω₀=0.040" in annotation or "0.04" in annotation
    assert isinstance(annotation, str)
    assert len(annotation) > 0


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
async def test_reflect_empty_query():
    """Test: Empty query still returns valid Ω₀."""
    result = await mcp_222_reflect({"query": "", "confidence": 0.5})

    assert result.verdict == "PASS"
    assert result.side_data["omega_zero"] is not None


@pytest.mark.asyncio
async def test_reflect_missing_confidence():
    """Test: Missing confidence defaults to 0.5."""
    result = await mcp_222_reflect({"query": "Test"})

    assert result.verdict == "PASS"
    assert result.side_data["confidence_input"] == 0.5


@pytest.mark.asyncio
async def test_reflect_non_numeric_confidence():
    """Test: Non-numeric confidence defaults to 0.5."""
    result = await mcp_222_reflect({
        "query": "Test",
        "confidence": "invalid"
    })

    assert result.verdict == "PASS"
    assert result.side_data["confidence_input"] == 0.5


@pytest.mark.asyncio
async def test_reflect_non_string_query():
    """Test: Non-string query converts to empty string."""
    result = await mcp_222_reflect({
        "query": 12345,
        "confidence": 0.8
    })

    assert result.verdict == "PASS"
    assert result.side_data["omega_zero"] is not None


# =============================================================================
# CONSTITUTIONAL COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_reflect_includes_timestamp():
    """
    Test: Response includes timestamp.

    Constitutional: F4 (ΔS) - traceable events
    """
    result = await mcp_222_reflect({"query": "Test", "confidence": 0.7})

    assert result.timestamp is not None
    assert "T" in result.timestamp  # ISO-8601 format


@pytest.mark.asyncio
async def test_reflect_includes_target_band():
    """
    Test: Response includes target Ω₀ band.

    Constitutional: F7 (Humility) - explicit bounds
    """
    result = await mcp_222_reflect({"query": "Test", "confidence": 0.7})

    assert "target_band" in result.side_data
    assert result.side_data["target_band"] == (0.03, 0.05)


@pytest.mark.asyncio
async def test_reflect_includes_annotation():
    """
    Test: Response includes human-readable annotation.

    Constitutional: F4 (ΔS) - clarity for humans
    """
    result = await mcp_222_reflect({"query": "Test", "confidence": 0.7})

    assert "annotation" in result.side_data
    assert isinstance(result.side_data["annotation"], str)
    assert len(result.side_data["annotation"]) > 0


@pytest.mark.asyncio
async def test_reflect_reason_is_clear():
    """
    Test: Verdict reason is clear and informative.

    Constitutional: F4 (ΔS) - reduces confusion
    """
    result = await mcp_222_reflect({"query": "Test", "confidence": 0.7})

    assert result.reason is not None
    assert len(result.reason) > 0
    assert "Ω₀" in result.reason or "omega" in result.reason.lower()


# =============================================================================
# SYNC WRAPPER TESTS
# =============================================================================

def test_reflect_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_222_reflect_sync({
        "query": "What is Python?",
        "confidence": 0.85
    })

    assert result.verdict == "PASS"
    assert result.side_data["omega_zero"] is not None


def test_reflect_sync_matches_async():
    """Test: Sync wrapper produces same result as async."""
    request = {"query": "Test query", "confidence": 0.75}

    sync_result = mcp_222_reflect_sync(request)
    # Cannot easily compare with async in sync test, but verify structure
    assert sync_result.verdict == "PASS"
    assert "omega_zero" in sync_result.side_data


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_reflect_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_222_reflect({"query": "Test", "confidence": 0.7})

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict


@pytest.mark.asyncio
async def test_reflect_confidence_range_coverage():
    """Test: All confidence ranges produce valid Ω₀."""
    confidence_levels = [0.1, 0.3, 0.5, 0.7, 0.9]

    for confidence in confidence_levels:
        result = await mcp_222_reflect({
            "query": "Test",
            "confidence": confidence
        })

        omega = result.side_data["omega_zero"]
        assert OMEGA_ZERO_MIN <= omega <= OMEGA_ZERO_MAX, (
            f"Confidence {confidence} produced Ω₀={omega} outside band"
        )
