"""
arifos/contracts/four_plane_contract.py — KX-009 Four-Plane Decision Vocabulary (F13 RATIFIED 2026-10-27)

Rule 1: epistemic_state describes the claim.
Rule 2: authority_state describes the actor.
Rule 3: action_disposition describes what may be done next.
Rule 4: constitutional_verdict governs state transition.

Separation Invariants:
- epistemic_state NEVER grants authority.
- authority_state NEVER determines truth.
- action_disposition is derived from explicit policy rules.
- constitutional_verdict governs transition; executor consumes permitted transition but does not create it.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class EpistemicState(str, Enum):
    """Plane 1: Truth status of the claim or proposition."""
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT = "INSUFFICIENT"
    CONFLICTING = "CONFLICTING"
    REFUTED = "REFUTED"
    NOT_VERIFIABLE = "NOT_VERIFIABLE"


class AuthorityState(str, Enum):
    """Plane 2: Cryptographic and institutional authorization of the actor."""
    AUTHORIZED = "AUTHORIZED"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    DENIED = "DENIED"
    HUMAN_REQUIRED = "HUMAN_REQUIRED"


class ActionDisposition(str, Enum):
    """Plane 3: Recommended or permitted operational next step."""
    REPORT_ONLY = "REPORT_ONLY"
    GATHER_EVIDENCE = "GATHER_EVIDENCE"
    REQUEST_AUTHORITY = "REQUEST_AUTHORITY"
    ELIGIBLE_FOR_EXECUTION = "ELIGIBLE_FOR_EXECUTION"
    BLOCKED = "BLOCKED"


class ConstitutionalVerdict(str, Enum):
    """Plane 4: Constitutional arbitration verdict governing transition."""
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"


class MachineResolvableItem(BaseModel):
    """Typed machine remediation requirement."""
    capability_id: str
    target_ref: str
    side_effect_class: str = Field(default="READ_ONLY", pattern="^(READ_ONLY|MUTATE)$")
    authority_required: str
    completion_evidence: list[str] = Field(default_factory=list)
    max_attempts: int = Field(default=1, ge=1)
    expires_at: str | None = None
    state_fingerprint: str | None = None


class HumanRequiredItem(BaseModel):
    """Typed human intervention requirement."""
    decision: str
    why_machine_cannot_decide: str
    evidence_refs: list[str] = Field(default_factory=list)
    allowed_answers: list[str] = Field(default_factory=list)


class ResumeContract(BaseModel):
    """Typed resume contract for rejudgment."""
    rejudge_after: list[str] = Field(default_factory=list)
    expires_at: str | None = None
    state_fingerprint: str | None = None


class RemediationContract(BaseModel):
    """Typed remediation contract schema."""
    blocking_conditions: list[str] = Field(default_factory=list)
    machine_resolvable: list[MachineResolvableItem] = Field(default_factory=list)
    human_required: list[HumanRequiredItem] = Field(default_factory=list)
    resume_contract: ResumeContract | None = None


class GovernedDecision(BaseModel):
    """Four-plane unified decision envelope."""
    epistemic_state: EpistemicState
    authority_state: AuthorityState
    action_disposition: ActionDisposition
    constitutional_verdict: ConstitutionalVerdict
    remediation: RemediationContract | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def derive_action_disposition(
    epistemic: EpistemicState,
    authority: AuthorityState,
    is_mutation: bool = False,
) -> ActionDisposition:
    """Canonical derivation of action disposition from epistemic and authority planes.

    Deterministic policy rules:
    - SUPPORTED + OBSERVE_ONLY cannot become ELIGIBLE_FOR_EXECUTION (remains REPORT_ONLY or REQUEST_AUTHORITY).
    - AUTHORIZED + INSUFFICIENT cannot become ELIGIBLE_FOR_EXECUTION (remains GATHER_EVIDENCE).
    - SUPPORTED + AUTHORIZED may become ELIGIBLE_FOR_EXECUTION.
    - DENIED or REFUTED yields BLOCKED.
    """
    if authority == AuthorityState.DENIED or epistemic == EpistemicState.REFUTED:
        return ActionDisposition.BLOCKED

    if authority == AuthorityState.OBSERVE_ONLY:
        if epistemic == EpistemicState.SUPPORTED:
            return ActionDisposition.REPORT_ONLY
        elif epistemic in (EpistemicState.INSUFFICIENT, EpistemicState.PARTIALLY_SUPPORTED):
            return ActionDisposition.GATHER_EVIDENCE
        return ActionDisposition.REPORT_ONLY

    if authority == AuthorityState.AUTHORIZED:
        if epistemic == EpistemicState.SUPPORTED:
            return ActionDisposition.ELIGIBLE_FOR_EXECUTION
        elif epistemic in (EpistemicState.INSUFFICIENT, EpistemicState.PARTIALLY_SUPPORTED):
            return ActionDisposition.GATHER_EVIDENCE
        elif epistemic == EpistemicState.CONFLICTING:
            return ActionDisposition.BLOCKED
        return ActionDisposition.GATHER_EVIDENCE

    if authority == AuthorityState.HUMAN_REQUIRED:
        return ActionDisposition.REQUEST_AUTHORITY

    return ActionDisposition.BLOCKED
