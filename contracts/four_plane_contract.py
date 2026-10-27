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


def evaluate_four_planes(
    candidate: Any = None,
    auth_valid: bool = False,
    actor_id: str | None = None,
    evidence: Any = None,
    reversibility_level: str | None = None,
    action_tier: str = "standard",
    auth_reason: str | None = None,
    current_verdict: str | None = None,
) -> tuple[str, str, str, str, dict[str, Any]]:
    """Evaluate KX-009 Four Planes and remediation contract.

    Returns:
        (epistemic_state, authority_state, action_disposition, constitutional_verdict, remediation)
    """
    cand_dict: dict[str, Any] = {}
    if isinstance(candidate, dict):
        cand_dict = candidate
    elif isinstance(candidate, str):
        if candidate.strip().startswith("{") and candidate.strip().endswith("}"):
            try:
                import json as _json
                parsed = _json.loads(candidate)
                if isinstance(parsed, dict):
                    cand_dict = parsed
            except Exception:
                pass

    action_name = cand_dict.get("action") or cand_dict.get("intent") or (candidate if isinstance(candidate, str) else "") or "unspecified_action"
    action_mode = str(cand_dict.get("action_mode") or cand_dict.get("mode") or ("EXECUTE" if cand_dict.get("reversibility") else "OBSERVE")).upper()
    reversibility = str(cand_dict.get("reversibility") or reversibility_level or "REVERSIBLE").upper()

    # 1. Authority Plane
    is_irreversible = reversibility in ("TIER_3_IRREVERSIBLE", "IRREVERSIBLE") or action_tier in ("c4", "c5")
    if is_irreversible:
        authority_state = AuthorityState.HUMAN_REQUIRED
    elif auth_valid:
        authority_state = AuthorityState.AUTHORIZED
    else:
        if action_mode == "EXECUTE":
            authority_state = AuthorityState.DENIED
        else:
            authority_state = AuthorityState.OBSERVE_ONLY

    # 2. Epistemic Plane
    has_unknown = False
    has_refuted = False
    has_conflicting = False
    evidence_count = 0

    ev_items: list[Any] = []
    if isinstance(evidence, dict):
        ev_items = evidence.get("items", []) or [evidence]
    elif isinstance(evidence, list):
        ev_items = evidence

    for item in ev_items:
        if isinstance(item, dict):
            evidence_count += 1
            st = str(item.get("status", "")).upper()
            tag = str(item.get("tag", "")).upper()
            if "UNKNOWN" in st or "UNKNOWN" in tag:
                has_unknown = True
            if "REFUTED" in st:
                has_refuted = True
            if "CONFLICTING" in st:
                has_conflicting = True

    if has_refuted:
        epistemic_state = EpistemicState.REFUTED
    elif has_conflicting:
        epistemic_state = EpistemicState.CONFLICTING
    elif has_unknown or evidence_count == 0:
        epistemic_state = EpistemicState.INSUFFICIENT
    else:
        epistemic_state = EpistemicState.SUPPORTED

    # 3. Action Disposition Plane
    action_disposition = derive_action_disposition(
        epistemic_state,
        authority_state,
        is_mutation=(action_mode == "EXECUTE" or is_irreversible),
    )

    # 4. Constitutional Verdict & Remediation
    remediation_data: dict[str, Any] = {
        "blocking_conditions": [],
        "machine_resolvable": [],
        "human_required": [],
        "resume_contract": None,
    }

    if authority_state == AuthorityState.HUMAN_REQUIRED:
        verdict = ConstitutionalVerdict.HOLD
        remediation_data["blocking_conditions"] = ["Irreversible action requires human sovereign authority (F13)."]
        remediation_data["human_required"] = [
            {
                "decision": f"Authorize {action_name}",
                "why_machine_cannot_decide": "Irreversible action requires human authority (F13 sovereign)",
                "evidence_refs": [],
                "allowed_answers": ["APPROVE", "REJECT", "HOLD"],
            }
        ]
        remediation_data["resume_contract"] = {
            "rejudge_after": ["human_decision"],
        }
    elif action_mode == "OBSERVE":
        if not auth_valid:
            verdict = ConstitutionalVerdict.SABAR
            remediation_data["blocking_conditions"] = [auth_reason or "L11 AUTH: session required"]
            remediation_data["machine_resolvable"] = [
                {
                    "capability_id": "arif_init",
                    "target_ref": "capability://arifos/init",
                    "side_effect_class": "READ_ONLY",
                    "authority_required": "OBSERVE_ONLY",
                    "completion_evidence": ["session_id"],
                    "max_attempts": 3,
                }
            ]
            remediation_data["resume_contract"] = {
                "rejudge_after": ["arif_init"],
            }
        else:
            verdict = ConstitutionalVerdict.SABAR if epistemic_state == EpistemicState.INSUFFICIENT else ConstitutionalVerdict.SEAL
            if current_verdict:
                try:
                    verdict = ConstitutionalVerdict(current_verdict)
                except ValueError:
                    pass
    else:
        # EXECUTE mode
        if not auth_valid:
            verdict = ConstitutionalVerdict.HOLD
            remediation_data["blocking_conditions"] = [auth_reason or "L11 AUTH: unauthorized actor for mutation"]
            remediation_data["machine_resolvable"] = [
                {
                    "capability_id": "arif_init",
                    "target_ref": "capability://arifos/init",
                    "side_effect_class": "READ_ONLY",
                    "authority_required": "OBSERVE_ONLY",
                    "completion_evidence": ["session_id"],
                    "max_attempts": 3,
                }
            ]
            remediation_data["resume_contract"] = {
                "rejudge_after": ["arif_init"],
            }
        else:
            if current_verdict:
                try:
                    verdict = ConstitutionalVerdict(current_verdict)
                except ValueError:
                    verdict = ConstitutionalVerdict.HOLD
            else:
                verdict = ConstitutionalVerdict.SEAL if (epistemic_state == EpistemicState.SUPPORTED and authority_state == AuthorityState.AUTHORIZED) else ConstitutionalVerdict.HOLD

    return (
        epistemic_state.value,
        authority_state.value,
        action_disposition.value,
        verdict.value,
        remediation_data,
    )

