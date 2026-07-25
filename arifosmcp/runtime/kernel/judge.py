"""
arifOS Kernel — 888 Constitutional Collapse

All branches collapse here. This is the only place where:
  - evidence is fused (source-weighted)
  - Δ (entropy/pressure) is evaluated
  - Ω (uncertainty) is evaluated
  - Ψ (integrity/drift) is evaluated
  - 6 tripwires are checked in sequence
  - verdict is assigned (SEAL, SABAR, HOLD, VOID)

Tripwire order (hardening):
  1. AUTHORITY     F13  — no authority → VOID
  2. UNCERTAINTY   F7   — Ω > hard limit → VOID; Ω > max → HOLD
  3. INTEGRITY     F2   — Ψ < min → HOLD
  4. ENTROPY       F4   — Δ critical + Ω elevated → SABAR
  5. REVERSIBILITY F1   — irreversible + uncertain → HOLD
  6. FLOOR         F10  — LLM-only → VOID

Multi-sovereign ordering (P3/ADVERSARIAL):
  F13 competing verdicts resolved by FIRST-SEAL-WINS per Merkle timestamp.
  First valid SEAL on an action chain locks it. Subsequent HOIDs/VOIDs
  from any sovereign on the same chain are recorded but do not override.
  Exception: a later VOID from the SAME sovereign overwrites their own SEAL.
  Rule codified in FLOOR_TABLE.json and enforced in cascade.py.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import time

from .compute import compute_omega, compute_source_consensus
from .types import (
    DELTA_CRITICAL,
    OMEGA_HARD_LIMIT,
    OMEGA_MAX,
    OMEGA_WARN,
    PSI_MIN,
    CollapseResult,
    EvidenceFusion,
    GovernanceState,
    TripwireResult,
    Verdict,
)

# ── 888 Constitutional Collapse ──────────────


def judge(state: GovernanceState) -> GovernanceState:
    """Execute the 888 collapse: run all 6 tripwires, fuse evidence, produce verdict."""
    tripwires: list[TripwireResult] = []

    # Tripwire 1: AUTHORITY
    tw = _check_authority(state)
    tripwires.append(tw)
    if tw.severity == "BLOCK":
        return _build_collapse(state, "VOID", tripwires)

    # Tripwire 2: UNCERTAINTY
    tw = _check_uncertainty(state)
    tripwires.append(tw)
    if tw.severity == "BLOCK":
        return _build_collapse(state, "VOID", tripwires)
    if tw.severity == "DELAY":
        return _build_collapse(state, "HOLD", tripwires)

    # Tripwire 3: INTEGRITY
    tw = _check_integrity(state)
    tripwires.append(tw)
    if tw.severity == "DELAY":
        return _build_collapse(state, "HOLD", tripwires)

    # Tripwire 4: ENTROPY
    tw = _check_entropy(state)
    tripwires.append(tw)
    if tw.severity == "DELAY":
        return _build_collapse(state, "SABAR", tripwires)

    # Tripwire 5: REVERSIBILITY
    tw = _check_reversibility(state)
    tripwires.append(tw)
    if tw.severity == "BLOCK":
        return _build_collapse(state, "HOLD", tripwires)

    # Tripwire 6: FLOOR
    tw = _check_floors(state)
    tripwires.append(tw)
    if tw.severity == "BLOCK":
        return _build_collapse(state, "VOID", tripwires)

    return _build_collapse(state, "SEAL", tripwires)


# ── Tripwire Definitions ──────────────────────


def _check_authority(state: GovernanceState) -> TripwireResult:
    if not state.authority_present:
        return TripwireResult(
            id="AUTHORITY",
            triggered=True,
            reason="F13 SOVEREIGN: No valid authority present. Requires lease, session, or sovereign ack.",
            severity="BLOCK",
        )
    return TripwireResult(
        id="AUTHORITY", triggered=False, reason="Authority present", severity="WARN"
    )


def _check_uncertainty(state: GovernanceState) -> TripwireResult:
    o = state.scalars.omega
    if o > OMEGA_HARD_LIMIT:
        return TripwireResult(
            id="UNCERTAINTY",
            triggered=True,
            reason=f"F7 HUMILITY: Ω={o:.3f} exceeds hard limit {OMEGA_HARD_LIMIT}. Evidence too weak.",
            severity="BLOCK",
        )
    if o > OMEGA_MAX:
        return TripwireResult(
            id="UNCERTAINTY",
            triggered=True,
            reason=f"F7 HUMILITY: Ω={o:.3f} > {OMEGA_MAX}. Epistemic discipline insufficient for SEAL.",
            severity="DELAY",
        )
    return TripwireResult(
        id="UNCERTAINTY", triggered=False, reason=f"Ω={o:.3f} within range", severity="WARN"
    )


def _check_integrity(state: GovernanceState) -> TripwireResult:
    p = state.scalars.psi
    if p < PSI_MIN:
        return TripwireResult(
            id="INTEGRITY",
            triggered=True,
            reason=f"F2 TRUTH: Ψ={p:.3f} < {PSI_MIN}. Floor compliance or drift intolerable.",
            severity="DELAY",
        )
    return TripwireResult(
        id="INTEGRITY", triggered=False, reason=f"Ψ={p:.3f} above minimum", severity="WARN"
    )


def _check_entropy(state: GovernanceState) -> TripwireResult:
    d, o = state.scalars.delta, state.scalars.omega
    if d > DELTA_CRITICAL and o > OMEGA_WARN:
        return TripwireResult(
            id="ENTROPY",
            triggered=True,
            reason=f"F4 CLARITY: Δ={d:.3f} > {DELTA_CRITICAL} with Ω={o:.3f} > {OMEGA_WARN}. Cooling required (900).",
            severity="DELAY",
        )
    return TripwireResult(
        id="ENTROPY", triggered=False, reason=f"Δ={d:.3f} within range", severity="WARN"
    )


def _check_reversibility(state: GovernanceState) -> TripwireResult:
    if not state.reversible and state.scalars.omega > OMEGA_WARN:
        return TripwireResult(
            id="REVERSIBILITY",
            triggered=True,
            reason="F1 AMANAH: Irreversible action with elevated uncertainty. Reduce Ω or add safeguards.",
            severity="BLOCK",
        )
    if not state.reversible:
        return TripwireResult(
            id="REVERSIBILITY",
            triggered=True,
            reason="F1 AMANAH: Irreversible action. Requires explicit sovereign confirmation.",
            severity="WARN",
        )
    return TripwireResult(
        id="REVERSIBILITY", triggered=False, reason="Action is reversible", severity="WARN"
    )


def _check_floors(state: GovernanceState) -> TripwireResult:
    if not state.evidence:
        return TripwireResult(
            id="FLOOR", triggered=True, reason="F4 CLARITY: No evidence provided. Evidence required for SEAL.",
            severity="BLOCK",
        )
    llm_only = all(e.source.upper() in ("LLM", "UNKNOWN") for e in state.evidence)
    if llm_only:
        return TripwireResult(
            id="FLOOR",
            triggered=True,
            reason="F10 ONTOLOGY: LLM-only evidence. At least one GEOX, WEALTH, or WELL source required.",
            severity="BLOCK",
        )
    return TripwireResult(
        id="FLOOR", triggered=False, reason="No floor violations", severity="WARN"
    )


# ── Collapse Builder ──────────────────────────


def _evidence_breakdown(evidence) -> dict[str, int]:
    b: dict[str, int] = {}
    for e in evidence:
        b[e.source] = b.get(e.source, 0) + 1
    return b


def _build_collapse(
    state: GovernanceState,
    verdict: Verdict,
    tripwires: list[TripwireResult],
) -> GovernanceState:
    breakdown = _evidence_breakdown(state.evidence)
    consensus = compute_source_consensus(state.evidence)
    weighted_omega = compute_omega(state.evidence)
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    collapse = CollapseResult(
        verdict=verdict,
        tripwires=tripwires,
        scalars=state.scalars,
        evidence_fusion=EvidenceFusion(
            total_items=len(state.evidence),
            source_breakdown=breakdown,
            weighted_omega=weighted_omega,
            source_consensus=consensus,
        ),
        timestamp=ts,
    )

    return state.clone(phase=888, verdict=verdict, collapse=collapse, timestamp=ts)


# ── Convenience: judge with structured result ──


def judge_with_reason(state: GovernanceState) -> tuple[GovernanceState, CollapseResult]:
    result = judge(state)
    return result, result.collapse  # type: ignore[return-value]
