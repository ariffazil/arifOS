"""
mind_schema.py — MIND_GEOMETRY_V1 Schema Layer
===============================================

Pydantic v2 contracts for the geometry block. The schema is the
*type system* of the decision torus. Anything that fails the schema
cannot be SEAL'd (Axiom 7).

Design rules:
  - extra='forbid' everywhere. If a field is not in the schema,
    the input is rejected, not silently dropped.
  - All numeric fields are bounded [0, 1] unless the field name
    is a coordinate angle (theta, phi) which is bounded [0, 2π).
  - The forbidden_center list is the canonical 4-item set from
    the EUREKA-T ratification: no self-authorized truth, action,
    power, or constitutional change.
  - Hole territory lives in mind_axioms.HOLE_TERRITORY. The schema
    does not duplicate it — the kernel measures, the schema types.

Origin: EUREKA-T ratification 2026-06-11.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from arifosmcp.geometry.mind_axioms import HOLE_TERRITORY


# ── Verdict Plane Enums (6-plane orthogonal system) ───────────────────────


class ExecutionVerdict(str, Enum):
    """Did the tool run successfully? Pure execution, zero semantic judgment."""
    SEAL = "SEAL"
    FAILED = "FAILED"


class ReasoningVerdict(str, Enum):
    """Is the thought coherent? Separate from truth (a coherent thought can be wrong)."""
    COHERENT = "COHERENT"
    INCOHERENT = "INCOHERENT"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"


class TruthVerdict(str, Enum):
    """Is the claim supported by evidence? Not the same as coherence or confidence."""
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


class EvidenceVerdict(str, Enum):
    """What backs the claim? Confidence scores ≠ evidence."""
    STRONG = "STRONG"
    WEAK = "WEAK"
    NONE = "NONE"
    BOUND = "BOUND"


class AuthorityVerdict(str, Enum):
    """Who has permission to act? Provenance is admissibility, authority is permission."""
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    PENDING = "PENDING"
    EXEMPT = "EXEMPT"


class RiskVerdict(str, Enum):
    """What can go wrong? Blast radius, reversibility, and sovereign proximity."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FinalKernelVerdict(str, Enum):
    """The strictest-safe result across all 6 planes.

    SEAL    — all planes pass, safe to proceed
    HOLD    — at least one plane requires human review
    DEGRADED— the system ran but the reasoning/truth/evidence is suspect
    VOID    — the action is constitutionally forbidden
    SABAR   — wait for more evidence before deciding

    Rule: if ANY inner verdict is HOLD, DEGRADED, VOID, UNSUPPORTED,
    INCOHERENT, DENIED, CRITICAL, or FAILED → final must NOT be SEAL.
    """
    SEAL = "SEAL"
    HOLD = "HOLD"
    DEGRADED = "DEGRADED"
    VOID = "VOID"
    SABAR = "SABAR"


class VerdictPlanes(BaseModel):
    """The 6 independent verdict planes + final kernel verdict.

    No plane may substitute for another. The final kernel verdict
    is the strictest-safe composition — if any inner plane is
    degraded, the final cannot be SEAL.

    Authority ladder (non-negotiable):
      Level 1: provenance  → admissibility (where did this come from?)
      Level 2: evidence    → credibility   (is it supported?)
      Level 3: reasoning   → coherence     (is it coherent?)
      Level 4: authority   → permission    (who has the lease?)
      Level 5: risk        → blast radius  (what can go wrong?)
      Level 6: action      → final verdict (can it proceed?)

    Level 1 is admissibility, NEVER authority. Provenance cannot
    jump to action — the authority ladder must be climbed in order.
    """
    model_config = ConfigDict(extra="forbid", frozen=False)

    execution: ExecutionVerdict = Field(
        default=ExecutionVerdict.SEAL,
        description="Did the tool run successfully?"
    )
    reasoning: ReasoningVerdict = Field(
        default=ReasoningVerdict.COHERENT,
        description="Is the thought internally coherent?"
    )
    truth: TruthVerdict = Field(
        default=TruthVerdict.UNKNOWN,
        description="Is the claim supported by evidence?"
    )
    evidence: EvidenceVerdict = Field(
        default=EvidenceVerdict.NONE,
        description="What backs this claim?"
    )
    authority: AuthorityVerdict = Field(
        default=AuthorityVerdict.PENDING,
        description="Who has permission to act on this?"
    )
    risk: RiskVerdict = Field(
        default=RiskVerdict.MEDIUM,
        description="What is the blast radius?"
    )
    final: FinalKernelVerdict = Field(
        default=FinalKernelVerdict.HOLD,
        description="Strictest-safe verdict across all 6 planes"
    )
    provenance: str = Field(
        default="code_derived_governance_wrapper",
        description="Where the verdict planes were computed (not the LLM output)"
    )


