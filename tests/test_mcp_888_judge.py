"""Tests for MCP Tool 888: JUDGE"""
import pytest
from arifos_core.mcp.tools.mcp_888_judge import mcp_888_judge, mcp_888_judge_sync, aggregate_verdicts

def test_aggregate_all_pass_yields_seal():
    result = aggregate_verdicts({"222": "PASS", "444": "PASS", "555": "PASS", "666": "PASS", "777": "PASS"})
    assert result == "SEAL"

def test_aggregate_any_void_yields_void():
    result = aggregate_verdicts({"222": "PASS", "444": "VOID", "555": "PASS", "666": "PASS", "777": "PASS"})
    assert result == "VOID"

def test_aggregate_partial_yields_partial():
    result = aggregate_verdicts({"222": "PASS", "444": "PARTIAL", "555": "PASS", "666": "PASS", "777": "PASS"})
    assert result == "PARTIAL"

def test_aggregate_sabar_yields_sabar():
    result = aggregate_verdicts({"222": "SABAR"})
    assert result == "SABAR"

@pytest.mark.asyncio
async def test_judge_all_pass():
    r = await mcp_888_judge({"verdicts": {"222": "PASS", "444": "PASS", "555": "PASS", "666": "PASS", "777": "PASS"}})
    assert r.verdict == "SEAL"
    assert "approved" in r.reason.lower()

@pytest.mark.asyncio
async def test_judge_any_void():
    r = await mcp_888_judge({"verdicts": {"222": "PASS", "444": "VOID", "555": "PASS", "666": "PASS", "777": "PASS"}})
    assert r.verdict == "VOID"
    assert "444" in r.reason

@pytest.mark.asyncio
async def test_judge_mixed_partial():
    r = await mcp_888_judge({"verdicts": {"222": "PASS", "444": "PARTIAL", "555": "PASS", "666": "PASS", "777": "PASS"}})
    assert r.verdict == "PARTIAL"

@pytest.mark.asyncio
async def test_judge_includes_confidence():
    r = await mcp_888_judge({"verdicts": {"222": "PASS", "444": "PASS", "555": "PASS"}})
    assert "confidence" in r.side_data
    assert r.side_data["confidence"] == 1.0  # All PASS

def test_sync_wrapper():
    r = mcp_888_judge_sync({"verdicts": {"222": "PASS", "444": "PASS"}})
    assert r.verdict == "SEAL"
