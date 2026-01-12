"""
Tests for MCP Tool 000: RESET

Tests session initialization logic and constitutional compliance.

Constitutional validation:
- F1 (Amanah): No side effects, reversible initialization
- F2 (Truth): Honest state representation
- F7 (Ω₀): Acknowledges clean slate starting point
"""

import pytest
from datetime import datetime

from arifos_core.mcp.tools.mcp_000_reset import mcp_000_reset, mcp_000_reset_sync


# =============================================================================
# BASIC FUNCTIONALITY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_reset_generates_session_id():
    """Test: mcp_000_reset generates UUID if not provided."""
    result = await mcp_000_reset({"session_id": None})

    assert result.verdict == "PASS"
    assert result.side_data is not None
    assert "session_id" in result.side_data
    assert result.side_data["session_id"] is not None
    assert len(result.side_data["session_id"]) > 0
    assert isinstance(result.side_data["session_id"], str)


@pytest.mark.asyncio
async def test_reset_accepts_session_id():
    """Test: mcp_000_reset accepts provided session_id."""
    provided_id = "test-session-123"
    result = await mcp_000_reset({"session_id": provided_id})

    assert result.verdict == "PASS"
    assert result.side_data["session_id"] == provided_id


@pytest.mark.asyncio
async def test_reset_includes_timestamp():
    """Test: mcp_000_reset includes ISO-8601 timestamp."""
    result = await mcp_000_reset({})

    assert result.timestamp is not None
    assert "T" in result.timestamp  # ISO-8601 format includes T separator
    assert result.side_data["timestamp"] is not None

    # Verify timestamp is recent (within last 10 seconds)
    timestamp = datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))
    now = datetime.now(timestamp.tzinfo)
    delta = (now - timestamp).total_seconds()
    assert delta < 10


@pytest.mark.asyncio
async def test_reset_initializes_metrics_container():
    """Test: mcp_000_reset initializes empty metrics container."""
    result = await mcp_000_reset({})

    assert "metrics_initialized" in result.side_data
    assert result.side_data["metrics_initialized"] == {}


@pytest.mark.asyncio
async def test_reset_clears_active_band():
    """Test: mcp_000_reset marks ACTIVE memory band as cleared."""
    result = await mcp_000_reset({})

    assert "memory_bands_cleared" in result.side_data
    assert "ACTIVE" in result.side_data["memory_bands_cleared"]


# =============================================================================
# EDGE CASES
# =============================================================================

@pytest.mark.asyncio
async def test_reset_with_empty_request():
    """Test: mcp_000_reset handles empty request dictionary."""
    result = await mcp_000_reset({})

    assert result.verdict == "PASS"
    assert result.side_data["session_id"] is not None


@pytest.mark.asyncio
async def test_reset_with_empty_string_session_id():
    """Test: mcp_000_reset generates UUID for empty string session_id."""
    result = await mcp_000_reset({"session_id": ""})

    # Empty string should trigger UUID generation
    assert result.verdict == "PASS"
    assert result.side_data["session_id"] != ""
    assert len(result.side_data["session_id"]) > 0


@pytest.mark.asyncio
async def test_reset_with_numeric_session_id():
    """Test: mcp_000_reset generates UUID for non-string session_id."""
    result = await mcp_000_reset({"session_id": 12345})

    # Non-string should trigger UUID generation
    assert result.verdict == "PASS"
    assert isinstance(result.side_data["session_id"], str)
    assert result.side_data["session_id"] != "12345"


# =============================================================================
# CONSTITUTIONAL COMPLIANCE
# =============================================================================

@pytest.mark.asyncio
async def test_reset_never_blocks():
    """
    Test: mcp_000_reset always returns PASS (never VOID/HOLD).

    Constitutional: F1 (Amanah) - initialization is always safe
    """
    test_cases = [
        {},
        {"session_id": None},
        {"session_id": "valid-id"},
        {"session_id": ""},
        {"session_id": 123},
        {"extra_field": "ignored"},
    ]

    for request in test_cases:
        result = await mcp_000_reset(request)
        assert result.verdict == "PASS", f"Failed for request: {request}"


@pytest.mark.asyncio
async def test_reset_reason_is_clear():
    """
    Test: mcp_000_reset provides clear reason.

    Constitutional: F4 (ΔS) - clarity, not confusion
    """
    result = await mcp_000_reset({})

    assert result.reason is not None
    assert len(result.reason) > 0
    assert "initialized" in result.reason.lower()


# =============================================================================
# SYNC WRAPPER TESTS
# =============================================================================

def test_reset_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_000_reset_sync({"session_id": "sync-test"})

    assert result.verdict == "PASS"
    assert result.side_data["session_id"] == "sync-test"


def test_reset_sync_generates_uuid():
    """Test: Sync wrapper generates UUID correctly."""
    result = mcp_000_reset_sync({})

    assert result.verdict == "PASS"
    assert result.side_data["session_id"] is not None
    assert len(result.side_data["session_id"]) > 0


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_reset_multiple_calls_generate_unique_ids():
    """Test: Multiple reset calls generate unique session IDs."""
    result1 = await mcp_000_reset({})
    result2 = await mcp_000_reset({})
    result3 = await mcp_000_reset({})

    session_ids = [
        result1.side_data["session_id"],
        result2.side_data["session_id"],
        result3.side_data["session_id"],
    ]

    # All should be unique
    assert len(session_ids) == len(set(session_ids))


@pytest.mark.asyncio
async def test_reset_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_000_reset({})

    # Should not raise exception
    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict
    assert result_dict["verdict"] == "PASS"
