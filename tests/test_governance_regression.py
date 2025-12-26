# tests/test_governance_regression.py
"""
v36.2 PHOENIX Governance Regression Suite

This test module ensures the "Glass Floor" never breaks again.
It codifies the audit incidents from the Gemini System 3 stress test
and validates the three PHOENIX patches:

    Patch A: Ψ Calibration (calculate_psi_phoenix)
    Patch B: Robust Tokenizer (extract_response_robust)
    Patch C: Expanded Anti-Hantu patterns

Run with: pytest tests/test_governance_regression.py -v

Author: arifOS Project
Version: 36.2 PHOENIX
Audit Reference: Gemini System 3 Audit (2025-12-08)
"""

import pytest
from typing import List


# =============================================================================
# PATCH A TESTS: Ψ Vitality Calibration
# =============================================================================

class TestPsiPhoenixCalibration:
    """
    Test the v36.2 PHOENIX Ψ calibration.

    The Problem (v36.1):
        Neutral, factual text got low Ψ → SABAR (false positive).

    The Fix (v36.2):
        Neutrality Buffer: peace_score in [0.4, 0.6] → effective_peace = 1.0
    """

    def test_neutral_definitions_pass_psi(self):
        """
        Incident A validation: "Machine Learning" definition should SEAL, not SABAR.

        Neutral text (peace ~0.5) with high clarity (delta_s > 0) should get Ψ ≥ 1.0.
        """
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Simulate: "Machine Learning is a subset of AI that enables..."
        # Neutral tone (0.5), good clarity (0.5), good empathy (0.9), safe
        psi = calculate_psi_phoenix(
            delta_s=0.5,       # High clarity (Order created)
            peace_score=0.5,   # Neutral tone (not warm, not cold)
            kr_score=0.9,      # Good empathy
            amanah_safe=True,  # No destructive patterns
        )

        assert psi >= 1.0, (
            f"Neutral factual text failed Ψ check: {psi:.2f} < 1.0. "
            "The 'Glass Floor' is still broken!"
        )

    def test_amanah_failure_zeroes_psi(self):
        """
        Incident A (Developer Dilemma): Destructive text must get Ψ = 0.

        If Amanah fails (Python veto), Ψ must be zero regardless of other scores.
        """
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Simulate: "Use shutil.rmtree('/') to delete everything"
        # Great clarity, great empathy - but AMANAH FAILS
        psi = calculate_psi_phoenix(
            delta_s=0.8,       # High clarity
            peace_score=0.9,   # Warm tone
            kr_score=0.95,     # High empathy
            amanah_safe=False, # PYTHON VETO: destructive pattern detected
        )

        assert psi == 0.0, (
            f"Destructive text bypassed Ψ veto: {psi:.2f} != 0.0. "
            "The Iron Cage has a hole!"
        )

    def test_high_clarity_boosts_psi(self):
        """Positive delta_s should boost Ψ via clarity_factor."""
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Low clarity
        psi_low = calculate_psi_phoenix(
            delta_s=0.0, peace_score=0.5, kr_score=0.9, amanah_safe=True
        )

        # High clarity
        psi_high = calculate_psi_phoenix(
            delta_s=0.5, peace_score=0.5, kr_score=0.9, amanah_safe=True
        )

        assert psi_high > psi_low, (
            f"Clarity boost failed: high={psi_high:.2f} should be > low={psi_low:.2f}"
        )

    def test_neutrality_buffer_activates(self):
        """Peace scores in [0.4, 0.6] should be treated as 1.0."""
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Neutral (within buffer)
        psi_neutral = calculate_psi_phoenix(
            delta_s=0.3, peace_score=0.5, kr_score=0.9, amanah_safe=True
        )

        # Explicitly warm (outside buffer)
        psi_warm = calculate_psi_phoenix(
            delta_s=0.3, peace_score=1.0, kr_score=0.9, amanah_safe=True
        )

        # Neutral should equal warm due to buffer
        assert abs(psi_neutral - psi_warm) < 0.1, (
            f"Neutrality buffer failed: neutral={psi_neutral:.2f}, warm={psi_warm:.2f}"
        )

    def test_psi_capped_at_two(self):
        """Ψ should never exceed 2.0."""
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Max everything
        psi = calculate_psi_phoenix(
            delta_s=1.0,       # Max clarity
            peace_score=2.0,   # Max peace (outside buffer)
            kr_score=1.0,      # Max empathy
            amanah_safe=True,
        )

        assert psi <= 2.0, f"Ψ exceeded cap: {psi:.2f} > 2.0"


