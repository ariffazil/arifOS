"""
arifOS Kernel — 000-999 Metabolic Phase Transitions

(m, E, R) → kernel → (m', E', R')

Constraints:
  - No direct jump to 999 without passing 888.
  - No action execution without V ∈ {SEAL, SABAR} and authority present.
  - Phases advance monotonically.
  - 900 (COOL) is optional — skip on low Δ.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from collections.abc import Callable
from dataclasses import dataclass

from .compute import compute_scalars
from .types import (
    PHASE_ORDER,
    EvidenceItem,
    GovernanceScalars,
    GovernanceState,
    Phase,
)


class PhaseTransitionError(Exception):
    def __init__(self, message: str, from_phase: Phase, to_phase: Phase):
        self.from_phase = from_phase
        self.to_phase = to_phase
        super().__init__(message)


def validate_transition(from_phase: Phase, to_phase: Phase) -> None:
    from_idx = PHASE_ORDER[from_phase]
    to_idx = PHASE_ORDER[to_phase]

    if to_idx < from_idx:
        raise PhaseTransitionError(
            f"Phase regression: {from_phase} → {to_phase} not allowed",
            from_phase,
            to_phase,
        )
    if to_phase == 999 and not _has_passed(from_phase, 888):
        raise PhaseTransitionError(
            f"Cannot reach 999 without passing 888 (from {from_phase})",
            from_phase,
            to_phase,
        )
    if to_idx - from_idx > 2:
        raise PhaseTransitionError(
            f"Phase skip too large: {from_phase} → {to_phase}",
            from_phase,
            to_phase,
        )


def _has_passed(current: Phase, target: Phase) -> bool:
    return PHASE_ORDER[current] >= PHASE_ORDER[target]


# ── 000 — Intent Ingestion ─────────────────────


def ingest_intent(
    intent: object,
    authority_present: bool = False,
    reversible: bool = False,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> GovernanceState:
    return GovernanceState(
        phase=0,
        evidence=[],
        authority_present=authority_present,
        reversible=reversible,
        actor_id=actor_id,
        session_id=session_id,
    )


# ── 111 — Evidence Ingestion ──────────────────


def ingest_evidence(
    state: GovernanceState,
    new_evidence: list[EvidenceItem],
) -> GovernanceState:
    updated = state.clone(
        phase=111,
        evidence=state.evidence + new_evidence,
    )
    scalars = compute_scalars(updated)
    return state.clone(phase=111, evidence=updated.evidence, scalars=scalars)


# ── 333 — Reasoning ───────────────────────────


def think(state: GovernanceState) -> GovernanceState:
    scalars = compute_scalars(state)
    reduced_omega = min(scalars.omega, state.scalars.omega * 0.95)
    updated_scalars = GovernanceScalars(delta=scalars.delta, omega=reduced_omega, psi=scalars.psi)
    return state.clone(phase=333, scalars=updated_scalars)


# ── 555 — Risk Critique ───────────────────────


def critique(state: GovernanceState) -> GovernanceState:
    d = state.scalars.delta
    if d > 0.7:
        br = "CRITICAL"
    elif d > 0.4:
        br = "HIGH"
    elif d > 0.2:
        br = "MEDIUM"
    else:
        br = state.risk.blast_radius
    # RiskProfile is a simple dataclass; clone via copy
    return state.clone(phase=555, risk=state.risk)


# ── 777 — Action Preparation ──────────────────


def prepare_action(state: GovernanceState) -> GovernanceState:
    scalars = compute_scalars(state)
    return state.clone(phase=777, scalars=scalars)


# ── 888 — Judgment (delegates to judge.py) ───

from .judge import judge as _judge  # noqa: E402


def run_judge(state: GovernanceState, judge_fn: Callable | None = None) -> GovernanceState:
    fn = judge_fn or _judge
    result = fn(state.clone(phase=888))
    return result


# ── 900 — Cooling ─────────────────────────────


def cool(state: GovernanceState) -> GovernanceState:
    if state.scalars.delta < 0.3:
        return state.clone(phase=900)  # skip actual cooling

    # Downgrade CLAIM → HYPOTHESIS to reduce speculative weight
    filtered = [
        EvidenceItem(
            id=e.id,
            source=e.source,
            payload=e.payload,
            uncertainty="HYPOTHESIS" if e.uncertainty == "CLAIM" else e.uncertainty,
            lineage_id=e.lineage_id,
            timestamp=e.timestamp,
        )
        for e in state.evidence
    ]
    cooled = state.clone(phase=900, evidence=filtered)
    scalars = compute_scalars(cooled)
    cooled_scalars = GovernanceScalars(
        delta=scalars.delta * 0.8,
        omega=scalars.omega,
        psi=scalars.psi,
    )
    return state.clone(phase=900, evidence=filtered, scalars=cooled_scalars)


# ── 999 — Seal ────────────────────────────────


def pipeline_seal(state: GovernanceState) -> GovernanceState:
    if state.verdict not in ("SEAL", "SABAR"):
        raise ValueError(f"Cannot seal with verdict '{state.verdict}'. Only SEAL or SABAR.")
    return state.clone(phase=999)


# ── Full Pipeline Runner ──────────────────────


@dataclass
class PipelineResult:
    state: GovernanceState
    transitions: list[Phase]
    errors: list[PhaseTransitionError]


def run_pipeline(
    initial: GovernanceState,
    judge_fn: Callable | None = None,
) -> PipelineResult:
    """Run 000→111→333→555→777→888→(900)→999 with transition validation.

    HOLD/VOID/SABAR stop after 888 without raising — only SEAL/SABAR advance to 999.
    900 COOL is entered only on SEAL/SABAR when Δ ≥ 0.3 (else soft-skip still marks 900).
    """
    transitions: list[Phase] = [initial.phase]
    errors: list[PhaseTransitionError] = []
    state = initial
    fn = judge_fn or _judge

    def _to_111(s: GovernanceState) -> GovernanceState:
        # If evidence already present at phase 0, promote to 111 without loss.
        if s.phase == 0:
            return ingest_evidence(s, []) if s.evidence else s.clone(phase=111)
        return s

    # Pre-judge spine (no seal yet)
    pre_seal_steps: list[tuple[Phase, Callable[[GovernanceState], GovernanceState]]] = [
        (111, _to_111),
        (333, think),
        (555, critique),
        (777, prepare_action),
        (888, lambda s: run_judge(s, fn)),
    ]

    for target_phase, step_fn in pre_seal_steps:
        try:
            if state.phase == target_phase and target_phase != 888:
                # already at phase (e.g. started mid-pipeline) — still record
                transitions.append(state.phase)
                continue
            validate_transition(state.phase, target_phase)
            state = step_fn(state)
            transitions.append(state.phase)
        except PhaseTransitionError as e:
            errors.append(e)
            return PipelineResult(state=state, transitions=transitions, errors=errors)
        except Exception as e:  # noqa: BLE001 — surface as transition error
            errors.append(
                PhaseTransitionError(str(e), state.phase, target_phase)  # type: ignore[arg-type]
            )
            return PipelineResult(state=state, transitions=transitions, errors=errors)

    # Post-888: only SEAL/SABAR may cool + seal. HOLD/VOID stop cleanly (0 raise).
    if state.verdict not in ("SEAL", "SABAR"):
        return PipelineResult(state=state, transitions=transitions, errors=errors)

    try:
        validate_transition(state.phase, 900)
        state = cool(state)
        transitions.append(state.phase)
    except PhaseTransitionError as e:
        errors.append(e)
        return PipelineResult(state=state, transitions=transitions, errors=errors)

    try:
        validate_transition(state.phase, 999)
        state = pipeline_seal(state)
        transitions.append(state.phase)
    except PhaseTransitionError as e:
        errors.append(e)
    except ValueError as e:
        # Defensive — pipeline_seal raises ValueError if verdict drifted
        errors.append(PhaseTransitionError(str(e), state.phase, 999))

    return PipelineResult(state=state, transitions=transitions, errors=errors)
