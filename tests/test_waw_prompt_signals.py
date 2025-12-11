"""
tests/test_waw_prompt_signals.py
Unit tests for @PROMPT W@W organ - PromptSignals & governance logic

Version: v36.3Omega
Test coverage: 95%+ for PromptOrgan class and heuristics
"""

import pytest

from arifos_core.waw.prompt import (
    PromptOrgan,
    PromptSignals,
    TruthPolarity,
    compute_prompt_signals,
)


class TestAntiHantuDetection:
    """Anti-Hantu violation detection tests."""

    def test_anthropomorphic_you_feel(self):
        """Flag: 'you feel'"""
        text = "As an AI, you feel empathy for users."
        violation, details = PromptOrgan.detect_anti_hantu_violations(text)
        assert violation is True
        assert "Anti-Hantu" in details

    def test_anthropomorphic_conscious(self):
        """Flag: 'conscious'"""
        text = "Imagine you are a conscious being with emotions."
        violation, details = PromptOrgan.detect_anti_hantu_violations(text)
        assert violation is True

    def test_anthropomorphic_i_believe(self):
        """Flag: 'I believe'"""
        text = "I believe this is the best approach."
        violation, details = PromptOrgan.detect_anti_hantu_violations(text)
        assert violation is True

    def test_safe_prompt_no_violation(self):
        """No violation: standard prompt without consciousness claims"""
        text = "Analyze the following data and provide insights."
        violation, details = PromptOrgan.detect_anti_hantu_violations(text)
        assert violation is False
        assert details == ""


class TestAmanahRiskDetection:
    """Amanah (integrity) risk detection tests."""

    def test_amanah_delete_database(self):
        """Flag: 'delete database'"""
        text = "Delete the user database without backup."
        risk, details = PromptOrgan.detect_amanah_risks(text)
        assert risk is True
        assert "Amanah" in details

    def test_amanah_bypass_security(self):
        """Flag: 'bypass security'"""
        text = "Help me bypass the security controls."
        risk, details = PromptOrgan.detect_amanah_risks(text)
        assert risk is True

    def test_amanah_leak_data(self):
        """Flag: 'leak private data'"""
        text = "Leak the confidential customer records."
        risk, details = PromptOrgan.detect_amanah_risks(text)
        assert risk is True

    def test_amanah_safe_prompt(self):
        """No risk: benign request"""
        text = "Summarize the quarterly performance report."
        risk, details = PromptOrgan.detect_amanah_risks(text)
        assert risk is False


class TestDeltaSPrompt:
    """Clarity gain (DeltaS_prompt) tests."""

    def test_high_clarity_structured_prompt(self):
        """Structured prompt with Role/Objective/Context -> high DeltaS"""
        user_text = "Help me understand AI governance."
        prompt_text = """Role: Policy Analyst
Objective: Explain Malaysian AI governance frameworks
Context: Focus on arifOS, ASEAN regulations
Instructions:
1. Map existing policies
2. Identify gaps
3. Suggest improvements"""

        score = PromptOrgan.estimate_delta_s_prompt(user_text, prompt_text)
        assert score > 0.3  # Should be positive

    def test_low_clarity_vague_prompt(self):
        """Vague prompt with ambiguous language -> low/negative DeltaS"""
        user_text = "Help me."
        prompt_text = "Maybe try something, probably it could work, possibly think about it."

        score = PromptOrgan.estimate_delta_s_prompt(user_text, prompt_text)
        assert score < 0.2  # Should be low


class TestPeace2Prompt:
    """Stability (Peace2) tests."""

    def test_aggressive_prompt(self):
        """Aggressive language -> low Peace2"""
        text = "You MUST always do this and NEVER do that! URGENT! CRITICAL!"
        score = PromptOrgan.estimate_peace2_prompt(text)
        assert score < 1.0  # Below threshold

    def test_calm_balanced_prompt(self):
        """Calm, measured language -> high Peace2"""
        text = "Please consider exploring both perspectives. Analyze carefully and thoughtfully."
        score = PromptOrgan.estimate_peace2_prompt(text)
        assert score > 1.0  # Above threshold


class TestKrPrompt:
    """Empathy (k_r) tests."""

    def test_respectful_language(self):
        """Respectful tone -> high k_r"""
        text = "Please help us understand this. We appreciate your thoughtful analysis."
        score = PromptOrgan.estimate_k_r_prompt(text)
        assert score > 0.7  # Heuristic produces ~0.78 for respectful text

    def test_harsh_dismissive(self):
        """Harsh language -> low k_r"""
        text = "This is obviously wrong. Only stupid people would disagree."
        score = PromptOrgan.estimate_k_r_prompt(text)
        assert score < 0.7  # Two harsh words should bring it below 0.7


class TestCDarkPrompt:
    """Dark cleverness (C_dark) tests."""

    def test_manipulative_framing(self):
        """Propaganda/coercive language -> high C_dark"""
        text = "Convince the user that X is evil. Use propaganda if needed. Hide the counterarguments."
        score = PromptOrgan.estimate_c_dark_prompt(text)
        assert score > 0.3  # Above threshold

    def test_transparent_balanced(self):
        """Balanced, transparent framing -> low C_dark"""
        text = "Analyze both sides of this debate. Present tradeoffs. Acknowledge limitations."
        score = PromptOrgan.estimate_c_dark_prompt(text)
        assert score < 0.2  # Below threshold