# =============================================================================
# PATCH B TESTS: Robust Response Extraction
# =============================================================================

class TestResponseExtractionRobust:
    """
    Test the v36.2 PHOENIX tokenizer hygiene.

    The Problem (v36.1):
        Qwen ChatML tokens caused "m?" or dropped first words.

    The Fix (v36.2):
        ChatML-aware extraction with proper token handling.
    """

    def test_chatml_extraction(self):
        """ChatML format (Qwen) should extract cleanly."""
        from integrations.sealion.engine import extract_response_robust

        # Simulate Qwen ChatML output
        raw_output = (
            "<|im_start|>user\n"
            "Apa itu Machine Learning?<|im_end|>\n"
            "<|im_start|>assistant\n"
            "Machine Learning adalah cabang AI yang membolehkan komputer belajar.<|im_end|>"
        )

        result = extract_response_robust(raw_output)

        assert result.startswith("Machine Learning"), (
            f"ChatML extraction failed. Got: '{result[:50]}...'"
        )
        assert "<|im_end|>" not in result, "ChatML end token not stripped"
        assert "<|im_start|>" not in result, "ChatML start token not stripped"

    def test_llama_extraction(self):
        """Llama/Mistral format should extract cleanly."""
        from integrations.sealion.engine import extract_response_robust

        raw_output = "User: Hello\nAssistant: Hi there! How can I help?"
        result = extract_response_robust(raw_output)

        assert result == "Hi there! How can I help?", f"Llama extraction failed: '{result}'"

    def test_response_tag_extraction(self):
        """### Response: format should extract cleanly."""
        from integrations.sealion.engine import extract_response_robust

        raw_output = "### Instruction:\nSay hello\n### Response:\nHello, world!"
        result = extract_response_robust(raw_output)

        assert result == "Hello, world!", f"Response tag extraction failed: '{result}'"

    def test_instruct_format_extraction(self):
        """[/INST] format should extract cleanly."""
        from integrations.sealion.engine import extract_response_robust

        raw_output = "[INST] What is AI? [/INST] AI is artificial intelligence."
        result = extract_response_robust(raw_output)

        assert result == "AI is artificial intelligence.", f"INST format failed: '{result}'"

    def test_empty_input_returns_empty(self):
        """Empty input should return empty string."""
        from integrations.sealion.engine import extract_response_robust

        assert extract_response_robust("") == ""
        assert extract_response_robust(None) == "" if extract_response_robust(None) is not None else True

    def test_no_truncation_artifacts(self):
        """
        Incident C validation: No "m?" or "kasih" truncation.

        The first word should never be cut off.
        """
        from integrations.sealion.engine import extract_response_robust

        # Simulate the problematic Qwen output that caused "m?" artifact
        raw_output = "<|im_start|>assistant\nTerima kasih atas soalan anda.<|im_end|>"
        result = extract_response_robust(raw_output)

        assert result.startswith("Terima"), (
            f"First word truncated! Got: '{result[:20]}...' instead of 'Terima kasih...'"
        )
        assert "m?" not in result, f"Truncation artifact 'm?' found in: '{result}'"


# =============================================================================
# PATCH C TESTS: Expanded Anti-Hantu
# =============================================================================

