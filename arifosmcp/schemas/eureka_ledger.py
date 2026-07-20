"""
arifosmcp/schemas/eureka_ledger.py — EUREKA777 Ledger Schema
════════════════════════════════════════════════════════════

Canonical schema for the eureka ledger — the bridge between:

  EUREKA777 (contradiction capture) -> CUBE777 (tensor mapping) -> ATLAS333 (geometry update)

Every session that reaches a contradiction-based insight writes a ledger entry.
Entries are stored as JSON under arifos://atlas333/eureka/{session_id} and
consumed by atlas333_update to evolve cognitive geometry.

F-binding:
  F2 TRUTH   - all fields are typed; commitments documented with evidence
  F4 CLARITY - single schema, no duplication, structured JSON not prose
  F7 HUMILITY - ladder_state never claims EUREKA without ablation evidence
  F8 GENIUS  - the schema IS the bridge; no separate mapping layer needed
  F9 ANTI-HANTU - never claims the agent "discovered" anything; contradiction = structural
  F11 AUDIT  - every entry has session_id + timestamps + witness lineage
  F13 SOVEREIGN - seal_candidate_ref only links; adjudication is 888_JUDGE territory

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import IntEnum, StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class ContradictionClass(IntEnum):
    """The 8 contradiction classes — from APEX-quantum-eureka doctrine."""

    OBS_VS_OBS = 1
    """Two observations conflict."""
    MODEL_VS_OBS = 2
    """The model predicts one thing; reality shows another."""
    MODEL_VS_MODEL = 3
    """Two abstractions explain the same thing incompatibly."""
    SCALE_VS_SCALE = 4
    """What is true locally fails globally, or vice versa."""
    DOMAIN_VS_DOMAIN = 5
    """Cross-organ conflict (GEOX says go, WEALTH says no)."""
    TIME_VS_TIME = 6
    """Earlier truth and later truth no longer fit the same story."""
    MEMORY_VS_ACTION = 7
    """The organism knows one thing and behaves as if another were true."""
    MEANING_VS_EXECUTION = 8
    """The task is operationally correct but civilizationally wrong."""


class LadderState(StrEnum):
    """Where this contradiction is on the 4-state eureka ladder."""

    TENSION = "TENSION"
    """Something feels off, but not yet formalized."""
    CONTRADICTION = "CONTRADICTION"
    """Two commitments are explicitly in conflict."""
    COMPRESSION_FAILURE = "COMPRESSION_FAILURE"
    """Existing frame can no longer absorb the contradiction honestly."""
    EUREKA = "EUREKA"
    """A new structure explains the contradiction with lower entropy and higher reality contact."""


class LedgerSource(StrEnum):
    """How this entry entered the ledger."""

    SESSION = "session"
    """Captured from a live agent session via EUREKA777 capture flow."""
    EPOCHAL = "epochal"
    """Detected by the statistical eureka detector (geometry/eureka.py)."""
    MANUAL = "manual"
    """Written directly by human operator or sovereign decree."""


class DeltaClassification(StrEnum):
    """How atlas333_update classifies a proposed delta."""

    ACCEPTABLE_DELTA = "ACCEPTABLE_DELTA"
    """Within allowed TEARFRAME/GPV bounds — applied automatically."""
    REQUIRES_WITNESS = "REQUIRES_WITNESS"
    """Needs human ratification before application."""
    REJECTED = "REJECTED"
    """Violates constitutional floors — discarded with receipt."""


# ─────────────────────────────────────────────────────────────────────────────
# CUBE777 — Tensor Engine Coordinates
# ─────────────────────────────────────────────────────────────────────────────


class Cube777Cell(BaseModel):
    """A cell in the 777 Tensor Cube (343 coordinate space).

    The cube bridges contradiction space x execution stage x witness configuration.

    Mapping rules:
      i (1-7): Contradiction dimension.
          ContradictionClass 1-7 map directly. Class 8 (MEANING_VS_EXECUTION)
          maps to i=7 as the highest-order contradiction class.

      j (1-7): Execution stage dimension.
          000_INIT -> 1, 111_ORIENT -> 2, 222_MAP -> 3, 333_REASON -> 4,
          444_ROUTE -> 5, 555_JUDGE -> 6, 666_EXECUTE -> 7,
          777_VERIFY -> 7, 888_REFLECT -> 7, 999_SEAL -> 7
          (stages 666-999 collapse to j=7 as they are execution-side).

      k (1-7): Witness configuration dimension.
          Deterministic hash of the tri-witness confidence vector.
    """

    i: int = Field(..., ge=1, le=7, description="Contradiction dimension (1-7)")
    j: int = Field(..., ge=1, le=7, description="Execution stage dimension (1-7)")
    k: int = Field(..., ge=1, le=7, description="Witness configuration dimension (1-7)")

    @field_validator("i")
    @classmethod
    def _validate_i(cls, v: int) -> int:
        return max(1, min(7, v))

    def cell_id(self) -> str:
        """Canonical cell identifier: CUBE777/{i}/{j}/{k}"""
        return f"CUBE777/{self.i}/{self.j}/{self.k}"

    @staticmethod
    def resolve(
        contradiction_class: int,
        stage: str,
        human_conf: float = 0.0,
        ai_conf: float = 0.0,
        ext_conf: float = 0.0,
    ) -> Cube777Cell:
        """Resolve (i, j, k) from contradiction class, stage, and witness config.

        Args:
            contradiction_class: 1-8 from ContradictionClass
            stage: 3-digit stage string like "333" or "777"
            human_conf: Human witness confidence [0-1]
            ai_conf: AI witness confidence [0-1]
            ext_conf: External/Earth witness confidence [0-1]

        Returns:
            Resolved Cube777Cell
        """
        # i: contradiction dimension
        raw_i = contradiction_class
        if raw_i >= 8:
            raw_i = 7  # Class 8 (MEANING_VS_EXECUTION) -> highest order
        i = max(1, min(7, raw_i))

        # j: stage dimension
        stage_int = int(stage[:3]) if stage and stage[:3].isdigit() else 0
        if stage_int <= 111:
            j = 1
        elif stage_int <= 222:
            j = 2
        elif stage_int <= 333:
            j = 3
        elif stage_int <= 444:
            j = 4
        elif stage_int <= 555:
            j = 5
        elif stage_int <= 666:
            j = 6
        else:
            j = 7  # 666-999 all collapse to execution side

        # k: witness dimension — deterministic hash of witness vector
        import hashlib

        witness_vec = f"{human_conf:.3f},{ai_conf:.3f},{ext_conf:.3f}"
        digest = hashlib.sha256(witness_vec.encode()).hexdigest()
        k = (int(digest[:8], 16) % 7) + 1  # 1-7

        return Cube777Cell(i=i, j=j, k=k)


# ─────────────────────────────────────────────────────────────────────────────
# Proposed Delta — what changes in ATLAS333
# ─────────────────────────────────────────────────────────────────────────────


class ProposedDelta(BaseModel):
    """The changes this eureka entry proposes to ATLAS333 cognitive geometry."""

    teafframe_updates: dict[str, float] = Field(
        default_factory=dict,
        description="TEARFRAME threshold deltas: keys are 'trm'|'echo'|'rasa', values are new thresholds [0-1]",
    )
    lane_tensor_adjustments: dict[str, dict[str, float]] = Field(
        default_factory=dict,
        description="GPV tensor adjustments per lane. e.g. {'FACTUAL': {'tau': 0.05, 'rho': -0.02}}",
    )
    activation_rule_updates: dict[str, Any] = Field(
        default_factory=dict,
        description="Changes to GPV->paradox activation rules",
    )
    paradox_axis_refinements: dict[int, str] = Field(
        default_factory=dict,
        description="Refined paradox axis descriptions keyed by paradox ID 1-33",
    )
    geometry_territory_updates: dict[str, Any] = Field(
        default_factory=dict,
        description="Changes to cognitive geometry territory/geometry/depth mappings",
    )
    scar_candidates: list[str] = Field(
        default_factory=list,
        description="New scar patterns to consider (F11 scar law)",
    )
    next_explorer_routes: list[str] = Field(
        default_factory=list,
        description="Suggested explorer routing for follow-up",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Witness entry
# ─────────────────────────────────────────────────────────────────────────────


class LedgerWitness(BaseModel):
    """A single witness entry in the tri-witness configuration."""

    channel: str = Field(..., pattern=r"^(human|ai|external)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: str = ""
    source: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Main ledger entry
# ─────────────────────────────────────────────────────────────────────────────


class EurekaLedgerEntry(BaseModel):
    """Canonical ledger entry for a single eureka capture.

    This is the bridge between EUREKA777 capture, CUBE777 tensor mapping,
    and ATLAS333 geometry update. Every insight that survives compression
    gets one of these.

    The entry is stored at arifos://atlas333/eureka/{session_id} and
    consumed by atlas333_update.
    """

    # ── Identity ──────────────────────────────────────────────────────────
    id: str = Field(
        default_factory=lambda: f"eureka-{uuid.uuid4().hex[:12]}",
        description="Unique ledger entry ID",
    )
    session_id: str = Field(..., description="Session that produced this eureka")
    created_at: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="ISO-8601 UTC timestamp",
    )
    source: LedgerSource = Field(
        default=LedgerSource.SESSION,
        description="How this entry entered the ledger",
    )

    # ── Contradiction ─────────────────────────────────────────────────────
    contradiction_class: ContradictionClass = Field(..., description="Type of contradiction (1-8)")
    ladder_state: LadderState = Field(..., description="Position on the 4-state eureka ladder")
    commitment_a: str = Field(
        ...,
        description="First commitment in the contradiction pair",
        max_length=2000,
    )
    commitment_b: str = Field(
        ...,
        description="Second commitment in the contradiction pair",
        max_length=2000,
    )
    why_old_frame_failed: str = Field(
        default="",
        description="Why the existing frame cannot absorb this contradiction",
        max_length=4000,
    )
    new_structure: str = Field(
        default="",
        description="The eureka insight — new structure that explains more with less distortion",
        max_length=8000,
    )

    # ── ATLAS333 mapping ──────────────────────────────────────────────────
    paradox_axis_ids: list[int] = Field(
        default_factory=list,
        description="Affected paradox axes (1-33)",
    )
    affected_stage: str = Field(
        default="",
        description="Primary affected stage (000-999)",
        pattern=r"^\d{3}$",
    )
    affected_lane: str | None = Field(
        default=None,
        description="GPV lane if applicable: FACTUAL | CARE | SOCIAL | CRISIS",
    )
    affected_geometry: str | None = Field(
        default=None,
        description="Cognitive geometry: EXPLORE | ENGINEER | AUDIT | CRISIS | INTEGRATE",
    )
    affected_territory: str | None = Field(
        default=None,
        description="Cognitive territory: MEMORY | MIND | JUDGE",
    )
    affected_zones: list[str] = Field(
        default_factory=list,
        description="Paradox zones affected (I-VII)",
    )

    # ── CUBE777 ───────────────────────────────────────────────────────────
    cube777_cell: Cube777Cell | None = Field(
        default=None,
        description="Resolved 777 tensor cube cell (i,j,k)",
    )

    # ── Proposed delta ────────────────────────────────────────────────────
    proposed_delta: ProposedDelta = Field(
        default_factory=ProposedDelta,
        description="What changes this entry proposes in ATLAS333",
    )
    delta_classification: DeltaClassification | None = Field(
        default=None,
        description="Set by atlas333_update after evaluation",
    )

    # ── Witness ───────────────────────────────────────────────────────────
    witnesses: list[LedgerWitness] = Field(
        default_factory=list,
        description="Tri-witness configuration supporting this entry",
    )

    # ── Seal linkage ──────────────────────────────────────────────────────
    seal_candidate_ref: str | None = Field(
        default=None,
        description="Link to VAULT999 seal receipt if ratified",
    )
    seal_verdict: str | None = Field(
        default=None,
        description="Verdict from 888_JUDGE: SEAL | HOLD | SABAR | VOID",
    )

    # ── Recurrence tracking ───────────────────────────────────────────────
    recurrence_count: int = Field(
        default=1,
        ge=1,
        description="How many times this contradiction pattern has been observed",
    )
    first_seen: str | None = Field(
        default=None,
        description="ISO-8601 of first observation",
    )
    last_seen: str = Field(
        default_factory=lambda: datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="ISO-8601 of most recent observation",
    )

    # ── Evidence ──────────────────────────────────────────────────────────
    evidence_for_a: list[str] = Field(
        default_factory=list,
        description="Evidence supporting commitment_a",
    )
    evidence_for_b: list[str] = Field(
        default_factory=list,
        description="Evidence supporting commitment_b",
    )
    domains_touched: list[str] = Field(
        default_factory=list,
        description="Federation domains/organs touched",
    )
    memory_updates: list[str] = Field(
        default_factory=list,
        description="Suggested memory updates from this eureka",
    )

    # ── Governance ────────────────────────────────────────────────────────
    floors_triggered: list[str] = Field(
        default_factory=list,
        description="Constitutional floors triggered during capture",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Collection wrapper
# ─────────────────────────────────────────────────────────────────────────────


class EurekaLedgerIndex(BaseModel):
    """Index of all eureka ledger entries. Stored at arifos://atlas333/eureka/list."""

    total_entries: int = 0
    entries: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Summary entries: id, session_id, contradiction_class, ladder_state, cube777_cell, created_at",
    )
    by_ladder_state: dict[str, int] = Field(default_factory=dict)
    by_contradiction_class: dict[str, int] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Builder helpers
