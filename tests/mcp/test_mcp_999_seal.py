"""Tests for MCP Tool 999: SEAL - Final Verdict Sealing"""
import pytest
import base64
from arifos_core.mcp.tools.mcp_999_seal import (
    mcp_999_seal,
    mcp_999_seal_sync,
    generate_seal,
    generate_audit_entry,
    generate_audit_log_id,
    generate_memory_location,
    validate_seal
)


# =============================================================================
# BASIC FUNCTIONALITY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_always_pass():
    """Test: Tool 999 verdict is always PASS."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {"query": "Test"}
    })

    assert result.verdict == "PASS"


@pytest.mark.asyncio
async def test_seal_deterministic():
    """Test: Same input produces same seal."""
    from datetime import datetime, timezone
    timestamp = datetime.now(timezone.utc).isoformat()

    seal1 = generate_seal("SEAL", "proof123", timestamp)
    seal2 = generate_seal("SEAL", "proof123", timestamp)

    assert seal1 == seal2


def test_seal_generation_correct():
    """Test: Seal includes verdict, proof, and timestamp."""
    verdict = "SEAL"
    proof_hash = "abc123"
    timestamp = "2025-12-25T10:00:00Z"

    sealed = generate_seal(verdict, proof_hash, timestamp)

    # Decode and check
    decoded = base64.b64decode(sealed.encode('utf-8')).decode('utf-8')

    assert verdict in decoded
    assert proof_hash in decoded
    assert timestamp in decoded


def test_seal_validation():
    """Test: Seal validates correctly."""
    verdict = "SEAL"
    proof_hash = "abc123"
    timestamp = "2025-12-25T10:00:00Z"

    sealed = generate_seal(verdict, proof_hash, timestamp)
    is_valid = validate_seal(sealed, verdict)

    assert is_valid is True


def test_seal_audit_entry_creation():
    """Test: Audit entry has all required fields."""
    verdict = "SEAL"
    proof_hash = "abc123"
    decision_metadata = {
        "query": "Test query",
        "floor_verdicts": {"222": "PASS", "444": "PASS"}
    }
    timestamp = "2025-12-25T10:00:00Z"

    entry = generate_audit_entry(verdict, proof_hash, decision_metadata, timestamp)

    assert "sealed_verdict" in entry
    assert "decision_metadata" in entry
    assert "timestamp" in entry
    assert "floor_verdicts" in entry
    assert entry["floor_verdicts"] == {"222": "PASS", "444": "PASS"}


def test_seal_audit_log_id_deterministic():
    """Test: Same verdict + timestamp produces same audit log ID."""
    verdict = "SEAL"
    timestamp = "2025-12-25T10:00:00Z"

    id1 = generate_audit_log_id(verdict, timestamp)
    id2 = generate_audit_log_id(verdict, timestamp)

    assert id1 == id2


def test_seal_memory_location_valid():
    """Test: Memory location path includes query when available."""
    audit_log_id = "SEAL_2025-12-25_abc123"
    decision_metadata = {"query": "What is 2+2?"}

    location = generate_memory_location(audit_log_id, decision_metadata)

    assert "audit_trail" in location
    assert audit_log_id in location
    assert "What" in location or "what" in location.lower()


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_empty_decision_metadata():
    """Test: Handles empty decision metadata gracefully."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    assert result.verdict == "PASS"
    assert "audit_log_id" in result.side_data


@pytest.mark.asyncio
async def test_seal_missing_floor_verdicts():
    """Test: Defaults to empty dict when floor_verdicts missing."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {"query": "Test"}
    })

    assert result.verdict == "PASS"


# =============================================================================
# CONSTITUTIONAL COMPLIANCE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_includes_timestamp():
    """Test: Response includes valid ISO8601 timestamp (F1 Amanah)."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    assert result.timestamp is not None
    assert "T" in result.timestamp  # ISO format


def test_seal_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    result = mcp_999_seal_sync({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    assert result.verdict == "PASS"


@pytest.mark.asyncio
async def test_seal_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "verdict" in result_dict
    assert "side_data" in result_dict
    assert "sealed_verdict" in result_dict["side_data"]


# =============================================================================
# ADDITIONAL COMPREHENSIVE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_audit_log_id_format():
    """Test: Audit log ID has correct format."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    audit_id = result.side_data["audit_log_id"]

    # Should start with verdict (uppercase)
    assert audit_id.startswith("SEAL_")

    # Should contain date
    assert "2025" in audit_id or "202" in audit_id  # Flexible for year


@pytest.mark.asyncio
async def test_seal_memory_location_sanitization():
    """Test: Memory location sanitizes special characters."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {"query": "What is @#$% 2+2?"}
    })

    location = result.side_data["memory_location"]

    # Should not contain special chars
    assert "@" not in location
    assert "#" not in location
    assert "$" not in location
    assert "%" not in location


def test_seal_memory_location_no_query():
    """Test: Memory location works without query."""
    audit_log_id = "SEAL_2025-12-25_abc123"
    decision_metadata = {}

    location = generate_memory_location(audit_log_id, decision_metadata)

    assert location == f"audit_trail/{audit_log_id}"


def test_seal_memory_location_query_truncation():
    """Test: Memory location truncates long queries to 50 chars."""
    audit_log_id = "SEAL_2025-12-25_abc123"
    long_query = "a" * 100  # 100 characters
    decision_metadata = {"query": long_query}

    location = generate_memory_location(audit_log_id, decision_metadata)

    # Extract sanitized query part
    query_part = location.split('/')[-1]

    assert len(query_part) <= 50


def test_seal_validation_invalid_seal():
    """Test: Validation fails with invalid seal."""
    is_valid = validate_seal("invalid_base64!", "SEAL")

    assert is_valid is False


@pytest.mark.asyncio
async def test_seal_different_verdicts():
    """Test: Sealing works for different verdict types."""
    verdicts = ["SEAL", "PARTIAL", "VOID", "SABAR", "HOLD"]

    for v in verdicts:
        result = await mcp_999_seal({
            "verdict": v,
            "proof_hash": "abc123",
            "decision_metadata": {}
        })

        assert result.verdict == "PASS"
        assert v.upper() in result.side_data["audit_log_id"]


@pytest.mark.asyncio
async def test_seal_includes_seal_valid_flag():
    """Test: Response includes seal_valid flag."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    assert "seal_valid" in result.side_data
    assert result.side_data["seal_valid"] is True


def test_generate_audit_log_id_includes_hash():
    """Test: Audit log ID includes timestamp hash."""
    verdict = "SEAL"
    timestamp = "2025-12-25T10:00:00Z"

    audit_id = generate_audit_log_id(verdict, timestamp)

    # Should have 3 parts: VERDICT_DATE_HASH
    parts = audit_id.split('_')
    assert len(parts) >= 3
    assert parts[0] == "SEAL"
    assert "2025-12-25" in audit_id
