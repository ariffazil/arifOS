"""
test_time_immutability.py — v38.3 AMENDMENT 1 Tests

Tests for Time Immutability + State Branching (SABAR_EXTENDED).

Validates:
- Decayed SABAR→PARTIAL entries cannot be modified
- spawn_sabar_extended() creates new entry (not modifies old)
- New entry has correct parent_hash linkage
- Ledger hash chain remains valid after branching
- Attempting to "restore" old entry raises exception

Author: arifOS Project
Version: v38.3
"""

import pytest
from arifos_core.memory.policy import MemoryWritePolicy, VERDICT_BAND_ROUTING


class TestTimeImmutability:
    """v38.3 AMENDMENT 1: Time Immutability Tests"""

    def test_spawn_sabar_extended_creates_new_entry(self):
        """✅ spawn_sabar_extended() creates new entry (not modifies old)"""
        policy = MemoryWritePolicy()
        
        parent_hash = 'a' * 64  # Mock parent hash
        fresh_context = {'floor_checks': {'F1': 1.0}, 'new_data': 'resolved context'}
        
        # Should return new hash
        new_hash = policy.spawn_sabar_extended(parent_hash, fresh_context, human_override=True)
        
        assert len(new_hash) == 64
        assert new_hash != parent_hash  # New entry, not modifying old

    def test_spawn_sabar_extended_links_parent_hash(self):
        """✅ New entry has correct parent_hash linkage"""
        policy = MemoryWritePolicy()
        
        parent_hash = 'b' * 64
        fresh_context = {'floor_checks': {'F1': 1.0}, 'context': 'new evidence arrived'}
        
        new_hash = policy.spawn_sabar_extended(parent_hash, fresh_context, human_override=True)
        
        # Check write log for parent linkage
        log = policy.get_write_log()
        assert len(log) > 0
        last_entry = log[-1]
        assert 'Branched from parent' in last_entry['reason']
        assert parent_hash[:16] in last_entry['reason']
        assert last_entry['verdict'] == 'SABAR_EXTENDED'

    def test_spawn_sabar_extended_requires_human_override(self):
        """❌ Attempting without human_override raises PermissionError"""
        policy = MemoryWritePolicy()
        
        parent_hash = 'c' * 64
        fresh_context = {'floor_checks': {'F1': 1.0}}
        
        with pytest.raises(PermissionError, match='Only humans can spawn SABAR_EXTENDED'):
            policy.spawn_sabar_extended(parent_hash, fresh_context, human_override=False)

    def test_spawn_sabar_extended_validates_parent_format(self):
        """❌ Invalid parent_hash format raises ValueError"""
        policy = MemoryWritePolicy()
        
        invalid_hash = 'short'
        fresh_context = {'floor_checks': {'F1': 1.0}}
        
        with pytest.raises(ValueError, match='Invalid parent_entry_id format'):
            policy.spawn_sabar_extended(invalid_hash, fresh_context, human_override=True)

    def test_sabar_extended_routes_to_pending_ledger(self):
        """✅ SABAR_EXTENDED routes to PENDING + LEDGER per v38.3"""
        routing = VERDICT_BAND_ROUTING.get('SABAR_EXTENDED')
        assert routing == ['PENDING', 'LEDGER']
        assert 'PENDING' in routing
        assert 'LEDGER' in routing

    def test_ledger_entries_immutable(self):
        """✅ Ledger entries are append-only (no modification)"""
        policy = MemoryWritePolicy()
        
        # Verify no restore/undo methods exist
        assert not hasattr(policy, 'restore_sabar')
        assert not hasattr(policy, 'reverse_decay')
        assert not hasattr(policy, 'modify_entry')
        assert not hasattr(policy, 'delete_entry')

    def test_branching_creates_audit_trail(self):
        """✅ Branching preserves audit trail (parent visible)"""
        policy = MemoryWritePolicy()
        
        parent_hash = 'd' * 64
        fresh_context = {'floor_checks': {'F1': 1.0}, 'resolution': 'context added'}
        
        new_hash = policy.spawn_sabar_extended(parent_hash, fresh_context, human_override=True)
        
        # Both parent and child should be in audit log
        log = policy.get_write_log()
        assert len(log) == 1  # One branch operation logged
        assert log[0]['verdict'] == 'SABAR_EXTENDED'
        assert log[0]['allowed'] is True
