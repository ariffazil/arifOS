"""
Tests for v46 Conflict Routing
Verify deterministic routing signals based on evidence physics thresholds.

v46 Update: Changed from Verdict to RoutingSignal to enforce architectural clarity.
"""
import pytest
from arifos_core.evidence.evidence_pack import EvidencePack
from arifos_core.evidence.conflict_routing import ConflictRouter
from arifos_core.evidence.routing_signal import RoutingSignal
from tests.utils import make_valid_evidence_pack

def create_pack(conflict=0.0, coverage=1.0, freshness=1.0):
    # Use valid helper but map args to v45 schema overrides
    return make_valid_evidence_pack(
        conflict_score=conflict,
        coverage_pct=coverage,
        freshness_score=freshness,
        conflict_flag=(conflict > 0.15) # Assuming older test logic expected flag
    )

def test_high_conflict_governed():
    """Conflict > 0.15 MUST trigger GOVERNED routing."""
    pack = create_pack(conflict=0.16)
    result = ConflictRouter.evaluate(pack)

    assert result.signal == RoutingSignal.GOVERNED
    assert result.pathway == "GOVERNED"
    assert result.confidence_modifier == 0.0

def test_incomplete_coverage_slow_path():
    """Coverage < 1.0 on factual query MUST trigger SLOW_PATH routing."""
    pack = create_pack(coverage=0.9)
    result = ConflictRouter.evaluate(pack, requires_fact=True)

    assert result.signal == RoutingSignal.SLOW_PATH
    assert result.pathway == "SLOW"
    # Confidence should be downgraded by coverage
    assert result.confidence_modifier == 0.9

def test_stale_evidence_decay():
    """Freshness < 0.7 MUST trigger SLOW_PATH + Decay."""
    pack = create_pack(freshness=0.5)
    result = ConflictRouter.evaluate(pack)

    assert result.signal == RoutingSignal.SLOW_PATH
    # Decay factor = 0.5 / 0.7 = ~0.71
    expected_decay = 0.5 / 0.7
    assert abs(result.confidence_modifier - expected_decay) < 0.01

def test_perfect_fast_path():
    """Perfect evidence triggers FAST_PATH and FAST pathway (if conflict 0)."""
    pack = create_pack(conflict=0.0, coverage=1.0, freshness=1.0)
    result = ConflictRouter.evaluate(pack)

    assert result.signal == RoutingSignal.FAST_PATH
    assert result.pathway == "FAST"
    assert result.confidence_modifier == 1.0
