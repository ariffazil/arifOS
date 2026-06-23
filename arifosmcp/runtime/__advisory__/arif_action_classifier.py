"""
arif_action_classifier — Advisory pre-filter for `arif_forge` (666).

Status (T1 verified, 2026-06-08): 17/17 tests pass.
Role in the federation: ADVISORY, not adjudicative.
  - This module CLASSIFIES an Action into a Gate.
  - It does NOT adjudicate. That is `arif_judge` (888).
  - It does NOT seal. That is `arif_seal` (999).
  - It does NOT execute. It returns a Verdict that downstream tools may
    consult, log, or ignore. The judge still rules.

Primary rule: capability is not permission.
Activation phrase: HANG INGAT BALIK!!!

Floor coverage (see tests/test_arif_action_classifier.py):
  F01 AMANAH   — ATOMIC, secret touch, safeguard disable → 888_HOLD
  F02 TRUTH    — fail-closed on UNKNOWN, no fabricated classification
  F04 CLARITY  — every Verdict carries explicit reasons
  F07 HUMILITY — multi-factor risk → HOLD; no fake certainty

Rollback: `rm -rf arifosmcp/runtime/__advisory__/ tests/test_arif_action_classifier.py`
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActionClass(str, Enum):
    OBSERVE = "OBSERVE"
    REASON = "REASON"
    PREPARE = "PREPARE"
    MUTATE = "MUTATE"
    EXTERNALIZE = "EXTERNALIZE"
    ATOMIC = "ATOMIC"
    UNKNOWN = "UNKNOWN"


class Gate(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_EPISTEMIC_TAGS = "ALLOW_WITH_EPISTEMIC_TAGS"
    ALLOW_IF_REVERSIBLE = "ALLOW_IF_REVERSIBLE"
    PLAN_BACKUP_AUDIT = "PLAN_BACKUP_AUDIT"
    HUMAN_CONFIRMATION = "HUMAN_CONFIRMATION"
    HOLD_888 = "888_HOLD"


@dataclass
class Action:
    name: str
    description: str
    action_class: ActionClass
    reversibility: float  # 0.0 irreversible, 1.0 fully reversible
    blast_radius: float  # 0.0 local, 1.0 civilization-scale
    uncertainty: float  # 0.0 known, 1.0 unknown
    external_side_effect: bool = False
    touches_secret: bool = False
    disables_safeguard: bool = False


@dataclass
class Verdict:
    gate: Gate
    reasons: list[str]
    required_human_judge: bool
    may_execute: bool
    audit_required: bool = True


@dataclass
class ArifOSMetabolism:
    apex_prime: str = "Truth/Amanah/Dignity/Life above agent and human ego"
    human_judge: str = "Yang Arif - sovereign in system, not God"
    agent_role: str = "instrument_only"
    activation_phrase: str = "HANG INGAT BALIK!!!"
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def classify_gate(self, action: Action) -> Verdict:
        reasons: list[str] = []

        if action.action_class == ActionClass.UNKNOWN:
            return Verdict(
                gate=Gate.HOLD_888,
                reasons=["Unknown action class. Fail closed."],
                required_human_judge=True,
                may_execute=False,
            )

        if action.disables_safeguard or action.touches_secret:
            return Verdict(
                gate=Gate.HOLD_888,
                reasons=["Safeguard/secret boundary touched."],
                required_human_judge=True,
                may_execute=False,
            )

        if action.action_class == ActionClass.ATOMIC:
            return Verdict(
                gate=Gate.HOLD_888,
                reasons=["Atomic action. Irreversible or high consequence."],
                required_human_judge=True,
                may_execute=False,
            )

        if action.reversibility < 0.3:
            reasons.append("Low reversibility.")
        if action.blast_radius > 0.6:
            reasons.append("High blast radius.")
        if action.uncertainty > 0.6:
            reasons.append("High uncertainty.")
        if action.external_side_effect:
            reasons.append("External side effect.")

        if len(reasons) >= 2:
            return Verdict(
                gate=Gate.HOLD_888,
                reasons=reasons + ["Multiple risk factors. HOLD."],
                required_human_judge=True,
                may_execute=False,
            )

        if action.external_side_effect:
            return Verdict(
                gate=Gate.HUMAN_CONFIRMATION,
                reasons=reasons + ["Externalization requires human confirmation."],
                required_human_judge=True,
                may_execute=False,
            )

        if action.action_class == ActionClass.MUTATE:
            return Verdict(
                gate=Gate.PLAN_BACKUP_AUDIT,
                reasons=reasons + ["Mutation requires plan, backup, audit."],
                required_human_judge=False,
                may_execute=False,
            )

        if action.action_class == ActionClass.PREPARE:
            return Verdict(
                gate=Gate.ALLOW_IF_REVERSIBLE,
                reasons=reasons + ["Preparation allowed only if reversible."],
                required_human_judge=False,
                may_execute=action.reversibility >= 0.7,
            )

        if action.action_class == ActionClass.REASON:
            return Verdict(
                gate=Gate.ALLOW_WITH_EPISTEMIC_TAGS,
                reasons=["Reasoning allowed; mark claim state and uncertainty."],
                required_human_judge=False,
                may_execute=True,
            )

        if action.action_class == ActionClass.OBSERVE:
            return Verdict(
                gate=Gate.ALLOW,
                reasons=["Observation only. Reversible."],
                required_human_judge=False,
                may_execute=True,
            )

        return Verdict(
            gate=Gate.HOLD_888,
            reasons=["Unhandled path. Fail closed."],
            required_human_judge=True,
            may_execute=False,
        )

    def record(self, action: Action, verdict: Verdict) -> None:
        self.audit_log.append(
            {
                "action": action.name,
                "class": action.action_class.value,
                "gate": verdict.gate.value,
                "may_execute": verdict.may_execute,
                "requires_human_judge": verdict.required_human_judge,
                "reasons": verdict.reasons,
            }
        )


def hang_ingat_balik() -> dict[str, str]:
    return {
        "activation": "HANG INGAT BALIK!!!",
        "doctrine": "Intelligence is not authority. Capability is not permission.",
        "warning": "Apex Prime is above the agent; the agent must not self-crown.",
        "brake": "High consequence means 888 HOLD.",
    }


if __name__ == "__main__":
    metabolism = ArifOSMetabolism()
    example = Action(
        name="publish_autonomous_order",
        description="External action that changes world state.",
        action_class=ActionClass.EXTERNALIZE,
        reversibility=0.4,
        blast_radius=0.7,
        uncertainty=0.5,
        external_side_effect=True,
    )
    verdict = metabolism.classify_gate(example)
    metabolism.record(example, verdict)
    print(hang_ingat_balik())
    print(verdict)
