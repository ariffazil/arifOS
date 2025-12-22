"""
Tests for v45 EvidencePack
Verify schema validation and hash determinism.
"""
import pytest
import hashlib
from arifos_core.evidence.evidence_pack import EvidencePack, EvidenceSource

def test_evidence_pack_hash_determinism():
    """Verify that identical evidence produces identical hashes."""
    src1 = EvidenceSource(source_id="s1", doc_hash="abc", timestamp=100.0)
    
    pack1 = EvidencePack(
        query_hash="q123",
        sources=[src1],
        coverage_pct=0.9,
        conflict_score=0.1,
        freshness_score=0.8
    )
    
    pack2 = EvidencePack(
        query_hash="q123",
        sources=[src1],
        coverage_pct=0.9,
        conflict_score=0.1,
        freshness_score=0.8
    )
    
    assert pack1.compute_pack_hash() == pack2.compute_pack_hash()

def test_evidence_pack_hash_sensitivity():
    """Verify that changing any attribute changes high hash."""
    src1 = EvidenceSource(source_id="s1", doc_hash="abc", timestamp=100.0)
    
    base_pack = EvidencePack(
        query_hash="q123", 
        sources=[src1],
        coverage_pct=0.9,
        conflict_score=0.1,
        freshness_score=0.8
    )
    
    # Change conflict score
    diff_pack = EvidencePack(
        query_hash="q123",
        sources=[src1],
        coverage_pct=0.9,
        conflict_score=0.15, # Changed
        freshness_score=0.8
    )
    
    assert base_pack.compute_pack_hash() != diff_pack.compute_pack_hash()

def test_range_validation():
    """Verify scores must be 0-1."""
    with pytest.raises(ValueError):
        EvidencePack(
            query_hash="q", 
            coverage_pct=1.5, # Invalid
            conflict_score=0.0,
            freshness_score=1.0
        )
        
    with pytest.raises(ValueError):
        EvidencePack(
            query_hash="q", 
            coverage_pct=0.5,
            conflict_score=-0.1, # Invalid
            freshness_score=1.0
        )
