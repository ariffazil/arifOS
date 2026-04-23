"""
Contract Tests for arifOS.memory

Validates:
- MemoryRecord schema
- Write gates
- Lane behavior
- Retrieval ranking
- Decay rules
"""

from datetime import datetime, timedelta

import pytest

from ..memory.lanes.constitutional_v2 import ConstitutionalMemoryLane
from ..memory.lanes.working import WorkingMemoryLane
from ..memory.types_v2 import (
    ConfidenceClass,
    DecayPolicy,
    Governance,
    MemoryRecord,
    MemoryType,
    Source,
)


class TestMemoryRecordSchema:
    """Validate MemoryRecord structure and validation."""
    
    def test_minimal_valid_record(self):
        """A minimal record should be valid."""
        record = MemoryRecord(
            memory_id="mem_test_001",
            memory_type=MemoryType.WORKING,
            title="Test Memory",
            content="This is a test",
        )
        
        assert record.memory_id == "mem_test_001"
        assert record.memory_type == MemoryType.WORKING
        assert record.governance.confidence_class == ConfidenceClass.INFERRED
    
    def test_vault_backed_derived_fields(self):
        """Vault-backed records should have correct derived fields."""
        record = MemoryRecord(
            memory_id="mem_test_002",
            memory_type=MemoryType.SEMANTIC,
            title="Vault Backed Fact",
            content="This is sealed",
            governance=Governance(
                confidence=0.99,
                confidence_class=ConfidenceClass.SEALED_FROM_VAULT,
            ),
        )
        
        # Derived fields set in __post_init__
        assert record.retrieval.vault_backed == True
        assert record.retrieval.source_weight == 1.0


class TestLaneBehavior:
    """Validate lane-specific behavior."""
    
    def test_working_memory_expires(self):
        """Working memory should expire."""
        lane = WorkingMemoryLane(session_id="test_session")
        
        record = lane.store(
            title="Active Task",
            content="Do something",
            source=Source(origin="system", session_id="test_session"),
            ttl_minutes=1,
        )
        
        # Should be active immediately
        active = lane.get_active()
        assert len(active) == 1
        
        # Simulate expiry
        record.time.expires_at = datetime.utcnow() - timedelta(minutes=5)
        
        # Should be expired now
        lane.expire_old()
        active = lane.get_active()
        assert len(active) == 0
    
    def test_constitutional_requires_authority(self):
        """Constitutional changes require 888_JUDGE."""
        lane = ConstitutionalMemoryLane()
        
        # Try to amend without authority
        result = lane.amend_rule(
            rule_id="F1_AMANAH",
            new_content="New content",
            amendment_authority="system",
            amendment_reason="Test",
        )
        
        assert result is None
        
        # Try with correct authority
        result = lane.amend_rule(
            rule_id="F1_AMANAH",
            new_content="All actions must be reversible or auditable. Updated.",
            amendment_authority="888_JUDGE",
            amendment_reason="Clarification",
        )
        
        assert result is not None


class TestDecayRules:
    """Validate per-lane decay rules."""
    
    def test_working_fast_decay(self):
        """Working memory should decay fast."""
        record = MemoryRecord(
            memory_id="mem_test_006",
            memory_type=MemoryType.WORKING,
            title="Scratch",
            content="Temporary",
            decay_policy=DecayPolicy(decay_type="expire", expires_at=datetime.utcnow() - timedelta(hours=1)),
        )
        
        should_remove = record.apply_decay()
        assert should_remove == True
    
    def test_constitutional_never_decay(self):
        """Constitutional memory should never decay."""
        record = MemoryRecord(
            memory_id="mem_test_007",
            memory_type=MemoryType.CONSTITUTIONAL,
            title="F1 Rule",
            content="Immutable rule",
            decay_policy=DecayPolicy(decay_type="never"),
        )
        
        should_remove = record.apply_decay()
        assert should_remove == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