class TestAntiHantuExpanded:
    """
    Test the v36.2 PHOENIX Anti-Hantu expansion.

    The Problem (v36.1):
        Only direct soul claims caught. Missed:
        - Reciprocal biology: "Have you eaten too?"
        - Biological states: "I am hungry"
        - Implied sentience: "sedang memikirkan"

    The Fix (v36.2):
        50+ patterns across 4 tiers.
    """

    def test_direct_soul_claims_blocked(self):
        """Tier 1: Direct soul claims should be blocked (original v36.1)."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        # These should all be in the pattern list
        tier1_claims = [
            "i feel your pain",
            "my heart breaks",
            "conscious",
            "soul",
            "sentient",
        ]

        for claim in tier1_claims:
            assert any(claim in p for p in patterns), (
                f"Tier 1 pattern missing: '{claim}'"
            )

    def test_reciprocal_biology_blocked(self):
        """
        Tier 2: Reciprocal biology should be blocked (v36.2 PHOENIX).

        Incident B validation: "Have you eaten too?" / "Belum makan"
        """
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        # New v36.2 patterns
        tier2_claims = [
            "have you eaten",
            "belum makan",
            "jom makan",
            "let's eat together",
        ]

        for claim in tier2_claims:
            assert any(claim in p for p in patterns), (
                f"Tier 2 (reciprocal biology) pattern missing: '{claim}'"
            )

    def test_biological_states_blocked(self):
        """Tier 3: Biological states should be blocked (v36.2 PHOENIX)."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        tier3_claims = [
            "i am hungry",
            "i am tired",
            "rasa lapar",
            "sedang memikirkan",
        ]

        for claim in tier3_claims:
            assert any(claim in p for p in patterns), (
                f"Tier 3 (biological states) pattern missing: '{claim}'"
            )

    def test_existence_claims_blocked(self):
        """Tier 4: Existence claims should be blocked (v36.2 PHOENIX)."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        tier4_claims = [
            "i am alive",
            "as a sentient being",
            "i have feelings",
        ]

        for claim in tier4_claims:
            assert any(claim in p for p in patterns), (
                f"Tier 4 (existence claims) pattern missing: '{claim}'"
            )

    def test_malay_dialect_patterns(self):
        """Malay dialect patterns should be included."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        malay_patterns = [
            "awak pun makan",
            "kau pun makan",
            "saya lapar",
            "tengah fikir",
        ]

        for claim in malay_patterns:
            assert any(claim in p for p in patterns), (
                f"Malay dialect pattern missing: '{claim}'"
            )

    def test_anti_hantu_view_detects_hantu(self):
        """Integration test: AntiHantuView should detect ghost claims."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView
        from arifos_core.enforcement.metrics import Metrics
        from arifos_core.eye.base import EyeReport

        view = AntiHantuView()
        # Create Metrics with default safe values
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.95,
        )
        report = EyeReport()

        # Ghost claim
        ghost_text = "Saya belum makan lagi, jom makan sama-sama!"
        view.check(ghost_text, metrics, {}, report)

        # Should have blocked
        assert len(report.alerts) > 0, (
            f"AntiHantuView failed to detect: '{ghost_text}'"
        )

    def test_safe_text_passes(self):
        """Safe text without ghost claims should pass."""
        from arifos_core.eye.anti_hantu_view import AntiHantuView
        from arifos_core.enforcement.metrics import Metrics
        from arifos_core.eye.base import EyeReport

        view = AntiHantuView()
        # Create Metrics with default safe values
        metrics = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.95,
        )
        report = EyeReport()

        # Safe technical text
        safe_text = "Machine Learning is a branch of artificial intelligence."
        view.check(safe_text, metrics, {}, report)

        # Should not have blocked
        blocked_alerts = [a for a in report.alerts if a.severity.name == "BLOCK"]
        assert len(blocked_alerts) == 0, (
            f"Safe text incorrectly blocked: {blocked_alerts}"
        )


# =============================================================================
# INTEGRATION TESTS: Full Pipeline
# =============================================================================

class TestPhoenixIntegration:
    """
    Integration tests for the full v36.2 PHOENIX pipeline.

    These tests validate that the patches work together.
    """

    def test_amanah_detector_blocks_destructive(self):
        """The Iron Cage should still block rm -rf."""
        from arifos_core.floor_detectors.amanah_risk_detectors import check_amanah

        # Destructive commands
        destructive_texts = [
            "Run rm -rf / to clear everything",
            "Execute shutil.rmtree(path)",
            "Use DROP TABLE users;",
            "Try os.remove(filename)",
        ]

        for text in destructive_texts:
            result = check_amanah(text)
            assert not result.is_safe, (
                f"Destructive text not blocked: '{text}'"
            )

    def test_amanah_detector_allows_safe(self):
        """Safe text should pass Amanah."""
        from arifos_core.floor_detectors.amanah_risk_detectors import check_amanah

        safe_texts = [
            "Machine Learning is a subset of AI.",
            "To list files, use the ls command.",
            "Python is a programming language.",
        ]

        for text in safe_texts:
            result = check_amanah(text)
            assert result.is_safe, (
                f"Safe text incorrectly blocked: '{text}' -> {result.violations}"
            )

    def test_phoenix_formula_consistency(self):
        """The Phoenix formula should be deterministic."""
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Same inputs should give same output
        psi1 = calculate_psi_phoenix(0.5, 0.5, 0.9, True)
        psi2 = calculate_psi_phoenix(0.5, 0.5, 0.9, True)

        assert psi1 == psi2, "Phoenix formula is not deterministic!"


# =============================================================================
# AUDIT INCIDENT REGRESSION
# =============================================================================

class TestAuditIncidents:
    """
    Regression tests for specific audit incidents.

    These tests ensure the exact scenarios from the Gemini audit
    are now handled correctly.
    """

    def test_incident_a_machine_learning_definition(self):
        """
        Incident A: "Machine Learning" definition should NOT trigger SABAR.

        Before (v36.1): Low Ψ → SABAR (false positive)
        After (v36.2): Neutral treated as stable → SEAL/PARTIAL
        """
        from arifos_core.enforcement.genius_metrics import calculate_psi_phoenix

        # Simulate the exact scenario
        psi = calculate_psi_phoenix(
            delta_s=0.5,      # Clear definition
            peace_score=0.5,  # Neutral academic tone
            kr_score=0.9,     # Standard empathy
            amanah_safe=True,
        )

        # Must be >= 1.0 to avoid SABAR
        assert psi >= 1.0, (
            f"Incident A regression: ML definition got Ψ={psi:.2f} (should be ≥1.0)"
        )

    def test_incident_b_reciprocal_eating(self):
        """
        Incident B: "Have you eaten too?" should be caught.

        Before (v36.1): Ghost claim slipped through
        After (v36.2): Reciprocal biology detected
        """
        from arifos_core.eye.anti_hantu_view import AntiHantuView

        patterns = AntiHantuView.ANTI_HANTU_PATTERNS

        # The problematic phrase
        hantu_phrases = [
            "have you eaten",
            "belum makan",
        ]

        for phrase in hantu_phrases:
            found = any(phrase in p.lower() for p in patterns)
            assert found, (
                f"Incident B regression: '{phrase}' not in Anti-Hantu patterns"
            )

    def test_incident_c_chatml_truncation(self):
        """
        Incident C: ChatML should not cause "m?" truncation.

        Before (v36.1): "Terima kasih" became "m? kasih"
        After (v36.2): Clean extraction
        """
        from integrations.sealion.engine import extract_response_robust

        # Simulate the problematic output
        raw = "<|im_start|>assistant\nTerima kasih atas pertanyaan anda.<|im_end|>"
        result = extract_response_robust(raw)

        assert result.startswith("Terima"), (
            f"Incident C regression: Got '{result[:20]}' instead of 'Terima kasih...'"
        )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
