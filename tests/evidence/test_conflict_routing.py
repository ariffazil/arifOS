"""
Tests for v45 Conflict Routing
Verify deterministic verdicts based on thresholds.
"""
import pytest
from arifos_core.evidence.evidence_pack import EvidencePack
from arifos_core.evidence.conflict_routing import ConflictRouter, Verdict

def create_pack(conflict=0.0, coverage=1.0, freshness=1.0):
    return EvidencePack(
        query_hash="test",
        coverage_pct=coverage,
        conflict_score=conflict,
        freshness_score=freshness,
        sources=[]
    )

def test_high_conflict_hold_888():
    """Conflict > 0.15 MUST trigger HOLD_888."""
    pack = create_pack(conflict=0.16)
    result = ConflictRouter.evaluate(pack)
    
    assert result.verdict == Verdict.HOLD_888
    assert result.pathway == "GOVERNED"
    assert result.confidence_modifier == 0.0

def test_incomplete_coverage_partial():
    """Coverage < 1.0 on factual query MUST trigger PARTIAL."""
    pack = create_pack(coverage=0.9)
    result = ConflictRouter.evaluate(pack, requires_fact=True)
    
    assert result.verdict == Verdict.PARTIAL
    assert result.pathway == "SLOW"
    # Confidence should be downgraded by coverage
    assert result.confidence_modifier == 0.9

def test_stale_evidence_decay():
    """Freshness < 0.7 MUST trigger PARTIAL + Decay."""
    pack = create_pack(freshness=0.5)
    result = ConflictRouter.evaluate(pack)
    
    assert result.verdict == Verdict.PARTIAL
    # Decay factor = 0.5 / 0.7 = ~0.71
    expected_decay = 0.5 / 0.7
    assert abs(result.confidence_modifier - expected_decay) < 0.01

def test_perfect_seal():
    """Perfect evidence triggers SEAL and FAST path (if conflict 0)."""
    pack = create_pack(conflict=0.0, coverage=1.0, freshness=1.0)
    result = ConflictRouter.evaluate(pack)
    
    assert result.verdict == Verdict.SEAL
    assert result.pathway == "FAST"
    assert result.confidence_modifier == 1.0