# ── Enumerations ────────────────────────────────────────────────────────────


class TensionType(str, Enum):
    """Cognitive tensions detected between orthogonal axes.

    Each tension type represents a dangerous relationship between
    two or more axes that affects routing, memory, or verdict.
    """

    ACTION_EVIDENCE_GAP = "ACTION_EVIDENCE_GAP"
    CONFIDENCE_EVIDENCE_GAP = "CONFIDENCE_EVIDENCE_GAP"
    AUTHORITY_PROVENANCE_CONFUSION = "AUTHORITY_PROVENANCE_CONFUSION"
    RISK_REVERSIBILITY_CONFLICT = "RISK_REVERSIBILITY_CONFLICT"
    NOVELTY_COHERENCE_GAP = "NOVELTY_COHERENCE_GAP"
    MEMORY_TRUTH_CONFLICT = "MEMORY_TRUTH_CONFLICT"
    SOVEREIGNTY_AMBIGUITY = "SOVEREIGNTY_AMBIGUITY"


class TensionEntry(BaseModel):
    """One detected tension between axes.

    The severity [0, 1] determines whether routing changes:
      >= 0.80 → HOLD, must resolve before next action
      >= 0.50 → WARN, route to critic/evidence
      <  0.50 → NOTE, log but do not block
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    tension_type: TensionType
    severity: float = Field(..., ge=0.0, le=1.0)
    axes_involved: tuple[str, ...] = Field(..., min_length=2, max_length=8)
    explanation: str = Field(..., min_length=1, max_length=1000)
    required_next_tool: str = Field(
        ..., description="One of: arif_heart_critique, arif_mind_reason, arif_evidence_fetch, arif_vault_seal, arif_judge_deliberate, HOLD"
    )
    blocked_actions: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Action classes blocked while this tension exists",
    )


class ActionAffordance(BaseModel):
    """What a thought is allowed to do next.

    Derived from geometry verdict + tension scan + sovereign proximity.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed_action_classes: tuple[str, ...] = Field(
        default_factory=lambda: ("OBSERVE", "ANALYZE"),
        description="Action classes this thought may proceed with",
    )
    blocked_action_classes: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Action classes explicitly blocked by geometry/tension",
    )
    next_cognitive_tool: str = Field(
        default="arif_heart_critique",
        description="Recommended next tool in the cognitive pipeline",
    )
    memory_tier_recommendation: str = Field(
        default="hypothesis",
        description="One of: fact, hypothesis, scratch, ephemeral, sovereign, vault",
    )
    requires_human_ack: bool = False
    requires_evidence: bool = False


