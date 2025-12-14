"""
test_memory_phase1_invariants.py — Phase 1 EUREKA Invariant Tests

Tests core constitutional invariants:
1. TOOL writes are always dropped (F1 Amanah)
2. VAULT requires human seal
3. VOID verdict routes to VOID band
4. SEAL without human seal routes to LEDGER (not VAULT)

Author: arifOS Project
Version: v38.3 Phase 1
"""

import pytest
from arifos_core.memory.eureka_types import (
    ActorRole,
    MemoryBand,
    Verdict,
    MemoryWriteRequest,
    MemoryWriteDecision,
)
from arifos_core.memory.eureka_router import route_write


class TestPhase1Invariants:
    """Test constitutional memory invariants."""

    def test_tool_writes_always_dropped(self):
        """INV-1: TOOL writes are always dropped (F1 Amanah)."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.TOOL,
            verdict=Verdict.SEAL,
            reason="Tool attempting write",
            content={"test": "data"},
            human_seal=True,  # Even with human seal
        )
        decision = route_write(req)
        
        assert decision.allowed is False
        assert decision.action == "DROP"
        assert "Tool" in decision.why or "Amanah" in decision.why

    def test_vault_requires_human_seal_explicit(self):
        """INV-2a: VAULT requires explicit human seal."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.HUMAN,
            verdict=Verdict.SEAL,
            reason="Human sealing to vault",
            content={"law": "amendment"},
            human_seal=True,  # Explicit seal
        )
        decision = route_write(req)
        
        assert decision.allowed is True
        assert decision.target_band == MemoryBand.VAULT
        assert decision.action == "APPEND"

    def test_vault_forbidden_without_human_seal(self):
        """INV-2b: VAULT write forbidden without human seal."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.HUMAN,
            verdict=Verdict.SEAL,
            reason="Human without seal",
            content={"law": "amendment"},
            human_seal=False,  # No seal
        )
        decision = route_write(req)
        
        # Should route to LEDGER, not VAULT
        assert decision.target_band == MemoryBand.LEDGER
        assert decision.target_band != MemoryBand.VAULT

    def test_vault_forbidden_for_engine(self):
        """INV-2c: ENGINE cannot write to VAULT even with seal flag."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SEAL,
            reason="Engine attempting vault write",
            content={"law": "amendment"},
            human_seal=True,  # Even with seal flag
        )
        decision = route_write(req)
        
        # Should NOT route to VAULT
        assert decision.target_band != MemoryBand.VAULT
        assert decision.target_band == MemoryBand.LEDGER

    def test_void_verdict_routes_to_void_band(self):
        """INV-3: VOID verdict always routes to VOID band."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.VOID,
            reason="Floor violation",
            content={"error": "details"},
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.VOID
        assert decision.allowed is True  # VOID is allowed for diagnostics

    def test_seal_without_human_seal_routes_to_ledger(self):
        """INV-4: SEAL without human seal routes to LEDGER (SEAL-ready, not canon)."""
        # Test with ENGINE
        req_engine = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SEAL,
            reason="Engine SEAL verdict",
            content={"result": "success"},
            human_seal=False,
        )
        decision_engine = route_write(req_engine)
        
        assert decision_engine.target_band == MemoryBand.LEDGER
        assert decision_engine.target_band != MemoryBand.VAULT
        
        # Test with JUDICIARY
        req_judiciary = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.SEAL,
            reason="APEX PRIME SEAL verdict",
            content={"verdict": "SEAL"},
            human_seal=False,
        )
        decision_judiciary = route_write(req_judiciary)
        
        assert decision_judiciary.target_band == MemoryBand.LEDGER
        assert decision_judiciary.target_band != MemoryBand.VAULT

    def test_void_never_canonical(self):
        """INV-5: VOID band is never canonical (diagnostic only)."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.VOID,
            reason="Diagnostic write",
            content={"error": "test"},
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.VOID
        # VOID should never be marked as requiring human seal (it's diagnostic)
        assert decision.requires_human_seal is False

    def test_human_role_authority_boundary(self):
        """INV-6: Only HUMAN role can write to VAULT (authority boundary)."""
        # Test that JUDICIARY cannot write to VAULT
        req_judiciary = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.SEAL,
            reason="APEX attempting vault",
            content={"law": "test"},
            human_seal=True,
        )
        decision_judiciary = route_write(req_judiciary)
        assert decision_judiciary.target_band != MemoryBand.VAULT
        
        # Test that ENGINE cannot write to VAULT
        req_engine = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SEAL,
            reason="Engine attempting vault",
            content={"law": "test"},
            human_seal=True,
        )
        decision_engine = route_write(req_engine)
        assert decision_engine.target_band != MemoryBand.VAULT
        
        # Only HUMAN + human_seal can write to VAULT
        req_human = MemoryWriteRequest(
            actor_role=ActorRole.HUMAN,
            verdict=Verdict.SEAL,
            reason="Human sealing",
            content={"law": "test"},
            human_seal=True,
        )
        decision_human = route_write(req_human)
        assert decision_human.target_band == MemoryBand.VAULT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
