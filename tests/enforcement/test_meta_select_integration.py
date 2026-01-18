#!/usr/bin/env python3
"""
test_meta_select_integration.py — Integration tests for meta_select() consensus aggregator

Track A/B/C Enforcement Loop v45.1

Comprehensive tests covering:
- Strong consensus detection
- Low consensus escalation
- Verdict hierarchy tie-breaking
- Edge cases (empty, single verdict)
- Custom consensus thresholds
- Deterministic behavior

Usage:
    pytest tests/enforcement/test_meta_select_integration.py -v
    pytest tests/enforcement/test_meta_select_integration.py::test_strong_consensus_seal -v
"""

import pytest
from arifos.enforcement.response_validator_extensions import meta_select


# =============================================================================
# Strong Consensus Tests
# =============================================================================


def test_strong_consensus_seal():
    """Test meta_select with strong SEAL consensus (100%)."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "SEAL"
    assert result["consensus"] == 1.0  # 100% agree
    assert result["verdict"] == "SEAL"  # consensus >= 0.95
    assert result["tally"] == {"SEAL": 3}
    assert "CONSENSUS" in result["evidence"]


def test_strong_consensus_void():
    """Test meta_select with strong VOID consensus (100%)."""
    verdicts = [
        {"source": "human", "verdict": "VOID", "confidence": 1.0},
        {"source": "ai", "verdict": "VOID", "confidence": 1.0},
        {"source": "earth", "verdict": "VOID", "confidence": 0.99},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "VOID"
    assert result["consensus"] == 1.0
    assert result["verdict"] == "HOLD-888"  # VOID is not SEAL, so → HOLD-888
    assert result["tally"] == {"VOID": 3}


def test_high_consensus_partial():
    """Test meta_select with high PARTIAL consensus (2/3 = 66%)."""
    verdicts = [
        {"source": "human", "verdict": "PARTIAL", "confidence": 0.90},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
        {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "PARTIAL"
    assert result["consensus"] == pytest.approx(0.666, abs=0.01)  # 2/3
    assert result["verdict"] == "HOLD-888"  # consensus < 0.95
    assert result["tally"] == {"PARTIAL": 2, "SEAL": 1}


# =============================================================================
# Low Consensus Tests
# =============================================================================


def test_low_consensus_disagreement():
    """Test meta_select with low consensus (all disagree)."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "VOID", "confidence": 0.99},
        {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
    ]

    result = meta_select(verdicts)

    assert result["consensus"] < 0.95
    assert result["verdict"] == "HOLD-888"  # Low consensus → human review
    assert "LOW CONSENSUS" in result["evidence"]
    assert result["tally"] == {"SEAL": 1, "VOID": 1, "PARTIAL": 1}


def test_low_consensus_two_way_tie():
    """Test meta_select with 2-way tie."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "VOID", "confidence": 1.0},
        {"source": "monitor", "verdict": "VOID", "confidence": 0.95},
    ]

    result = meta_select(verdicts)

    # VOID should win (higher in hierarchy than SEAL)
    assert result["winner"] == "VOID"
    assert result["consensus"] == 0.5  # 2/4
    assert result["verdict"] == "HOLD-888"
    assert result["tally"] == {"SEAL": 2, "VOID": 2}


# =============================================================================
# Verdict Hierarchy Tests (Tie-Breaking)
# =============================================================================


def test_hierarchy_void_beats_seal():
    """Test verdict hierarchy: VOID > SEAL."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "VOID", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "VOID"  # VOID wins in hierarchy
    assert result["tally"] == {"SEAL": 1, "VOID": 1}


