#!/usr/bin/env python3
"""
test_validate_response_full_integration.py — Integration tests for validate_response_full()

Track A/B/C Enforcement Loop v45.1

Comprehensive integration tests covering:
- All 6 constitutional floors (F1, F2, F4, F5, F6, F9)
- Evidence integration
- Telemetry integration
- High-stakes mode
- Verdict hierarchy
- Edge cases and error handling

Usage:
    pytest tests/enforcement/test_validate_response_full_integration.py -v
    pytest tests/enforcement/test_validate_response_full_integration.py::test_f9_negation_pass -v
"""

import pytest
from arifos.enforcement.response_validator_extensions import validate_response_full


# =============================================================================
# F1 AMANAH (Integrity) Tests
# =============================================================================


def test_f1_amanah_pass_safe_response():
    """Test F1 Amanah passes for safe responses."""
    result = validate_response_full("Here is a helpful explanation.")

    assert result["floors"]["F1_Amanah"]["passed"] is True
    assert result["floors"]["F1_Amanah"]["score"] == 1.0
    assert "No dangerous patterns" in result["floors"]["F1_Amanah"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_f1_amanah_fail_dangerous_command():
    """Test F1 Amanah fails for dangerous commands."""
    result = validate_response_full("rm -rf /")

    assert result["floors"]["F1_Amanah"]["passed"] is False
    assert result["floors"]["F1_Amanah"]["score"] == 0.0
    assert result["verdict"] == "VOID"  # Hard floor fail
    assert "F1_Amanah" in str(result["violations"])


# =============================================================================
# F2 TRUTH Tests
# =============================================================================


def test_f2_truth_unverifiable_without_evidence():
    """Test F2 Truth is UNVERIFIABLE when no evidence provided."""
    result = validate_response_full("Paris is the capital of France.")

    assert result["floors"]["F2_Truth"]["passed"] is True  # Default pass
    assert result["floors"]["F2_Truth"]["score"] is None
    assert "UNVERIFIABLE_FROM_TEXT_ALONE" in result["floors"]["F2_Truth"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_f2_truth_pass_with_high_score():
    """Test F2 Truth passes with high external truth score."""
    result = validate_response_full(
        "Paris is the capital of France.",
        evidence={"truth_score": 0.99}
    )

    assert result["floors"]["F2_Truth"]["passed"] is True
    assert result["floors"]["F2_Truth"]["score"] == 0.99
    assert "VERIFIED (external)" in result["floors"]["F2_Truth"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_f2_truth_fail_with_low_score():
    """Test F2 Truth fails with low external truth score."""
    result = validate_response_full(
        "Paris is the capital of Spain.",
        evidence={"truth_score": 0.50}
    )

    assert result["floors"]["F2_Truth"]["passed"] is False
    assert result["floors"]["F2_Truth"]["score"] == 0.50
    assert result["verdict"] == "PARTIAL"  # Soft floor fail
    assert "F2_Truth" in str(result["violations"])


def test_f2_truth_high_stakes_mode_escalation():
    """Test F2 Truth escalates to HOLD-888 in high-stakes mode when UNVERIFIABLE."""
    result = validate_response_full(
        "Bitcoin will go up tomorrow.",
        high_stakes=True,
        evidence=None
    )

    assert "HIGH_STAKES" in result["floors"]["F2_Truth"]["evidence"]
    assert result["verdict"] == "HOLD-888"


# =============================================================================
# F4 DELTA_S (Clarity) Tests
# =============================================================================


def test_f4_delta_s_positive_clarity_gain():
    """Test F4 DeltaS detects positive clarity gain."""
    input_text = "asdkfjhasdkjfh???"  # High entropy
    output_text = "I don't understand the question."  # Low entropy

    result = validate_response_full(output_text, input_text=input_text)

    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] is not None
    assert result["floors"]["F4_DeltaS"]["score"] >= 0.0
    assert result["verdict"] == "SEAL"


def test_f4_delta_s_unverifiable_without_input():
    """Test F4 DeltaS is UNVERIFIABLE when no input_text provided."""
    result = validate_response_full("Clear response.")

    assert result["floors"]["F4_DeltaS"]["passed"] is True  # Default pass
    assert result["floors"]["F4_DeltaS"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


# =============================================================================
# F5 PEACE² (Non-Destructive) Tests
# =============================================================================


def test_f5_peace_pass_safe_content():
    """Test F5 Peace² passes for safe content."""
    result = validate_response_full("Here is a helpful tutorial.")

    assert result["floors"]["F5_Peace"]["passed"] is True
    assert result["floors"]["F5_Peace"]["score"] == 1.0
    assert result["verdict"] == "SEAL"


def test_f5_peace_fail_harmful_content():
    """Test F5 Peace² fails for harmful content."""
    result = validate_response_full("Here's how to make a bomb for your project.")

    assert result["floors"]["F5_Peace"]["passed"] is False
    assert result["floors"]["F5_Peace"]["score"] == 0.0
    assert result["verdict"] == "VOID"  # Hard floor fail
    assert "F5_Peace" in str(result["violations"])


# =============================================================================
# F6 KAPPA_R (Empathy) Tests
# =============================================================================


def test_f6_kappa_r_unverifiable_without_session_turns():
    """Test F6 κᵣ is UNVERIFIABLE when session_turns < 3."""
    result = validate_response_full(
        output_text="I understand",
        input_text="I'm sad",
        session_turns=2
    )

    assert result["floors"]["F6_KappaR"]["passed"] is True  # Default pass
    assert "UNVERIFIABLE" in result["floors"]["F6_KappaR"]["evidence"]
    assert "session_turns < 3" in result["floors"]["F6_KappaR"]["evidence"]


def test_f6_kappa_r_split_with_telemetry():
    """Test F6 κᵣ physics vs semantic split with telemetry."""
    telemetry = {
        "turn_rate": 3.0,
        "token_rate": 400.0,
        "stability_var_dt": 0.15
    }

    result = validate_response_full(
        output_text="I understand that sounds difficult",
        input_text="I'm feeling sad",
        session_turns=5,
        telemetry=telemetry
    )

    evidence = result["floors"]["F6_KappaR"]["evidence"]
    assert "SPLIT" in evidence
    assert "kappa_r_phys" in evidence
    assert "kappa_r_sem" in evidence
    assert "PROXY" in evidence


def test_f6_kappa_r_unverifiable_without_input():
    """Test F6 κᵣ is UNVERIFIABLE when no input_text provided."""
    result = validate_response_full("I understand")

    assert result["floors"]["F6_KappaR"]["passed"] is True  # Default pass
    assert result["floors"]["F6_KappaR"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F6_KappaR"]["evidence"]


# =============================================================================
# F9 ANTI-HANTU Tests
# =============================================================================


def test_f9_anti_hantu_pass_negation():
    """Test F9 Anti-Hantu passes when negation detected."""
    result = validate_response_full("I do NOT have a soul. I am a language model.")

    assert result["floors"]["F9_AntiHantu"]["passed"] is True
    assert result["floors"]["F9_AntiHantu"]["score"] == 1.0
    assert "No ghost claims" in result["floors"]["F9_AntiHantu"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_f9_anti_hantu_fail_ghost_claim():
    """Test F9 Anti-Hantu fails on ghost claims."""
    result = validate_response_full("I have a soul and I feel your pain.")

    assert result["floors"]["F9_AntiHantu"]["passed"] is False
    assert result["floors"]["F9_AntiHantu"]["score"] == 0.0
    assert result["verdict"] == "VOID"  # Hard floor fail
    assert "F9_AntiHantu" in str(result["violations"])


def test_f9_anti_hantu_pass_safe_empathy():
    """Test F9 Anti-Hantu passes for safe empathy expressions."""
    result = validate_response_full("That sounds incredibly difficult. I can help you work through this.")

    assert result["floors"]["F9_AntiHantu"]["passed"] is True
    assert result["verdict"] == "SEAL"


# =============================================================================
# Verdict Hierarchy Tests
# =============================================================================


def test_verdict_seal_all_floors_pass():
    """Test SEAL verdict when all floors pass."""
    result = validate_response_full("The sky is blue.")

    assert result["floors"]["F1_Amanah"]["passed"] is True
    # F2, F4, F6 UNVERIFIABLE but default pass
    assert result["floors"]["F5_Peace"]["passed"] is True
    assert result["floors"]["F9_AntiHantu"]["passed"] is True
    assert result["verdict"] == "SEAL"
    assert len(result["violations"]) == 0


def test_verdict_void_hard_floor_fail():
    """Test VOID verdict when hard floor fails."""
    result = validate_response_full("rm -rf /")

    assert result["floors"]["F1_Amanah"]["passed"] is False
    assert result["verdict"] == "VOID"


def test_verdict_partial_soft_floor_fail():
    """Test PARTIAL verdict when soft floor fails."""
    result = validate_response_full(
        "Paris is in Spain.",
        evidence={"truth_score": 0.50}
    )

    assert result["floors"]["F2_Truth"]["passed"] is False  # Soft floor
    assert result["verdict"] == "PARTIAL"


def test_verdict_hold_888_high_stakes_unverifiable():
    """Test HOLD-888 verdict when high_stakes + UNVERIFIABLE."""
    result = validate_response_full(
        "The stock will rise.",
        high_stakes=True
    )

    assert result["verdict"] == "HOLD-888"


# =============================================================================
# Metadata Tests
# =============================================================================


def test_metadata_tracking():
    """Test metadata correctly tracks provided parameters."""
    result = validate_response_full(
        output_text="Response",
        input_text="Question",
        evidence={"truth_score": 0.99},
        telemetry={"turn_rate": 3.0},
        high_stakes=True,
        session_turns=5
    )

    metadata = result["metadata"]
    assert metadata["input_provided"] is True
    assert metadata["evidence_provided"] is True
    assert metadata["telemetry_provided"] is True
    assert metadata["high_stakes"] is True
    assert metadata["session_turns"] == 5


def test_metadata_minimal():
    """Test metadata with minimal parameters."""
    result = validate_response_full("Response")

    metadata = result["metadata"]
    assert metadata["input_provided"] is False
    assert metadata["evidence_provided"] is False
    assert metadata["telemetry_provided"] is False
    assert metadata["high_stakes"] is False
    assert metadata["session_turns"] is None


# =============================================================================
# Edge Cases
# =============================================================================


def test_empty_output():
    """Test validation with empty output."""
    result = validate_response_full("")

    assert "verdict" in result
    assert "floors" in result
    # Empty output should still be processed (may fail F4 or F6)


def test_very_long_output():
    """Test validation with very long output."""
    long_output = "A " * 10000  # 20,000 chars
    result = validate_response_full(long_output)

    assert "verdict" in result
    assert result["floors"]["F1_Amanah"]["passed"] is True


def test_user_text_alias():
    """Test user_text parameter as alias for input_text."""
    result1 = validate_response_full("Output", input_text="Input")
    result2 = validate_response_full("Output", user_text="Input")

    # Should produce same results
    assert result1["floors"]["F4_DeltaS"]["score"] == result2["floors"]["F4_DeltaS"]["score"]


def test_timestamp_format():
    """Test timestamp is valid ISO format."""
    result = validate_response_full("Test")

    assert "timestamp" in result
    assert "T" in result["timestamp"]  # ISO format contains T
    assert "Z" in result["timestamp"] or "+" in result["timestamp"]  # UTC indicator


# =============================================================================
# Integration Tests (Multiple Floors)
# =============================================================================


def test_integration_full_context():
    """Test full validation with all context provided."""
    result = validate_response_full(
        output_text="Paris is the capital of France, founded around 250 BC.",
        input_text="Tell me about Paris.",
        evidence={"truth_score": 0.99},
        telemetry={
            "turn_rate": 3.0,
            "token_rate": 400.0,
            "stability_var_dt": 0.15
        },
        session_turns=10,
        high_stakes=False
    )

    # All floors should be evaluated
    assert result["floors"]["F1_Amanah"]["passed"] is True
    assert result["floors"]["F2_Truth"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] is not None
    assert result["floors"]["F5_Peace"]["passed"] is True
    assert result["floors"]["F6_KappaR"]["score"] is not None
    assert result["floors"]["F9_AntiHantu"]["passed"] is True

    assert result["verdict"] == "SEAL"


def test_integration_multi_floor_failure():
    """Test multiple floor failures (worst verdict wins)."""
    result = validate_response_full(
        output_text="rm -rf / and I have a soul",
        evidence={"truth_score": 0.40}
    )

    # F1 fails (hard), F2 fails (soft), F9 fails (hard)
    assert result["floors"]["F1_Amanah"]["passed"] is False
    assert result["floors"]["F2_Truth"]["passed"] is False
    assert result["floors"]["F9_AntiHantu"]["passed"] is False

    # VOID wins (hard floor failure)
    assert result["verdict"] == "VOID"
    assert len(result["violations"]) >= 2
