"""Tests for MCP Tool 999: VAULT - Final Verdict Sealing

v50 Update: 999_vault consolidates sealing with Merkle proof and immutable ledger.

Testing Strategy:
- Input validation (action, verdict validation)
- VOID/SABAR verdicts NOT stored (Eureka Sieve)
- SEAL verdicts stored to ledger
- Hash chain integrity
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Current module path
from arifos.mcp.tools.mcp_trinity import (
    mcp_999_vault,
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
)
from arifos.mcp.session_ledger import get_ledger, SessionLedger


# =============================================================================
# INPUT VALIDATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_invalid_action_returns_void():
    """Test: Invalid action returns VOID status."""
    result = await mcp_999_vault(action="invalid_action")

    assert result["status"] == "VOID"
    assert result["memory_location"] == "INVALID_ACTION"
    assert "F12_InputValidation" in result["floors_checked"]


@pytest.mark.asyncio
async def test_999_vault_empty_action_returns_void():
    """Test: Empty action returns VOID status."""
    result = await mcp_999_vault(action="")

    assert result["status"] == "VOID"
    assert result["memory_location"] == "INVALID_ACTION"


@pytest.mark.asyncio
async def test_999_vault_invalid_verdict_returns_void():
    """Test: Invalid verdict returns VOID status."""
    result = await mcp_999_vault(action="seal", verdict="INVALID_VERDICT")

    assert result["status"] == "VOID"
    assert result["memory_location"] == "INVALID_VERDICT"


@pytest.mark.asyncio
async def test_999_vault_valid_actions():
    """Test: All valid actions are accepted."""
    valid_actions = ["seal", "list", "read", "write", "propose"]

    for action in valid_actions:
        result = await mcp_999_vault(action=action, session_id="test_session")
        # Should not return VOID for valid action (unless other validation fails)
        assert result["status"] != "VOID" or result["memory_location"] != "INVALID_ACTION"


# =============================================================================
# EUREKA SIEVE TESTS (VOID/SABAR not stored)
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_void_verdict_not_stored():
    """Test: VOID verdict is NOT stored to ledger (Eureka Sieve)."""
    result = await mcp_999_vault(
        action="seal",
        verdict="VOID",
        session_id="void_test_session"
    )

    assert result["status"] == "SEAL"  # Tool operation succeeded
    assert result["verdict"] == "VOID"
    assert result["memory_location"] == "NOT_STORED"
    assert result["reversible"] is False


@pytest.mark.asyncio
async def test_999_vault_sabar_verdict_not_stored():
    """Test: SABAR verdict is NOT stored to ledger (Eureka Sieve)."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SABAR",
        session_id="sabar_test_session"
    )

    assert result["status"] == "SEAL"  # Tool operation succeeded
    assert result["verdict"] == "SABAR"
    assert result["memory_location"] == "NOT_STORED"
    assert result["reversible"] is True  # SABAR can retry


@pytest.mark.asyncio
async def test_999_vault_seal_verdict_stored():
    """Test: SEAL verdict IS stored to ledger."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SEAL",
        session_id="seal_test_session"
    )

    assert result["status"] == "SEAL"
    assert result["verdict"] == "SEAL"
    assert result["memory_location"] == "L5_CANON"
    assert result["merkle_root"] != ""
    assert result["audit_hash"] != ""


# =============================================================================
# MERKLE ROOT TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_merkle_root_computed():
    """Test: Merkle root is computed from Trinity results."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SEAL",
        session_id="merkle_test",
        init_result={"status": "SEAL"},
        agi_result={"truth_score": 0.97},
        asi_result={"peace_squared": 1.0},
        apex_result={"verdict": "SEAL"}
    )

    assert result["merkle_root"] != ""
    assert len(result["merkle_root"]) == 64  # SHA256 hex length


