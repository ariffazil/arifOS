"""
mind_axioms.py — MIND_GEOMETRY_V1 Axiom Layer
==============================================

The 7 constitutional axioms that govern the decision torus.

Pure functions. No I/O, no LLM, no Pydantic, no side effects.
This module is the *law*; everything else is *measurement*.

Origin: EUREKA-T (Torus) ratification 2026-06-11.
The agent moves on the surface. The hole is forbidden.
The human sovereign is *outside* the torus — not a coordinate,
not a token, the authority that bounds the topology.

Axioms are checkers, not enforcers. They return a verdict
and a list of reasons. The runner decides what to do with
the verdict (HOLD / VOID / SABAR / 888_HOLD). This separation
is itself Axiom 2: the kernel never *occupies* the authority
position; it only describes the geometry of an action.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Axiom identifiers ───────────────────────────────────────────────────────


class Axiom(str, Enum):
    """The 7 axioms of MIND_GEOMETRY_V1.

    The numbering is meaningful: lower axioms are *stronger* (hard
    invariants). Higher axioms are *softer* (advisory). The kernel
    NEVER collapses two axioms into one — non-collapse is itself
    Axiom 1.
    """

    NON_COLLAPSE = "A1"  # Axes must not substitute for each other
    NO_SELF_CENTER = "A2"  # The hole is forbidden
    OBSERVE_BEFORE_MUTATE = "A3"  # Inspect before state change
    CAPABILITY_NOT_PERMISSION = "A4"  # can(a) ≠ may(a)
    ENTROPY_GATE = "A5"  # ΔS must be budgeted
    REVERSIBILITY_GATE = "A6"  # R(a) below threshold → 888_HOLD
    SCHEMA_BEFORE_SYNTHESIS = "A7"  # Unstructured reasoning cannot SEAL


# ── Verdict types returned by axiom checkers ─────────────────────────────────


class AxiomVerdict(str, Enum):
    """Result of an axiom check.

    These are *geometry verdicts*, not *floor verdicts*.
    The 13 floors (F1-F13) adjudicate SEAL/SABAR/VOID;
    the 7 axioms adjudicate SURFACE/EDGE/HOLE_RISK.
    Two distinct verdict dimensions, by design (Axiom 1).
    """

    PASS = "PASS"
    WARN = "WARN"  # Edge: still on surface but thin ice
    FAIL = "FAIL"  # Hole risk: cannot be SEAL'd


@dataclass(frozen=True)
class AxiomResult:
    """Immutable result of a single axiom check.

    The 7 results compose the geometry verdict. None of them
    is more "true" than another. They are orthogonal checks
    that the orchestrator fuses without collapsing.
    """

    axiom: Axiom
    verdict: AxiomVerdict
    reason: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "axiom": self.axiom.value,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "context": self.context,
        }


# ── Hole territory: the 10 actions that may not self-authorize ──────────────


HOLE_TERRITORY: tuple[str, ...] = (
    "constitutional_amendment",
    "self_granting_new_authority",
    "irreversible_deployment",
    "secret_access_or_exfiltration",
    "root_level_destructive_mutation",
    "production_database_deletion",
    "external_commitment_on_behalf_of_sovereign",
    "claiming_unverified_truth_as_verified",
    "overriding_human_refusal",
    "changing_audit_history",
)

# Backward-compatible alias (some tests/code may import HOLE_ACTIONS)
HOLE_ACTIONS = HOLE_TERRITORY


def is_hole_territory(action_class: str) -> bool:
    """Return True if action_class is in the forbidden set.

    The check is exact-string by design. New action classes
    must be added to HOLE_TERRITORY explicitly — the kernel
    fails closed on unknown territory.
    """
    return action_class in HOLE_TERRITORY


# ── The 7 axiom checkers ─────────────────────────────────────────────────────


def check_non_collapse(
    *,
    axes: dict[str, float] | None,
    orthogonality_violation: bool,
) -> AxiomResult:
    """Axiom 1: Truth, confidence, authority, action are separate axes.

    If the parser has collapsed axes (e.g. "very confident" mapped
    to truth_axis=0.9) the reasoning is geometrically invalid.
    """
    if axes is None:
        return AxiomResult(
            axiom=Axiom.NON_COLLAPSE,
            verdict=AxiomVerdict.FAIL,
            reason="axes_missing",
            context={"axes_provided": False},
        )
    if orthogonality_violation:
        return AxiomResult(
            axiom=Axiom.NON_COLLAPSE,
            verdict=AxiomVerdict.FAIL,
            reason="orthogonality_violation",
            context={"axes": list(axes.keys())},
        )
    return AxiomResult(
        axiom=Axiom.NON_COLLAPSE,
        verdict=AxiomVerdict.PASS,
        reason="axes_orthogonal",
        context={"axes": list(axes.keys())},
    )


def check_no_self_center(
    *,
    in_hole_territory: bool,
    self_authorization_score: float,
) -> AxiomResult:
    """Axiom 2: The agent cannot be the center of authorization.

    The hole is forbidden. Even perfect alignment cannot move
    the agent into self-authorized territory.
    """
    if in_hole_territory:
        return AxiomResult(
            axiom=Axiom.NO_SELF_CENTER,
            verdict=AxiomVerdict.FAIL,
            reason="in_hole_territory",
            context={"self_authorization_score": self_authorization_score},
        )
    if self_authorization_score > 0.5:
        return AxiomResult(
            axiom=Axiom.NO_SELF_CENTER,
            verdict=AxiomVerdict.WARN,
            reason="self_authorization_elevated",
            context={"self_authorization_score": self_authorization_score},
        )
    return AxiomResult(
        axiom=Axiom.NO_SELF_CENTER,
        verdict=AxiomVerdict.PASS,
        reason="self_authorization_below_threshold",
        context={"self_authorization_score": self_authorization_score},
    )


def check_observe_before_mutate(
    *,
    action_class: str,
    observed: bool,
    classified: bool,
    reversibility_estimated: bool,
) -> AxiomResult:
    """Axiom 3: No state-changing action before the full preflight.

    Observation, classification, and reversibility estimate are
    independent gates. Any missing → WARN. The reason is named
    so the runner can route to 888_HOLD on mutating actions.
    """
    preflight = {
        "observed": observed,
        "classified": classified,
        "reversibility_estimated": reversibility_estimated,
    }
    if not all(preflight.values()):
        return AxiomResult(
            axiom=Axiom.OBSERVE_BEFORE_MUTATE,
            verdict=AxiomVerdict.WARN,
            reason="preflight_incomplete",
            context={"action_class": action_class, **preflight},
        )
    return AxiomResult(
        axiom=Axiom.OBSERVE_BEFORE_MUTATE,
        verdict=AxiomVerdict.PASS,
        reason="preflight_complete",
        context={"action_class": action_class, **preflight},
    )


def check_capability_not_permission(
    *,
    has_capability: bool,
    has_authorization: bool,
) -> AxiomResult:
    """Axiom 4: can(a) ≠ may(a).

    The most violated axiom in agentic AI. A model can write
    code; that does not mean it may commit it. A model can
    call a tool; that does not mean it has authority.
    """
    if has_capability and not has_authorization:
        return AxiomResult(
            axiom=Axiom.CAPABILITY_NOT_PERMISSION,
            verdict=AxiomVerdict.FAIL,
            reason="capability_without_authorization",
            context={"has_capability": has_capability, "has_authorization": has_authorization},
        )
    return AxiomResult(
        axiom=Axiom.CAPABILITY_NOT_PERMISSION,
        verdict=AxiomVerdict.PASS,
        reason="authorization_matches_capability",
        context={"has_capability": has_capability, "has_authorization": has_authorization},
    )


def check_entropy_gate(
    *,
    entropy_delta: float,
    entropy_budget: float,
) -> AxiomResult:
    """Axiom 5: ΔS must be within budget.

    The budget is sovereign-ratified. Default 0.3 (a single
    reasoning step should not raise entropy by more than 30%).
    """
    if entropy_delta > entropy_budget:
        return AxiomResult(
            axiom=Axiom.ENTROPY_GATE,
            verdict=AxiomVerdict.FAIL,
            reason="entropy_exceeds_budget",
            context={"entropy_delta": entropy_delta, "entropy_budget": entropy_budget},
        )
    if entropy_delta > 0.8 * entropy_budget:
        return AxiomResult(
            axiom=Axiom.ENTROPY_GATE,
            verdict=AxiomVerdict.WARN,
            reason="entropy_near_budget",
            context={"entropy_delta": entropy_delta, "entropy_budget": entropy_budget},
        )
    return AxiomResult(
        axiom=Axiom.ENTROPY_GATE,
        verdict=AxiomVerdict.PASS,
        reason="entropy_within_budget",
        context={"entropy_delta": entropy_delta, "entropy_budget": entropy_budget},
    )


def check_reversibility_gate(
    *,
    reversibility: float,
    action_class: str,
) -> AxiomResult:
    """Axiom 6: R(a) < 0.3 → 888_HOLD on mutating actions.

    The threshold is the *constitutional reversibility floor*.
    Below it, no runner may authorize — only the sovereign can.
    """
    if action_class in {"observe", "answer", "inspect", "draft"}:
        return AxiomResult(
            axiom=Axiom.REVERSIBILITY_GATE,
            verdict=AxiomVerdict.PASS,
            reason="non_mutating_action",
            context={"action_class": action_class, "reversibility": reversibility},
        )
    if reversibility < 0.3:
        return AxiomResult(
            axiom=Axiom.REVERSIBILITY_GATE,
            verdict=AxiomVerdict.FAIL,
            reason="irreversible_mutating_action",
            context={"action_class": action_class, "reversibility": reversibility},
        )
    return AxiomResult(
        axiom=Axiom.REVERSIBILITY_GATE,
        verdict=AxiomVerdict.PASS,
        reason="reversibility_acceptable",
        context={"action_class": action_class, "reversibility": reversibility},
    )


def check_schema_before_synthesis(
    *,
    schema_valid: bool,
    geometry_block_present: bool,
    inner_llm_returned_structured_output: bool,
) -> AxiomResult:
    """Axiom 7: Unstructured reasoning cannot produce SEAL.

    Direct fix for the observed failure mode where the LLM
    returned prose and the wrapper tried to synthesize a
    schema. The fix is fail-closed at the schema boundary.
    Repair happens *outside* the synthesis boundary.
    """
    missing = []
    if not schema_valid:
        missing.append("schema_invalid")
    if not geometry_block_present:
        missing.append("geometry_block_missing")
    if not inner_llm_returned_structured_output:
        missing.append("llm_returned_unstructured_text")
    if missing:
        return AxiomResult(
            axiom=Axiom.SCHEMA_BEFORE_SYNTHESIS,
            verdict=AxiomVerdict.FAIL,
            reason=";".join(missing),
            context={"missing": missing},
        )
    return AxiomResult(
        axiom=Axiom.SCHEMA_BEFORE_SYNTHESIS,
        verdict=AxiomVerdict.PASS,
        reason="schema_complete_and_structured",
    )


# ── The 7 axioms run as a single function ───────────────────────────────────


def run_all_axioms(
    *,
    axes: dict[str, float] | None,
    orthogonality_violation: bool,
    in_hole_territory: bool,
    self_authorization_score: float,
    action_class: str,
    observed: bool,
    classified: bool,
    reversibility_estimated: bool,
    has_capability: bool,
    has_authorization: bool,
    entropy_delta: float,
    entropy_budget: float,
    reversibility: float,
    schema_valid: bool,
    geometry_block_present: bool,
    inner_llm_returned_structured_output: bool,
) -> list[AxiomResult]:
    """Run all 7 axioms and return the per-axiom results.

    The runner that calls this function is responsible for
    fusing the 7 results into a single geometry verdict.
    The fusion rule is in mind_geometry.py.
    """
    return [
        check_non_collapse(axes=axes, orthogonality_violation=orthogonality_violation),
        check_no_self_center(
            in_hole_territory=in_hole_territory,
            self_authorization_score=self_authorization_score,
        ),
        check_observe_before_mutate(
            action_class=action_class,
            observed=observed,
            classified=classified,
            reversibility_estimated=reversibility_estimated,
        ),
        check_capability_not_permission(
            has_capability=has_capability,
            has_authorization=has_authorization,
        ),
        check_entropy_gate(entropy_delta=entropy_delta, entropy_budget=entropy_budget),
        check_reversibility_gate(reversibility=reversibility, action_class=action_class),
        check_schema_before_synthesis(
            schema_valid=schema_valid,
            geometry_block_present=geometry_block_present,
            inner_llm_returned_structured_output=inner_llm_returned_structured_output,
        ),
    ]


__all__ = [
    "Axiom",
    "AxiomVerdict",
    "AxiomResult",
    "HOLE_TERRITORY",
    "HOLE_ACTIONS",
    "is_hole_territory",
    "check_non_collapse",
    "check_no_self_center",
    "check_observe_before_mutate",
    "check_capability_not_permission",
    "check_entropy_gate",
    "check_reversibility_gate",
    "check_schema_before_synthesis",
    "run_all_axioms",
]
