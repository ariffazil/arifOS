"""
test_memory_phase1_routing.py — Phase 1 EUREKA Routing Tests

Tests verdict-to-band routing correctness:
1. SABAR → PENDING
2. SABAR_EXTENDED → PENDING
3. HOLD_888 → PENDING
4. PARTIAL → PHOENIX
5. Forbidden writes return DROP

Author: arifOS Project
Version: v38.3 Phase 1
"""

import pytest
from arifos_core.memory.eureka_types import (
    ActorRole,
    MemoryBand,
    Verdict,
    MemoryWriteRequest,
)
from arifos_core.memory.eureka_router import route_write
from arifos_core.memory.eureka_store import InMemoryStore


class TestPhase1Routing:
    """Test verdict-to-band routing logic."""

    def test_sabar_routes_to_pending(self):
        """SABAR verdict routes to PENDING band."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SABAR,
            reason="Missing context",
            content={"issue": "incomplete data"},
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.PENDING
        assert decision.allowed is True
        assert decision.action == "APPEND"

    def test_sabar_extended_routes_to_pending(self):
        """SABAR_EXTENDED verdict routes to PENDING band."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SABAR_EXTENDED,
            reason="Branched state for retry",
            content={"parent": "abc123"},
            parent_hash="abc123",
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.PENDING
        assert decision.allowed is True

    def test_hold_888_routes_to_pending(self):
        """HOLD_888 verdict routes to PENDING band."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.HOLD_888,
            reason="High-stakes action requires human review",
            content={"action": "database migration"},
            high_stakes=True,
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.PENDING
        assert decision.allowed is True

    def test_partial_routes_to_phoenix(self):
        """PARTIAL verdict routes to PHOENIX band."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.PARTIAL,
            reason="Floor concern detected",
            content={"concern": "Peace² threshold"},
        )
        decision = route_write(req)
        
        assert decision.target_band == MemoryBand.PHOENIX
        assert decision.allowed is True

    def test_forbidden_write_returns_drop(self):
        """Forbidden writes return DROP action."""
        # TOOL writes are always forbidden
        req = MemoryWriteRequest(
            actor_role=ActorRole.TOOL,
            verdict=Verdict.SEAL,
            reason="Tool write attempt",
            content={"test": "data"},
        )
        decision = route_write(req)
        
        assert decision.allowed is False
        assert decision.action == "DROP"

    def test_routing_preserves_reason(self):
        """Router preserves reason in decision."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SABAR,
            reason="Need more evidence",
            content={"query": "incomplete"},
        )
        decision = route_write(req)
        
        assert "SABAR" in decision.why or "PENDING" in decision.why

    def test_high_stakes_flag_preserved(self):
        """High-stakes flag is considered in routing."""
        req = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.HOLD_888,
            reason="Production deployment",
            content={"action": "deploy"},
            high_stakes=True,
        )
        decision = route_write(req)
        
        # High-stakes HOLD_888 goes to PENDING for review
        assert decision.target_band == MemoryBand.PENDING

    def test_in_memory_store_append(self):
        """InMemoryStore correctly appends records."""
        store = InMemoryStore()
        
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SEAL,
            reason="Test append",
            content={"test": "data"},
        )
        decision = route_write(req)
        
        store.append(decision.target_band, req, decision)
        
        assert len(store.records) == 1
        assert store.records[0]["band"] == decision.target_band.value
        assert store.records[0]["request"] == req
        assert store.records[0]["decision"] == decision

    def test_multiple_writes_to_different_bands(self):
        """Multiple writes route to correct bands independently."""
        store = InMemoryStore()
        
        # SABAR → PENDING
        req1 = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SABAR,
            reason="Test 1",
            content={"id": 1},
        )
        dec1 = route_write(req1)
        store.append(dec1.target_band, req1, dec1)
        
        # PARTIAL → PHOENIX
        req2 = MemoryWriteRequest(
            actor_role=ActorRole.JUDICIARY,
            verdict=Verdict.PARTIAL,
            reason="Test 2",
            content={"id": 2},
        )
        dec2 = route_write(req2)
        store.append(dec2.target_band, req2, dec2)
        
        # VOID → VOID
        req3 = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.VOID,
            reason="Test 3",
            content={"id": 3},
        )
        dec3 = route_write(req3)
        store.append(dec3.target_band, req3, dec3)
        
        assert len(store.records) == 3
        assert store.records[0]["band"] == "PENDING"
        assert store.records[1]["band"] == "PHOENIX"
        assert store.records[2]["band"] == "VOID"

    def test_store_clear(self):
        """InMemoryStore clear() removes all records."""
        store = InMemoryStore()
        
        req = MemoryWriteRequest(
            actor_role=ActorRole.ENGINE,
            verdict=Verdict.SEAL,
            reason="Test",
            content={},
        )
        decision = route_write(req)
        store.append(decision.target_band, req, decision)
        
        assert len(store.records) == 1
        store.clear()
        assert len(store.records) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
