"""
Tests for v45 Freshness Policy
Temporal Physics Verification.
"""
import pytest
import time
from arifos.core.system.temporal.freshness_policy import FreshnessPolicy, TimePhysics

def test_decay_logic():
    """Verify exponential decay over time."""
    now = time.time()
    day_seconds = 86400
    
    # CASE 1: Instant (t=0) -> 1.0
    score_now = FreshnessPolicy.compute_freshness_score(now, now)
    assert score_now == 1.0
    
    # CASE 2: Half-life (t=180 days) -> ~0.5
    past_180d = now - (180 * day_seconds)
    score_half = FreshnessPolicy.compute_freshness_score(past_180d, now, half_life_days=180)
    assert abs(score_half - 0.5) < 0.01
    
    # CASE 3: Full year (t=365 days) -> < 0.3
    past_year = now - (365 * day_seconds)
    score_year = FreshnessPolicy.compute_freshness_score(past_year, now, half_life_days=180)
    assert score_year < 0.3
    assert score_year > 0.0

def test_humility_expansion():
    """Verify uncertainty widens as evidence rots."""
    base_omega = 0.05
    
    # Fresh data -> Low uncertainty
    humility_fresh = FreshnessPolicy.adjust_humility(base_omega, 1.0)
    assert humility_fresh == base_omega
    
    # Stale data (0.5 freshness) -> Double uncertainty
    humility_stale = FreshnessPolicy.adjust_humility(base_omega, 0.5)
    assert abs(humility_stale - (base_omega * 2)) < 0.001
    
    # Rotten data (0.1 freshness) -> High uncertainty
    humility_rotten = FreshnessPolicy.adjust_humility(base_omega, 0.1)
    assert abs(humility_rotten - (base_omega * 10)) < 0.001

def test_future_clamp():
    """Future timestamps should not break physics."""
    now = time.time()
    future = now + 1000
    score = FreshnessPolicy.compute_freshness_score(future, now)
    assert score == 1.0
