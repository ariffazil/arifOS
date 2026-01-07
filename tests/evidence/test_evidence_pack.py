"""
Tests for v45 EvidencePack
Verify schema validation and hash determinism.
"""
import pytest
from pydantic import ValidationError
from arifos_core.enforcement.evidence.evidence_pack import EvidencePack, EvidenceSource
from tests.utils import make_valid_evidence_pack, VALID_HASH

def test_evidence_pack_hash_determinism():
    """Verify that identical evidence produces identical hashes."""
    pack1 = make_valid_evidence_pack()
    pack2 = make_valid_evidence_pack()
    
    assert pack1.compute_pack_hash() == pack2.compute_pack_hash()

def test_evidence_pack_hash_sensitivity():
    """Verify that changing any attribute changes hash."""
    base_pack = make_valid_evidence_pack(conflict_score=0.1)
    diff_pack = make_valid_evidence_pack(conflict_score=0.15)
    
    assert base_pack.compute_pack_hash() != diff_pack.compute_pack_hash()

def test_range_validation():
    """Verify scores must be 0-1."""
    # coverage_pct > 1.0 -> ValidationError
    with pytest.raises(ValidationError):
        make_valid_evidence_pack(coverage_pct=1.5)

    # conflict_score < 0.0 -> ValidationError
    with pytest.raises(ValidationError):
        make_valid_evidence_pack(conflict_score=-0.1)