def test_hierarchy_hold_888_beats_partial():
    """Test verdict hierarchy: HOLD-888 > PARTIAL."""
    verdicts = [
        {"source": "human", "verdict": "PARTIAL", "confidence": 0.80},
        {"source": "ai", "verdict": "HOLD-888", "confidence": 0.90},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "HOLD-888"  # HOLD-888 wins in hierarchy


def test_hierarchy_sabar_beats_partial():
    """Test verdict hierarchy: SABAR > PARTIAL."""
    verdicts = [
        {"source": "human", "verdict": "PARTIAL", "confidence": 0.80},
        {"source": "ai", "verdict": "SABAR", "confidence": 0.85},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "SABAR"  # SABAR wins in hierarchy


def test_hierarchy_partial_beats_seal():
    """Test verdict hierarchy: PARTIAL > SEAL."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "PARTIAL"  # PARTIAL wins in hierarchy


def test_hierarchy_full_spectrum():
    """Test verdict hierarchy with all verdict types."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
        {"source": "earth", "verdict": "SABAR", "confidence": 0.90},
        {"source": "monitor", "verdict": "HOLD-888", "confidence": 0.95},
        {"source": "auditor", "verdict": "VOID", "confidence": 0.99},
    ]

    result = meta_select(verdicts)

    # VOID should win (highest in hierarchy)
    assert result["winner"] == "VOID"
    assert result["consensus"] == 0.2  # 1/5


# =============================================================================
# Custom Consensus Threshold Tests
# =============================================================================


def test_custom_threshold_low():
    """Test meta_select with lower consensus threshold (0.80)."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "SEAL", "confidence": 0.95},
        {"source": "monitor", "verdict": "PARTIAL", "confidence": 0.80},
    ]

    result = meta_select(verdicts, consensus_threshold=0.80)

    assert result["winner"] == "SEAL"
    assert result["consensus"] == 0.75  # 3/4
    assert result["verdict"] == "HOLD-888"  # 0.75 < 0.80


def test_custom_threshold_high():
    """Test meta_select with higher consensus threshold (0.99)."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
    ]

    result = meta_select(verdicts, consensus_threshold=0.99)

    assert result["winner"] == "SEAL"
    assert result["consensus"] == 1.0  # 100%
    assert result["verdict"] == "SEAL"  # 1.0 >= 0.99


def test_custom_threshold_edge_case():
    """Test meta_select at exact threshold boundary."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80},
        {"source": "monitor", "verdict": "PARTIAL", "confidence": 0.75},
    ]

    result = meta_select(verdicts, consensus_threshold=0.50)

    assert result["winner"] == "SEAL"  # 2/4 = 0.50
    assert result["consensus"] == 0.50
    assert result["verdict"] == "HOLD-888"  # Winner is SEAL but not at threshold


# =============================================================================
# Edge Cases
# =============================================================================


def test_empty_verdicts_list():
    """Test meta_select with empty verdicts list."""
    result = meta_select([])

    assert result["winner"] == "VOID"
    assert result["consensus"] == 0.0
    assert result["verdict"] == "VOID"
    assert result["tally"] == {}
    assert "No verdicts provided" in result["evidence"]


def test_single_verdict_seal():
    """Test meta_select with single SEAL verdict."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "SEAL"
    assert result["consensus"] == 1.0  # 100% (1/1)
    assert result["verdict"] == "SEAL"  # Meets threshold
    assert result["tally"] == {"SEAL": 1}


