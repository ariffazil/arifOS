
from __future__ import annotations
import pytest
import time
from core.governance_kernel import GovernanceKernel, GovernanceState, AuthorityLevel
from core.enforcement.genius import calculate_genius, floors_to_dials

@pytest.fixture
def kernel():
    return GovernanceKernel(session_id="test_temporal")

def test_metabolic_flux_calculation(kernel):
    # Simulate work: 1000 tokens in 1 second
    kernel.tokens_consumed = 1000
    kernel.last_transition_at = time.time() - 1.0
    
    stability = kernel.temporal_stability
    # Flux should be ~1000.0
    assert kernel.metabolic_flux == pytest.approx(1000.0, rel=0.1)
    assert 0.0 <= stability <= 1.0

def test_high_flux_dampens_stability(kernel):
    # Scenario: Extreme haste (10,000 tokens in 0.01s)
    kernel.tokens_consumed = 10000
    kernel.last_transition_at = time.time() - 0.01 
    
    stability = kernel.temporal_stability
    # Flux penalty will be maxed at 1.0
    # Stability = 1.0 - (0.6*1.0 + 0.4*0) = 0.4
    assert stability == pytest.approx(0.4)

def test_temporal_jitter_dampens_stability(kernel):
    # Scenario: High jitter (100ms)
    kernel.temporal_jitter = 100.0
    # No tokens consumed, so no flux
    kernel.tokens_consumed = 0
    kernel.last_transition_at = time.time()
    
    stability = kernel.temporal_stability
    # Jitter penalty maxed at 1.0
    # Stability = 1.0 - (0.6*0 + 0.4*1.0) = 0.6
    assert stability == pytest.approx(0.6)

def test_combined_temporal_stress(kernel):
    # High flux AND high jitter
    kernel.tokens_consumed = 5000
    kernel.last_transition_at = time.time() - 0.01 
    kernel.temporal_jitter = 100.0
    
    stability = kernel.temporal_stability
    # Stability = 1.0 - (0.6*1.0 + 0.4*1.0) = 0.0
    assert stability == pytest.approx(0.0)

def test_p_dial_integration(kernel):
    # Verify that kernel.temporal_stability affects the P dial
    from core.shared.types import FloorScores
    
    # 1. Register this kernel as 'global' so floors_to_dials sees it
    from core.governance_kernel import _governance_kernels
    _governance_kernels["global"] = kernel
    
    # Reset kernel to perfect stability
    kernel.tokens_consumed = 0
    kernel.temporal_jitter = 0
    kernel.last_transition_at = time.time()
    
    floors = FloorScores()
    
    # Baseline P
    dials_perfect = floors_to_dials(floors)
    p_perfect = dials_perfect.P
    
    # Forced instability
    kernel.tokens_consumed = 10000
    kernel.last_transition_at = time.time() - 0.01 # Stability = 0.4
    
    dials_unstable = floors_to_dials(floors)
    p_unstable = dials_unstable.P
    
    assert p_unstable < p_perfect
    assert p_unstable == pytest.approx(p_perfect * 0.4)

def test_get_current_state_telemetry(kernel):
    kernel.tokens_consumed = 100
    kernel.last_transition_at = time.time() - 1.0
    kernel.temporal_jitter = 10.0
    
    state = kernel.get_current_state()
    telemetry = state["telemetry"]
    
    assert "metabolic_flux" in telemetry
    assert "temporal_stability" in telemetry
    assert telemetry["metabolic_flux"] == pytest.approx(100.0, rel=0.1)
    assert telemetry["temporal_stability"] > 0.0
