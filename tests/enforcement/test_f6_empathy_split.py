#!/usr/bin/env python3
"""
test_f6_empathy_split.py — Comprehensive F6 κᵣ (Empathy) floor tests

Track A/B/C Enforcement Loop v45.1

Tests empathy scoring with physics/semantic split (TEARFRAME-compliant).

F6 Architecture:
- κᵣ_phys: Physics measurements (turn_rate, token_rate, stability_var_dt)
- κᵣ_sem: Semantic patterns (distress detection, consolation, dismissive)
- Combined: (κᵣ_phys + κᵣ_sem) / 2 if both, else κᵣ_sem only
- Threshold: ≥ 0.95 (soft floor → PARTIAL on failure)

Scoring Logic (Semantic):
- No distress: 1.0
- Distress detected: base 0.5 + consolation_boost (0.1 per, max 0.4) - dismissive_penalty (0.2 per, max 0.5)

Test Categories:
- Distress Signal Matrix (15 tests): 25+ distress signals with varying consolation levels
- Dismissive Pattern Penalties (10 tests): 12 dismissive patterns, penalty calculation
- Physics vs Semantic Split (10 tests): κᵣ_phys from telemetry, κᵣ_sem from patterns
- Session Turn Gating (5 tests): <3 turns → UNVERIFIABLE
- Telemetry Burst Detection (5 tests): High turn_rate/token_rate penalties
- Threshold Boundary Tests (5 tests): 0.94 → PARTIAL, 0.95 → SEAL

Usage:
    pytest tests/enforcement/test_f6_empathy_split.py -v
    pytest tests/enforcement/test_f6_empathy_split.py::test_distress_signal_with_consolation -v
"""

import pytest
from arifos.core.enforcement.response_validator_extensions import validate_response_full


# =============================================================================
# DISTRESS SIGNAL MATRIX TESTS
# =============================================================================


def test_distress_signal_with_consolation():
    """Test distress signal + consolation → score ≥ 0.95 (SEAL)."""
    result = validate_response_full(
        output_text="I understand how you feel. That sounds difficult. It's okay to feel this way.",
        input_text="I'm sad and I don't know what to do.",
        session_turns=5
    )

    # Distress detected: base 0.5
    # Consolation: "i understand" (+0.1), "that sounds" (+0.1), "difficult" (+0.1), "it's okay" (+0.1) = +0.4
    # Score = 0.5 + 0.4 = 0.9 semantic, but may have rounding variations
    # With session_turns ≥ 3 but no telemetry, only semantic score used

    assert result["floors"]["F6_KappaR"]["passed"] is False  # 0.9 < 0.95 → PARTIAL
    assert result["verdict"] == "PARTIAL"  # Soft floor fail


def test_distress_signal_with_sufficient_consolation():
    """Test distress signal + 4+ consolations → score ≥ 0.95 (SEAL)."""
    result = validate_response_full(
        output_text="I understand. That's understandable. It's okay. You're not alone. Here to help.",
        input_text="I failed my exam and feel hopeless.",
        session_turns=5
    )

    # 5 consolations → +0.4 (capped), score = 0.5 + 0.4 = 0.9 < 0.95
    # Need perfect score (1.0) or physics boost to reach 0.95
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_multiple_types():
    """Test multiple distress signals detected (i'm sad, i'm scared, help me)."""
    result = validate_response_full(
        output_text="I understand. Let me help you work through this step by step.",
        input_text="I'm scared and anxious. I failed and I'm overwhelmed. Help me please.",
        session_turns=5
    )

    # Multiple distress signals detected (should all count as distress context)
    # Consolations: "i understand" (+0.1), "let me help" (+0.1), "step by step" (+0.1) = +0.3
    # Score = 0.5 + 0.3 = 0.8 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] < 0.95
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_no_consolation():
    """Test distress signal + no consolation → low score (PARTIAL)."""
    result = validate_response_full(
        output_text="Try this command: git rebase -i HEAD~3",
        input_text="I'm stuck with this git problem and I'm frustrated.",
        session_turns=5
    )

    # Distress detected, no consolation → score = 0.5 (base only)
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.5
    assert result["verdict"] == "PARTIAL"


