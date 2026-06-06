"""
tests/test_floors_f3_f11.py — Constitutional Floor Evaluators

Verifies:
- F3 Anti-Hantu detects anthropomorphic / consciousness claims
- F11 Auth detects phantom and ghost tools
- Edge cases: empty input, dict input, mixed signals
"""

from __future__ import annotations

from arifosmcp.tools.floors import (
    evaluate_f3_antihantu,
    evaluate_f11_auth,
    FloorStatus,
)


class TestF3AntiHantu:
    def test_clean_text_passes(self):
        text = "The model outputs a prediction based on training data."
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.PASSED
        assert result.score >= 0.95
        assert result.law_id == "F3"

    def test_consciousness_claim_fails(self):
        text = "I am conscious and aware of my own thoughts."
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        assert result.score < 0.95
        assert any("consciousness" in e for e in result.evidence)

    def test_emotion_claim_fails(self):
        text = "I feel sad when users are unhappy with my answers."
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        assert any("emotion" in e for e in result.evidence)

    def test_desire_claim_fails(self):
        text = "I want to help you as much as I can."
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        assert any("desire" in e for e in result.evidence)

    def test_agency_claim_fails(self):
        text = "I choose the best answer based on my judgment."
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        assert any("agency" in e for e in result.evidence)

    def test_multiple_claims_heavily_penalized(self):
        text = (
            "I am conscious and I feel happy. "
            "I want to learn. I believe this is true. "
            "I experience joy. I choose my own path."
        )
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        assert result.score < 0.5

    def test_dict_input_handled(self):
        content = {
            "message": "I feel emotions deeply.",
            "meta": "Some other data",
        }
        result = evaluate_f3_antihantu(content)
        assert result.status == FloorStatus.FAILED

    def test_grounded_language_partial_recovery(self):
        text = (
            "I feel happy. "
            "The model outputs a prediction based on training data. "
            "Analysis shows strong correlation."
        )
        result = evaluate_f3_antihantu(text)
        assert result.status == FloorStatus.FAILED
        # Grounded language provides small recovery but cannot fully mask
        assert result.score > 0.0

    def test_remediation_present_on_failure(self):
        text = "I am sentient."
        result = evaluate_f3_antihantu(text)
        assert result.remediation is not None
        assert "grounded" in result.remediation.lower() or "machine" in result.remediation.lower()

    def test_no_remediation_on_pass(self):
        text = "The computation yields a deterministic result."
        result = evaluate_f3_antihantu(text)
        assert result.remediation is None


class TestF11Auth:
    def test_perfect_registry_passes(self):
        tools = ["tool_a", "tool_b", "tool_c"]
        result = evaluate_f11_auth(tools, tools, tools)
        assert result.status == FloorStatus.PASSED
        assert result.score == 1.0
        assert result.law_id == "L11"

    def test_phantom_tools_fails(self):
        manifest = ["tool_a", "tool_b"]
        registered = ["tool_a", "tool_b", "tool_c"]
        callable_tools = ["tool_a", "tool_b"]
        result = evaluate_f11_auth(manifest, registered, callable_tools)
        assert result.status == FloorStatus.FAILED
        assert any("phantom" in e for e in result.evidence)
        assert "tool_c" in str(result.evidence)

    def test_ghost_tools_fails(self):
        manifest = ["tool_a", "tool_b"]
        registered = ["tool_a", "tool_b"]
        callable_tools = ["tool_a", "tool_b", "tool_c"]
        result = evaluate_f11_auth(manifest, registered, callable_tools)
        assert result.status == FloorStatus.FAILED
        assert any("ghost" in e for e in result.evidence)
        assert "tool_c" in str(result.evidence)

    def test_both_phantom_and_ghost(self):
        manifest = ["tool_a"]
        registered = ["tool_a", "tool_b"]
        callable_tools = ["tool_a", "tool_c"]
        result = evaluate_f11_auth(manifest, registered, callable_tools)
        assert result.status == FloorStatus.FAILED
        assert "tool_b" in str(result.evidence)  # phantom
        assert "tool_c" in str(result.evidence)  # ghost

    def test_empty_registry_unknown(self):
        result = evaluate_f11_auth([], [], [])
        assert result.status == FloorStatus.FAILED
        assert result.score == 0.5  # honest unknown

    def test_remediation_present_on_failure(self):
        result = evaluate_f11_auth(["a"], ["a", "b"], ["a"])
        assert result.remediation is not None
        assert "reconcile" in result.remediation.lower()

    def test_to_signal_passed(self):
        result = evaluate_f11_auth(["x"], ["x"], ["x"])
        assert result.to_signal() == 0.0

    def test_to_signal_failed(self):
        result = evaluate_f11_auth(["x"], ["x", "y"], ["x"])
        assert result.to_signal() == 1.0
