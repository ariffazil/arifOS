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


# =============================================================================
# ADDITIONAL COMPREHENSIVE TESTS (10-20)
# =============================================================================

def test_aggregate_hold_verdict():
    """Test: HOLD verdict is propagated."""
    result = aggregate_verdicts({"222": "PASS", "444": "HOLD", "555": "PASS"})
    assert result == "HOLD"


def test_aggregate_multiple_void():
    """Test: Multiple VOID verdicts still yield VOID."""
    result = aggregate_verdicts({"222": "VOID", "444": "VOID", "555": "PASS"})
    assert result == "VOID"


def test_aggregate_empty_dict():
    """Test: Empty verdicts dict yields VOID."""
    result = aggregate_verdicts({})
    assert result == "VOID"


def test_confidence_band_partial_case():
    """Test: Confidence band calculation for partial approval."""
    from arifos_core.mcp.tools.mcp_888_judge import assign_confidence_band

    verdicts = {"222": "PASS", "444": "PARTIAL", "555": "PASS", "666": "PASS"}
    confidence = assign_confidence_band(verdicts)
    assert confidence == 0.75  # 3 PASS out of 4 total


@pytest.mark.asyncio
async def test_judge_veto_cascade_666():
    """Test: Tool 666 VOID triggers veto cascade."""
    r = await mcp_888_judge({
        "verdicts": {
            "222": "PASS",
            "444": "PASS",
            "555": "PASS",
            "666": "VOID",  # Critical veto
            "777": "PASS"
        }
    })

    assert r.verdict == "VOID"
    assert "666" in r.reason


@pytest.mark.asyncio
async def test_judge_mixed_sabar_partial():
    """Test: PARTIAL takes precedence over SABAR."""
    r = await mcp_888_judge({
        "verdicts": {
            "222": "SABAR",
            "444": "PARTIAL",
            "555": "PASS"
        }
    })

    assert r.verdict == "PARTIAL"


@pytest.mark.asyncio
async def test_judge_all_void():
    """Test: All VOID verdicts yield VOID."""
    r = await mcp_888_judge({
        "verdicts": {
            "222": "VOID",
            "444": "VOID",
            "555": "VOID"
        }
    })

    assert r.verdict == "VOID"
    assert r.side_data["confidence"] == 0.0


@pytest.mark.asyncio
async def test_judge_single_tool():
    """Test: Single tool verdict handled correctly."""
    r_pass = await mcp_888_judge({"verdicts": {"222": "PASS"}})
    r_void = await mcp_888_judge({"verdicts": {"222": "VOID"}})

    assert r_pass.verdict == "SEAL"
    assert r_void.verdict == "VOID"


@pytest.mark.asyncio
async def test_judge_includes_timestamp():
    """Test: Response includes timestamp (F4 ΔS - traceable events)."""
    r = await mcp_888_judge({"verdicts": {"222": "PASS"}})

    assert r.timestamp is not None
    assert "T" in r.timestamp  # ISO format


@pytest.mark.asyncio
async def test_judge_reason_clarity():
    """Test: Verdict reason is clear and informative (F4 ΔS)."""
    r_seal = await mcp_888_judge({"verdicts": {"222": "PASS", "444": "PASS"}})
    r_void = await mcp_888_judge({"verdicts": {"222": "VOID"}})
    r_partial = await mcp_888_judge({"verdicts": {"222": "PARTIAL"}})

    assert "approved" in r_seal.reason.lower()
    assert "violation" in r_void.reason.lower()
    assert "partial" in r_partial.reason.lower()


@pytest.mark.asyncio
async def test_judge_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    r = await mcp_888_judge({
        "verdicts": {
            "222": "PASS",
            "444": "PASS",
            "555": "PASS"
        }
    })

    result_dict = r.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "reason" in result_dict
    assert "side_data" in result_dict
    assert "timestamp" in result_dict
