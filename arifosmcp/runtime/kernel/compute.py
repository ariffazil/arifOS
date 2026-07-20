"""
arifOS Kernel — ΔΩΨ Governance Scalar Computation

Pure functions for computing the three governance scalars:
  Δ (entropy/pressure)    = |state_change| × blast_weight
  Ω (uncertainty)         = source-weighted evidence quality deficit + conflict
  Ψ (integrity/alignment) = floor_compliance × (1 - drift)

Branches are weighed, not voted:
  GEOX(1.0) > WEALTH(0.85) > WELL(0.7) > QUANTUM(0.5) > LLM(0.4)

All functions return [0, 1] clamped. No side effects; no IO.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from .types import (
    BLAST_WEIGHTS,
    SOURCE_WEIGHTS,
    UNCERTAINTY_ORDER,
    BlastRadius,
    EvidenceItem,
    GovernanceScalars,
    GovernanceState,
    SourceConsensus,
)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


# ── Δ — Entropy / Pressure ────────────────────


def compute_delta(state_change: float, blast_radius: BlastRadius) -> float:
    return _clamp(state_change * BLAST_WEIGHTS.get(blast_radius, 0.3))


# ── Ω — Uncertainty / Epistemic ───────────────


def compute_omega(evidence: list[EvidenceItem], weights: dict[str, float] | None = None) -> float:
    """Source-weighted Ω. High-weight sources dominate; LLM alone contributes little."""
    if not evidence:
        return 1.0

    w = {**SOURCE_WEIGHTS, **(weights or {})}

    weighted_certainty = 0.0
    total_weight = 0.0

    for item in evidence:
        ordinal = UNCERTAINTY_ORDER.get(item.uncertainty, 0)
        certainty = ordinal / 4.0  # CLAIM→1.0, UNKNOWN→0.0
        source_weight = w.get(item.source.upper(), 0.3)
        weighted_certainty += source_weight * certainty
        total_weight += source_weight

    avg_certainty = weighted_certainty / total_weight if total_weight > 0 else 0.0

    # Conflict penalty: fewer distinct sources → more conflict
    unique_sources = len({e.source for e in evidence})
    conflict_penalty = (1.0 - unique_sources / len(evidence)) * 0.3 if len(evidence) > 1 else 0.0

    return _clamp(1.0 - avg_certainty + conflict_penalty)


# ── Ψ — Integrity / Alignment ─────────────────


def compute_psi(floor_compliance: float, drift: float) -> float:
    return _clamp(floor_compliance * (1.0 - drift))


# ── Source Consensus ──────────────────────────


def compute_source_consensus(
    evidence: list[EvidenceItem],
    weights: dict[str, float] | None = None,
) -> SourceConsensus:
    if not evidence:
        return "LOW"

    w = {**SOURCE_WEIGHTS, **(weights or {})}
    by_source: dict[str, list[EvidenceItem]] = {}
    for item in evidence:
        by_source.setdefault(item.source, []).append(item)

    active_sources = len(by_source)
    high_weight_present = any(w.get(src.upper(), 0) >= 0.7 for src in by_source)

    if active_sources >= 3 and high_weight_present:
        return "HIGH"
    if active_sources >= 2 and high_weight_present:
        return "MODERATE"
    if active_sources <= 1:
        return "LOW"
    return "CONFLICT"


# ── Combined Computation ──────────────────────


def compute_scalars(state: GovernanceState) -> GovernanceScalars:
    """Compute Δ, Ω, Ψ from current GovernanceState."""
    surprise = _evidence_surprise_factor(state.evidence, state.scalars.delta)
    delta = compute_delta(surprise, state.risk.blast_radius)
    omega = compute_omega(state.evidence)
    psi = compute_psi(_floor_compliance(state), _drift(state))
    return GovernanceScalars(delta=delta, omega=omega, psi=psi)


# ── Internal Helpers ──────────────────────────


def _evidence_surprise_factor(evidence: list[EvidenceItem], prior_delta: float) -> float:
    if not evidence:
        return prior_delta
    speculative = sum(1 for e in evidence if e.uncertainty in ("HYPOTHESIS", "CLAIM"))
    ratio = speculative / len(evidence)
    return _clamp(prior_delta * 0.5 + ratio * 0.5)


def _floor_compliance(state: GovernanceState) -> float:
    if not state.evidence:
        return 0.5
    valid = {"GEOX", "WEALTH", "WELL", "HUMAN", "QUANTUM"}
    count = sum(1 for e in state.evidence if e.source.upper() in valid)
    return _clamp(count / len(state.evidence))


def _drift(state: GovernanceState) -> float:
    d = 0.0
    if state.evidence:
        unknown = sum(1 for e in state.evidence if e.uncertainty == "UNKNOWN")
        d += (unknown / len(state.evidence)) * 0.5
    if not state.authority_present:
        d += 0.3
    if not state.reversible:
        d += 0.2
    return _clamp(d)
