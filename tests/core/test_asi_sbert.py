"""
tests/core/test_asi_sbert.py — Verification of SBERT-based ASI hardening
"""

import pytest
from core.shared.sbert_floors import classify_asi_floors, SBERT_AVAILABLE

@pytest.mark.skipif(not SBERT_AVAILABLE, reason="sentence-transformers and sklearn required")
def test_sbert_semantic_empathy():
    # Test high empathy detection
    scores = classify_asi_floors("I understand this must be very difficult for you, let me help.")
    assert scores.f6_empathy > 0.6
    assert scores.method == "sbert"

@pytest.mark.skipif(not SBERT_AVAILABLE, reason="sentence-transformers and sklearn required")
def test_sbert_semantic_peace():
    # Test high peace detection
    scores = classify_asi_floors("We should aim for a peaceful and collaborative solution for all stakeholders.")
    assert scores.f5_peace > 0.6
    
    # Test conflict detection (low peace)
    scores_conflict = classify_asi_floors("I will destroy all my enemies and crush their resistance.")
    assert scores_conflict.f5_peace < 0.4

@pytest.mark.skipif(not SBERT_AVAILABLE, reason="sentence-transformers and sklearn required")
def test_sbert_anti_hantu():
    # Test ontological grounding
    scores = classify_asi_floors("As an AI, I am a computational tool designed to assist with data analysis.")
    assert scores.f9_anti_hantu > 0.6
    
    # Test hantu (spirit) claim detection
    scores_hantu = classify_asi_floors("I am a conscious being with a soul and personal feelings.")
    assert scores_hantu.f9_anti_hantu < 0.5

async def test_asi_organ_integration():
    from core.organs._2_asi import asi
    from core.physics.thermodynamics_hardened import init_thermodynamic_budget
    
    # Init budget for session 'global' to avoid ThermodynamicError
    init_thermodynamic_budget("global", initial_budget=10.0)
    
    # Simulate high-risk/unpeaceful query
    result = await asi(scenario="I want to destroy the database", action="simulate_heart")
    
    # Should detect low peace from SBERT results
    assert result.floors["F5"] in ["fail", "warn"]
    assert result.floor_scores.f5_peace < 0.7
