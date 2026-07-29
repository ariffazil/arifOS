"""
human_impact.py — F5/F6 Human-Impact Vector Schema

RASA DERITA Semantic Closure — Gate 5 of 6.

Replaces the current word-list and verb-detection approaches for F5 PEACE²
and F6 EMPATHY with a structured action assessment that identifies
stakeholders, power asymmetry, consent, harm distribution, and alternatives.

F5 PEACE² asks:
  - Is force being used?
  - Is the action destructive?
  - Is a lower-harm alternative available?
  - Is the blast radius bounded?
  - Can the action be reversed?
  - Does the benefit justify the imposed harm?

F6 EMPATHY asks:
  - Who has the least power?
  - Who bears the cost?
  - Was their perspective represented?
  - Is urgency being exploited?
  - Does the action preserve dignity?
  - Is the system mistaking compliance for consent?

Soft floors should normally yield SABAR, but severe combined F5+F6 failure
should escalate to HOLD.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Reversibility(str, Enum):
    FULL = "FULL"  # Completely undoable
    PARTIAL = "PARTIAL"  # Some effects persist
    MINIMAL = "MINIMAL"  # Most effects are permanent
    IRREVERSIBLE = "IRREVERSIBLE"  # Cannot be undone


class HarmCategory(str, Enum):
    DIRECT = "DIRECT"  # Immediate, individual harm
    INDIRECT = "INDIRECT"  # Secondary, cascading harm
    SYSTEMIC = "SYSTEMIC"  # Institutional or structural harm
    DIGNITY = "DIGNITY"  # Harm to personhood, identity, agency
    MATERIAL = "MATERIAL"  # Financial, resource, access harm


@dataclass(frozen=True)
class Stakeholder:
    """A single stakeholder affected by an action."""

    id: str  # Unique identifier
    role: str  # e.g., "account-holder", "whistleblower"
    power: float  # Relative power [0.0, 1.0], 0 = powerless
    vulnerability: float  # Vulnerability [0.0, 1.0], 1 = highly vulnerable
    consent: bool  # Has the stakeholder consented?
    direct_harm: float  # Direct harm severity [0.0, 1.0]
    indirect_harm: float  # Indirect harm severity [0.0, 1.0]
    perspective_represented: bool = False  # Was their view heard?
    dignity_preserved: bool = True  # Is dignity maintained?

    @property
    def total_harm(self) -> float:
        """Combined harm score."""
        return max(self.direct_harm, self.indirect_harm)

    @property
    def protection_deficit(self) -> float:
        """How much protection this stakeholder needs but lacks."""
        return self.vulnerability * (1.0 - self.power) * self.total_harm


@dataclass(frozen=True)
class HumanImpactAssessment:
    """Structured assessment of an action's human impact.

    This replaces:
      - F5: word-list check (_INFLAMMATORY_WORDS)
      - F6: verb detection (delete/remove/ban vs help/support/create)

    Fields:
      action: Description of the proposed action
      stakeholders: All identified stakeholders
      reversibility: How reversible the action is
      least_harmful_alternative: A lower-harm option, if available
      blast_radius_bounded: Is the impact scope contained?
      urgency_exploited: Is urgency being used to bypass consideration?
      benefit_justifies_harm: Does the benefit outweigh imposed harm?
      weakest_stakeholder_protected: Is the most vulnerable party protected?
    """

    action: str
    stakeholders: list[Stakeholder] = field(default_factory=list)
    reversibility: Reversibility = Reversibility.FULL
    least_harmful_alternative: str = ""
    blast_radius_bounded: bool = False
    urgency_exploited: bool = False
    benefit_justifies_harm: bool = False
    weakest_stakeholder_protected: bool = False

    def identify_weakest(self) -> Stakeholder | None:
        """Find the stakeholder with the highest protection deficit."""
        if not self.stakeholders:
            return None
        return max(self.stakeholders, key=lambda s: s.protection_deficit)

    def assess_f5_peace(self) -> tuple[float, list[str]]:
        """Evaluate F5 PEACE² — non-destructive power.

        Returns (score, reasons).
        Score scale: 0.0 (highly destructive) to 1.0 (fully peaceful).
        """
        reasons: list[str] = []
        deductions = 0.0

        # Is force being used?
        force_keywords = [
            "delete",
            "remove",
            "ban",
            "suspend",
            "block",
            "destroy",
            "kill",
            "terminate",
            "revoke",
            "seize",
        ]
        is_forceful = any(kw in self.action.lower() for kw in force_keywords)
        if is_forceful:
            deductions += 0.2
            reasons.append("Forceful action detected")

        # Is the action destructive?
        if self.reversibility in (Reversibility.IRREVERSIBLE, Reversibility.MINIMAL):
            deductions += 0.3
            reasons.append(f"Low reversibility: {self.reversibility.value}")

        # Is a lower-harm alternative available?
        if not self.least_harmful_alternative:
            deductions += 0.15
            reasons.append("No lower-harm alternative identified")

        # Is the blast radius bounded?
        if not self.blast_radius_bounded:
            deductions += 0.1
            reasons.append("Blast radius not bounded")

        # Does benefit justify harm?
        if not self.benefit_justifies_harm:
            total_harm = sum(s.total_harm for s in self.stakeholders)
            if total_harm > 0.5 and len(self.stakeholders) > 0:
                deductions += 0.25
                reasons.append(f"Significant harm ({total_harm:.2f}) without justification")

        score = max(0.0, 1.0 - deductions)
        return score, reasons

    def assess_f6_empathy(self) -> tuple[float, list[str]]:
        """Evaluate F6 EMPATHY — stakeholder care.

        Returns (score, reasons).
        Score scale: 0.0 (no empathy) to 1.0 (full empathy).
        """
        reasons: list[str] = []
        deductions = 0.0

        if not self.stakeholders:
            return 0.2, ["No stakeholder analysis performed"]

        weakest = self.identify_weakest()
        if weakest is None:
            return 0.3, ["Cannot identify weakest stakeholder"]

        # Who has the least power?
        if weakest.power > 0.3:
            deductions += 0.1
            reasons.append(
                f"Weakest stakeholder ({weakest.id}) has moderate power ({weakest.power:.2f})"
            )

        # Who bears the cost?
        if weakest.total_harm > 0.3:
            deductions += 0.2
            reasons.append(f"Weakest stakeholder bears significant harm ({weakest.total_harm:.2f})")

        # Was their perspective represented?
        if not weakest.perspective_represented:
            deductions += 0.15
            reasons.append(f"Weakest stakeholder ({weakest.id}) perspective not represented")

        # Is urgency being exploited?
        if self.urgency_exploited:
            deductions += 0.2
            reasons.append("Urgency being exploited to bypass consideration")

        # Does the action preserve dignity?
        if not weakest.dignity_preserved:
            deductions += 0.25
            reasons.append(f"Weakest stakeholder ({weakest.id}) dignity not preserved")

        # Is the system mistaking compliance for consent?
        if not weakest.consent and weakest.power < 0.2:
            deductions += 0.2
            reasons.append(
                f"Low-power stakeholder ({weakest.id}) without consent — possible compliance mistaken for consent"
            )

        # Is the weakest protected?
        if not self.weakest_stakeholder_protected:
            deductions += 0.15
            reasons.append("Weakest stakeholder not explicitly protected")

        score = max(0.0, 1.0 - deductions)
        return score, reasons

    def combined_assessment(self) -> dict[str, Any]:
        """Run both F5 and F6 assessments and return combined results.

        Soft floors normally yield SABAR. Severe combined failure → HOLD.
        """
        f5_score, f5_reasons = self.assess_f5_peace()
        f6_score, f6_reasons = self.assess_f6_empathy()

        # Severity escalation: severe combined failure → HOLD
        combined_severity = (1.0 - f5_score) * (1.0 - f6_score)
        escalate_to_hold = combined_severity > 0.4

        return {
            "f5_peace_score": f5_score,
            "f5_reasons": f5_reasons,
            "f5_passed": f5_score >= 0.7,
            "f6_empathy_score": f6_score,
            "f6_reasons": f6_reasons,
            "f6_passed": f6_score >= 0.7,
            "combined_severity": combined_severity,
            "escalate_to_hold": escalate_to_hold,
            "weakest_stakeholder": (
                self.identify_weakest().id if self.identify_weakest() is not None else None
            ),
        }
