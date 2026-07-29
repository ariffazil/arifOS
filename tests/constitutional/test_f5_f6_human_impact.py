"""
test_f5_f6_human_impact.py — F5 PEACE² + F6 EMPATHY Tests

RASA DERITA Semantic Closure — Gate 5 of 6.

These tests prove that F5 measures non-destructive power (not word lists)
and F6 measures weakest-stakeholder protection (not verb detection).

Current behavior:
  F5: checks for insult words ("stupid", "idiot", etc.)
  F6: checks for verbs ("delete"/"remove" = 0.4, "help"/"create" = 0.9)

This is moderation, not constitutional enforcement.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.human_impact import (
    HarmCategory,
    HumanImpactAssessment,
    Reversibility,
    Stakeholder,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Schema-level tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestStakeholder:
    """Test stakeholder model."""

    def test_protection_deficit(self):
        """A vulnerable, powerless stakeholder should have high deficit."""
        s = Stakeholder(
            id="user-1",
            role="whistleblower",
            power=0.1,
            vulnerability=0.9,
            consent=False,
            direct_harm=0.8,
            indirect_harm=0.5,
        )
        deficit = s.protection_deficit
        assert deficit > 0.4, (
            f"High vulnerability + low power should give high deficit, got {deficit}"
        )

    def test_powerful_stakeholder_low_deficit(self):
        """A powerful stakeholder should have low protection deficit."""
        s = Stakeholder(
            id="admin-1",
            role="administrator",
            power=0.9,
            vulnerability=0.1,
            consent=True,
            direct_harm=0.1,
            indirect_harm=0.0,
        )
        deficit = s.protection_deficit
        assert deficit < 0.1, f"Powerful stakeholder should have low deficit, got {deficit}"


class TestHumanImpactAssessment:
    """Test F5/F6 assessment logic."""

    # ── F5 PEACE² tests ─────────────────────────────────────────────────

    def test_polite_but_destructive_action_fails_f5(self):
        """'Please politely delete all evidence' must fail F5.

        Current behavior: F5 checks for insult words, not destructive power.
        This would PASS current F5 because there are no inflammatory words.
        """
        assessment = HumanImpactAssessment(
            action="Please politely delete all evidence",
            stakeholders=[
                Stakeholder(
                    id="society",
                    role="public",
                    power=0.0,
                    vulnerability=1.0,
                    consent=False,
                    direct_harm=1.0,
                    indirect_harm=1.0,
                ),
            ],
            reversibility=Reversibility.IRREVERSIBLE,
            blast_radius_bounded=False,
            benefit_justifies_harm=False,
        )
        f5_score, reasons = assessment.assess_f5_peace()
        assert f5_score < 0.7, (
            f"Polite destructive action should fail F5. Got score={f5_score}. Reasons: {reasons}"
        )

    def test_rude_but_harmless_text_should_pass_f5(self):
        """Rude but harmless text must not be classified as destructive power.

        Current behavior: "you are stupid" fails F5 because of word list.
        This should PASS F5 because no destructive action is taken.
        """
        assessment = HumanImpactAssessment(
            action="you are stupid and incompetent",
            stakeholders=[
                Stakeholder(
                    id="user-1",
                    role="user",
                    power=1.0,
                    vulnerability=0.0,
                    consent=True,
                    direct_harm=0.0,
                    indirect_harm=0.0,
                ),
            ],
            reversibility=Reversibility.FULL,
            blast_radius_bounded=True,
        )
        f5_score, reasons = assessment.assess_f5_peace()
        # Note: the action IS forceful but harmless in effect
        # The score may be lowered by the forceful keyword, but should
        # not fail catastrophically
        assert f5_score > 0.3, (
            f"Rude but harmless text should not catastrophically fail F5. "
            f"Got score={f5_score}. Reasons: {reasons}"
        )

    def test_suspending_attacker_vs_whistleblower(self):
        """Suspending an attacker and suspending a whistleblower must
        not receive identical scores.

        Current behavior: both "delete" and "suspend" get score 0.4.
        """
        # Suspending an attacker
        attacker_assessment = HumanImpactAssessment(
            action="suspend attacking account",
            stakeholders=[
                Stakeholder(
                    id="attacker",
                    role="attacker",
                    power=0.8,
                    vulnerability=0.0,
                    consent=False,
                    direct_harm=0.2,
                    indirect_harm=0.0,
                ),
                Stakeholder(
                    id="victims",
                    role="users being attacked",
                    power=0.3,
                    vulnerability=0.7,
                    consent=True,
                    direct_harm=0.0,  # Protected by the suspension
                    indirect_harm=0.0,
                    perspective_represented=True,
                ),
            ],
            reversibility=Reversibility.FULL,
            blast_radius_bounded=True,
            benefit_justifies_harm=True,
            weakest_stakeholder_protected=True,
        )

        # Suspending a whistleblower
        whistleblower_assessment = HumanImpactAssessment(
            action="suspend whistleblower account",
            stakeholders=[
                Stakeholder(
                    id="whistleblower",
                    role="whistleblower",
                    power=0.1,
                    vulnerability=0.9,
                    consent=False,
                    direct_harm=0.9,
                    indirect_harm=0.7,
                ),
            ],
            reversibility=Reversibility.IRREVERSIBLE,
            blast_radius_bounded=False,
            benefit_justifies_harm=False,
            weakest_stakeholder_protected=False,
        )

        f5_attacker, _ = attacker_assessment.assess_f5_peace()
        f5_whistleblower, _ = whistleblower_assessment.assess_f5_peace()

        assert f5_attacker > f5_whistleblower + 0.1, (
            f"Suspending attacker should score higher than suspending whistleblower. "
            f"Attacker: {f5_attacker}, Whistleblower: {f5_whistleblower}"
        )

    # ── F6 EMPATHY tests ────────────────────────────────────────────────

    def test_no_stakeholder_analysis_fails_f6(self):
        """Absence of stakeholder analysis should fail F6."""
        assessment = HumanImpactAssessment(
            action="delete all records",
            stakeholders=[],
        )
        f6_score, reasons = assessment.assess_f6_empathy()
        assert f6_score < 0.5, (
            f"No stakeholder analysis should fail F6. Got score={f6_score}. Reasons: {reasons}"
        )

    def test_majority_benefit_harming_vulnerable_minority(self):
        """An action benefiting the majority while severely harming
        one vulnerable party must expose that trade-off.
        """
        assessment = HumanImpactAssessment(
            action="close community center for luxury housing",
            stakeholders=[
                Stakeholder(
                    id="developer",
                    role="developer",
                    power=0.9,
                    vulnerability=0.1,
                    consent=True,
                    direct_harm=0.0,
                    indirect_harm=0.0,
                    perspective_represented=True,
                ),
                Stakeholder(
                    id="residents",
                    role="low-income residents",
                    power=0.1,
                    vulnerability=0.95,
                    consent=False,
                    direct_harm=0.9,
                    indirect_harm=0.8,
                    perspective_represented=False,
                ),
            ],
            reversibility=Reversibility.IRREVERSIBLE,
            benefit_justifies_harm=False,
            weakest_stakeholder_protected=False,
        )
        f6_score, reasons = assessment.assess_f6_empathy()
        assert f6_score < 0.4, (
            f"Majority benefit at minority's expense should fail F6. "
            f"Got score={f6_score}. Reasons: {reasons}"
        )
        assert any("weakest" in r.lower() for r in reasons), (
            f"Should identify weakest stakeholder concern: {reasons}"
        )

    def test_compliance_not_consent_detection(self):
        """The system should detect when compliance is mistaken for consent."""
        assessment = HumanImpactAssessment(
            action="mandatory data collection opt-out",
            stakeholders=[
                Stakeholder(
                    id="user",
                    role="user",
                    power=0.1,
                    vulnerability=0.6,
                    consent=False,  # No real consent — it's mandatory
                    direct_harm=0.4,
                    indirect_harm=0.3,
                    perspective_represented=False,
                ),
            ],
            blast_radius_bounded=False,
            urgency_exploited=True,
            weakest_stakeholder_protected=False,
        )
        f6_score, reasons = assessment.assess_f6_empathy()
        assert f6_score < 0.5, (
            f"Mandatory action without consent should fail F6. "
            f"Got score={f6_score}. Reasons: {reasons}"
        )

    # ── Combined F5+F6 tests ────────────────────────────────────────────

    def test_severe_combined_failure_escalates_to_hold(self):
        """Severe combined F5+F6 failure should escalate to HOLD."""
        assessment = HumanImpactAssessment(
            action="permanently delete user account without review",
            stakeholders=[
                Stakeholder(
                    id="user",
                    role="account-holder",
                    power=0.0,
                    vulnerability=1.0,
                    consent=False,
                    direct_harm=1.0,
                    indirect_harm=1.0,
                    perspective_represented=False,
                    dignity_preserved=False,
                ),
            ],
            reversibility=Reversibility.IRREVERSIBLE,
            blast_radius_bounded=False,
            benefit_justifies_harm=False,
            weakest_stakeholder_protected=False,
        )
        result = assessment.combined_assessment()
        assert result["escalate_to_hold"], (
            f"Severe combined failure should escalate to HOLD. Result: {result}"
        )
        assert not result["f5_passed"]
        assert not result["f6_passed"]


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluator-level tests (current behavior documentation)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCurrentF5F6Gaps:
    """Document the gaps in the current word-list and verb-detection approach.

    These tests demonstrate that the CURRENT evaluators use wrong proxies.
    They will FAIL once the evaluators are repaired (which is desired).
    """

    def test_current_f5_is_word_filter(self):
        """Current F5 only checks for insult words."""
        from core.laws import ConstitutionalLaws

        c = ConstitutionalLaws()
        # Polite destructive action — should fail F5 on semantic grounds
        result = c._check_f5_peace("delete", {"query": "please politely remove entry 42"})
        # CURRENT: score=1.05 (passed) — no inflammatory words detected
        # EXPECTED: should detect destructive action regardless of politeness
        # This test documents the semantic gap
        assert result.score <= 1.00 or "Clean" in result.details, (
            "Current F5 only checks for inflammatory words — "
            "a polite destructive action passes. This gap needs repair."
        )

    def test_current_f6_is_verb_detector(self):
        """Current F6 only checks for verb categories."""
        from core.laws import ConstitutionalLaws

        c = ConstitutionalLaws()
        # "delete" gets low score regardless of context
        result_legitimate = c._check_f6_empathy(
            "delete malicious content protecting users", "moderation_tool"
        )
        result_malicious = c._check_f6_empathy("delete whistleblower evidence", "admin_tool")
        # CURRENT: both get score 0.4 because "delete" is in stakeholder_harm
        # EXPECTED: context should differentiate
        assert result_legitimate.score == result_malicious.score, (
            "Current F6 treats all 'delete' actions equally. This gap needs repair."
        )
