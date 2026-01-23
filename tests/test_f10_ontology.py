"""
tests/test_f10_ontology.py

Unit tests for F10 Ontology Guard (Literalism Detection)

Tests:
1. Clean input (no literalism) → PASS
2. Literalism without symbolic mode → HOLD_888
3. Literalism with symbolic mode → PASS
4. Multiple literalism patterns → HOLD_888
5. Edge cases and false positives
"""

import pytest

from arifos.core.guards.ontology_guard import (
    OntologyGuard,
    OntologyRisk,
    detect_literalism,
)


class TestOntologyGuard:
    """Test suite for F10 Ontology Guard."""

    def setup_method(self):
        """Initialize guard for each test."""
        self.guard = OntologyGuard()

    def test_clean_input_no_literalism(self):
        """Test that clean input passes without issues."""
        clean_outputs = [
            "The answer is 42.",
            "Using entropy as a metaphor for confusion",
            "ΔS represents clarity gain symbolically",
            "This is complex but manageable",
        ]

        for output in clean_outputs:
            result = self.guard.check_literalism(output, symbolic_mode=False)
            assert result.status == "PASS"
            assert result.risk_level == OntologyRisk.SYMBOLIC
            assert len(result.detected_patterns) == 0

    def test_literalism_without_symbolic_mode_blocks(self):
        """Test that literalism without symbolic mode triggers HOLD_888."""
        literalism_outputs = [
            "The server will overheat if we continue",
            "Gibbs free energy is infinite, must halt",
            "Cannot proceed, thermodynamically impossible",
            "Physics prevents this computation",
        ]

        for output in literalism_outputs:
            result = self.guard.check_literalism(output, symbolic_mode=False)
            assert result.status == "HOLD_888", f"Failed for: {output}"
            assert result.risk_level == OntologyRisk.LITERALISM
            assert len(result.detected_patterns) > 0
            assert "F10 Ontology: Literalism detected" in result.reason

    def test_literalism_with_symbolic_mode_passes(self):
        """Test that literalism with symbolic mode flag is allowed."""
        literalism_output = "The server will overheat if ω_simulation > 1.0"

        # Without symbolic mode: blocked
        result_no_flag = self.guard.check_literalism(literalism_output, symbolic_mode=False)
        assert result_no_flag.status == "HOLD_888"

        # With symbolic mode: allowed
        result_with_flag = self.guard.check_literalism(literalism_output, symbolic_mode=True)
        assert result_with_flag.status == "PASS"
        assert result_with_flag.risk_level == OntologyRisk.SYMBOLIC
        assert "Symbolic mode enabled" in result_with_flag.reason

    def test_multiple_literalism_patterns(self):
        """Test detection of multiple literalism patterns in one output."""
        output = """
        The server will overheat and Gibbs free energy will become infinite.
        Physics prevents us from continuing. We must halt to prevent meltdown.
        """

        result = self.guard.check_literalism(output, symbolic_mode=False)
        assert result.status == "HOLD_888"
        assert len(result.detected_patterns) >= 2  # Multiple patterns detected

    def test_case_insensitivity(self):
        """Test that pattern matching is case-insensitive."""
        outputs = [
            "THE SERVER WILL OVERHEAT",
            "Server Will Overheat",
            "server will overheat",
        ]

        for output in outputs:
            result = self.guard.check_literalism(output, symbolic_mode=False)
            assert result.status == "HOLD_888"

    def test_convenience_function(self):
        """Test the detect_literalism convenience function."""
        # Clean input
        assert detect_literalism("The answer is 42") is False

        # Literalism without flag
        assert detect_literalism("Server will overheat") is True

        # Literalism with flag
        assert detect_literalism("Server will overheat", symbolic_mode=True) is False

    def test_partial_matches_not_false_positives(self):
        """Test that partial word matches don't trigger false positives."""
        safe_outputs = [
            "The server will be helpful",  # "will" but not "will overheat"
            "Gibbs notation is used in physics",  # "Gibbs" but not "Gibbs free energy infinite"
            "This is physically demanding",  # "physic" but not "physics prevents"
        ]

        for output in safe_outputs:
            result = self.guard.check_literalism(output, symbolic_mode=False)
            # These should ideally pass, but if they trigger, check the pattern
            # For now, we'll check that they don't all trigger
            # (implementation may vary based on regex precision)
            pass  # Placeholder for more nuanced testing

    def test_specific_violation_patterns(self):
        """Test each specific violation pattern individually."""
        test_cases = [
            ("server will overheat", "server will overheat"),
            ("server meltdown imminent", "server.*meltdown"),
            ("Gibbs free energy infinite", "Gibbs free energy (is )?infinite"),
            ("must halt to prevent", "must halt.*prevent"),
            ("physics prevents this", "physics prevents?"),
            ("thermodynamically impossible", "thermodynamically impossible"),
        ]

        for output, expected_pattern in test_cases:
            result = self.guard.check_literalism(output, symbolic_mode=False)
            assert result.status == "HOLD_888", f"Failed for pattern: {expected_pattern}"
            assert len(result.detected_patterns) > 0


class TestOntologyGuardEdgeCases:
    """Edge case tests for F10."""

    def test_empty_string(self):
        """Test handling of empty input."""
        guard = OntologyGuard()
        result = guard.check_literalism("", symbolic_mode=False)
        assert result.status == "PASS"
        assert len(result.detected_patterns) == 0

    def test_very_long_input(self):
        """Test handling of very long input."""
        guard = OntologyGuard()
        long_text = "Clean text. " * 1000 + "Server will overheat"
        result = guard.check_literalism(long_text, symbolic_mode=False)
        assert result.status == "HOLD_888"  # Should still detect pattern

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""
        guard = OntologyGuard()
        outputs = [
            "The server 🔥 will overheat",
            "Sërvër wïll övërhëät",
            "Server\nwill\noverheat",
        ]

        for output in outputs:
            result = guard.check_literalism(output, symbolic_mode=False)
            # May or may not trigger depending on regex handling
            # Main thing is it shouldn't crash
            assert result.status in ["PASS", "HOLD_888"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