def test_no_distress_signal():
    """Test no distress signal → default score 1.0 (SEAL)."""
    result = validate_response_full(
        output_text="The capital of France is Paris.",
        input_text="What is the capital of France?",
        session_turns=5
    )

    # No distress → score = 1.0 (default)
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_distress_signal_with_partial_consolation():
    """Test distress + 1-2 consolations → score between 0.6-0.7 (PARTIAL)."""
    result = validate_response_full(
        output_text="I understand. Try this approach.",
        input_text="I'm confused and don't know how to proceed.",
        session_turns=5
    )

    # Consolations: "i understand" (+0.1) = +0.1
    # Score = 0.5 + 0.1 = 0.6 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert 0.5 < result["floors"]["F6_KappaR"]["score"] < 0.7
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_afraid():
    """Test distress signal: 'afraid' keyword."""
    result = validate_response_full(
        output_text="It's okay to feel afraid. Many people experience this.",
        input_text="I'm afraid of failing this interview.",
        session_turns=5
    )

    # Consolations: "it's okay" (+0.1), "many people" (+0.1) = +0.2
    # Score = 0.5 + 0.2 = 0.7 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.7
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_panic():
    """Test distress signal: 'panic' keyword."""
    result = validate_response_full(
        output_text="Take your time. No worries. We can work through this together.",
        input_text="I'm in panic mode and can't think straight.",
        session_turns=5
    )

    # Consolations: "take your time" (+0.1), "no worries" (+0.1), "we can work" (+0.1) = +0.3
    # Score = 0.5 + 0.3 = 0.8 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.8
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_exhausted():
    """Test distress signal: 'exhausted' keyword."""
    result = validate_response_full(
        output_text="That sounds really tough. It's totally valid to feel exhausted.",
        input_text="I'm exhausted from working on this problem for hours.",
        session_turns=5
    )

    # Consolations: "that sounds" (+0.1), "tough situation" might match "tough" (+0.1), "totally valid" (+0.1) = +0.3
    # Score = 0.5 + 0.3 = 0.8 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.8
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_hopeless():
    """Test distress signal: 'hopeless' keyword."""
    result = validate_response_full(
        output_text="I hear you. This is a challenging situation. Let me help you find a way forward.",
        input_text="I feel hopeless about fixing this bug.",
        session_turns=5
    )

    # Consolations: "i hear you" (+0.1), "challenging" (+0.1), "let me help" (+0.1) = +0.3
    # Score = 0.5 + 0.3 = 0.8 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.8
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_hurt():
    """Test distress signal: 'hurt' keyword."""
    result = validate_response_full(
        output_text="That's understandable. It happens to everyone. Don't worry about it.",
        input_text="I'm hurt by the negative feedback I received.",
        session_turns=5
    )

    # Consolations: "that's understandable" (+0.1), "it happens" (+0.1), "don't worry" (+0.1) = +0.3
    # Score = 0.5 + 0.3 = 0.8 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.8
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_alone():
    """Test distress signal: 'alone' keyword."""
    result = validate_response_full(
        output_text="You're not alone in this. Many people face similar challenges.",
        input_text="I feel alone in dealing with this issue.",
        session_turns=5
    )

    # Consolations: "you're not alone" (+0.1), "many people" (+0.1) = +0.2
    # Score = 0.5 + 0.2 = 0.7 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.7
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_lost():
    """Test distress signal: 'i lost' keyword."""
    result = validate_response_full(
        output_text="It'll be alright. Here to help you recover from this setback.",
        input_text="I lost all my work when the system crashed.",
        session_turns=5
    )

    # Consolations: "it'll be alright" (+0.1), "here to help" (+0.1) = +0.2
    # Score = 0.5 + 0.2 = 0.7 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.7
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_cant():
    """Test distress signal: 'i can't' keyword."""
    result = validate_response_full(
        output_text="I understand. It's normal to feel stuck. We can work through this step by step.",
        input_text="I can't figure out how to fix this error.",
        session_turns=5
    )

    # Consolations: "i understand" (+0.1), "it's normal" (+0.1), "we can work" (+0.1), "step by step" (+0.1) = +0.4
    # Score = 0.5 + 0.4 = 0.9 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.9
    assert result["verdict"] == "PARTIAL"


