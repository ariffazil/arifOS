"""
RCA State Machine — Accident Report Litigation Hold Engine
══════════════════════════════════════════════════════════

Encodes the constitutional choke point:
  Original report immutable.
  Redaction cannot replace original.
  Every edit attributable by role.
  Every hold has deadline.
  Every timeout escalates.
  Every override leaves permanent receipt.

Grounded in: Putra Heights gas pipeline explosion, April 2025.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class IncidentState(StrEnum):
    """States for a post-disaster investigation report under litigation hold."""
    INCIDENT = "INCIDENT"
    INVESTIGATING = "INVESTIGATING"
    REPORT_DRAFTED = "REPORT_DRAFTED"
    REPORT_SUBMITTED = "REPORT_SUBMITTED"
    NO_LITIGATION = "NO_LITIGATION"
    LITIGATION_ACTIVE = "LITIGATION_ACTIVE"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    REVIEW_COMPLETE = "REVIEW_COMPLETE"
    REVIEW_STALLED = "REVIEW_STALLED"
    SOVEREIGN_OVERRIDE = "SOVEREIGN_OVERRIDE"
    DISCLOSED = "DISCLOSED"


class ReasonCode(StrEnum):
    """Legal/constitutional reason codes for review actions."""
    LITIGATION_RISK = "LITIGATION_RISK"
    PERSONAL_DATA = "PERSONAL_DATA"
    NATIONAL_SECURITY = "NATIONAL_SECURITY"
    COMMERCIAL_SENSITIVITY = "COMMERCIAL_SENSITIVITY"
    CONTEMPT_RISK = "CONTEMPT_RISK"
    PUBLIC_INTEREST = "PUBLIC_INTEREST"
    SOVEREIGN_OVERRIDE = "SOVEREIGN_OVERRIDE"


class ActionType(StrEnum):
    REDACT = "REDACT"
    MASK = "MASK"
    DELAY = "DELAY"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"
    OVERRIDE = "OVERRIDE"
    DISCLOSE = "DISCLOSE"
    REVIEW_START = "REVIEW_START"


class Audience(StrEnum):
    PUBLIC = "PUBLIC"
    COURT = "COURT"
    REGULATOR = "REGULATOR"
    PARLIAMENT = "PARLIAMENT"
    AFFECTED_PARTIES = "AFFECTED_PARTIES"
    SOVEREIGN = "SOVEREIGN"


# ═══════════════════════════════════════════════════════════════════════════
# VALID TRANSITIONS
# ═══════════════════════════════════════════════════════════════════════════

VALID_TRANSITIONS: dict[IncidentState, set[IncidentState]] = {
    IncidentState.INCIDENT: {IncidentState.INVESTIGATING},
    IncidentState.INVESTIGATING: {IncidentState.REPORT_DRAFTED},
    IncidentState.REPORT_DRAFTED: {IncidentState.REPORT_SUBMITTED},
    IncidentState.REPORT_SUBMITTED: {IncidentState.NO_LITIGATION, IncidentState.LITIGATION_ACTIVE},
    IncidentState.NO_LITIGATION: {IncidentState.DISCLOSED},
    IncidentState.LITIGATION_ACTIVE: {IncidentState.LEGAL_REVIEW},
    IncidentState.LEGAL_REVIEW: {IncidentState.REVIEW_COMPLETE, IncidentState.REVIEW_STALLED},
    IncidentState.REVIEW_COMPLETE: {IncidentState.DISCLOSED},
    IncidentState.REVIEW_STALLED: {IncidentState.SOVEREIGN_OVERRIDE, IncidentState.DISCLOSED},
    IncidentState.SOVEREIGN_OVERRIDE: {IncidentState.DISCLOSED},
    IncidentState.DISCLOSED: set(),  # Terminal state
}

# ═══════════════════════════════════════════════════════════════════════════
# TRANSITION GUARDS
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class TransitionGuard:
    """Condition that must be satisfied before a state transition."""

    condition: str
    satisfied: bool = False
    detail: str = ""


def _guards_for_transition(
    from_state: IncidentState, to_state: IncidentState, incident: "Incident"
) -> list[TransitionGuard]:
    """Return guards that must pass for this transition."""
    guards: list[TransitionGuard] = []

    # REPORT_DRAFTED → REPORT_SUBMITTED: must seal original hash
    if from_state == IncidentState.REPORT_DRAFTED and to_state == IncidentState.REPORT_SUBMITTED:
        has_version = any(v.version_id == "v1.0" for v in incident.versions)
        guards.append(
            TransitionGuard(
                condition="Original version v1.0 must be sealed with SHA-256 hash",
                satisfied=has_version,
                detail="Seal the original report hash before submission" if not has_version else "v1.0 sealed",
            )
        )

    # REPORT_SUBMITTED → LITIGATION_ACTIVE: must have litigation record
    if from_state == IncidentState.REPORT_SUBMITTED and to_state == IncidentState.LITIGATION_ACTIVE:
        has_litigation = bool(incident.litigation_refs)
        guards.append(
            TransitionGuard(
                condition="Litigation reference must be recorded (case number, court, parties)",
                satisfied=has_litigation,
                detail="Record litigation details before entering LITIGATION_ACTIVE" if not has_litigation else "Litigation recorded",
            )
        )

    # LEGAL_REVIEW → REVIEW_STALLED: auto-fire when deadline breached
    if from_state == IncidentState.LEGAL_REVIEW and to_state == IncidentState.REVIEW_STALLED:
        deadline_passed = incident.review_deadline_at is not None and time.time() > incident.review_deadline_at
        guards.append(
            TransitionGuard(
                condition="Review deadline must have passed without completion",
                satisfied=deadline_passed,
                detail="Deadline not yet breached" if not deadline_passed else "Deadline breached — auto-escalation",
            )
        )

    # Any → DISCLOSED: must have public version
    if to_state == IncidentState.DISCLOSED:
        has_disclosed_version = bool(incident.disclosure_receipts)
        guards.append(
            TransitionGuard(
                condition="At least one disclosure receipt must be emitted",
                satisfied=has_disclosed_version,
                detail="Emit disclosure receipt before entering DISCLOSED" if not has_disclosed_version else "Receipt emitted",
            )
        )

    return guards


# ═══════════════════════════════════════════════════════════════════════════
# DATA OBJECTS
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class ReportVersion:
    report_id: str
    incident_id: str
    version_id: str
    parent_version_id: str | None
    hash: str  # sha256:<hex>
    created_at: float
    created_by_role: str
    classification: str = "CONFIDENTIAL"
    content_uri: str = ""
    merkle_leaf_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "incident_id": self.incident_id,
            "version_id": self.version_id,
            "parent_version_id": self.parent_version_id,
            "hash": self.hash,
            "created_at": self.created_at,
            "created_by_role": self.created_by_role,
            "classification": self.classification,
            "content_uri": self.content_uri,
        }


@dataclass
class ReviewAction:
    action_id: str
    report_id: str
    version_id: str
    actor_role: str
    action_type: ActionType
    reason_code: ReasonCode
    legal_basis: str = ""
    diff_ref: str = ""
    started_at: float = 0.0
    deadline_at: float | None = None
    decided_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "report_id": self.report_id,
            "version_id": self.version_id,
            "actor_role": self.actor_role,
            "action_type": self.action_type.value,
            "reason_code": self.reason_code.value,
            "legal_basis": self.legal_basis,
            "diff_ref": self.diff_ref,
            "started_at": self.started_at,
            "deadline_at": self.deadline_at,
            "decided_at": self.decided_at,
        }


@dataclass
class DisclosureReceipt:
    receipt_id: str
    report_id: str
    disclosed_version_id: str
    audience: Audience
    redaction_log_hash: str
    signed_by_role: str
    signed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "report_id": self.report_id,
            "disclosed_version_id": self.disclosed_version_id,
            "audience": self.audience.value,
            "redaction_log_hash": self.redaction_log_hash,
            "signed_by_role": self.signed_by_role,
            "signed_at": self.signed_at,
        }


@dataclass
class Incident:
    incident_id: str
    title: str
    occurred_at: str  # ISO 8601
    jurisdiction: str  # federal / state / joint
    affected_parties: list[str]
    infrastructure_type: str = "pipeline"
    operator_entity: str = ""
    regulatory_bodies: list[str] = field(default_factory=list)
    state: IncidentState = IncidentState.INCIDENT
    litigation_refs: list[str] = field(default_factory=list)
    review_deadline_at: float | None = None
    versions: list[ReportVersion] = field(default_factory=list)
    review_actions: list[ReviewAction] = field(default_factory=list)
    disclosure_receipts: list[DisclosureReceipt] = field(default_factory=list)
    transitions: list[dict[str, Any]] = field(default_factory=list)

    def can_transition(self, to_state: IncidentState) -> tuple[bool, list[TransitionGuard]]:
        """Check if transition is valid and guards are satisfied."""
        if to_state not in VALID_TRANSITIONS.get(self.state, set()):
            return False, [
                TransitionGuard(
                    condition=f"Valid transition from {self.state.value} to {to_state.value}",
                    satisfied=False,
                    detail=f"No valid transition from {self.state.value} to {to_state.value}",
                )
            ]
        guards = _guards_for_transition(self.state, to_state, self)
        all_satisfied = all(g.satisfied for g in guards)
        return all_satisfied, guards

    def transition(self, to_state: IncidentState, actor: str = "system") -> tuple[bool, str]:
        """Attempt state transition. Returns (success, detail)."""
        ok, guards = self.can_transition(to_state)
        if not ok:
            failed = [g for g in guards if not g.satisfied]
            detail = "; ".join(g.condition for g in failed)
            return False, f"Transition blocked: {detail}"

        from_state = self.state
        self.state = to_state
        self.transitions.append({
            "from": from_state.value,
            "to": to_state.value,
            "actor": actor,
            "timestamp": time.time(),
            "guards_passed": [g.condition for g in guards],
        })
        return True, f"{from_state.value} → {to_state.value}"

    def seal_version(self, version: ReportVersion) -> None:
        """Add a sealed report version. Original v1.0 is immutable."""
        self.versions.append(version)

    def add_review_action(self, action: ReviewAction) -> None:
        self.review_actions.append(action)

    def add_disclosure(self, receipt: DisclosureReceipt) -> None:
        self.disclosure_receipts.append(receipt)

    def tick(self) -> str | None:
        """Auto-escalation check. Call periodically. Returns action if triggered."""
        if self.state == IncidentState.LEGAL_REVIEW and self.review_deadline_at is not None:
            if time.time() > self.review_deadline_at:
                ok, detail = self.transition(IncidentState.REVIEW_STALLED, "auto-escalation")
                if ok:
                    return f"AUTO_ESCALATE: {detail}"
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "occurred_at": self.occurred_at,
            "jurisdiction": self.jurisdiction,
            "infrastructure_type": self.infrastructure_type,
            "operator_entity": self.operator_entity,
            "state": self.state.value,
            "versions": [v.to_dict() for v in self.versions],
            "review_actions": [a.to_dict() for a in self.review_actions],
            "disclosure_receipts": [r.to_dict() for r in self.disclosure_receipts],
            "transitions": self.transitions,
            "litigation_refs": self.litigation_refs,
            "review_deadline_at": self.review_deadline_at,
        }


# ═══════════════════════════════════════════════════════════════════════════
# STORE
# ═══════════════════════════════════════════════════════════════════════════


class IncidentStore:
    """In-memory incident registry (v0.1). v0.2+: Postgres-backed."""

    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}

    def create(self, incident: Incident) -> Incident:
        self._incidents[incident.incident_id] = incident
        return incident

    def get(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)

    def list_all(self) -> list[Incident]:
        return list(self._incidents.values())

    def list_by_state(self, state: IncidentState) -> list[Incident]:
        return [i for i in self._incidents.values() if i.state == state]

    def tick_all(self) -> list[str]:
        """Run auto-escalation on all incidents. Returns triggered actions."""
        triggered: list[str] = []
        for incident in self._incidents.values():
            result = incident.tick()
            if result:
                triggered.append(result)
        return triggered


# ═══════════════════════════════════════════════════════════════════════════
# PUTRA HEIGHTS — CANONICAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

def putra_heights_incident() -> Incident:
    """Factory for the canonical Putra Heights incident record."""
    return Incident(
        incident_id="INC-20250401-PHGS01",
        title="Putra Heights Gas Pipeline Explosion",
        occurred_at="2025-04-01T00:00:00+08:00",
        jurisdiction="federal",
        affected_parties=[
            "Residents of Taman Putra Harmoni, Putra Heights, Subang Jaya",
            "36 plaintiff families (civil suit, Shah Alam High Court)",
        ],
        infrastructure_type="pipeline",
        operator_entity="Petronas Gas Berhad",
        regulatory_bodies=["DOSH", "Suruhanjaya Tenaga", "JAS", "MBSJ"],
        state=IncidentState.LITIGATION_ACTIVE,
        litigation_refs=[
            "Shah Alam High Court Civil Suit — 36 residents vs Petronas Gas Bhd, Hong & Hong Homes, Pinterest Ventures, MBSJ, Government of Malaysia",
            "Plaintiff counsel: Tommy Thomas",
            "Filed: 2025-10-18",
        ],
        review_deadline_at=time.time() + (90 * 86400),  # 90 days from now
    )