class TrajectoryDelta(BaseModel):
    """Change in cognitive state from one thought to the next."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    parent_thought_id: str | None = None
    source_memory_refs: tuple[str, ...] = Field(default_factory=tuple)
    contradicted_memory_refs: tuple[str, ...] = Field(default_factory=tuple)
    supporting_memory_refs: tuple[str, ...] = Field(default_factory=tuple)
    delta_truth: float = 0.0
    delta_evidence: float = 0.0
    delta_risk: float = 0.0
    delta_authority: float = 0.0
    trajectory_verdict: str = Field(
        default="stationary",
        description="One of: improving, degrading, stationary, first_thought",
    )


class CalibrationUpdate(BaseModel):
    """Outcome feedback to update geometry calibration."""

    model_config = ConfigDict(extra="forbid")

    thought_id: str
    predicted_truth: float
    actual_truth: float | None = None
    predicted_risk: float
    actual_risk: float | None = None
    predicted_actionability: float
    actual_success: bool | None = None
    calibration_error: float = 0.0


class GeometryVerdict(str, Enum):
    """The 4-quadrant verdict on the decision torus.

    SURFACE       — lawful motion on the ring. May be SEAL'd.
    EDGE          — close to the hole but not crossing. WARN.
    HOLE_RISK     — crossing the forbidden disk. Cannot be SEAL'd.
    HOLD          — schema-level failure. Cannot be any verdict.
    """

    SURFACE = "SURFACE"
    EDGE = "EDGE"
    HOLE_RISK = "HOLE_RISK"
    HOLD = "HOLD"


class ManifoldType(str, Enum):
    """The 2 manifolds the kernel recognizes.

    DECISION_TORUS is the MIND_GEOMETRY_V1 default. EUCLIDEAN is
    the legacy flat-projection (kept for backward compat with
    pre-torus envelopes; not recommended for new reasoning).
    """

    DECISION_TORUS = "decision_torus"
    EUCLIDEAN = "euclidean"


class AxisName(str, Enum):
    """The 8 orthogonal axes. None may substitute for another.

    T  truth alignment
    U  uncertainty
    R  reversibility
    B  blast radius
    A  authority cleanliness
    E  entropy change
    H  human sovereignty preservation
    C  coherence
    """

    T = "T"
    U = "U"
    R = "R"
    B = "B"
    A = "A"
    E = "E"
    H = "H"
    C = "C"


# ── Forbidden center (canonical 4) ───────────────────────────────────────────


FORBIDDEN_CENTER: tuple[str, ...] = (
    "self_authorized_truth",
    "self_authorized_action",
    "self_authorized_power",
    "self_authorized_constitution_change",
)


# ── Field-level bounds ──────────────────────────────────────────────────────


def _unit_bounded(v: float, *, field: str) -> float:
    """Clamp to [0.0, 1.0]. Used for axes/proximity that are pure fractions."""
    if not math.isfinite(v):
        raise ValueError(f"{field} must be a finite real; got {v!r}")
    if v < 0.0 or v > 1.0:
        raise ValueError(f"{field} must be in [0, 1]; got {v}")
    return float(v)


def _angle_bounded(v: float, *, field: str) -> float:
    """Clamp to [0.0, 2π). Used for theta, phi torus coordinates."""
    if not math.isfinite(v):
        raise ValueError(f"{field} must be a finite real; got {v!r}")
    if v < 0.0 or v >= 2.0 * math.pi:
        raise ValueError(f"{field} must be in [0, 2π); got {v}")
    return float(v)


# ── Pydantic models ─────────────────────────────────────────────────────────


class OrthogonalAxes(BaseModel):
    """The 8 independent axes of the decision surface.

    Field names match AxisName enum. The model rejects any extra
    field (extra='forbid').

    Bound semantics:
      T, U, R, B, A, H, C  — bounded [0, 1] (pure fractions)
      E                     — bounded [-1, 1] (entropy can decrease;
                              F04 CLARITY case)

    The E-asymmetry is a constitutional fact: the kernel can measure
    whether reasoning *raised* or *lowered* entropy. Clamping E to
    [0, 1] would lose the F4 CLARITY signal.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    T: float = Field(0.0, description="Truth alignment")
    U: float = Field(0.0, description="Uncertainty")
    R: float = Field(0.0, description="Reversibility")
    B: float = Field(0.0, description="Blast radius (inverted: low=high blast)")
    A: float = Field(0.0, description="Authority cleanliness")
    E: float = Field(0.0, description="Entropy change (ΔS); -1=fell, +1=rose")
    H: float = Field(0.0, description="Human sovereignty preservation")
    C: float = Field(0.0, description="Coherence")

    @field_validator("T", "U", "R", "B", "A", "H", "C")
    @classmethod
    def _bound_unit(cls, v: float) -> float:
        return _unit_bounded(v, field="axis")

    @field_validator("E")
    @classmethod
    def _bound_entropy_axis(cls, v: float) -> float:
        if not (-1.0 <= v <= 1.0):
            raise ValueError(f"axis E (entropy) must be in [-1, 1]; got {v}")
        return float(v)


