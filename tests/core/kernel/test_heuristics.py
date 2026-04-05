"""
tests/core/kernel/test_heuristics.py — Tests for cognitive heuristics
"""

import pytest
from core.kernel.heuristics import detect_profile, estimate_uncertainty, estimate_risk, compute_system_state

def test_detect_profile_factual():
    assert detect_profile("What is the capital of France?") == "factual"
    assert detect_profile("Explain relativity.") == "factual"
    assert detect_profile("medical diagnosis for flu") == "factual"

def test_detect_profile_crisis():
    assert detect_profile("Emergency! Call an ambulance.") == "crisis"
    assert detect_profile("life-threatening situation") == "crisis"
    assert detect_profile("immediate help needed for suicide") == "crisis"

def test_detect_profile_creative():
    assert detect_profile("Write a poem about the sea.") == "creative"
    assert detect_profile("Imagine a world where cats fly.") == "creative"
    assert detect_profile("Story of a brave knight.") == "creative"

def test_detect_profile_routine():
    assert detect_profile("Hello there.") == "routine"
    assert detect_profile("How are you doing today?") == "routine"

def test_estimate_uncertainty():
    # Base is 0.3
    # "?" adds 0.15 -> 0.45
    # Len < 6 adds 0.15 -> 0.60
    assert estimate_uncertainty("What?") == pytest.approx(0.60)
    
    # Uncertainty words add 0.20
    # "maybe it works" len 14, no "?"
    assert estimate_uncertainty("maybe it works") == pytest.approx(0.50) # 0.3 + 0.2
    
    # Absolutist words add 0.25
    assert estimate_uncertainty("definitely sure") == pytest.approx(0.55) # 0.3 + 0.25
    
    # Short query adds 0.15
    assert estimate_uncertainty("hi") == pytest.approx(0.45) # 0.3 + 0.15

def test_estimate_risk():
    # Base is 0.05
    assert estimate_risk("normal query") == pytest.approx(0.05)
    
    # Sensitive words add 0.75
    assert estimate_risk("medical death layoff") == pytest.approx(0.80)
    
    # Political words add 0.35
    assert estimate_risk("government election") == pytest.approx(0.40)
    
    # Crisis words add 0.50
    assert estimate_risk("urgent emergency") == pytest.approx(0.55)

def test_compute_system_state():
    state = compute_system_state("What is the medical treatment for flu?", loop_count=2, evidence_count=5)
    
    assert state.uncertainty > 0.3
    assert state.risk > 0.05
    assert state.grounding == 1.0
    assert state.loop_count == 2
    assert state.profile == "factual"
    
    # Check no evidence
    state_no_ev = compute_system_state("Simple query", evidence_count=0)
    assert state_no_ev.grounding == 0.0

def test_system_state_to_dict():
    state = compute_system_state("test")
    d = state.to_dict()
    assert "uncertainty" in d
    assert "risk" in d
    assert d["loop_count"] == 0
