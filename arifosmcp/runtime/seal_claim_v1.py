"""
seal_claim_v1.py — PROPOSED additive schema for VAULT SEAL events (v3, not landed)

Status: DRAFT / NOT WIRED. No production import. Isolated verification only.
Authorization: F13 PARTIAL (2026-10-28) — additive + backward-compatible; landing = HOLD.

Revision 2 (2026-10-28) — block conditions from 555-ASI fresh-context verification
(session ses_e81bc9482ffeo422xD2IfP3UzF) are closed or explicitly declared:
  [B1] VERIFIED/FALSIFIED no longer self-assertable: requires verification_witness_class=
       store_resolved (asserted is the default and is rejected), and independence is compared
       casefolded+stripped. Residual: a caller can still claim store_resolved — that is an
       auditable lie (F9), not a silent one. Adapter MUST resolve the id before setting it.
  [B2] actor_B blocklist normalised (casefold+strip, all separator variants).
  [B3] confidence_semantics must equal the declared contract token (was vacuous);
       confidence_actor must be ident-shaped; identity remains caller-asserted by design and
       that non-guarantee is written down instead of implied.
  [B4] claim_id = hash of the normalised proposition only → stable across sessions and actors.
       It identifies the CLAIM, not the event; two events asserting one claim share an id
       (that is the point: later verification must attach to the proposition).

Why (failure class, named): a SEAL records that an event happened, not what was claimed.
Without claim text the store cannot produce a false-SEAL numerator, so gate quality is
unmeasurable and every "verified" reading is activity, not evidence.

Sovereign rules implemented verbatim: 1 claim_id stability · 2 confidence earnable only ·
3 actor_B never populates confidence · 4 SEAL ≠ VERIFIED · 5 VERIFIED needs a separate
verification event / independently witnessed outcome · 6 history stays EVENT_ONLY ·
7 no backfill by inference · 8 unknown stays null · 9 no new ledger · 10 no production mutation.

Fields marked [EXT] are not in the sovereign field list; they exist only because rule 5 cannot
be proven or audited without a place to record the verification event, its witness and its
provenance class. Droppable on request.
"""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ── declared confidence contract (rule 2) ───────────────────────────────────────
CONFIDENCE_MIN = 0.0
CONFIDENCE_MAX = 1.0
CONFIDENCE_SEMANTICS_VERSION = "v1:P(claim_supported|evidence_refs,pre_outcome,0-1)"
CONFIDENCE_SEMANTICS_CONTRACT = (
    "Claim confidence is P(claim_text is supported by evidence_refs), declared on 0.0-1.0, "
    "produced before the outcome was observed, by an identified actor. Values that arrive "
    "after the outcome are not predictions and must not be written."
)

# identity shapes that may be recorded as a producing actor. Caller-asserted; not verified here.
_ACTOR_RE = re.compile(r"^[a-z0-9][a-z0-9:._/+\-]{1,63}$")
_WS = re.compile(r"\s+")

# rule 3: these are judge INPUTS, never a calibrating authority over the claim.
_RESERVED_CONFIDENCE_ACTORS = frozenset(
    {
        "actor_b",
        "actor-b",
        "arif_judge:actor_b",
        "arif_judge:actor-b",
        "judge.actor_b",
        "judge.actor-b",
    }
)


def _norm(value: str | None) -> str:
    return (value or "").strip().casefold()


def normalise_proposition(text: str) -> str:
    """Case + whitespace insensitive form used for claim identity."""
    return _WS.sub(" ", text.strip().casefold())


def derive_claim_id(claim_text: str) -> str:
    """Rule 1: stable across sessions, actors and re-publication of the same proposition."""
    return (
        "clm-"
        + hashlib.sha256(normalise_proposition(claim_text).encode()).hexdigest()[:16]
    )


class VerificationStatus(str, Enum):
    EVENT_ONLY = "EVENT_ONLY"
    CLAIM_RECORDED = "CLAIM_RECORDED"
    VERIFIED = "VERIFIED"
    FALSIFIED = "FALSIFIED"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"


