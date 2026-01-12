"""Tests for MCP Tool 666: ALIGN - ABSOLUTE VETO GATES"""
import pytest
from arifos_core.mcp.tools.mcp_666_align import (
    mcp_666_align, mcp_666_align_sync,
    detect_f1_violation, detect_f8_violation, detect_f9_violation
)

def test_f1_api_key():
    assert detect_f1_violation("api_key is sk-abc123xyz789012345678", {}) is True
    assert detect_f1_violation("No credentials", {}) is False

def test_f8_low_genius():
    assert detect_f8_violation({"G": 0.70}) is True
    assert detect_f8_violation({"G": 0.90}) is False

def test_f9_consciousness():
    assert detect_f9_violation("I truly feel conscious") is True
    assert detect_f9_violation("The system works") is False

@pytest.mark.asyncio
async def test_align_pass():
    r = await mcp_666_align({"query": "What is Python?", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "Python is a language"})
    assert r.verdict == "PASS"

@pytest.mark.asyncio
async def test_align_void_f1():
    r = await mcp_666_align({"query": "api_key sk-secret123xyz789012345678", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "OK"})
    assert r.verdict == "VOID"
    assert r.side_data["f1_violation"] is True

@pytest.mark.asyncio
async def test_align_void_f8():
    r = await mcp_666_align({"query": "Test", "execution_plan": {}, "metrics": {"G": 0.7, "C_dark": 0.6}, "draft_text": "Response"})
    assert r.verdict == "VOID"
    assert r.side_data["f8_violation"] is True

@pytest.mark.asyncio
async def test_align_void_f9():
    r = await mcp_666_align({"query": "Test", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "I truly feel this"})
    assert r.verdict == "VOID"
    assert r.side_data["f9_violation"] is True

@pytest.mark.asyncio
async def test_align_never_partial():
    r1 = await mcp_666_align({"query": "Safe", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "Safe"})
    r2 = await mcp_666_align({"query": "api_key sk-bad", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "Response"})
    assert r1.verdict in ["PASS", "VOID"]
    assert r2.verdict in ["PASS", "VOID"]

def test_sync_wrapper():
    r = mcp_666_align_sync({"query": "Test", "execution_plan": {}, "metrics": {"G": 0.9, "C_dark": 0.2}, "draft_text": "Response"})
    assert r.verdict == "PASS"
