"""Tests for MCP Tool 777: FORGE"""
import pytest
from arifos_core.mcp.tools.mcp_777_forge import mcp_777_forge, mcp_777_forge_sync, detect_contradictions, inject_humility_markers

def test_detect_contradictions():
    assert len(detect_contradictions("always true never false")) > 0
    assert len(detect_contradictions("sometimes true")) == 0

def test_inject_humility_high_omega():
    result = inject_humility_markers("Test response", 0.048)
    assert "uncertainty" in result.lower()

def test_inject_humility_low_omega():
    result = inject_humility_markers("Test response", 0.03)
    assert result == "Test response"

@pytest.mark.asyncio
async def test_forge_always_pass():
    r = await mcp_777_forge({"draft_response": "Test", "omega_zero": 0.04})
    assert r.verdict == "PASS"

@pytest.mark.asyncio
async def test_forge_refines_text():
    r = await mcp_777_forge({"draft_response": "Test   response", "omega_zero": 0.04})
    assert "refined_response" in r.side_data
    assert r.side_data["refined_response"] == "Test response"

def test_sync_wrapper():
    r = mcp_777_forge_sync({"draft_response": "Test", "omega_zero": 0.04})
    assert r.verdict == "PASS"


# =============================================================================
# ADDITIONAL COMPREHENSIVE TESTS (7-14)
# =============================================================================

@pytest.mark.asyncio
async def test_forge_empty_text():
    """Test: Empty draft_response handled gracefully."""
    r = await mcp_777_forge({"draft_response": "", "omega_zero": 0.04})
    assert r.verdict == "PASS"
    assert r.side_data["refined_response"] == ""


def test_detect_contradictions_multiple():
    """Test: Multiple contradiction patterns detected."""
    text = "This is always true and never false. All users have none of the rights."
    contradictions = detect_contradictions(text)
    assert len(contradictions) >= 2


@pytest.mark.asyncio
async def test_forge_clarity_score_calculation():
    """Test: Clarity score = 1.0 when refined <= original length."""
    r = await mcp_777_forge({"draft_response": "Test   response!!!", "omega_zero": 0.03})
    assert r.side_data["clarity_score"] == 1.0  # Refined is shorter


@pytest.mark.asyncio
async def test_forge_humility_boundary():
    """Test: Humility injection at exact boundary (0.04)."""
    r_below = await mcp_777_forge({"draft_response": "Test", "omega_zero": 0.04})
    r_above = await mcp_777_forge({"draft_response": "Test", "omega_zero": 0.041})

    assert "uncertainty" not in r_below.side_data["refined_response"].lower()
    assert "uncertainty" in r_above.side_data["refined_response"].lower()


@pytest.mark.asyncio
async def test_forge_non_string_input():
    """Test: Non-string draft_response converts to empty."""
    r = await mcp_777_forge({"draft_response": 12345, "omega_zero": 0.04})
    assert r.verdict == "PASS"


@pytest.mark.asyncio
async def test_forge_includes_timestamp():
    """Test: Response includes timestamp (F4 ΔS - traceable events)."""
    r = await mcp_777_forge({"draft_response": "Test", "omega_zero": 0.04})
    assert r.timestamp is not None
    assert "T" in r.timestamp  # ISO format


@pytest.mark.asyncio
async def test_forge_side_data_complete():
    """Test: Side data includes all expected fields."""
    r = await mcp_777_forge({"draft_response": "Test", "omega_zero": 0.048})

    assert "refined_response" in r.side_data
    assert "clarity_score" in r.side_data
    assert "contradictions_found" in r.side_data
    assert "humility_injected" in r.side_data


def test_improve_clarity_removes_repeated_punctuation():
    """Test: Clarity improvement removes repeated punctuation."""
    from arifos_core.mcp.tools.mcp_777_forge import improve_clarity

    result = improve_clarity("What???? Really!!!")
    assert "????" not in result
    assert "!!!" not in result
    assert result == "What? Really!"
