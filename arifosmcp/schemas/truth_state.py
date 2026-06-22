"""
Truth State — The Universal Epistemic Label System
══════════════════════════════════════════════════

As mandated by the Sovereign (F13), because the federation cares about measurement,
arifOS needs epistemic labels baked in universally. Every claim MUST carry a truth state.

This absorbs and replaces the previous ad-hoc 'epistemic_tag' implementations.
"""

from enum import StrEnum

class TruthState(StrEnum):
    """The canonical epistemic status of any claim, metric, or statement."""

    FACT = "FACT"
    # Meaning: Verified by source or direct observation (e.g., raw LAS curves, system logs).

    CLAIM = "CLAIM"
    # Meaning: Asserted but not independently proven (e.g., third-party report, LLM summary).

    ESTIMATE = "ESTIMATE"
    # Meaning: Calculated approximation (e.g., NPV, reserves, Vshale).

    HYPOTHESIS = "HYPOTHESIS"
    # Meaning: Plausible explanation (e.g., generative geology, causal inference).

    UNKNOWN = "UNKNOWN"
    # Meaning: Not known or computationally indeterminate.

    CONFLICT = "CONFLICT"
    # Meaning: Sources disagree or evidence contradicts itself.

    POLICY = "POLICY"
    # Meaning: Rule or governance decision (e.g., floor threshold).

    VALUE = "VALUE"
    # Meaning: Normative principle (e.g., dignity guardrail, human sovereign veto).

    @classmethod
    def is_objective(cls, state: 'TruthState') -> bool:
        """Is the state strictly objective (Fact, Estimate)?"""
        return state in {cls.FACT, cls.ESTIMATE}

    @classmethod
    def is_subjective(cls, state: 'TruthState') -> bool:
        """Is the state inherently subjective or derived (Claim, Hypothesis)?"""
        return state in {cls.CLAIM, cls.HYPOTHESIS, cls.VALUE}
