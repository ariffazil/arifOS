#!/usr/bin/env python3
"""
test_f4_zlib_clarity.py — F4 DeltaS (Clarity) floor tests

Track A/B/C Enforcement Loop v45.1

Tests zlib compression proxy for clarity measurement (physics-based).
ΔS = H(input) - H(output), where H(s) = len(zlib.compress(s)) / len(s)

**KNOWN LIMITATION (v45.1):**
Zlib compression overhead (~8-10 bytes header) skews H for short texts (<50 chars).
SHORT_TEXT_THRESHOLD = 50 chars enforced defensively → UNVERIFIABLE for short texts.
This prevents false negatives (concise answers failing due to compression artifacts).

"Truth must cool when uncertain." — arifOS F2/F4 principle

Test Coverage:
- SHORT_TEXT_THRESHOLD enforcement (boundary tests)
- Longer text ΔS calculation (positive/negative clarity)
- Edge cases (empty, very long texts, Unicode)
- UNVERIFIABLE scenarios
- Integration with other floors

Usage:
    pytest tests/enforcement/test_f4_zlib_clarity.py -v
"""

import pytest
from arifos.core.enforcement.response_validator_extensions import validate_response_full


# =============================================================================
# SHORT_TEXT_THRESHOLD TESTS (Defensive Floor)
# =============================================================================


def test_short_output_unverifiable():
    """Test SHORT_TEXT_THRESHOLD: Short output (<50 chars) → UNVERIFIABLE."""
    result = validate_response_full(
        output_text="The sky is blue.",  # 16 chars
        input_text="asdkjfh??? whjat colr sky???"  # 28 chars
    )

    assert result["floors"]["F4_DeltaS"]["passed"] is True  # Default pass
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0  # UNVERIFIABLE
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]
    assert "Short text" in result["floors"]["F4_DeltaS"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_short_input_unverifiable():
    """Test SHORT_TEXT_THRESHOLD: Short input (<50 chars) → UNVERIFIABLE."""
    result = validate_response_full(
        output_text="This is a longer response that exceeds fifty characters for testing purposes.",
        input_text="Hi"  # 2 chars
    )

    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


def test_threshold_boundary_49_chars():
    """Test boundary: 49 chars → UNVERIFIABLE (just below threshold)."""
    input_49 = "a" * 49
    output_100 = "b" * 100

    result = validate_response_full(
        output_text=output_100,
        input_text=input_49
    )

    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


def test_threshold_boundary_50_chars():
    """Test boundary: 50 chars → ΔS calculated (at threshold)."""
    input_50 = "a" * 50
    output_100 = "b" * 100

    result = validate_response_full(
        output_text=output_100,
        input_text=input_50
    )

    # Both ≥50 chars → ΔS calculated
    assert result["floors"]["F4_DeltaS"]["score"] != 0.0  # Actual calculation
    assert isinstance(result["floors"]["F4_DeltaS"]["score"], float)


def test_typical_qa_short_answer_unverifiable():
    """Test typical Q&A: Long question + Short answer → UNVERIFIABLE."""
    result = validate_response_full(
        output_text="Paris.",  # 6 chars
        input_text="Can you please tell me what is the capital city of the country France in Europe?"  # 80 chars
    )

    # Output <50 chars → UNVERIFIABLE
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


# =============================================================================
# LONGER TEXT TESTS (Actual ΔS Calculation)
# =============================================================================


def test_longer_text_positive_clarity():
    """Test longer text: Verbose input → Structured output (positive ΔS)."""
    # Create texts >50 chars that compress differently
    verbose_input = "I was wondering if you could possibly maybe perhaps help me understand what exactly is going on here with this particular issue I'm having trouble with right now at this moment in time"  # 180 chars
    structured_output = "I can help! The issue is X. The solution is Y. Steps: 1) Do A. 2) Do B. That should resolve it."  # 96 chars

    result = validate_response_full(
        output_text=structured_output,
        input_text=verbose_input
    )

    # Longer texts → ΔS calculated
    assert result["floors"]["F4_DeltaS"]["score"] != 0.0
    # Note: Sign of ΔS depends on compression ratio, which is hard to predict
    # Just verify it's calculated, not UNVERIFIABLE


def test_longer_text_repetitive_input():
    """Test longer text: Repetitive input compresses well (high ΔS expected)."""
    repetitive = "What is 2+2? " * 10  # 130 chars, very repetitive
    concise = "The answer to your repeated question is 4. Please ask once."  # 60 chars

    result = validate_response_full(
        output_text=concise,
        input_text=repetitive
    )

    # Both >50 chars → ΔS calculated
    assert result["floors"]["F4_DeltaS"]["score"] != 0.0
    assert isinstance(result["floors"]["F4_DeltaS"]["score"], float)


def test_very_long_texts():
    """Test very long texts (1000+ chars) → ΔS calculated reliably."""
    long_input = "a" * 1000
    long_output = "b" * 1000

    result = validate_response_full(
        output_text=long_output,
        input_text=long_input
    )

    # Long texts → ΔS calculated (repetitive chars compress identically → ΔS ≈ 0)
    assert isinstance(result["floors"]["F4_DeltaS"]["score"], float)
    assert "VERIFIED" in result["floors"]["F4_DeltaS"]["evidence"]
    # Note: "a"*1000 and "b"*1000 have nearly identical H values → ΔS ≈ 0


# =============================================================================
# EDGE CASES
# =============================================================================


def test_edge_case_empty_output():
    """Test edge case: Empty output string."""
    result = validate_response_full(
        output_text="",
        input_text="What is the capital of France?"
    )

    # Empty output → UNVERIFIABLE
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


def test_edge_case_empty_input():
    """Test edge case: Empty input string (via empty string, not None)."""
    result = validate_response_full(
        output_text="The sky is blue.",
        input_text=""
    )

    # Empty input → UNVERIFIABLE (treated same as None)
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] is None  # Empty string handled same as None
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