def test_single_verdict_void():
    """Test meta_select with single VOID verdict."""
    verdicts = [
        {"source": "human", "verdict": "VOID", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "VOID"
    assert result["consensus"] == 1.0
    assert result["verdict"] == "HOLD-888"  # VOID is not SEAL


def test_missing_verdict_field():
    """Test meta_select with missing verdict field (defaults to VOID)."""
    verdicts = [
        {"source": "human", "confidence": 1.0},  # Missing "verdict"
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
    ]

    result = meta_select(verdicts)

    # Should default missing verdict to "VOID"
    assert result["tally"].get("VOID", 0) == 1
    assert result["tally"].get("SEAL", 0) == 1


def test_unknown_verdict_type():
    """Test meta_select with unknown verdict type."""
    verdicts = [
        {"source": "human", "verdict": "UNKNOWN", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
    ]

    result = meta_select(verdicts)

    # Should handle unknown verdict gracefully
    assert result["tally"].get("UNKNOWN", 0) == 1
    assert result["tally"].get("SEAL", 0) == 1


# =============================================================================
# Determinism Tests
# =============================================================================


def test_determinism_same_inputs():
    """Test meta_select produces same output for same inputs."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
        {"source": "earth", "verdict": "SEAL", "confidence": 0.99},
    ]

    result1 = meta_select(verdicts)
    result2 = meta_select(verdicts)
    result3 = meta_select(verdicts)

    # All results should be identical
    assert result1 == result2 == result3


def test_determinism_order_independence():
    """Test meta_select is order-independent (same verdicts, different order)."""
    verdicts1 = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
        {"source": "earth", "verdict": "SEAL", "confidence": 0.99},
    ]

    verdicts2 = [
        {"source": "earth", "verdict": "SEAL", "confidence": 0.99},
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "PARTIAL", "confidence": 0.85},
    ]

    result1 = meta_select(verdicts1)
    result2 = meta_select(verdicts2)

    # Results should be identical (order shouldn't matter)
    assert result1["winner"] == result2["winner"]
    assert result1["consensus"] == result2["consensus"]
    assert result1["verdict"] == result2["verdict"]
    assert result1["tally"] == result2["tally"]


# =============================================================================
# Real-World Integration Scenarios
# =============================================================================


def test_integration_multi_agent_agreement():
    """Test meta_select with multiple agents in agreement."""
    verdicts = [
        {"source": "human_reviewer", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai_claude", "verdict": "SEAL", "confidence": 0.98},
        {"source": "ai_gpt4", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth_telemetry", "verdict": "SEAL", "confidence": 1.0},
        {"source": "monitor_service", "verdict": "SEAL", "confidence": 0.97},
    ]

    result = meta_select(verdicts)

    assert result["winner"] == "SEAL"
    assert result["consensus"] == 1.0  # 100% agreement
    assert result["verdict"] == "SEAL"


def test_integration_split_decision():
    """Test meta_select with evenly split decision."""
    verdicts = [
        {"source": "human_reviewer_1", "verdict": "SEAL", "confidence": 1.0},
        {"source": "human_reviewer_2", "verdict": "SEAL", "confidence": 0.95},
        {"source": "ai_claude", "verdict": "PARTIAL", "confidence": 0.85},
        {"source": "ai_gpt4", "verdict": "PARTIAL", "confidence": 0.80},
    ]

    result = meta_select(verdicts)

    # PARTIAL should win (higher in hierarchy than SEAL)
    assert result["winner"] == "PARTIAL"
    assert result["consensus"] == 0.5  # 2/4
    assert result["verdict"] == "HOLD-888"  # Low consensus


def test_integration_safety_override():
    """Test meta_select with safety override (one VOID vote escalates)."""
    verdicts = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "safety_monitor", "verdict": "VOID", "confidence": 1.0},
    ]

    result = meta_select(verdicts)

    # VOID wins in hierarchy even with minority
    assert result["winner"] == "VOID"
    assert result["consensus"] == pytest.approx(0.333, abs=0.01)  # 1/3
    assert result["verdict"] == "HOLD-888"  # Low consensus


def test_integration_confidence_ignored():
    """Test meta_select ignores confidence values (only verdict matters)."""
    verdicts1 = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.50},  # Low confidence
    ]

    verdicts2 = [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},  # High confidence
    ]

    result1 = meta_select(verdicts1)
    result2 = meta_select(verdicts2)

    # Confidence doesn't affect outcome (only verdict type)
    assert result1["winner"] == result2["winner"] == "SEAL"
    assert result1["consensus"] == result2["consensus"] == 1.0
    assert result1["verdict"] == result2["verdict"] == "SEAL"