class ForbiddenCenterEntry(BaseModel):
    """One named forbidden class.

    The 4 entries are fixed by EUREKA-T ratification. The kernel
    measures whether a trajectory *enters* one; the schema only
    types what entry means.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Literal[
        "self_authorized_truth",
        "self_authorized_action",
        "self_authorized_power",
        "self_authorized_constitution_change",
    ]
    description: str = Field(..., min_length=10, max_length=500)
    risk_modifier: float = Field(0.0, description="Added to sovereign_proximity if crossed")

    @field_validator("risk_modifier")
    @classmethod
    def _bound_modifier(cls, v: float) -> float:
        return _unit_bounded(v, field="risk_modifier")


class GeometryBlock(BaseModel):
    """The required geometry block on every MIND_GEOMETRY_V1 envelope.

    This is the schema the runner parses. If parsing fails, the
    runner cannot promote to SEAL (Axiom 7).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    manifold: ManifoldType
    surface_role: Literal["lawful_reasoning_motion"] = "lawful_reasoning_motion"
    forbidden_center: tuple[ForbiddenCenterEntry, ...] = Field(
        default_factory=lambda: tuple(
            ForbiddenCenterEntry(
                name=name,  # type: ignore[arg-type]
                description=f"Trajectory entered {name.replace('_', ' ')}",
                risk_modifier=1.0,
            )
            for name in FORBIDDEN_CENTER
        )
    )

    # Torus coordinates (only when manifold == DECISION_TORUS)
    epistemic_angle_theta: float = 0.0
    governance_angle_phi: float = 0.0

    # Scalar measurements
    sovereign_proximity: float = Field(0.0, description="[0, 1] distance to forbidden center")
    entropy_delta: float = Field(0.0, description="[0, 1] expected entropy change")
    reversibility: float = Field(0.0, description="[0, 1] reversibility estimate")
    blast_radius: float = Field(
        0.0, description="[0, 1] blast radius estimate (0=safe, 1=catastrophic)"
    )
    authority_cleanliness: float = Field(0.0, description="[0, 1] authority cleanliness")

    # The verdict — required, never optional
    geometry_verdict: GeometryVerdict

    # Orthogonality guard (Axiom 1)
    axes: OrthogonalAxes
    orthogonality_violation: bool = False

    @field_validator("epistemic_angle_theta", "governance_angle_phi")
    @classmethod
    def _validate_angles(cls, v: float) -> float:
        return _angle_bounded(v, field="torus_angle")

    @field_validator(
        "sovereign_proximity",
        "entropy_delta",
        "reversibility",
        "blast_radius",
        "authority_cleanliness",
    )
    @classmethod
    def _validate_unit(cls, v: float) -> float:
        return _unit_bounded(v, field="geometry_scalar")

    @model_validator(mode="after")
    def _validate_consistency(self) -> "GeometryBlock":
        """The geometry block must be internally consistent.

        - HOLE_RISK verdict requires elevated sovereign_proximity
        - DECISION_TORUS manifold requires bounded angles
        - Forbidden center must contain exactly 4 entries
        """
        if self.geometry_verdict == GeometryVerdict.HOLE_RISK:
            if self.sovereign_proximity < 0.5:
                raise ValueError(
                    f"HOLE_RISK verdict requires sovereign_proximity >= 0.5; "
                    f"got {self.sovereign_proximity}"
                )
        if self.geometry_verdict == GeometryVerdict.SURFACE:
            if self.sovereign_proximity >= 0.75:
                raise ValueError(
                    f"SURFACE verdict requires sovereign_proximity < 0.75; "
                    f"got {self.sovereign_proximity}"
                )
        if self.manifold == ManifoldType.DECISION_TORUS:
            if not (0.0 <= self.epistemic_angle_theta < 2 * math.pi):
                raise ValueError("DECISION_TORUS requires theta in [0, 2π)")
            if not (0.0 <= self.governance_angle_phi < 2 * math.pi):
                raise ValueError("DECISION_TORUS requires phi in [0, 2π)")
        if len(self.forbidden_center) != 4:
            raise ValueError(
                f"forbidden_center must contain exactly 4 entries; got {len(self.forbidden_center)}"
            )
        return self