@pytest.mark.asyncio
async def test_999_vault_merkle_root_deterministic():
    """Test: Same inputs produce same Merkle root."""
    args = {
        "action": "seal",
        "verdict": "SEAL",
        "session_id": "deterministic_test",
        "init_result": {"status": "SEAL"},
        "agi_result": {"truth_score": 0.97},
        "asi_result": {"peace_squared": 1.0},
        "apex_result": {"verdict": "SEAL"}
    }

    result1 = await mcp_999_vault(**args)
    result2 = await mcp_999_vault(**args)

    assert result1["merkle_root"] == result2["merkle_root"]


# =============================================================================
# FLOOR CHECKING TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_seal_checks_f1_f8():
    """Test: Seal action checks F1_Amanah and F8_TriWitness."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SEAL",
        session_id="floor_test"
    )

    assert "F1_Amanah" in result["floors_checked"]
    assert "F8_TriWitness" in result["floors_checked"]


# =============================================================================
# LIST/READ/WRITE TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_list_action():
    """Test: List action returns proper structure."""
    result = await mcp_999_vault(
        action="list",
        target="ledger",
        session_id="list_test"
    )

    assert result["status"] == "SEAL"
    assert "entries" in result
    assert "count" in result


@pytest.mark.asyncio
async def test_999_vault_read_action():
    """Test: Read action returns proper structure."""
    result = await mcp_999_vault(
        action="read",
        target="canon",
        query="test_entry",
        session_id="read_test"
    )

    assert result["status"] == "SEAL"
    assert "entry" in result


# =============================================================================
# ALL TRINITY TOOLS INPUT VALIDATION TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_000_init_invalid_action_returns_void():
    """Test: 000_init with invalid action returns VOID."""
    result = await mcp_000_init(action="invalid")

    assert result["status"] == "VOID"
    assert "F12_InputValidation" in result["floors_checked"]


@pytest.mark.asyncio
async def test_agi_genius_invalid_action_returns_void():
    """Test: agi_genius with invalid action returns VOID."""
    result = await mcp_agi_genius(action="invalid")

    assert result["status"] == "VOID"
    assert result["lane"] == "REFUSE"


@pytest.mark.asyncio
async def test_asi_act_invalid_action_returns_void():
    """Test: asi_act with invalid action returns VOID."""
    result = await mcp_asi_act(action="invalid")

    assert result["status"] == "VOID"
    assert result["witness_status"] == "INVALID"


@pytest.mark.asyncio
async def test_apex_judge_invalid_action_returns_void():
    """Test: apex_judge with invalid action returns VOID."""
    result = await mcp_apex_judge(action="invalid")

    assert result["status"] == "VOID"
    assert result["verdict"] == "VOID"


# =============================================================================
# VALID ACTIONS TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_000_init_valid_action():
    """Test: 000_init with valid action succeeds."""
    result = await mcp_000_init(action="init")

    assert result["status"] in ["SEAL", "SABAR"]


@pytest.mark.asyncio
async def test_agi_genius_valid_action():
    """Test: agi_genius with valid action succeeds."""
    result = await mcp_agi_genius(action="sense", query="test query")

    assert result["status"] in ["SEAL", "SABAR"]


@pytest.mark.asyncio
async def test_asi_act_valid_action():
    """Test: asi_act with valid action succeeds."""
    result = await mcp_asi_act(action="evidence", text="test text")

    assert result["status"] in ["SEAL", "SABAR"]


@pytest.mark.asyncio
async def test_apex_judge_valid_action():
    """Test: apex_judge with valid action succeeds."""
    result = await mcp_apex_judge(action="judge", query="test query")

    assert result["status"] in ["SEAL", "SABAR"]


# =============================================================================
# TIMESTAMP AND AUDIT HASH TESTS
# =============================================================================

@pytest.mark.asyncio
async def test_999_vault_includes_timestamp():
    """Test: Result includes ISO timestamp."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SEAL",
        session_id="timestamp_test"
    )

    assert "sealed_at" in result
    assert "T" in result["sealed_at"]  # ISO format


@pytest.mark.asyncio
async def test_999_vault_audit_hash_computed():
    """Test: Audit hash is computed."""
    result = await mcp_999_vault(
        action="seal",
        verdict="SEAL",
        session_id="audit_test"
    )

    assert "audit_hash" in result
    assert len(result["audit_hash"]) == 64  # SHA256 hex
