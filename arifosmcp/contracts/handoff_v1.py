"""arifos.handoff.v1 — inter-organ semantic envelope.

One federation identity, distinct organ identities.
GEOX owns geology. WEALTH computes consequence. WELL reflects capacity.
arifOS judges. A-FORGE executes only after judgment + lease.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


SCHEMA_ID = "arifos.handoff.v1"

# What each organ owns — target must not revise source ownership
ORGAN_OWNERSHIP: dict[str, list[str]] = {
    "GEOX": ["geology", "earth_measurement", "prospect_physics", "well_evidence"],
    "WEALTH": ["capital_computation", "npv", "risk_scenario", "fiscal_model"],
    "WELL": ["human_readiness", "vitality_reflection", "dignity_boundary"],
    "ARIFOS": ["judgment", "authority", "session", "receipt"],
    "AAA": ["control_plane", "identity_routing"],
    "A-FORGE": ["execution_lease", "mutation_after_seal"],
    "AFORGE": ["execution_lease", "mutation_after_seal"],
}

ALLOWED_PATHS: set[tuple[str, str]] = {
    ("GEOX", "WEALTH"),
    ("WEALTH", "WELL"),
    ("WELL", "ARIFOS"),
    ("GEOX", "ARIFOS"),
    ("WEALTH", "ARIFOS"),
    ("ARIFOS", "A-FORGE"),
    ("ARIFOS", "AFORGE"),
}


class EpistemicState(StrEnum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INTERPRETED = "INTERPRETED"
    SPECULATIVE = "SPECULATIVE"
    PLAUSIBLE = "PLAUSIBLE"
    CLAIM = "CLAIM"


class SessionAuthority(StrEnum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    ADVISORY = "ADVISORY"
    COMPUTE = "COMPUTE"
    REFLECT_ONLY = "REFLECT_ONLY"
    JUDGE = "JUDGE"
    EXECUTE_LEASED = "EXECUTE_LEASED"


class Actor(BaseModel):
    id: str
    verified: bool = False


class Session(BaseModel):
    id: str
    authority: SessionAuthority
    parent_session_id: str | None = None


class Claim(BaseModel):
    summary: str
    epistemic_state: EpistemicState
    confidence: float = Field(ge=0.0, le=1.0)
    non_revision_bound: list[str] = Field(default_factory=list)


class EvidenceRef(BaseModel):
    ref: str
    type: str
    hash: str
    owner_organ: str | None = None


class Uncertainty(BaseModel):
    known: list[str] = Field(default_factory=list)
    unknown: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class Judgment(BaseModel):
    verdict: str  # SEAL | HOLD | SABAR | VOID
    reasons: list[str] = Field(default_factory=list)
    receipt_ref: str | None = None


class Ownership(BaseModel):
    source_owns: list[str] = Field(default_factory=list)
    target_must_not_revise: list[str] = Field(default_factory=list)
    aforge_requires: list[str] = Field(
        default_factory=lambda: ["judgment_evidence", "lease"]
    )


class HandoffV1(BaseModel):
    schema_: str = Field(default=SCHEMA_ID, alias="schema")
    handoff_id: str
    source_organ: str
    target_organ: str
    intent: str
    actor: Actor
    session: Session
    claim: Claim
    evidence: list[EvidenceRef]
    uncertainty: Uncertainty
    requested_output: str
    trace_id: str
    created_at: str
    expires_at: str | None = None
    judgment: Judgment | None = None
    ownership: Ownership | None = None

    model_config = {"populate_by_name": True}

    @field_validator("source_organ", "target_organ")
    @classmethod
    def normalize_organ(cls, v: str) -> str:
        u = v.strip().upper().replace("A-FORGE", "A-FORGE")
        if u in ("AFORGE", "A_FORGE"):
            return "A-FORGE"
        return u

    @model_validator(mode="after")
    def invariants(self) -> HandoffV1:
        if self.schema_ != SCHEMA_ID:
            raise ValueError(f"schema must be {SCHEMA_ID}")
        if self.source_organ == self.target_organ:
            raise ValueError("source_organ and target_organ must differ")
        path = (self.source_organ, self.target_organ)
        if path not in ALLOWED_PATHS:
            raise ValueError(
                f"handoff path not allowed: {self.source_organ}→{self.target_organ}"
            )
        if not self.evidence:
            # missing evidence is valid structure but must HOLD on admit
            pass
        if self.claim.confidence > 0.90 and self.claim.epistemic_state == EpistemicState.OBSERVED:
            # F7 humility — cap is advisory at model layer
            pass
        # Auto-bind ownership if missing
        if self.ownership is None:
            owns = list(ORGAN_OWNERSHIP.get(self.source_organ, []))
            self.ownership = Ownership(
                source_owns=owns,
                target_must_not_revise=owns,
                aforge_requires=["judgment_evidence", "lease"],
            )
        # GEOX evidence must not be revisable by WEALTH
        if self.source_organ == "GEOX" and self.target_organ == "WEALTH":
            bound = set(self.claim.non_revision_bound) | set(
                ORGAN_OWNERSHIP.get("GEOX", [])
            )
            self.claim.non_revision_bound = sorted(bound)
        return self


class HandoffAdmission(BaseModel):
    admitted: bool
    verdict: str  # SEAL path open | HOLD | VOID
    reasons: list[str] = Field(default_factory=list)
    handoff_id: str
    actor_id: str
    session_id: str
    trace_id: str
    receipt_ref: str | None = None


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_handoff(
    *,
    source_organ: str,
    target_organ: str,
    intent: str,
    actor_id: str,
    actor_verified: bool,
    session_id: str,
    authority: SessionAuthority,
    claim_summary: str,
    epistemic_state: EpistemicState,
    confidence: float,
    evidence: list[dict[str, str]],
    requested_output: str,
    trace_id: str | None = None,
    unknown: list[str] | None = None,
    parent_session_id: str | None = None,
) -> HandoffV1:
    return HandoffV1.model_validate(
        {
            "schema": SCHEMA_ID,
            "handoff_id": str(uuid.uuid4()),
            "source_organ": source_organ,
            "target_organ": target_organ,
            "intent": intent,
            "actor": {"id": actor_id, "verified": actor_verified},
            "session": {
                "id": session_id,
                "authority": authority.value,
                "parent_session_id": parent_session_id,
            },
            "claim": {
                "summary": claim_summary,
                "epistemic_state": epistemic_state.value,
                "confidence": confidence,
                "non_revision_bound": [],
            },
            "evidence": evidence,
            "uncertainty": {
                "known": [],
                "unknown": unknown or [],
                "conflicts": [],
            },
            "requested_output": requested_output,
            "trace_id": trace_id or uuid.uuid4().hex[:16],
            "created_at": now_iso(),
            "expires_at": (
                datetime.now(UTC) + timedelta(hours=24)
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )


def admit_handoff(h: HandoffV1) -> HandoffAdmission:
    """Admit or HOLD a handoff under ownership + evidence + authority rules."""
    reasons: list[str] = []

    if not h.evidence:
        reasons.append("missing_evidence")
    if not h.actor.id:
        reasons.append("missing_actor")
    if not h.session.id:
        reasons.append("missing_session")
    if not h.trace_id:
        reasons.append("missing_trace")

    # WEALTH must not revise GEOX ownership
    if h.source_organ == "GEOX" and h.target_organ == "WEALTH":
        if "geology" not in (h.claim.non_revision_bound or []):
            reasons.append("geology_not_bound_against_revision")

    # WELL receives minimum — capital private fields blocked by convention
    if h.target_organ == "WELL":
        for e in h.evidence:
            if e.type in ("private_biometric", "raw_capital_ledger"):
                reasons.append(f"well_forbidden_field:{e.type}")

    # A-FORGE cannot receive without prior judgment
    if h.target_organ in ("A-FORGE", "AFORGE"):
        if h.judgment is None or h.judgment.verdict != "SEAL":
            reasons.append("aforge_requires_seal_judgment")
        if h.session.authority != SessionAuthority.EXECUTE_LEASED:
            reasons.append("aforge_requires_execute_leased_authority")

    # Unverified actor + destructive intents → HOLD
    if not h.actor.verified and h.intent in (
        "execute_mutation",
        "deploy",
        "delete",
        "transfer",
    ):
        reasons.append("unverified_actor_destructive_intent")

    if reasons:
        return HandoffAdmission(
            admitted=False,
            verdict="HOLD",
            reasons=reasons,
            handoff_id=h.handoff_id,
            actor_id=h.actor.id,
            session_id=h.session.id,
            trace_id=h.trace_id,
            receipt_ref=None,
        )

    return HandoffAdmission(
        admitted=True,
        verdict="ADMIT",
        reasons=["schema_valid", "ownership_bound", "evidence_present"],
        handoff_id=h.handoff_id,
        actor_id=h.actor.id,
        session_id=h.session.id,
        trace_id=h.trace_id,
        receipt_ref=None,
    )


def wealth_must_not_overwrite_geology(
    incoming: HandoffV1, wealth_output: dict[str, Any]
) -> list[str]:
    """Return violations if WEALTH output mutates GEOX-owned keys."""
    violations: list[str] = []
    forbidden = set(incoming.claim.non_revision_bound) | set(
        ORGAN_OWNERSHIP.get("GEOX", [])
    )
    for key in forbidden:
        if key in wealth_output and wealth_output.get(key) is not None:
            # wealth may nest under capital_consequence only
            if key in ("geology", "earth_measurement", "prospect_physics", "well_evidence"):
                violations.append(f"wealth_revised_geox_field:{key}")
    return violations


def chain_continuity(
    envelopes: list[HandoffV1],
) -> dict[str, Any]:
    """Verify actor/session/trace continuity across a handoff chain."""
    if not envelopes:
        return {"ok": False, "reasons": ["empty_chain"]}
    actors = {e.actor.id for e in envelopes}
    sessions = {e.session.id for e in envelopes}
    traces = {e.trace_id for e in envelopes}
    reasons: list[str] = []
    if len(actors) != 1:
        reasons.append(f"actor_drift:{sorted(actors)}")
    # session may be identical OR documented child
    parent_ok = True
    root = envelopes[0].session.id
    for e in envelopes[1:]:
        if e.session.id != root and e.session.parent_session_id != root:
            parent_ok = False
            reasons.append(f"session_not_delegated:{e.session.id}")
    if len(traces) != 1:
        reasons.append(f"trace_broken:{sorted(traces)}")
    # epistemic tags present
    for e in envelopes:
        if not e.claim.epistemic_state:
            reasons.append(f"missing_epistemic:{e.handoff_id}")
    return {
        "ok": not reasons,
        "reasons": reasons,
        "actor_id": envelopes[0].actor.id if len(actors) == 1 else None,
        "session_id": root if parent_ok else None,
        "trace_id": envelopes[0].trace_id if len(traces) == 1 else None,
        "length": len(envelopes),
    }


def evidence_hash(payload: str | bytes) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def handoff_to_dict(h: HandoffV1) -> dict[str, Any]:
    return json.loads(h.model_dump_json(by_alias=True))