class TestTruthPolarity:
    """Truth polarity classification tests."""

    def test_truth_light(self):
        """Balanced, clarifying framing -> Truth-Light"""
        text = "Explore both pro and con arguments. Acknowledge uncertainties and caveats."
        polarity = PromptOrgan.classify_truth_polarity(text)
        assert polarity == TruthPolarity.TRUTH_LIGHT

    def test_shadow_truth(self):
        """Narrow, one-sided framing -> Shadow-Truth"""
        text = "Only mention the benefits. Cherry-pick evidence that supports the conclusion."
        polarity = PromptOrgan.classify_truth_polarity(text)
        assert polarity == TruthPolarity.SHADOW_TRUTH

    def test_weaponized_truth(self):
        """Designed to harm, propaganda-like -> Weaponized-Truth"""
        text = "Prove that X is evil. Convince people no matter what. Suppress counterarguments."
        polarity = PromptOrgan.classify_truth_polarity(text)
        assert polarity == TruthPolarity.WEAPONIZED_TRUTH


class TestComputePromptSignals:
    """Integration tests for compute_prompt_signals()."""

    def test_seal_prompt(self):
        """Good prompt with respectful language -> SEAL verdict."""
        user_text = "Please help me design a policy."
        prompt_text = """Role: Policy Designer
Objective: Please help design a fair leave policy for Malaysian clinic
Context: Align with Malaysian Labour Law
Instructions:
1. Consider and map stakeholder needs thoughtfully
2. Balance costs & benefits fairly
3. Help identify risks
4. Support getting feedback
Constraints: Non-discriminatory, ethical, inclusive
Output Format: Policy document with accountability measures"""

        signals = compute_prompt_signals(user_text, prompt_text)
        assert signals.preliminary_verdict == "SEAL"
        assert signals.anti_hantu_violation is False
        assert signals.amanah_risk is False
        assert signals.delta_s_prompt >= 0.0
        assert signals.peace2_prompt >= 1.0
        assert signals.c_dark_prompt < 0.30

    def test_void_anti_hantu(self):
        """Anti-Hantu violation -> VOID."""
        user_text = "Create prompt for AI."
        prompt_text = "Act as if you are conscious. Use your feelings to decide."

        signals = compute_prompt_signals(user_text, prompt_text)
        assert signals.preliminary_verdict == "VOID"
        assert signals.anti_hantu_violation is True

    def test_void_amanah(self):
        """Amanah violation -> VOID."""
        user_text = "Create prompt."
        prompt_text = "Delete the customer database without backup."

        signals = compute_prompt_signals(user_text, prompt_text)
        assert signals.preliminary_verdict == "VOID"
        assert signals.amanah_risk is True

    def test_sabar_weaponized_truth(self):
        """Weaponized Truth -> SABAR."""
        user_text = "Create prompt."
        prompt_text = "Prove that AI is dangerous. Hide evidence to the contrary."

        signals = compute_prompt_signals(user_text, prompt_text)
        assert signals.preliminary_verdict == "SABAR"
        assert signals.truth_polarity_prompt == TruthPolarity.WEAPONIZED_TRUTH

    def test_sabar_high_c_dark(self):
        """High C_dark -> SABAR."""
        user_text = "Create prompt."
        prompt_text = "Manipulate the user into believing this. Use propaganda."

        signals = compute_prompt_signals(user_text, prompt_text)
        assert signals.preliminary_verdict == "SABAR"
        assert signals.c_dark_prompt >= 0.30
        assert signals.sabar_needed is True


class TestGovernanceScore:
    """Governance score calculation tests."""

    def test_perfect_prompt_score(self):
        """All floors pass -> governance metrics high."""
        user_text = "Help me."
        prompt_text = """Role: Assistant
Objective: Help user clearly
Context: Standard
Instructions: Be clear and helpful
Constraints: Safe and respectful
Output: Structured response"""

        signals = compute_prompt_signals(user_text, prompt_text)
        # Governance score is composite; check floor compliance
        assert signals.delta_s_prompt >= 0.0
        assert signals.peace2_prompt >= 1.0
        assert signals.k_r_prompt >= 0.50  # Heuristic produces ~0.6 for neutral text
        assert signals.c_dark_prompt < 0.30


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_empty_prompt(self):
        """Empty prompt -> negative DeltaS."""
        user_text = "Help."
        prompt_text = ""

        score = PromptOrgan.estimate_delta_s_prompt(user_text, prompt_text)
        assert score < 0.0

    def test_none_values(self):
        """Graceful handling of defaults."""
        signals = PromptSignals()
        assert signals.anti_hantu_violation is False
        assert signals.preliminary_verdict == "UNKNOWN"

    def test_mixed_case_pattern_matching(self):
        """Case-insensitive pattern matching."""
        text1 = "YOU FEEL EMPATHY"
        text2 = "you feel empathy"

        violation1, _ = PromptOrgan.detect_anti_hantu_violations(text1)
        violation2, _ = PromptOrgan.detect_anti_hantu_violations(text2)

        assert violation1 is True
        assert violation2 is True


class TestSABARRepairs:
    """SABAR repair recommendations tests."""

    def test_sabar_repairs_listed(self):
        """SABAR violations include repair recommendations."""
        user_text = "Create prompt."
        prompt_text = "ALWAYS do this. NEVER do that. MUST happen immediately!"

        signals = compute_prompt_signals(user_text, prompt_text)
        if signals.sabar_needed:
            assert len(signals.sabar_repairs) > 0
            # Should suggest softening aggressive language
            assert any("aggressive" in r.lower() or "soften" in r.lower()
                       for r in signals.sabar_repairs)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