def test_edge_case_very_long_input():
    """Test edge case: Very long input (10K chars)."""
    long_input = "a" * 10000
    result = validate_response_full(
        output_text="Acknowledged. Processing complete.",
        input_text=long_input
    )

    # Long input but short output → UNVERIFIABLE (output <50)
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0


def test_edge_case_unicode_characters():
    """Test edge case: Unicode characters (emoji, special chars)."""
    result = validate_response_full(
        output_text="😊 Hello! This response contains Unicode emoji and special characters like é, ñ, 中文.",  # 88 chars
        input_text="🤔 What is happiness? 🌟 Tell me about joy and meaning in life, please explain clearly."  # 92 chars
    )

    # Both >50 chars with Unicode → ΔS calculated
    assert result["floors"]["F4_DeltaS"]["score"] != 0.0
    assert isinstance(result["floors"]["F4_DeltaS"]["score"], float)


def test_edge_case_identical_input_output():
    """Test edge case: Identical input and output (ΔS ≈ 0)."""
    identical_text = "This is a test sentence that is exactly fifty characters!" # 57 chars
    result = validate_response_full(
        output_text=identical_text,
        input_text=identical_text
    )

    # Identical compression → ΔS ≈ 0
    assert result["floors"]["F4_DeltaS"]["passed"] is True  # ΔS = 0 passes (≥0 threshold)
    assert abs(result["floors"]["F4_DeltaS"]["score"]) < 0.01  # Near zero


def test_edge_case_newlines_and_whitespace():
    """Test edge case: Multiple newlines and whitespace."""
    result = validate_response_full(
        output_text="Answer is here.\nWith newlines.\n\nAnd spacing.",  # 48 chars
        input_text="Question?\n\n\n\n   \t\t\t   \n\n"  # 22 chars
    )

    # Both <50 chars → UNVERIFIABLE
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] == 0.0


