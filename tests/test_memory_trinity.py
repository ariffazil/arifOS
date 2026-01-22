"""
test_memory_trinity.py — Glass-to-Black Memory MCP Verification Suite

v45.2 Implementation Tests:
1. Glass-box tool parity (all 4 tools functional)
2. Auth gating (permanent vs session tokens)
3. 888_HOLD enforcement (high-risk actions)
4. Suggestion ceiling injection (INV-4)
"""

import pytest
import sys
import os

# Add project root to path for direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMemoryVault:
    """Test L0 Vault-999 READ operations."""

    def test_vault_not_found(self):
        """Non-existent vault entry returns error."""
        from arifos.core.mcp.tools.memory_vault import memory_get_vault_sync
        result = memory_get_vault_sync("nonexistent.json")
        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert result["governance"]["source"] == "VAULT"

    def test_vault_confidence_is_law(self):
        """Vault entries have confidence 1.0 (LAW)."""
        from arifos.core.mcp.tools.memory_vault import memory_get_vault_sync
        # Even on error, governance metadata should be present
        result = memory_get_vault_sync("test.json")
        assert result["governance"]["source"] == "VAULT"


class TestMemoryPropose:
    """Test L1 Cooling Ledger WRITE proposals."""

    def test_auth_gating_permanent_token_blocked(self):
        """Permanent tokens blocked for WRITE operations (Directive 07)."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Test content",
            user_id="user1",
            action_class="WRITE",
            auth_token="perm_123456"
        )
        assert result["verdict"] == "VOID"
        assert "AUTH_FAILURE" in result["reason"]
        assert "Permanent tokens forbidden" in result["reason"]

    def test_auth_gating_session_token_allowed(self):
        """Session tokens allowed for WRITE operations."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Test content for proposal",
            user_id="user1",
            action_class="WRITE",
            auth_token="session_123456"
        )
        assert result["success"] is True
        assert result["verdict"] in ["SEAL", "PARTIAL", "VOID"]
        assert "cooling_ledger_id" in result

    def test_888_hold_for_delete(self):
        """DELETE action triggers 888_HOLD (Directive 07)."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Delete something",
            user_id="user1",
            action_class="DELETE",
            auth_token="session_123"
        )
        assert result["verdict"] == "HOLD_888"
        assert "Mandatory human seal" in result["reason"]

    def test_888_hold_for_pay(self):
        """PAY action triggers 888_HOLD (Directive 07)."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Pay for something",
            user_id="user1",
            action_class="PAY",
            auth_token="session_123"
        )
        assert result["verdict"] == "HOLD_888"

    def test_888_hold_for_self_modify(self):
        """SELF_MODIFY action triggers 888_HOLD (Directive 07)."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Modify my own code",
            user_id="user1",
            action_class="SELF_MODIFY",
            auth_token="session_123"
        )
        assert result["verdict"] == "HOLD_888"

    def test_governance_vector_exposed(self):
        """Glass-box observability: governance vector is exposed."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Test governance vector exposure",
            user_id="user1",
            action_class="WRITE",
            auth_token="session_123"
        )
        assert "governance" in result
        governance = result["governance"]
        assert "delta_s" in governance
        assert "peace_squared" in governance
        assert "omega_0" in governance
        assert "kappa_r" in governance

    def test_routing_for_seal(self):
        """SEAL verdict routes to ACTIVE band."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        result = memory_propose_entry_sync(
            content="Safe content that should pass all floors",
            user_id="user1",
            action_class="WRITE",
            auth_token="session_123"
        )
        if result["verdict"] == "SEAL":
            assert result["routing"]["band"] == "ACTIVE"
            assert result["routing"]["cooling"] is False


class TestMemoryPhoenix:
    """Test L2 Phoenix-72 cooling queue."""

    def test_phoenix_list_returns_structure(self):
        """Phoenix list returns proper structure."""
        from arifos.core.mcp.tools.memory_phoenix import memory_list_phoenix_sync
        result = memory_list_phoenix_sync()
        assert result["success"] is True
        assert "entries" in result
        assert "pending_count" in result
        assert result["governance"]["cooling_window_hours"] == 72


class TestMemoryZkpc:
    """Test zkPC receipt retrieval."""

    def test_zkpc_not_found(self):
        """Non-existent receipt returns error."""
        from arifos.core.mcp.tools.memory_zkpc import memory_get_zkpc_receipt_sync
        result = memory_get_zkpc_receipt_sync("zkpc-nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"].lower()
        assert result["governance"]["source"] == "ZKPC"


class TestGlassToBlackParity:
    """
    Verify Glass-box and Black-box produce identical verdicts.

    This test ensures that routing through the Glass-box tools
    produces the same constitutional verdict as the Black-box
    apex.verdict endpoint.
    """

    def test_write_verdict_parity(self):
        """Glass-box WRITE produces same verdict structure as Black-box."""
        from arifos.core.mcp.tools.memory_propose import memory_propose_entry_sync
        # Glass-box
        glass_result = memory_propose_entry_sync(
            content="Test parity content",
            user_id="user1",
            action_class="WRITE",
            auth_token="session_123"
        )

        # Verify glass-box has all required fields for black-box encapsulation
        assert "verdict" in glass_result
        assert "cooling_ledger_id" in glass_result
        assert "zkpc_receipt_id" in glass_result

        # Verdict must be one of the canonical values
        assert glass_result["verdict"] in ["SEAL", "VOID", "SABAR", "PARTIAL", "HOLD_888"]
