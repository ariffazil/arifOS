"""
Tests for v45 Semantic Firewall (Telemetry Isolation)
Verify that APEX receives only physics attributes.
"""
import pytest
from arifos.core.enforcement.judiciary.semantic_firewall import SemanticFirewall, ApexTelemetry
from arifos.core.enforcement.evidence.evidence_pack import EvidencePack
from tests.utils import make_valid_evidence_pack

def test_sanitization_integrity():
    """Verify raw metrics are converted to clean telemetry."""
    
    # 1. Raw Input (Simulated)
    raw_metrics = {
        "truth": 0.99,
        "delta_s": 0.5,
        "peace_squared": 1.0,
        "kappa_r": 0.95,
        "omega_0": 0.04,
        "tri_witness": 0.98
    }
    
    evidence = make_valid_evidence_pack(
        coverage_pct=1.0,
        conflict_score=0.0
    )
    
    flags = []
    
    # 2. Firewalled
    telemetry = SemanticFirewall.sanitize(raw_metrics, evidence, flags)
    
    # 3. Assertions
    assert isinstance(telemetry, ApexTelemetry)
    assert telemetry.truth_score == 0.99
    assert telemetry.conflict_flag is False
    assert telemetry.evidence_pack_hash == evidence.compute_pack_hash()
    
    # Verify Hash Determinism
    t2 = SemanticFirewall.sanitize(raw_metrics, evidence, flags)
    assert telemetry.compute_hash() == t2.compute_hash()

def test_semantic_exclusion():
    """Verify telemetry object has NO text fields."""
    telemetry = ApexTelemetry(
        truth_score=1.0, delta_entropy=1.0, peace_squared=1.0,
        empathy_score=1.0, humility_score=1.0, tri_witness_score=1.0,
        coverage_pct=1.0, conflict_score=0.0, freshness_score=1.0,
        jargon_density=0.0, conflict_flag=False, sentinel_flag_blocking=False,
        evidence_pack_hash="hash"
    )
    
    # Inspect attributes
    attrs = vars(telemetry)
    for key, value in attrs.items():
        # Ensure no long strings (heuristic for text)
        if isinstance(value, str):
            assert len(value) < 128, f"Field {key} contains potentially raw text: {value}"
            assert " " not in value, f"Field {key} contains spaces (likely text): {value}"

def test_default_safety():
    """Verify missing metrics default to safe/pessimistic values."""
    empty_metrics = {}
    # Duck typing mock for broken evidence
    class BrokenEvidence:
        pass
        
    telemetry = SemanticFirewall.sanitize(empty_metrics, BrokenEvidence(), [])
    
    # Should default to high conflict/low truth
    assert telemetry.truth_score == 0.0
    assert telemetry.conflict_score == 1.0 # High conflict default
    assert telemetry.conflict_flag is True