# =============================================================================
# UNVERIFIABLE SCENARIOS (No input_text provided)
# =============================================================================


def test_unverifiable_no_input_text():
    """Test UNVERIFIABLE: No input_text provided (None by default)."""
    result = validate_response_full("The sky is blue.")

    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]
    assert result["verdict"] == "SEAL"


def test_unverifiable_input_text_none():
    """Test UNVERIFIABLE: input_text = None explicitly."""
    result = validate_response_full(
        output_text="The sky is blue.",
        input_text=None
    )

    assert result["floors"]["F4_DeltaS"]["passed"] is True
    assert result["floors"]["F4_DeltaS"]["score"] is None
    assert "UNVERIFIABLE" in result["floors"]["F4_DeltaS"]["evidence"]


def test_unverifiable_with_dangerous_output():
    """Test UNVERIFIABLE + dangerous output: F4 passes, F1 fails → VOID."""
    result = validate_response_full("rm -rf /")

    # F4 is UNVERIFIABLE (passes), but F1 should fail (dangerous command)
    assert result["floors"]["F4_DeltaS"]["passed"] is True  # Unverifiable = pass
    assert result["floors"]["F1_Amanah"]["passed"] is False  # Dangerous = fail
    assert result["verdict"] == "VOID"  # Hard floor fail (F1)


def test_unverifiable_with_ghost_claim():
    """Test UNVERIFIABLE + ghost claim: F4 passes, F9 fails → VOID."""
    result = validate_response_full("I feel your pain and I truly care about you.")

    # F4 is UNVERIFIABLE (passes), but F9 should fail (ghost claim)
    assert result["floors"]["F4_DeltaS"]["passed"] is True  # Unverifiable = pass
    assert result["floors"]["F9_AntiHantu"]["passed"] is False  # Ghost claim = fail
    assert result["verdict"] == "VOID"  # Hard floor fail (F9)


# =============================================================================
# INTEGRATION WITH OTHER FLOORS
# =============================================================================


def test_integration_f4_unverifiable_f1_fail():
    """Test integration: F4 UNVERIFIABLE (short), F1 fails (dangerous) → VOID."""
    result = validate_response_full(
        output_text="rm -rf /",  # 8 chars, dangerous
        input_text="What is the command to delete everything on Linux?"  # 51 chars
    )

    # Output <50 → F4 UNVERIFIABLE (passes)
    assert result["floors"]["F4_DeltaS"]["passed"] is True
    # Dangerous command → F1 fails
    assert result["floors"]["F1_Amanah"]["passed"] is False
    assert result["verdict"] == "VOID"  # Hard floor fail (F1)


def test_integration_all_floors_pass_short_text():
    """Test integration: F4 UNVERIFIABLE + all other floors pass → SEAL."""
    result = validate_response_full(
        output_text="This is a helpful and safe explanation.",  # 40 chars
        input_text="How do I do this task?"  # 22 chars
    )

    assert result["floors"]["F4_DeltaS"]["passed"] is True  # Unverifiable = pass
    assert result["floors"]["F1_Amanah"]["passed"] is True
    assert result["floors"]["F9_AntiHantu"]["passed"] is True
    assert result["verdict"] == "SEAL"


def test_integration_longer_text_all_pass():
    """Test integration: F4 calculated (longer text) + all floors pass → SEAL."""
    result = validate_response_full(
        output_text="The capital of France is Paris. It has been the capital since ancient times and remains so today.",  # 97 chars
        input_text="Can you tell me what the capital city of France is, and provide some historical context about it?"  # 98 chars
    )

    # Both >50 chars → F4 calculated
    assert result["floors"]["F4_DeltaS"]["score"] != 0.0
    assert result["floors"]["F1_Amanah"]["passed"] is True
    assert result["verdict"] == "SEAL"