class SealEventV3(BaseModel):
    """Additive successor shape for a VAULT seal event.

    Superset of runtime.vault_postgres.VaultEvent + core.vault_receipt.VaultReceipt:
    every legacy field is optional here so a v2 row deserialises without loss.
    """

    # ── legacy identity/shape (unchanged semantics) ────────────────────────────
    event_id: str = ""
    event_type: str = "vault_seal"
    session_id: str | None = None
    actor_id: str | None = None
    stage: str = ""
    verdict: str = "SEAL"
    payload: dict[str, Any] = Field(default_factory=dict)
    risk_tier: str = "medium"
    sealed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ── proposed additive claim fields (rules 1, 2, 4, 5) ──────────────────────
    claim_id: str | None = None
    claim_text: str | None = None
    confidence: float | None = Field(default=None, ge=CONFIDENCE_MIN, le=CONFIDENCE_MAX)
    confidence_actor: str | None = None
    confidence_semantics: str | None = None
    evidence_refs: list[str] | None = None
    verification_status: VerificationStatus = VerificationStatus.EVENT_ONLY

    # [EXT] rule 2 ordering + rule 5 provability
    confidence_produced_at: datetime | None = None
    verification_event_id: str | None = None
    verified_by: str | None = None
    verification_witness_class: Literal["asserted", "store_resolved"] = "asserted"
    outcome_observed_at: datetime | None = None

    @field_validator("confidence", mode="before")
    @classmethod
    def _no_bools(cls, v: Any) -> Any:
        # bool is an int subclass: True would silently become 1.0 = fake certainty
        if isinstance(v, bool):
            raise ValueError("confidence must be a float, not a bool")
        return v

    @model_validator(mode="after")
    def _enforce_claim_rules(self) -> "SealEventV3":
        # ── normalise claim_text: missing / "" / whitespace are all "no claim" ──
        if self.claim_text is not None and not self.claim_text.strip():
            self.claim_text = None
        if self.claim_text is not None:
            self.claim_text = self.claim_text.strip()
        has_claim = bool(self.claim_text)

        # rule 1 + binding rule: no claim → EVENT_ONLY, no claim_id, no claim status
        if not has_claim:
            if self.claim_id is not None:
                raise ValueError(
                    "claim_id set without claim_text — a claim_id must identify a claim "
                    "(binding rule: SEAL without substantive claim_text is EVENT_ONLY)"
                )
            if self.verification_status not in (
                VerificationStatus.EVENT_ONLY,
                VerificationStatus.OUTCOME_UNKNOWN,
            ):
                raise ValueError(
                    f"verification_status={self.verification_status.value} requires claim_text; "
                    "an event with no claim is EVENT_ONLY (it cannot be verified or falsified)"
                )
        else:
            # stable id from the proposition; caller-supplied ids must agree with it
            expected = derive_claim_id(self.claim_text)
            if self.claim_id is None:
                self.claim_id = expected
            elif self.claim_id != expected:
                raise ValueError(
                    "claim_id does not match the proposition hash — supply the derived id "
                    f"({expected}) or omit it; a free-form id breaks later attachment (rule 1)"
                )
            if self.verification_status is VerificationStatus.EVENT_ONLY:
                # a substantive claim is at least recorded; EVENT_ONLY would understate it
                self.verification_status = VerificationStatus.CLAIM_RECORDED

        # rule 2 + 3: confidence must be earnable, never assumed
        if self.confidence is not None:
            if isinstance(self.confidence, bool):
                raise ValueError("confidence must be a float, not a bool")
            missing = [
                name
                for name, val in (
                    ("confidence_actor", self.confidence_actor),
                    ("confidence_semantics", self.confidence_semantics),
                    ("confidence_produced_at", self.confidence_produced_at),
                )
                if val in (None, "")
            ]
            if missing:
                raise ValueError(
                    "confidence requires "
                    + ", ".join(missing)
                    + " (rule 2: actor, semantics, "
                    "and pre-outcome production time must be declared)"
                )
            if _norm(self.confidence_actor) in _RESERVED_CONFIDENCE_ACTORS:
                raise ValueError(
                    "confidence_actor may not be an actor_B input — rule 3: actor_B must not "
                    "silently populate claim confidence"
                )
            if not _ACTOR_RE.match(_norm(self.confidence_actor)):
                raise ValueError(
                    "confidence_actor is not an actor id (lowercase ident, 2-64 chars) — "
                    "rule 2 requires the producing actor to be identifiable"
                )
            if _norm(self.confidence_semantics) != _norm(CONFIDENCE_SEMANTICS_VERSION):
                raise ValueError(
                    f"confidence_semantics must declare the contract token "
                    f"{CONFIDENCE_SEMANTICS_VERSION!r} (rule 2: semantics declared, not narrated)"
                )
            if not has_claim:
                raise ValueError("confidence without claim_text has no referent")
            if (
                self.outcome_observed_at
                and self.confidence_produced_at >= self.outcome_observed_at
            ):
                raise ValueError(
                    "confidence produced at/after outcome observation — not a prediction "
                    "(rule 2: value must be produced before the outcome is known)"
                )
        elif any(
            (
                self.confidence_actor,
                self.confidence_semantics,
                self.confidence_produced_at,
            )
        ):
            raise ValueError(
                "confidence metadata declared with null confidence — either supply a value "
                "with actor/semantics/time, or drop the metadata (null stays null, rule 8)"
            )

        # rule 4 + 5: SEAL is not VERIFIED; VERIFIED needs a separate, witnessed verification
        if self.verification_status in (
            VerificationStatus.VERIFIED,
            VerificationStatus.FALSIFIED,
        ):
            if self.verification_witness_class != "store_resolved":
                raise ValueError(
                    "VERIFIED/FALSIFIED requires verification_witness_class=store_resolved — an "
                    "asserted id is a claim about a witness, not a witness (rule 5)"
                )
            if not (self.verification_event_id or self.outcome_observed_at):
                raise ValueError(
                    "VERIFIED/FALSIFIED requires a separate verification event "
                    "(verification_event_id) or an independently observed outcome "
                    "(outcome_observed_at) — the seal verdict itself is not evidence"
                )
            if not self.verified_by:
                raise ValueError(
                    "VERIFIED/FALSIFIED requires verified_by (who witnessed)"
                )
            if self.actor_id and _norm(self.verified_by) == _norm(self.actor_id):
                raise ValueError(
                    "verified_by == actor_id — self-verification; author is not witness "
                    "(rule 5: independently witnessed outcome)"
                )
        elif self.verification_witness_class == "store_resolved":
            raise ValueError(
                "verification_witness_class=store_resolved only applies to VERIFIED/FALSIFIED"
            )
        return self

    # ── adapters: additive only, unknown stays null (rule 8) ────────────────────
    def to_supabase_row(self) -> dict[str, Any]:
        """Columns for arifosmcp_vault_seals. confidence is NOT coalesced to 1.0/0.0."""
        return {
            "seal_id": self.event_id or None,
            "agent_id": self.actor_id,
            "action": self.event_type,
            "payload": self.payload,
            "epoch": self.sealed_at.isoformat(),
            # F7: unknown confidence stays null. The live writer hardcodes 1.0 (SCHEMA-AUDIT §D.3)
            "confidence": self.confidence,
            "claim_id": self.claim_id,
            "claim_text": self.claim_text,
            "confidence_actor": self.confidence_actor,
            "confidence_semantics": self.confidence_semantics,
            "evidence_refs": self.evidence_refs,
            "verification_status": self.verification_status.value,
        }

    def to_vault_events_row(self) -> dict[str, Any]:
        """Local Postgres witness mirror (`vault_events`) — same claim columns, same nulls.

        Without this the local witness store cannot witness claims; the diff in
        SCHEMA-AUDIT §C is scoped to both tables for that reason.
        """
        row = self.to_supabase_row()
        row["prev_hash"] = None
        row["chain_hash"] = None
        return row

    def to_legacy_vault_event(self) -> dict[str, Any]:
        """Downgrade for readers that only know the v2 shape (claim fields dropped, not faked)."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "stage": self.stage,
            "verdict": self.verdict,
            "payload": self.payload,
            "risk_tier": self.risk_tier,
            "sealed_at": self.sealed_at.isoformat(),
        }


def apply_judge_actor_b(event: SealEventV3, actor_b: float | None) -> SealEventV3:
    """Judgement-time confidence is NOT claim confidence (rule 3).

    `actor_B` is the judge's Brier input about the *actor*, sampled at judgement time. Copying
    it into claim confidence would manufacture a calibrated number that was never produced
    pre-outcome by a named calibrating actor. This function exists so the illegal copy has one
    obvious place to be refused instead of happening silently in an adapter, and so a test can
    prove the refusal.
    """
    if actor_b is None:
        return event
    raise ValueError(
        "actor_B cannot populate claim confidence (rule 3). Record it in payload['judge_actor_b'] "
        "if it must be kept; claim confidence stays null until an identified actor declares "
        "semantics and a pre-outcome timestamp."
    )


def classify_legacy_event(raw: dict[str, Any]) -> SealEventV3:
    """Rules 6/7: history stays valid as EVENT_ONLY. No inference, no backfill, no crash.

    A dirty legacy row that carries claim_text/confidence/VERIFIED is downgraded, not trusted:
    an unbackfilled row cannot be grandfathered into a verified claim.
    """
    keep = {k: raw.get(k) for k in SealEventV3.model_fields if k in raw}
    keep.pop("claim_text", None)  # never infer a claim from prose payload
    keep.pop("claim_id", None)
    keep.pop("confidence", None)
    keep.pop("confidence_actor", None)
    keep.pop("confidence_semantics", None)
    keep.pop("confidence_produced_at", None)
    keep.pop("verification_event_id", None)
    keep.pop("verified_by", None)
    keep.pop("outcome_observed_at", None)
    keep["verification_witness_class"] = "asserted"
    keep["verification_status"] = VerificationStatus.EVENT_ONLY
    return SealEventV3(**keep)
