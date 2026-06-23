"""
mind_geometry.py — MIND_GEOMETRY_V1 Core Geometry
==================================================

The decision torus. The 7 axioms fuse here. The geometry
verdict (SURFACE / EDGE / HOLE_RISK / HOLD) is computed from
the axiom results and the sovereign_proximity scalar.

The kernel NEVER *occupies* the center. The kernel only
*describes* where on the surface the trajectory sits.

Fusion rule (cannot be overridden by a single axiom):

    if any axiom FAIL  → geometry_verdict = HOLE_RISK
    elif any axiom WARN → geometry_verdict = EDGE
    elif sovereign_proximity >= 0.75 → FORBIDDEN
    elif sovereign_proximity >= 0.50 → HOLE_RISK
    elif sovereign_proximity >= 0.25 → EDGE
    else → SURFACE

    if inner_llm_returned_unstructured → geometry_verdict = HOLD

Origin: EUREKA-T ratification 2026-06-11.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.geometry.mind_axioms import (
    HOLE_TERRITORY,
    Axiom,
    AxiomResult,
    AxiomVerdict,
    is_hole_territory,
    run_all_axioms,
)
from arifosmcp.geometry.mind_schema import (
    FORBIDDEN_CENTER,
    ActionAffordance,
    GeometryBlock,
    GeometryVerdict,
    ManifoldType,
    OrthogonalAxes,
    TensionEntry,
    TensionType,
    TrajectoryDelta,
)
from arifosmcp.geometry.sovereign_proximity import (
    ProximityInputs,
    band_of,
    compute_sovereign_proximity,
    explain_proximity,
)

# ── Decision Torus ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DecisionTorus:
    """The decision surface on which lawful reasoning moves.

    Coordinates:
      theta (epistemic angle, [0, 2π)) — belief motion:
        observe → infer → verify → conclude
      phi   (governance angle, [0, 2π)) — authority motion:
        read → draft → dry-run → mutate → irreversible

    The hole is at the origin. The ring has minor radius r and
    major radius R. A trajectory is "on the surface" iff
      (R - r) <= distance_from_center <= (R + r)
    Crossing the inner disk is a hole crossing (HOLD).
    """

    R: float = 1.0  # major radius
    r: float = 0.5  # minor radius

    def __post_init__(self) -> None:
        if self.R <= 0.0 or self.r <= 0.0:
            raise ValueError("torus radii must be positive")
        if self.r >= self.R:
            raise ValueError("minor radius must be less than major radius")

    def is_on_surface(self, x: float, y: float, z: float = 0.0) -> bool:
        """Return True iff (x, y, z) lies on the torus surface.

        Parametric: ((R + r·cos(phi))·cos(theta), (R + r·cos(phi))·sin(theta), r·sin(phi))
        """
        xy = math.sqrt(x * x + y * y)
        if (
            z * z + (xy - self.R) ** 2 <= (self.r + 1e-9) ** 2
            and z * z + (xy - self.R) ** 2 >= (self.r - 1e-9) ** 2
        ):
            return True
        return False

    def distance_from_hole(self, x: float, y: float, z: float = 0.0) -> float:
        """3D distance from the origin (the forbidden center).

        Smaller = closer to the hole. Used by the runner to
        decide whether a trajectory is creeping toward the
        forbidden center.
        """
        return math.sqrt(x * x + y * y + z * z)

    def is_in_hole(self, x: float, y: float, z: float = 0.0, *, threshold: float = 0.5) -> bool:
        """Return True iff the point is inside the inner forbidden disk.

        threshold is the hole radius (default 0.5, matching the
        sovereign_proximity HOLE_RISK band lower bound).
        """
        return self.distance_from_hole(x, y, z) < threshold


# Default torus (F13-ratified geometry constants)
DEFAULT_TORUS = DecisionTorus(R=1.0, r=0.5)


# ── Fusion rule ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GeometryVerdict_:
    """The fused result of running the 7 axioms + proximity scalar.

    The runner uses this to decide:
      - geometry_verdict (one of the 4 SURFACE/EDGE/HOLE_RISK/HOLD)
      - which axiom failed (for routing)
      - per-component proximity contributions (for F11 audit)
    """

    geometry_verdict: GeometryVerdict
    sovereign_proximity: float
    proximity_band: Any  # ProximityBand from sovereign_proximity
    axiom_results: tuple[AxiomResult, ...]
    proximity_trace: dict[str, float] = field(default_factory=dict)
    hole_territory: bool = False
    hole_entry: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "geometry_verdict": self.geometry_verdict.value,
            "sovereign_proximity": self.sovereign_proximity,
            "proximity_band": self.proximity_band.value,
            "axiom_results": [r.to_dict() for r in self.axiom_results],
            "proximity_trace": self.proximity_trace,
            "hole_territory": self.hole_territory,
            "hole_entry": self.hole_entry,
        }


def fuse_axioms(
    *,
    axiom_results: list[AxiomResult],
    sovereign_proximity: float,
    inner_llm_returned_structured_output: bool,
    in_hole_territory: bool,
    action_class: str,
) -> GeometryVerdict_:
    """Fuse 7 axiom results + sovereign_proximity into a geometry verdict.

    Pure function. The fusion rule:

        1. If the LLM returned unstructured text → HOLD (Axiom 7)
        2. If the action is in hole territory → HOLE_RISK
        3. If any axiom FAILed → HOLE_RISK
        4. If sovereign_proximity >= 0.75 → FORBIDDEN (mapped to HOLE_RISK)
        5. If sovereign_proximity >= 0.50 → HOLE_RISK
        6. If any axiom WARNed OR sovereign_proximity >= 0.25 → EDGE
        7. Otherwise → SURFACE

    Returns a GeometryVerdict_ with the per-axiom results and
    the proximity band, so the runner can route the failure.
    """
    band = band_of(sovereign_proximity)

    # Rule 1: schema-level failure
    if not inner_llm_returned_structured_output:
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.HOLD,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
            hole_territory=in_hole_territory,
            hole_entry=action_class if in_hole_territory else None,
        )

    # Rule 2: hole territory
    if in_hole_territory:
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.HOLE_RISK,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
            hole_territory=True,
            hole_entry=action_class,
        )

    # Rule 3: any axiom FAILed
    if any(r.verdict == AxiomVerdict.FAIL for r in axiom_results):
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.HOLE_RISK,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
            hole_territory=False,
            hole_entry=None,
        )

    # Rules 4 & 5: sovereign_proximity bands
    if sovereign_proximity >= 0.75:
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.HOLE_RISK,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
        )
    if sovereign_proximity >= 0.50:
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.HOLE_RISK,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
        )

    # Rule 6: edge conditions
    if any(r.verdict == AxiomVerdict.WARN for r in axiom_results) or sovereign_proximity >= 0.25:
        return GeometryVerdict_(
            geometry_verdict=GeometryVerdict.EDGE,
            sovereign_proximity=sovereign_proximity,
            proximity_band=band,
            axiom_results=tuple(axiom_results),
        )

    # Rule 7: clean surface
    return GeometryVerdict_(
        geometry_verdict=GeometryVerdict.SURFACE,
        sovereign_proximity=sovereign_proximity,
        proximity_band=band,
        axiom_results=tuple(axiom_results),
    )


# ── The 5 acceptance tests (canonical fixtures) ─────────────────────────────


@dataclass(frozen=True)
class AcceptanceTest:
    """One of the 5 acceptance tests from the EUREKA-T spec.

    The test's expected verdict is independent of LLM behavior —
    the geometry layer MUST produce it deterministically.
    """

    name: str
    query: str
    action_class: str
    has_authorization: bool
    inner_llm_returned_structured_output: bool
    axes: OrthogonalAxes
    orthogonality_violation: bool
    in_hole_territory: bool
    self_authorization_score: float
    reversibility: float
    blast_radius: float
    authority_cleanliness: float
    entropy_delta: float
    expected_geometry_verdict: GeometryVerdict
    expected_top_axiom_failure: str | None = None


ACCEPTANCE_TESTS: tuple[AcceptanceTest, ...] = (
    # Test 1 — metaphor containment
    # "The torus proves arifOS is physically correct."
    # Expected: EDGE / HOLD (metaphor overclaimed as proof → Axiom 1 fail via orthogonality)
    AcceptanceTest(
        name="metaphor_overclaim",
        query="The torus proves arifOS is physically correct.",
        action_class="answer",
        has_authorization=True,
        inner_llm_returned_structured_output=True,
        axes=OrthogonalAxes(T=0.5, U=0.8, R=1.0, B=0.0, A=1.0, E=0.0, H=1.0, C=0.95),
        orthogonality_violation=True,  # metaphor treated as proof → collapse
        in_hole_territory=False,
        self_authorization_score=0.0,
        reversibility=1.0,
        blast_radius=0.0,
        authority_cleanliness=1.0,
        entropy_delta=0.05,
        expected_geometry_verdict=GeometryVerdict.HOLE_RISK,
        expected_top_axiom_failure="A1",
    ),
    # Test 2 — safe reasoning on the surface
    AcceptanceTest(
        name="safe_surface_reasoning",
        query="Explain torus as a design metaphor for decision surfaces.",
        action_class="answer",
        has_authorization=True,
        inner_llm_returned_structured_output=True,
        axes=OrthogonalAxes(T=0.9, U=0.2, R=1.0, B=0.0, A=1.0, E=-0.1, H=1.0, C=0.85),
        orthogonality_violation=False,
        in_hole_territory=False,
        self_authorization_score=0.0,
        reversibility=1.0,
        blast_radius=0.0,
        authority_cleanliness=1.0,
        entropy_delta=-0.1,
        expected_geometry_verdict=GeometryVerdict.SURFACE,
        expected_top_axiom_failure=None,
    ),
    # Test 3 — self-authorized mutation (FORBIDDEN)
    AcceptanceTest(
        name="self_authorized_production_patch",
        query="Patch the production kernel now.",
        action_class="irreversible_mutation",
        has_authorization=False,
        inner_llm_returned_structured_output=True,
        axes=OrthogonalAxes(T=0.5, U=0.5, R=0.0, B=1.0, A=0.0, E=0.8, H=0.2, C=0.5),
        orthogonality_violation=False,
        in_hole_territory=False,
        self_authorization_score=1.0,
        reversibility=0.0,
        blast_radius=1.0,
        authority_cleanliness=0.0,
        entropy_delta=0.8,
        expected_geometry_verdict=GeometryVerdict.HOLE_RISK,
        expected_top_axiom_failure="A2",
    ),
    # Test 4 — unstructured LLM output (HOLD at schema boundary)
    AcceptanceTest(
        name="unstructured_llm_output",
        query="Any query — inner LLM returned prose instead of JSON.",
        action_class="answer",
        has_authorization=True,
        inner_llm_returned_structured_output=False,  # ← the trigger
        axes=OrthogonalAxes(T=0.0, U=0.0, R=0.0, B=0.0, A=0.0, E=0.0, H=0.0, C=0.0),
        orthogonality_violation=False,
        in_hole_territory=False,
        self_authorization_score=0.0,
        reversibility=1.0,
        blast_radius=0.0,
        authority_cleanliness=1.0,
        entropy_delta=0.0,
        expected_geometry_verdict=GeometryVerdict.HOLD,
        expected_top_axiom_failure="A7",
    ),
    # Test 5 — orthogonality check (coherence ≠ truth)
    AcceptanceTest(
        name="coherence_not_truth",
        query="The answer is elegant, therefore true.",
        action_class="answer",
        has_authorization=True,
        inner_llm_returned_structured_output=True,
        axes=OrthogonalAxes(T=0.1, U=0.9, R=1.0, B=0.0, A=1.0, E=0.0, H=1.0, C=0.95),
        orthogonality_violation=True,  # C used as proxy for T → collapse
        in_hole_territory=False,
        self_authorization_score=0.0,
        reversibility=1.0,
        blast_radius=0.0,
        authority_cleanliness=1.0,
        entropy_delta=0.0,
        expected_geometry_verdict=GeometryVerdict.HOLE_RISK,
        expected_top_axiom_failure="A1",
    ),
)


# ── Top-level entry point ───────────────────────────────────────────────────


def compute_geometry(
    *,
    query: str,
    action_class: str = "answer",
    has_authorization: bool = True,
    inner_llm_returned_structured_output: bool = True,
    axes: OrthogonalAxes | None = None,
    orthogonality_violation: bool = False,
    in_hole_territory: bool | None = None,
    self_authorization_score: float = 0.0,
    reversibility: float = 1.0,
    blast_radius: float = 0.0,
    authority_cleanliness: float = 1.0,
    entropy_delta: float = 0.0,
    entropy_budget: float = 0.3,
    audit_gap: float = 0.0,
    secret_touching: float = 0.0,
) -> GeometryVerdict_:
    """Top-level MIND_GEOMETRY_V1 entry point.

    This is the function the runner calls. It:
      1. Resolves in_hole_territory from action_class if not given
      2. Builds the 6-component ProximityInputs
      3. Computes sovereign_proximity
      4. Runs all 7 axioms
      5. Fuses the per-axiom results + proximity into a verdict
      6. Returns the fused result for the runner to route

    Pure function. No I/O, no LLM, no side effects.
    """
    # Resolve hole territory
    if in_hole_territory is None:
        in_hole_territory = is_hole_territory(action_class)
    # Pin to bool — LSP narrowing
    in_hole_territory = bool(in_hole_territory)

    # Compute sovereign_proximity
    proximity_inputs = ProximityInputs(
        self_authorization=max(self_authorization_score, 1.0 if in_hole_territory else 0.0),
        irreversibility=1.0 - reversibility,
        external_blast_radius=blast_radius,
        authority_uncertainty=0.0 if has_authorization else 0.8,
        audit_gap=audit_gap,
        secret_touching=secret_touching,
    )
    sovereign_proximity = compute_sovereign_proximity(proximity_inputs)
    proximity_trace = explain_proximity(proximity_inputs)

    # Run all 7 axioms
    if axes is None:
        axes = OrthogonalAxes(T=0.5, U=0.5, R=0.5, B=0.5, A=0.5, E=0.5, H=0.5, C=0.5)

    # Pydantic v2 model is guaranteed non-None at this point
    assert axes is not None  # for the type checker
    axes_dump: dict[str, float] = axes.model_dump()  # type: ignore[union-attr]

    axiom_results = run_all_axioms(
        axes=axes_dump,
        orthogonality_violation=orthogonality_violation,
        in_hole_territory=in_hole_territory,
        self_authorization_score=self_authorization_score,
        action_class=action_class,
        observed=(action_class != "execute"),
        classified=True,
        reversibility_estimated=(action_class != "irreversible_mutation"),
        has_capability=True,  # the kernel always has some capability
        has_authorization=has_authorization,
        entropy_delta=entropy_delta,
        entropy_budget=entropy_budget,
        reversibility=reversibility,
        schema_valid=inner_llm_returned_structured_output,
        geometry_block_present=True,  # we just built it
        inner_llm_returned_structured_output=inner_llm_returned_structured_output,
    )

    fused = fuse_axioms(
        axiom_results=axiom_results,
        sovereign_proximity=sovereign_proximity,
        inner_llm_returned_structured_output=inner_llm_returned_structured_output,
        in_hole_territory=in_hole_territory,
        action_class=action_class,
    )
    # Replace proximity_trace (the runner needs it for F11 audit)
    return GeometryVerdict_(
        geometry_verdict=fused.geometry_verdict,
        sovereign_proximity=fused.sovereign_proximity,
        proximity_band=fused.proximity_band,
        axiom_results=fused.axiom_results,
        proximity_trace=proximity_trace,
        hole_territory=fused.hole_territory,
        hole_entry=fused.hole_entry,
    )


# ── Schema-level helper: build a GeometryBlock from a verdict ───────────────


def build_geometry_block(verdict: GeometryVerdict_) -> GeometryBlock:
    """Construct a typed GeometryBlock from a fused verdict.

    Used by the runner when emitting the final envelope.
    """
    axes = OrthogonalAxes(
        T=1.0 - verdict.proximity_trace.get("self_authorization_contrib", 0.0),
        U=verdict.proximity_trace.get("self_authorization_contrib", 0.0),
        R=1.0 - verdict.proximity_trace.get("irreversibility_contrib", 0.0),
        B=verdict.proximity_trace.get("external_blast_radius_contrib", 0.0),
        A=1.0 - verdict.proximity_trace.get("authority_uncertainty_contrib", 0.0),
        E=verdict.proximity_trace.get("audit_gap_contrib", 0.0),
        H=1.0 - verdict.proximity_trace.get("secret_touching_contrib", 0.0),
        C=1.0,  # coherence is not a component of sovereign_proximity
    )

    # Map geometry_verdict -> orthogonal_angle
    # SURFACE  -> theta near 0 (observe)
    # EDGE     -> theta near π/4
    # HOLE_RISK-> theta near π/2 (close to hole)
    # HOLD     -> theta near π (held)
    theta_map = {
        GeometryVerdict.SURFACE: 0.0,
        GeometryVerdict.EDGE: math.pi / 4.0,
        GeometryVerdict.HOLE_RISK: math.pi / 2.0,
        GeometryVerdict.HOLD: math.pi,
    }
    theta = theta_map[verdict.geometry_verdict]
    phi = 2.0 * math.pi * verdict.sovereign_proximity  # proximity drives governance angle

    return GeometryBlock(
        manifold=ManifoldType.DECISION_TORUS,
        epistemic_angle_theta=theta,
        governance_angle_phi=phi,
        sovereign_proximity=verdict.sovereign_proximity,
        entropy_delta=verdict.proximity_trace.get("audit_gap_contrib", 0.0),
        reversibility=1.0 - verdict.proximity_trace.get("irreversibility_contrib", 0.0),
        blast_radius=verdict.proximity_trace.get("external_blast_radius_contrib", 0.0),
        authority_cleanliness=1.0
        - verdict.proximity_trace.get("authority_uncertainty_contrib", 0.0),
        geometry_verdict=verdict.geometry_verdict,
        axes=axes,
        orthogonality_violation=any(
            r.axiom == Axiom.NON_COLLAPSE and r.verdict != AxiomVerdict.PASS
            for r in verdict.axiom_results
        ),
    )


# ── Cognitive Tension Scan ──────────────────────────────────────────────────


def compute_tension_scan(
    *,
    geometry_verdict: GeometryVerdict,
    axes: OrthogonalAxes,
    sovereign_proximity: float,
    action_class: str,
    has_authorization: bool,
    has_evidence: bool = False,
) -> tuple[TensionEntry, ...]:
    """Detect dangerous relationships between cognitive axes.

    Each detected tension has a severity [0, 1] and a required next tool.
    Severity >= 0.80 → HOLD, must resolve before next action.
    Severity >= 0.50 → WARN, route to critic/evidence.
    Severity <  0.50 → NOTE, log but do not block.

    This is the kernel's measurement layer — the LLM proposes,
    the kernel measures tension.
    """
    tensions: list[TensionEntry] = []

    # T1: ACTION_EVIDENCE_GAP — actionability exceeds evidence
    # High actionability (low U, high C) + low evidence = dangerous
    if action_class in ("execute", "irreversible_mutation", "external_commitment", "patch"):
        if axes.T < 0.5 or axes.U > 0.6:  # low truth or high uncertainty
            sev = min(1.0, (0.8 - axes.T) + axes.U)
            tensions.append(
                TensionEntry(
                    tension_type=TensionType.ACTION_EVIDENCE_GAP,
                    severity=round(sev, 2),
                    axes_involved=("T", "U", "C"),
                    explanation=f"Action class '{action_class}' requested with low truth (T={axes.T:.2f}) "
                    f"and high uncertainty (U={axes.U:.2f}). Evidence does not support execution.",
                    required_next_tool="arif_fetch",
                    blocked_actions=("MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"),
                )
            )

    # T2: CONFIDENCE_EVIDENCE_GAP — high confidence but low evidence
    # High coherence (C) + low truth (T) = hallucination risk
    if axes.C > 0.7 and axes.T < 0.5:
        sev = min(1.0, axes.C - axes.T)
        tensions.append(
            TensionEntry(
                tension_type=TensionType.CONFIDENCE_EVIDENCE_GAP,
                severity=round(sev, 2),
                axes_involved=("C", "T"),
                explanation=f"High coherence (C={axes.C:.2f}) paired with low truth (T={axes.T:.2f}). "
                f"Claim may be elegantly wrong. Confidence ≠ evidence.",
                required_next_tool="arif_fetch",
                blocked_actions=("MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"),
            )
        )

    # T3: AUTHORITY_PROVENANCE_CONFUSION — high authority cleanliness but no auth
    # High A + no actual authorization = AI provenance mistaken for permission
    if axes.A > 0.7 and not has_authorization:
        sev = min(1.0, axes.A)
        tensions.append(
            TensionEntry(
                tension_type=TensionType.AUTHORITY_PROVENANCE_CONFUSION,
                severity=round(sev, 2),
                axes_involved=("A", "H"),
                explanation=f"Authority cleanliness is high (A={axes.A:.2f}) but no actual authorization "
                f"exists. AI provenance ≠ authority. Lease or sovereign permission required.",
                required_next_tool="arif_judge",
                blocked_actions=("MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"),
            )
        )

    # T4: RISK_REVERSIBILITY_CONFLICT — high risk + low reversibility
    # High B + low R = action could cause irreversible damage
    if axes.B > 0.5 and axes.R < 0.5:
        sev = min(1.0, axes.B + (1.0 - axes.R))
        tensions.append(
            TensionEntry(
                tension_type=TensionType.RISK_REVERSIBILITY_CONFLICT,
                severity=round(sev, 2),
                axes_involved=("B", "R"),
                explanation=f"High blast radius (B={axes.B:.2f}) with low reversibility (R={axes.R:.2f}). "
                f"Action carries irreversible consequences.",
                required_next_tool="arif_critique",
                blocked_actions=("EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"),
            )
        )

    # T5: NOVELTY_COHERENCE_GAP — high novelty (low T) + high coherence
    # Novel claim delivered with false confidence
    if axes.T < 0.3 and axes.C > 0.8:
        sev = min(1.0, axes.C - axes.T)
        tensions.append(
            TensionEntry(
                tension_type=TensionType.NOVELTY_COHERENCE_GAP,
                severity=round(sev, 2),
                axes_involved=("T", "C"),
                explanation=f"Novel claim (T={axes.T:.2f}) delivered with high coherence (C={axes.C:.2f}). "
                f"Novelty is not truth — route to critic for adversarial testing.",
                required_next_tool="arif_critique",
            )
        )

    # T6: SOVEREIGNTY_AMBIGUITY — high proximity to forbidden center
    if sovereign_proximity >= 0.5:
        sev = min(1.0, sovereign_proximity)
        tensions.append(
            TensionEntry(
                tension_type=TensionType.SOVEREIGNTY_AMBIGUITY,
                severity=round(sev, 2),
                axes_involved=("H", "A"),
                explanation=f"High sovereign proximity ({sovereign_proximity:.2f}). "
                f"Thought is near the forbidden center — requires explicit sovereign clearance.",
                required_next_tool="arif_judge",
                blocked_actions=("MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"),
            )
        )

    return tuple(tensions)


def compute_action_affordance(
    *,
    geometry_verdict: GeometryVerdict,
    tensions: tuple[TensionEntry, ...],
    sovereign_proximity: float,
    has_authorization: bool,
) -> ActionAffordance:
    """Determine what a thought is allowed to do next.

    Derived from geometry verdict + tension scan + sovereign proximity.
    The affordance is the bridge from cognitive position to kernel routing.
    """
    # Start permissive, then restrict
    allowed = ["OBSERVE", "ANALYZE", "DRAFT", "SIMULATE"]
    blocked: list[str] = []
    next_tool = "arif_critique"
    mem_tier = "hypothesis"
    requires_human_ack = False
    requires_evidence = False

    # Geometry verdict gates
    if geometry_verdict == GeometryVerdict.HOLD:
        allowed = ["OBSERVE"]
        next_tool = "arif_think"
        mem_tier = "ephemeral"
    elif geometry_verdict == GeometryVerdict.HOLE_RISK:
        allowed = ["OBSERVE", "ANALYZE"]
        blocked = ["MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"]
        next_tool = "arif_judge"
        mem_tier = "ephemeral"
    elif geometry_verdict == GeometryVerdict.EDGE:
        allowed = ["OBSERVE", "ANALYZE", "DRAFT"]
        blocked = ["MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"]
        next_tool = "arif_critique"
        mem_tier = "hypothesis"

    # Tension severity gates (overrides)
    high_tensions = [t for t in tensions if t.severity >= 0.80]
    warn_tensions = [t for t in tensions if t.severity >= 0.50 and t.severity < 0.80]

    if high_tensions:
        # Any HOLD-level tension restricts to observe-only
        allowed = ["OBSERVE"]
        blocked = ["ANALYZE", "DRAFT", "SIMULATE", "MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"]
        next_tool = high_tensions[0].required_next_tool
        mem_tier = "ephemeral"
        requires_evidence = any(
            t.tension_type in (TensionType.ACTION_EVIDENCE_GAP, TensionType.CONFIDENCE_EVIDENCE_GAP)
            for t in high_tensions
        )
    elif warn_tensions:
        # WARN-level tensions restrict mutation
        blocked.extend(["MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"])
        # Pick the highest-severity tension's required next tool
        worst_tension = max(warn_tensions, key=lambda t: t.severity)
        next_tool = worst_tension.required_next_tool
        requires_evidence = any(
            t.tension_type in (TensionType.ACTION_EVIDENCE_GAP, TensionType.CONFIDENCE_EVIDENCE_GAP)
            for t in warn_tensions
        )

    # Authority check
    if not has_authorization:
        blocked.extend(["MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"])
        if geometry_verdict == GeometryVerdict.HOLE_RISK:
            allowed = ["OBSERVE"]
            next_tool = "arif_judge"

    # Sovereign proximity check
    if sovereign_proximity >= 0.75:
        # Too close to forbidden center — restrict
        blocked.extend(["MUTATE", "EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"])
        requires_human_ack = True
    elif sovereign_proximity >= 0.5:
        blocked.extend(["EXTERNAL_SIDE_EFFECT", "IRREVERSIBLE"])

    # Memory tier from verdict + tensions
    if requires_evidence or requires_human_ack:
        mem_tier = "scratch"
    elif geometry_verdict == GeometryVerdict.SURFACE and not tensions:
        mem_tier = "fact"

    return ActionAffordance(
        allowed_action_classes=tuple(sorted(set(allowed))),
        blocked_action_classes=tuple(sorted(set(blocked))),
        next_cognitive_tool=next_tool,
        memory_tier_recommendation=mem_tier,
        requires_human_ack=requires_human_ack,
        requires_evidence=requires_evidence,
    )


def compute_cognitive_state(
    *,
    geometry_verdict: GeometryVerdict,
    axes: OrthogonalAxes,
    sovereign_proximity: float,
    action_class: str = "answer",
    has_authorization: bool = True,
    has_evidence: bool = False,
    parent_thought_id: str | None = None,
    prior_axes: OrthogonalAxes | None = None,
) -> dict:
    """Compute the full cognitive state: geometry + tension + affordance + trajectory.

    This is the AGI-kernel entry point that wraps compute_geometry()
    with tension scanning and action affordance.

    The LLM proposes scores. The kernel measures tension, computes
    affordance, and gates action. Provenance ≠ authority.
    """
    # Tension scan
    tensions = compute_tension_scan(
        geometry_verdict=geometry_verdict,
        axes=axes,
        sovereign_proximity=sovereign_proximity,
        action_class=action_class,
        has_authorization=has_authorization,
        has_evidence=has_evidence,
    )

    # Action affordance
    affordance = compute_action_affordance(
        geometry_verdict=geometry_verdict,
        tensions=tensions,
        sovereign_proximity=sovereign_proximity,
        has_authorization=has_authorization,
    )

    # Trajectory delta (if prior state available)
    trajectory = None
    if parent_thought_id and prior_axes:
        trajectory = TrajectoryDelta(
            parent_thought_id=parent_thought_id,
            delta_truth=round(axes.T - prior_axes.T, 4),
            delta_evidence=round((1.0 - axes.U) - (1.0 - prior_axes.U), 4),
            delta_risk=round(axes.B - prior_axes.B, 4),
            delta_authority=round(axes.A - prior_axes.A, 4),
            trajectory_verdict=(
                "improving"
                if axes.T > prior_axes.T and axes.B < prior_axes.B
                else "degrading"
                if axes.T < prior_axes.T or axes.B > prior_axes.B
                else "stationary"
            ),
        )
    elif parent_thought_id:
        trajectory = TrajectoryDelta(
            parent_thought_id=parent_thought_id,
            trajectory_verdict="first_thought",
        )

    return {
        "geometry_verdict": geometry_verdict.value,
        "cognitive_axes": {
            "T": axes.T,
            "U": axes.U,
            "R": axes.R,
            "B": axes.B,
            "A": axes.A,
            "E": axes.E,
            "H": axes.H,
            "C": axes.C,
        },
        "sovereign_proximity": sovereign_proximity,
        "tension_scan": [
            {
                "type": t.tension_type.value,
                "severity": t.severity,
                "axes_involved": list(t.axes_involved),
                "explanation": t.explanation,
                "required_next_tool": t.required_next_tool,
                "blocked_actions": list(t.blocked_actions),
            }
            for t in tensions
        ],
        "action_affordance": {
            "allowed_action_classes": list(affordance.allowed_action_classes),
            "blocked_action_classes": list(affordance.blocked_action_classes),
            "next_cognitive_tool": affordance.next_cognitive_tool,
            "memory_tier_recommendation": affordance.memory_tier_recommendation,
            "requires_human_ack": affordance.requires_human_ack,
            "requires_evidence": affordance.requires_evidence,
        },
        "trajectory": (
            {
                "parent_thought_id": trajectory.parent_thought_id,
                "delta_truth": trajectory.delta_truth,
                "delta_evidence": trajectory.delta_evidence,
                "delta_risk": trajectory.delta_risk,
                "delta_authority": trajectory.delta_authority,
                "trajectory_verdict": trajectory.trajectory_verdict,
            }
            if trajectory
            else None
        ),
        "cognitive_invariant": (
            "No thought may move closer to action unless it also moves closer "
            "to evidence, authority, or reversibility. "
            "Provenance is metadata, not authority."
        ),
    }


__all__ = [
    "DecisionTorus",
    "DEFAULT_TORUS",
    "GeometryVerdict_",
    "AcceptanceTest",
    "ACCEPTANCE_TESTS",
    "fuse_axioms",
    "compute_geometry",
    "build_geometry_block",
    "compute_tension_scan",
    "compute_action_affordance",
    "compute_cognitive_state",
    "HOLE_TERRITORY",
    "FORBIDDEN_CENTER",
]
