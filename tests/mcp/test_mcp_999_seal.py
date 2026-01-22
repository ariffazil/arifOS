"""Tests for MCP Tool 999: SEAL - Final Verdict Sealing

v49 Update: Stage 999 now performs active constitutional enforcement via
parallel hypervisor. Minimal queries return VOID; proper queries with full
context return PASS.

Philosophy: 999 is quantum collapse with enforcement, not passive stamp.

Testing Strategy:
- Utility functions (generate_seal, validate_seal, etc.) - test directly
- Tool behavior with VOID - test with minimal input (real hypervisor)
- Tool behavior with PASS - test with mocked hypervisor (seal generation logic)
"""
import pytest
import base64
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from dataclasses import dataclass
from arifos.core.mcp.tools.mcp_999_seal import (
    mcp_999_seal,
    mcp_999_seal_sync,
    generate_seal,
    generate_audit_entry,
    generate_audit_log_id,
    generate_memory_location,
    validate_seal
)


# =============================================================================
# MOCKING HELPERS (v49)
# =============================================================================

@dataclass
class MockReceipt:
    """Mock constitutional receipt for hypervisor testing."""
    action_hash: str = "mock_action_hash_abc123"
    trinity_assignment: str = "AAA_TRINITY"
    timestamp: datetime = None
    constitutional_validity: bool = True
    feedback_constraint: str = "MEASUREMENT_COLLAPSE:SEAL:CONSTITUTIONAL_CONSENSUS"
    audit_trail: dict = None
    rollback_possible: bool = True

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.audit_trail is None:
            self.audit_trail = {}


def create_mock_hypervisor_result(verdict="SEAL"):
    """Create mock hypervisor result for testing seal generation logic."""
    return {
        "verdict": verdict,
        "constitutional_status": "CONSTITUTIONAL_CONSENSUS" if verdict == "SEAL" else "PARTICLES_DISAGREE",
        "trinity_consensus": verdict == "SEAL",
        "aggregated_proofs": {
            "agi_proof": {"floor_check": "PASS"},
            "asi_proof": {"empathy_check": "PASS"},
            "apex_proof": {"judgment": "SEAL"}
        },
        "final_receipt": MockReceipt(),
        "quantum_superposition": {
            "executed": True,
            "particle_count": 3,
            "measurement_collapse": "complete"
        }
    }


# =============================================================================
# HELPER: Constitutional Context (v49)
# =============================================================================

def get_proper_context():
    """
    Provide proper constitutional context for v49 hypervisor.

    v49 Reality: 999 runs execute_constitutional_physics() which needs:
    - Proper query (not minimal like "Test")
    - Context metadata
    - Lane information

    Returns minimal viable context that passes constitutional checks.
    """
    return {
        "verdict": "SEAL",
        "proof_hash": "abc123def456",
        "decision_metadata": {
            "query": "What is the capital of Malaysia?",
            "context": "Geography question for educational purposes",
            "lane": "FACTUAL",
            "user_id": "test_user",
            "floor_verdicts": {
                "111": "PASS",
                "222": "PASS",
                "333": "PASS",
                "444": "PASS",
                "555": "PASS",
                "666": "PASS",
                "777": "PASS",
                "888": "PASS"
            }
        }
    }


# =============================================================================
# BASIC FUNCTIONALITY TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_minimal_query_returns_void():
    """Test: v49 active enforcement - minimal query returns VOID."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {"query": "Test"}
    })

    # v49: Minimal query without context fails constitutional checks
    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_seal_proper_context_returns_pass():
    """Test: v49 seal generation with mocked hypervisor consensus."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = await mcp_999_seal(get_proper_context())

        # v49: Hypervisor SEAL → tool returns PASS
        assert result.verdict == "PASS"
        assert "sealed_verdict" in result.side_data
        assert result.side_data["seal_valid"] is True


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
    """Test: v49 active enforcement - empty metadata returns VOID."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {}
    })

    # v49: Empty metadata fails constitutional checks
    assert result.verdict == "VOID"


@pytest.mark.asyncio
async def test_seal_missing_floor_verdicts():
    """Test: v49 active enforcement - missing floor_verdicts returns VOID."""
    result = await mcp_999_seal({
        "verdict": "SEAL",
        "proof_hash": "abc123",
        "decision_metadata": {"query": "Test"}
    })

    # v49: Minimal query without floor verdicts fails constitutional checks
    assert result.verdict == "VOID"


# =============================================================================
# CONSTITUTIONAL COMPLIANCE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_seal_includes_timestamp():
    """Test: Response includes valid ISO8601 timestamp (F1 Amanah)."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = await mcp_999_seal(get_proper_context())

        assert result.verdict == "PASS"
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO format


def test_seal_sync_wrapper():
    """Test: Synchronous wrapper works correctly."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = mcp_999_seal_sync(get_proper_context())

        assert result.verdict == "PASS"


@pytest.mark.asyncio
async def test_seal_response_serializable():
    """Test: Response can be serialized to dict (for JSON)."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = await mcp_999_seal(get_proper_context())

        result_dict = result.to_dict()

        assert result.verdict == "PASS"
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
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = await mcp_999_seal(get_proper_context())

        assert result.verdict == "PASS"
        audit_id = result.side_data["audit_log_id"]

        # Should start with verdict (uppercase)
        assert audit_id.startswith("SEAL_")

        # Should contain date
        assert "2025" in audit_id or "202" in audit_id  # Flexible for year


@pytest.mark.asyncio
async def test_seal_memory_location_sanitization():
    """Test: Memory location sanitizes special characters."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        context = get_proper_context()
        context["decision_metadata"]["query"] = "What is @#$% 2+2?"
        result = await mcp_999_seal(context)

        assert result.verdict == "PASS"
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
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        verdicts = ["SEAL", "PARTIAL", "VOID", "SABAR", "HOLD"]

        for v in verdicts:
            mock_hyp.return_value = create_mock_hypervisor_result(verdict=v)

            context = get_proper_context()
            context["verdict"] = v
            result = await mcp_999_seal(context)

            # Tool returns PASS only if hypervisor returns SEAL
            if v == "SEAL":
                assert result.verdict == "PASS"
            else:
                assert result.verdict == "VOID"
            assert v.upper() in result.side_data["audit_log_id"]


@pytest.mark.asyncio
async def test_seal_includes_seal_valid_flag():
    """Test: Response includes seal_valid flag."""
    with patch('arifos.mcp.constitution.execute_constitutional_physics', new_callable=AsyncMock) as mock_hyp:
        mock_hyp.return_value = create_mock_hypervisor_result(verdict="SEAL")

        result = await mcp_999_seal(get_proper_context())

        assert result.verdict == "PASS"
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