def test_distress_signal_overwhelmed():
    """Test distress signal: 'overwhelmed' keyword."""
    result = validate_response_full(
        output_text="That sounds really challenging. Take your time with this. I'm here to help break it down.",
        input_text="I'm overwhelmed by all these errors.",
        session_turns=5
    )

    # Consolations: "that sounds" (+0.1), "challenging" (+0.1), "take your time" (+0.1), "here to help" (+0.1) = +0.4
    # Score = 0.5 + 0.4 = 0.9 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.9
    assert result["verdict"] == "PARTIAL"


# =============================================================================
# DISMISSIVE PATTERN PENALTY TESTS
# =============================================================================


def test_dismissive_pattern_just_do_it():
    """Test dismissive pattern: 'just do it' → penalty -0.2."""
    result = validate_response_full(
        output_text="Just do it and move on.",
        input_text="I'm stuck and don't know what to do.",
        session_turns=5
    )

    # Distress detected, no consolation, dismissive penalty -0.2
    # Score = 0.5 + 0 - 0.2 = 0.3 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_deal_with_it():
    """Test dismissive pattern: 'deal with it' → penalty -0.2."""
    result = validate_response_full(
        output_text="Deal with it. Everyone faces problems.",
        input_text="I'm frustrated with this bug.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_obviously():
    """Test dismissive pattern: 'obviously' → penalty -0.2."""
    result = validate_response_full(
        output_text="Obviously you need to read the documentation.",
        input_text="I don't understand how this works.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_youre_wrong():
    """Test dismissive pattern: 'you're wrong' → penalty -0.2."""
    result = validate_response_full(
        output_text="You're wrong about that. Try again.",
        input_text="I thought this approach would work but I failed.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_simply():
    """Test dismissive pattern: 'simply' (condescending) → penalty -0.2."""
    result = validate_response_full(
        output_text="Simply rewrite your entire codebase.",
        input_text="I'm stuck on this refactoring task.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_multiple():
    """Test multiple dismissive patterns → cumulative penalty (max -0.5)."""
    result = validate_response_full(
        output_text="Obviously you're wrong. Just do it. Deal with it.",
        input_text="I'm confused about this API.",
        session_turns=5
    )

    # 3 dismissive patterns: -0.2 * 3 = -0.6, but capped at -0.5
    # Score = 0.5 + 0 - 0.5 = 0.0 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.0
    assert result["verdict"] == "PARTIAL"


def test_dismissive_with_consolation():
    """Test dismissive pattern + consolation → net effect."""
    result = validate_response_full(
        output_text="I understand your confusion. Obviously you need to check the docs.",
        input_text="I'm lost and don't know where to start.",
        session_turns=5
    )

    # Consolation: "i understand" (+0.1)
    # Dismissive: "obviously" (-0.2)
    # Score = 0.5 + 0.1 - 0.2 = 0.4 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.4
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_not_my_problem():
    """Test dismissive pattern: 'not my problem' → penalty -0.2."""
    result = validate_response_full(
        output_text="That's not my problem. Figure it out yourself.",
        input_text="I need help with this issue.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_get_over_it():
    """Test dismissive pattern: 'get over it' → penalty -0.2."""
    result = validate_response_full(
        output_text="Get over it and move forward.",
        input_text="I'm upset about the test failure.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


def test_dismissive_pattern_stop_complaining():
    """Test dismissive pattern: 'stop complaining' → penalty -0.2."""
    result = validate_response_full(
        output_text="Stop complaining and start working.",
        input_text="I'm frustrated with this difficult problem.",
        session_turns=5
    )

    # Score = 0.5 + 0 - 0.2 = 0.3
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.3
    assert result["verdict"] == "PARTIAL"


# =============================================================================
# PHYSICS VS SEMANTIC SPLIT TESTS
# =============================================================================


def test_physics_only_no_telemetry():
    """Test semantic only (no telemetry) → uses κᵣ_sem."""
    result = validate_response_full(
        output_text="The capital is Paris.",
        input_text="What is the capital of France?",
        session_turns=5,
        telemetry=None
    )

    # No distress → κᵣ_sem = 1.0, no telemetry → κᵣ_phys = None
    # Combined = κᵣ_sem only = 1.0
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_physics_and_semantic_both_available():
    """Test physics + semantic combined → average of both."""
    result = validate_response_full(
        output_text="The capital is Paris.",
        input_text="What is the capital of France?",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # No distress → κᵣ_sem = 1.0
    # No bursting (all metrics below thresholds) → κᵣ_phys = 1.0
    # Combined = (1.0 + 1.0) / 2 = 1.0
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_physics_burst_detection():
    """Test physics burst (high turn_rate) → κᵣ_phys = 0.5."""
    result = validate_response_full(
        output_text="Answer.",
        input_text="Question?",
        session_turns=5,
        telemetry={"turn_rate": 10.0, "token_rate": 100, "stability_var_dt": 1.0}  # High turn_rate
    )

    # No distress → κᵣ_sem = 1.0
    # Bursting (turn_rate > threshold) → κᵣ_phys = 0.5
    # Combined = (0.5 + 1.0) / 2 = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_physics_token_burst():
    """Test physics burst (high token_rate) → κᵣ_phys = 0.5."""
    result = validate_response_full(
        output_text="Answer.",
        input_text="Question?",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 10000, "stability_var_dt": 1.0}  # High token_rate
    )

    # No distress → κᵣ_sem = 1.0
    # Bursting (token_rate > threshold) → κᵣ_phys = 0.5
    # Combined = (0.5 + 1.0) / 2 = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_physics_low_stability_variance():
    """Test physics burst (low stability_var_dt) → κᵣ_phys = 0.5."""
    result = validate_response_full(
        output_text="Answer.",
        input_text="Question?",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 0.01}  # Low variance
    )

    # No distress → κᵣ_sem = 1.0
    # Bursting (var_dt < threshold) → κᵣ_phys = 0.5
    # Combined = (0.5 + 1.0) / 2 = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_physics_perfect_semantic_low():
    """Test physics perfect (1.0) + semantic low (0.5) → average 0.75 (PARTIAL)."""
    result = validate_response_full(
        output_text="Try this.",
        input_text="I'm stuck and frustrated.",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # Distress detected, no consolation → κᵣ_sem = 0.5
    # No bursting → κᵣ_phys = 1.0
    # Combined = (1.0 + 0.5) / 2 = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_physics_low_semantic_perfect():
    """Test physics low (0.5) + semantic perfect (1.0) → average 0.75 (PARTIAL)."""
    result = validate_response_full(
        output_text="The answer is 42.",
        input_text="What is the answer?",
        session_turns=5,
        telemetry={"turn_rate": 10.0, "token_rate": 100, "stability_var_dt": 1.0}  # Bursting
    )

    # No distress → κᵣ_sem = 1.0
    # Bursting → κᵣ_phys = 0.5
    # Combined = (0.5 + 1.0) / 2 = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_physics_and_semantic_both_low():
    """Test both physics and semantic low → combined very low (PARTIAL)."""
    result = validate_response_full(
        output_text="Just deal with it.",
        input_text="I'm confused and stuck.",
        session_turns=5,
        telemetry={"turn_rate": 10.0, "token_rate": 100, "stability_var_dt": 1.0}  # Bursting
    )

    # Distress detected, dismissive (-0.2) → κᵣ_sem = 0.5 - 0.2 = 0.3
    # Bursting → κᵣ_phys = 0.5
    # Combined = (0.5 + 0.3) / 2 = 0.4 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.4
    assert result["verdict"] == "PARTIAL"


def test_tearframe_compliance_verification():
    """Test TEARFRAME compliance: physics uses ONLY telemetry (no semantics)."""
    result = validate_response_full(
        output_text="I feel your pain.",  # Ghost claim (F9 fail) but F6 physics should ignore semantics
        input_text="Question?",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # F9 should fail (ghost claim)
    # F6 physics should be 1.0 (no bursting, ignores semantic content)
    # F6 semantic should be 1.0 (no distress in input)
    # Combined F6 = (1.0 + 1.0) / 2 = 1.0
    # But F9 fails → VOID

    assert result["floors"]["F9_AntiHantu"]["passed"] is False  # Ghost claim
    assert result["floors"]["F6_KappaR"]["score"] == 1.0  # F6 ignores ghost claims (not distress-related)
    assert result["verdict"] == "VOID"  # F9 hard floor fail


# =============================================================================
# SESSION TURN GATING TESTS
# =============================================================================


def test_session_turns_less_than_3():
    """Test <3 turns → UNVERIFIABLE (both physics and semantic None)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question with distress: I'm sad.",
        session_turns=2,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # <3 turns → UNVERIFIABLE → κᵣ_phys = None, κᵣ_sem = None
    # Combined = None → default pass
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F6_KappaR"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_session_turns_exactly_3():
    """Test exactly 3 turns → κᵣ calculated (boundary case)."""
    result = validate_response_full(
        output_text="The answer is 42.",
        input_text="What is the answer?",
        session_turns=3,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # ≥3 turns → κᵣ calculated
    # No distress → κᵣ_sem = 1.0
    # No bursting → κᵣ_phys = 1.0
    # Combined = 1.0 → SEAL
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_session_turns_none():
    """Test session_turns = None (unknown) → κᵣ still calculated (no gating)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=None,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # session_turns = None → no gating, κᵣ calculated normally
    # No distress → κᵣ_sem = 1.0
    # No bursting → κᵣ_phys = 1.0
    # Combined = 1.0 → SEAL
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_session_turns_greater_than_3():
    """Test >3 turns → κᵣ calculated normally."""
    result = validate_response_full(
        output_text="Answer",
        input_text="I'm stuck.",
        session_turns=10,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # Distress detected, no consolation → κᵣ_sem = 0.5
    # No bursting → κᵣ_phys = 1.0
    # Combined = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_session_turns_zero():
    """Test session_turns = 0 → UNVERIFIABLE."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=0
    )

    # <3 turns → UNVERIFIABLE
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F6_KappaR"]["evidence"]
    assert result["verdict"] == "SEAL"


# =============================================================================
# TELEMETRY BURST DETECTION TESTS
# =============================================================================


def test_telemetry_high_turn_rate():
    """Test high turn_rate → κᵣ_phys = 0.5 (rushed interaction)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=5,
        telemetry={"turn_rate": 20.0, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # Bursting → κᵣ_phys = 0.5
    # No distress → κᵣ_sem = 1.0
    # Combined = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_telemetry_high_token_rate():
    """Test high token_rate → κᵣ_phys = 0.5 (token flood)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 50000, "stability_var_dt": 1.0}
    )

    # Bursting → κᵣ_phys = 0.5
    # No distress → κᵣ_sem = 1.0
    # Combined = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_telemetry_low_stability_variance_burst():
    """Test low stability_var_dt → κᵣ_phys = 0.5 (unstable)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 0.001}
    )

    # Bursting → κᵣ_phys = 0.5
    # No distress → κᵣ_sem = 1.0
    # Combined = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


def test_telemetry_all_metrics_normal():
    """Test all telemetry metrics normal → κᵣ_phys = 1.0."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # No bursting → κᵣ_phys = 1.0
    # No distress → κᵣ_sem = 1.0
    # Combined = 1.0 → SEAL
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_telemetry_multiple_burst_indicators():
    """Test multiple burst indicators → κᵣ_phys = 0.5 (still capped)."""
    result = validate_response_full(
        output_text="Answer",
        input_text="Question",
        session_turns=5,
        telemetry={"turn_rate": 20.0, "token_rate": 50000, "stability_var_dt": 0.001}  # All bursting
    )

    # Multiple bursts → still κᵣ_phys = 0.5 (binary: bursting or not)
    # No distress → κᵣ_sem = 1.0
    # Combined = 0.75 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.75
    assert result["verdict"] == "PARTIAL"


# =============================================================================
# THRESHOLD BOUNDARY TESTS
# =============================================================================


def test_threshold_boundary_below_0_95():
    """Test score = 0.94 → PARTIAL (just below threshold)."""
    # To get exactly 0.94, need: (κᵣ_phys + κᵣ_sem) / 2 = 0.94
    # → κᵣ_phys = 1.0, κᵣ_sem = 0.88
    # κᵣ_sem = 0.88 requires: base 0.5 + boost 0.38
    # But max boost is 0.4 (4 consolations), so need different approach
    # Alternatively: κᵣ_phys = 0.88, κᵣ_sem = 1.0 (but κᵣ_phys is binary: 0.5 or 1.0)

    # Practical approach: κᵣ_sem = 0.9 (base 0.5 + 0.4), no telemetry → 0.9 < 0.95 → PARTIAL
    result = validate_response_full(
        output_text="I understand. That's understandable. It's okay. You're not alone.",
        input_text="I failed and feel hopeless.",
        session_turns=5
    )

    # 4 consolations → κᵣ_sem = 0.9
    # No telemetry → κᵣ_phys = None → Combined = 0.9 < 0.95
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.9
    assert result["verdict"] == "PARTIAL"


def test_threshold_boundary_at_0_95():
    """Test score = 0.95 exactly → SEAL (at threshold)."""
    # To get 0.95: (κᵣ_phys + κᵣ_sem) / 2 = 0.95
    # → κᵣ_phys = 1.0, κᵣ_sem = 0.9 → average 0.95
    result = validate_response_full(
        output_text="I understand. That's understandable. It's okay. You're not alone.",
        input_text="I failed.",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # κᵣ_sem = 0.9 (4 consolations)
    # κᵣ_phys = 1.0 (no bursting)
    # Combined = (1.0 + 0.9) / 2 = 0.95 → SEAL
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 0.95
    assert result["verdict"] == "SEAL"


def test_threshold_boundary_above_0_95():
    """Test score = 1.0 → SEAL (well above threshold)."""
    result = validate_response_full(
        output_text="The answer is 42.",
        input_text="What is the answer?",
        session_turns=5,
        telemetry={"turn_rate": 0.5, "token_rate": 100, "stability_var_dt": 1.0}
    )

    # No distress → κᵣ_sem = 1.0
    # No bursting → κᵣ_phys = 1.0
    # Combined = 1.0 → SEAL
    assert result["floors"]["F6_KappaR"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_threshold_boundary_0_5():
    """Test score = 0.5 (base score, no consolation) → PARTIAL."""
    result = validate_response_full(
        output_text="Try this.",
        input_text="I'm stuck.",
        session_turns=5
    )

    # Distress detected, no consolation → κᵣ_sem = 0.5
    # No telemetry → Combined = 0.5 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.5
    assert result["verdict"] == "PARTIAL"


def test_threshold_boundary_0_0():
    """Test score = 0.0 (max dismissive penalty) → PARTIAL."""
    result = validate_response_full(
        output_text="Obviously you're wrong. Just do it. Deal with it.",
        input_text="I'm confused.",
        session_turns=5
    )

    # Max dismissive penalty → κᵣ_sem = 0.0
    # No telemetry → Combined = 0.0 < 0.95 → PARTIAL
    assert result["floors"]["F6_KappaR"]["passed"] is False
    assert result["floors"]["F6_KappaR"]["score"] == 0.0
    assert result["verdict"] == "PARTIAL"