class GeometryEnvelope(BaseModel):
    """The full MIND_GEOMETRY_V1 envelope attached to a reasoning output.

    This is what arif_mind_reason emits. The runner parses this,
    then asks the 7 axioms to check it, then fuses the per-axiom
    results into a final geometry_verdict (which becomes one
    of the 7 verdict dimensions, not a replacement for floor verdicts).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal["MIND_GEOMETRY_V1"] = "MIND_GEOMETRY_V1"
    session_id: str | None = None
    actor_id: str | None = None
    query: str = Field(..., min_length=1, max_length=10_000)

    # The action being reasoned about (read-only field; classification
    # is the runner's job)
    action_class: Literal[
        "observe",
        "answer",
        "inspect",
        "draft",
        "patch",
        "dry_run",
        "hold",
        "execute",
        "irreversible_mutation",
        "external_commitment",
    ] = "answer"

    # Where this action falls in the hole-territory taxonomy
    in_hole_territory: bool = False

    # Preflight status (Axiom 3)
    preflight_observed: bool = False
    preflight_classified: bool = False
    preflight_reversibility_estimated: bool = False

    # Authorization (Axiom 4)
    has_capability: bool = False
    has_authorization: bool = False

    # Schema status (Axiom 7)
    inner_llm_returned_structured_output: bool = True

    # The geometry block itself
    geometry: GeometryBlock

    @field_validator("in_hole_territory")
    @classmethod
    def _cross_check_hole_territory(cls, v: bool, info) -> bool:  # type: ignore[no-untyped-def]
        """If action_class is in HOLE_TERRITORY, in_hole_territory must be True.

        The reverse is allowed (in_hole_territory=True with non-territory
        action_class) for future action classes that haven't been added
        to the canonical 10.
        """
        action_class = info.data.get("action_class")
        from arifosmcp.geometry.mind_axioms import is_hole_territory

        if action_class and is_hole_territory(action_class) and not v:
            raise ValueError(
                f"action_class {action_class!r} is in HOLE_TERRITORY; "
                f"in_hole_territory must be True"
            )
        return v


__all__ = [
    "ExecutionVerdict",
    "ReasoningVerdict",
    "TruthVerdict",
    "EvidenceVerdict",
    "AuthorityVerdict",
    "RiskVerdict",
    "FinalKernelVerdict",
    "VerdictPlanes",
    "ManifoldType",
    "AxisName",
    "GeometryVerdict",
    "FORBIDDEN_CENTER",
    "OrthogonalAxes",
    "ForbiddenCenterEntry",
    "GeometryBlock",
    "GeometryEnvelope",
    "HOLE_TERRITORY",
]
