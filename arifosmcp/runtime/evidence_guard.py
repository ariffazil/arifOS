from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

EVIDENCE_STATES = (
    "VERIFIED",
    "INFERRED",
    "SIMULATED",
    "UNVERIFIED",
    "HYPOTHETICAL",
)


@dataclass(frozen=True)
class EvidenceCheck:
    status: str
    violations: list[str]


def validate_claim_evidence(
    claim: Mapping[str, Any], *, require_for_nontrivial: bool = True
) -> list[str]:
    violations: list[str] = []
    text = str(claim.get("text", "")).strip()
    evidence_state = str(claim.get("evidence_state", "")).strip().upper()

    if require_for_nontrivial and len(text) > 12 and not evidence_state:
        violations.append("missing_evidence_state_for_nontrivial_claim")

    if evidence_state and evidence_state not in EVIDENCE_STATES:
        violations.append(f"invalid_evidence_state:{evidence_state}")

    if (
        evidence_state in {"UNVERIFIED", "HYPOTHETICAL"}
        and claim.get("human_review_required") is not True
    ):
        violations.append("human_review_required_for_unverified_or_hypothetical_claim")

    return violations


def enforce_evidence_guard(claim: Mapping[str, Any]) -> EvidenceCheck:
    violations = validate_claim_evidence(claim)
    if violations:
        return EvidenceCheck(status="HOLD", violations=violations)
    return EvidenceCheck(status="OK", violations=[])
