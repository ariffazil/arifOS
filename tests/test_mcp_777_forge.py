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
