"""
arifOS Federation Metabolism Envelope — Python Validation Module
==========================================================================
The one canonical blood packet every organ must use to talk to every other organ.
Converts 7 separate repositories into one governed metabolic loop.

Usage:
    from arifosmcp.envelope import FederationEnvelope, validate_envelope

    envelope = FederationEnvelope(
        trace_id="uuid-...",
        actor_id="ARIF_FAZIL",
        organ_origin="GEOX",
        organ_target="WEALTH",
        intent="Assess Sabah Basin opportunity/risk",
        evidence_layer="OBSERVED",
        autonomy_band="T2_ANNOUNCE",
        reversibility_class="FULL",
        risk_class="MEDIUM",
        required_floor_checks=["F1","F2","F4","F11","F13"],
        proposed_action={"action_type": "basin_assessment", "parameters": {"basin": "Sabah"}},
        f13_required_boolean=False,
    )
    errors = validate_envelope(envelope)
    if errors:
        raise ValueError(f"Envelope validation failed: {errors}")

DITEMPA BUKAN DIBERI — Forged by FORGE (000Ω), 2026-07-01.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ──────────────────────────────────────────────────────────────────


class Organ(str, Enum):
    ARIFOS = "arifOS"
    AAA = "AAA"
    A_FORGE = "A-FORGE"
    GEOX = "GEOX"
    WEALTH = "WEALTH"
    WELL = "WELL"
    VAULT999 = "VAULT999"
    ARIFFAZIL = "ariffazil"


class EvidenceLayer(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    INTERPRETED = "INTERPRETED"
    SPECULATED = "SPECULATED"
    UNKNOWN = "UNKNOWN"


class AutonomyBand(str, Enum):
    T1_AUTO = "T1_AUTO"
    T2_ANNOUNCE = "T2_ANNOUNCE"
    T3_888_HOLD = "T3_888_HOLD"
    F13_SOVEREIGN = "F13_SOVEREIGN"


class ReversibilityClass(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class RiskClass(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    ROUTING = "ROUTING"
    DELIBERATING = "DELIBERATING"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"
    HOLD = "HOLD"


class F13Verdict(str, Enum):
    JITU = "JITU"
    HOLD = "HOLD"
    SABAR = "SABAR"
    VOID = "VOID"


class Floor(str, Enum):
    F1 = "F1"  # AMANAH
    F2 = "F2"  # TRUTH
    F3 = "F3"  # TRI_WITNESS
    F4 = "F4"  # CLARITY
    F5 = "F5"  # PEACE
    F6 = "F6"  # MARUAH
    F7 = "F7"  # HUMILITY
    F8 = "F8"  # LAW
    F9 = "F9"  # ANTI_HANTU
    F10 = "F10"  # ONTOLOGY
    F11 = "F11"  # AUDIT
    F12 = "F12"  # RESILIENCE
    F13 = "F13"  # SOVEREIGN


# ─── Organ Payloads ─────────────────────────────────────────────────────────


class GEOXPayload(BaseModel):
    claim_id: Optional[str] = None
    evidence_summary: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=0.9)
    physics_invariants: Optional[list[str]] = None


class WEALTHPayload(BaseModel):
    npv: Optional[float] = None
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    capital_class: Optional[str] = None
    wisdom_dimensions: Optional[dict[str, Any]] = None


class WELLPayload(BaseModel):
    readiness_color: Optional[str] = None
    fatigue_level: Optional[float] = Field(default=None, ge=0, le=1)
    dignity_preservation: Optional[float] = Field(default=None, ge=0, le=1)
    recommendation: Optional[str] = None


class AAAPayload(BaseModel):
    route: Optional[list[str]] = None
    display_state: Optional[str] = None
    warga_boundary_check: Optional[bool] = None


class ArifOSPayload(BaseModel):
    verdict: Optional[str] = None
    g_score: Optional[float] = Field(default=None, ge=0, le=1)
    violated_floors: Optional[list[str]] = None
    judge_reasoning: Optional[str] = None


class AForgePayload(BaseModel):
    execution_id: Optional[str] = None
    dry_run_result: Optional[str] = None
    execution_result: Optional[str] = None
    rollback_available: Optional[bool] = None


class VAULT999Payload(BaseModel):
    seal_id: Optional[str] = None
    seal_hash: Optional[str] = None
    sealed_at: Optional[datetime] = None
    witness_count: Optional[int] = None


class OrganPayloads(BaseModel):
    GEOX: Optional[GEOXPayload] = None
    WEALTH: Optional[WEALTHPayload] = None
    WELL: Optional[WELLPayload] = None
    AAA: Optional[AAAPayload] = None
    arifOS: Optional[ArifOSPayload] = None
    A_FORGE: Optional[AForgePayload] = Field(default=None, alias="A-FORGE")
    VAULT999: Optional[VAULT999Payload] = None


# ─── Route Entry ────────────────────────────────────────────────────────────


class OrganRouteEntry(BaseModel):
    organ: str
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    verdict: Optional[str] = None
    notes: Optional[str] = None


# ─── Main Envelope ──────────────────────────────────────────────────────────


class FederationEnvelope(BaseModel):
    """The one canonical blood packet. Every organ must use this to communicate."""

    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str
    organ_origin: Organ
    organ_target: Organ
    organ_route: list[OrganRouteEntry] = Field(default_factory=list)
    intent: str = Field(min_length=1, max_length=2000)
    evidence_layer: EvidenceLayer = EvidenceLayer.UNKNOWN
    autonomy_band: AutonomyBand = AutonomyBand.T2_ANNOUNCE
    reversibility_class: ReversibilityClass = ReversibilityClass.UNKNOWN
    risk_class: RiskClass = RiskClass.MEDIUM
    required_floor_checks: list[Floor] = Field(default_factory=list)
    proposed_action: dict[str, Any]
    execution_status: ExecutionStatus = ExecutionStatus.PENDING
    measurement_result: Optional[dict[str, Any]] = None
    vault_receipt_reference: Optional[str] = None
    f13_required_boolean: bool = False
    f13_verdict: Optional[F13Verdict] = None
    organ_payloads: OrganPayloads = Field(default_factory=OrganPayloads)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("trace_id")
    @classmethod
    def trace_id_must_be_valid_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError(f"trace_id must be a valid UUID, got: {v}")
        return v

    def stamp_route(
        self, organ: str, verdict: str | None = None, notes: str | None = None
    ) -> "FederationEnvelope":
        """Append a route entry for the current organ. Call this when an organ processes the envelope."""
        entry = OrganRouteEntry(
            organ=organ,
            received_at=datetime.now(timezone.utc),
            processed_at=datetime.now(timezone.utc),
            verdict=verdict or "PROCESSED",
            notes=notes,
        )
        self.organ_route.append(entry)
        return self

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, by_alias=True)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)


# ─── Validation ─────────────────────────────────────────────────────────────

CANONICAL_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent / "contracts" / "federation_envelope.schema.json"
)


def validate_envelope(envelope: FederationEnvelope | dict[str, Any]) -> list[str]:
    """Validate an envelope against the canonical schema. Returns list of errors (empty = valid)."""
    errors: list[str] = []

    if isinstance(envelope, dict):
        try:
            envelope = FederationEnvelope(**envelope)
        except Exception as e:
            return [f"Envelope construction failed: {e}"]

    # Hard rules
    if envelope.f13_required_boolean and envelope.autonomy_band not in (
        AutonomyBand.T3_888_HOLD,
        AutonomyBand.F13_SOVEREIGN,
    ):
        errors.append(
            "HARD_RULE: f13_required_boolean=True but autonomy_band is not T3_888_HOLD or F13_SOVEREIGN"
        )

    if envelope.reversibility_class == ReversibilityClass.NONE and envelope.risk_class in (
        RiskClass.HIGH,
        RiskClass.CRITICAL,
    ):
        errors.append(
            "HARD_RULE: Irreversible action with HIGH/CRITICAL risk. Requires F13 sovereign approval."
        )

    if (
        envelope.execution_status == ExecutionStatus.COMPLETED
        and not envelope.vault_receipt_reference
    ):
        errors.append(
            "HARD_RULE: Execution completed but no vault_receipt_reference. Must seal before completing."
        )

    if Floor.F13 not in envelope.required_floor_checks and envelope.f13_required_boolean:
        errors.append("HARD_RULE: f13_required_boolean=True but F13 not in required_floor_checks.")

    # No organ may output free-form truth without envelope (this is enforced at the transport layer)
    # No SEAL may be displayed unless VAULT999/arifOS actually sealed it
    if envelope.organ_payloads.VAULT999 and envelope.organ_payloads.VAULT999.seal_id:
        if not envelope.vault_receipt_reference:
            errors.append(
                "HARD_RULE: VAULT999 payload has seal_id but vault_receipt_reference is empty."
            )

    # No repo may claim sovereignty
    if envelope.organ_origin == Organ.ARIFFAZIL:
        errors.append(
            "HARD_RULE: ariffazil is the sovereign surface, not an organ. Cannot originate envelopes."
        )

    return errors


def validate_envelope_dict(data: dict[str, Any]) -> list[str]:
    """Validate a raw dict against the envelope schema."""
    return validate_envelope(data)


# ─── Pre-built Scenarios ────────────────────────────────────────────────────


def sabah_basin_envelope() -> FederationEnvelope:
    """Sabah Basin: GEOX → WEALTH → WELL → AAA → arifOS → A-FORGE → VAULT999 → Arif/F13."""
    return FederationEnvelope(
        trace_id=str(uuid.uuid4()),
        actor_id="ARIF_FAZIL",
        organ_origin=Organ.GEOX,
        organ_target=Organ.WEALTH,
        intent="Assess Sabah Basin opportunity/risk — subsurface viability, capital consequence, operator readiness",
        evidence_layer=EvidenceLayer.OBSERVED,
        autonomy_band=AutonomyBand.F13_SOVEREIGN,
        reversibility_class=ReversibilityClass.FULL,
        risk_class=RiskClass.MEDIUM,
        required_floor_checks=[
            Floor.F1,
            Floor.F2,
            Floor.F4,
            Floor.F6,
            Floor.F8,
            Floor.F11,
            Floor.F13,
        ],
        proposed_action={
            "action_type": "basin_opportunity_assessment",
            "parameters": {
                "basin": "Sabah",
                "assessment_type": "full_metabolic_loop",
                "organs_involved": [
                    "GEOX",
                    "WEALTH",
                    "WELL",
                    "AAA",
                    "arifOS",
                    "A-FORGE",
                    "VAULT999",
                ],
            },
        },
        execution_status=ExecutionStatus.PENDING,
        f13_required_boolean=True,
        metadata={
            "created_at": datetime.now(timezone.utc).isoformat(),
            "priority": "HIGH",
            "tags": ["sabah_basin", "metabolic_loop", "end_to_end_test"],
            "correlation_id": "SABAH-BASIN-001",
        },
    )


# ─── Self-test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick self-test
    envelope = sabah_basin_envelope()
    errors = validate_envelope(envelope)
    if errors:
        print("❌ VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ Envelope valid. Metabolic spine operational.")
        print(f"   trace_id: {envelope.trace_id}")
        print(f"   route: {envelope.organ_origin} → {envelope.organ_target}")
        print(f"   floors: {[f.value for f in envelope.required_floor_checks]}")
        print(f"   f13_required: {envelope.f13_required_boolean}")
    print(f"\n{envelope.to_json()}")