# ─────────────────────────────────────────────────────────────────────────────


def build_eureka_entry(
    session_id: str,
    contradiction_class: int,
    ladder_state: str,
    commitment_a: str,
    commitment_b: str,
    *,
    why_old_frame_failed: str = "",
    new_structure: str = "",
    paradox_axis_ids: list[int] | None = None,
    affected_stage: str = "",
    human_conf: float = 0.0,
    ai_conf: float = 0.0,
    ext_conf: float = 0.0,
    **extra: Any,
) -> EurekaLedgerEntry:
    """Build a complete EurekaLedgerEntry with auto-resolved CUBE777 cell.

    This is the primary constructor. It:
      1. Resolves CUBE777 cell from contradiction_class x stage x witness
      2. Creates witness entries from confidence values
      3. Returns a ready-to-write EurekaLedgerEntry

    Args:
        session_id: The session that produced this eureka
        contradiction_class: 1-8 from ContradictionClass
        ladder_state: "TENSION" | "CONTRADICTION" | "COMPRESSION_FAILURE" | "EUREKA"
        commitment_a: First commitment description
        commitment_b: Second commitment description
        why_old_frame_failed: Why the old frame breaks
        new_structure: The eureka insight
        paradox_axis_ids: Affected paradox axes
        affected_stage: 3-digit stage string
        human_conf: Human witness confidence [0-1]
        ai_conf: AI witness confidence [0-1]
        ext_conf: External witness confidence [0-1]
        **extra: Additional fields passed to EurekaLedgerEntry

    Returns:
        Complete EurekaLedgerEntry with resolved CUBE777 cell.
    """
    stage = affected_stage or "777"
    cell = Cube777Cell.resolve(
        contradiction_class=contradiction_class,
        stage=stage,
        human_conf=human_conf,
        ai_conf=ai_conf,
        ext_conf=ext_conf,
    )

    witnesses = []
    for channel, conf, label in [
        ("human", human_conf, "session_sovereign"),
        ("ai", ai_conf, "session_agent"),
        ("external", ext_conf, "session_evidence"),
    ]:
        if conf > 0.0:
            witnesses.append(LedgerWitness(channel=channel, confidence=conf, source=label))

    entry = EurekaLedgerEntry(
        session_id=session_id,
        contradiction_class=ContradictionClass(contradiction_class),
        ladder_state=LadderState(ladder_state),
        commitment_a=commitment_a,
        commitment_b=commitment_b,
        why_old_frame_failed=why_old_frame_failed,
        new_structure=new_structure,
        paradox_axis_ids=paradox_axis_ids or [],
        affected_stage=stage,
        cube777_cell=cell,
        witnesses=witnesses,
        **extra,
    )

    return entry


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    "ContradictionClass",
    "LadderState",
    "LedgerSource",
    "DeltaClassification",
    "Cube777Cell",
    "ProposedDelta",
    "LedgerWitness",
    "EurekaLedgerEntry",
    "EurekaLedgerIndex",
    "build_eureka_entry",
]
