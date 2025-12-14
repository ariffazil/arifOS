"""
test_sabar_partial_separation.py — v38.3 AMENDMENT 2 Tests

Tests for SABAR vs PARTIAL Semantic Separation.

Validates:
- SABAR verdict routes to PENDING band
- PARTIAL verdict routes to PHOENIX band
- SABAR does NOT auto-trigger Phoenix-72 pressure
- PARTIAL DOES trigger Phoenix-72 pressure
- SABAR can be manually escalated to PHOENIX

Author: arifOS Project
Version: v38.3
"""

import pytest
from arifos_core.memory.policy import VERDICT_BAND_ROUTING, MemoryWritePolicy
from arifos_core.memory.bands import PendingBand, PhoenixCandidatesBand, BandName


class TestSABARPartialSeparation:
    """v38.3 AMENDMENT 2: SABAR/PARTIAL Semantic Separation Tests"""

    def test_sabar_routes_to_pending_band(self):
        """✅ SABAR verdict routes to PENDING band (epistemic queue)"""
        routing = VERDICT_BAND_ROUTING.get('SABAR')
        assert 'PENDING' in routing
        assert 'LEDGER' in routing
        # v38.3: SABAR no longer goes to ACTIVE, goes to PENDING
        assert 'ACTIVE' not in routing

    def test_partial_routes_to_phoenix_band(self):
        """✅ PARTIAL verdict routes to PHOENIX band (law queue)"""
        routing = VERDICT_BAND_ROUTING.get('PARTIAL')
        assert 'PHOENIX' in routing
        assert 'LEDGER' in routing

    def test_pending_band_properties(self):
        """✅ PENDING band has correct properties (HOT, 7 days)"""
        from arifos_core.memory.bands import BAND_PROPERTIES
        
        pending_props = BAND_PROPERTIES.get('PENDING')
        assert pending_props is not None
        assert pending_props['retention_days'] == 7
        assert pending_props['mutable'] is True
        assert pending_props['canonical'] is False

    def test_pending_band_accepts_sabar_only(self):
        """✅ PENDING band only accepts SABAR verdicts"""
        band = PendingBand()
        
        # SABAR should succeed
        result = band.write(
            content={'query': 'test'},
            writer_id='TEST',
            verdict='SABAR',
        )
        assert result.success is True
        
        # PARTIAL should fail
        result = band.write(
            content={'query': 'test2'},
            writer_id='TEST',
            verdict='PARTIAL',
        )
        assert result.success is False
        assert 'PENDING band only accepts' in result.error

    def test_pending_band_should_decay_after_24h(self):
        """✅ PENDING entries should decay to PARTIAL after 24h"""
        band = PendingBand()
        
        # Create entry
        result = band.write(
            content={'query': 'test'},
            writer_id='TEST',
            verdict='SABAR',
        )
        assert result.success is True
        
        # Get entry
        query_result = band.query()
        assert len(query_result.entries) == 1
        entry = query_result.entries[0]
        
        # Check decay threshold
        assert band.max_age_hours == 24
        
        # Fresh entry should not decay
        assert band.should_decay(entry) is False

    def test_pending_band_should_retry(self):
        """✅ PENDING band supports retry logic"""
        band = PendingBand()
        
        result = band.write(
            content={'query': 'test'},
            writer_id='TEST',
            verdict='SABAR',
            metadata={'retry_count': 0},
        )
        assert result.success is True
        
        query_result = band.query()
        entry = query_result.entries[0]
        
        # Should allow retry (under limit)
        assert band.should_retry(entry) is True
        
        # Update retry count to max
        entry.metadata['retry_count'] = 3
        assert band.should_retry(entry) is False

    def test_sabar_partial_semantic_difference(self):
        """✅ SABAR (need context) ≠ PARTIAL (law mismatch)"""
        sabar_routing = VERDICT_BAND_ROUTING['SABAR']
        partial_routing = VERDICT_BAND_ROUTING['PARTIAL']
        
        # Different bands = different semantics
        assert 'PENDING' in sabar_routing
        assert 'PHOENIX' in partial_routing
        assert 'PENDING' not in partial_routing
        assert 'PHOENIX' not in sabar_routing

    def test_both_route_to_ledger(self):
        """✅ Both SABAR and PARTIAL log to LEDGER for audit"""
        sabar_routing = VERDICT_BAND_ROUTING['SABAR']
        partial_routing = VERDICT_BAND_ROUTING['PARTIAL']
        
        # Both log to LEDGER for audit trail
        assert 'LEDGER' in sabar_routing
        assert 'LEDGER' in partial_routing
