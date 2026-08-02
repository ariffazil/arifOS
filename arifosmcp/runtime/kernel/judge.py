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
    OMEGA_ZERO_MAX,
    OMEGA_ZERO_MIN,
    PSI_MIN,
    PSI_MIN_OBS,
    PSI_MIN_DER,
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

    # Tripwire 2.5: OMEGA_ZERO_BAND (F7 — Gödel Lock)
    tw = _check_omega_zero_band(state)
    tripwires.append(tw)
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

    # Tripwire 5.5: RASA DERITA — causal cascade + consent lease (Phase 3)
    tw = _check_rasa_derita(state)
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


def _check_omega_zero_band(state: GovernanceState) -> TripwireResult:
    """F7 HUMILITY: Ω₀ must fall within [0.03, 0.05] — no fake certainty, no fake humility."""
    oz = state.scalars.omega_zero
    if oz < OMEGA_ZERO_MIN:
        return TripwireResult(
            id="OMEGA_ZERO_BAND",
            triggered=True,
            reason=f"F7 HUMILITY: Ω₀={oz:.4f} < {OMEGA_ZERO_MIN}. Overconfidence detected — "
            f"confidence too high. Cap at {OMEGA_ZERO_MIN}.",
            severity="DELAY",
        )
    if oz > OMEGA_ZERO_MAX:
        return TripwireResult(
            id="OMEGA_ZERO_BAND",
            triggered=True,
            reason=f"F7 HUMILITY: Ω₀={oz:.4f} > {OMEGA_ZERO_MAX}. Over-humility detected — "
            f"uncertainty band too wide. Tighten to ≤ {OMEGA_ZERO_MAX}.",
            severity="DELAY",
        )
    return TripwireResult(
        id="OMEGA_ZERO_BAND",
        triggered=False,
        reason=f"Ω₀={oz:.4f} within [{OMEGA_ZERO_MIN}, {OMEGA_ZERO_MAX}]",
        severity="WARN",
    )


def _check_integrity(state: GovernanceState) -> TripwireResult:
    """F2 TRUTH: dual-mode integrity check (Compression-Kernel Doctrine, 2026-08-02).

    LIT (OBS/CLAIM): PSI ≥ 0.99 — direct observation, near-certain, range-encoded precision.
    REF (DER/INT/SPEC): PSI ≥ 0.85 — derivation inherits + decays from source.
    Base fallback: PSI ≥ 0.70 — ambiguous evidence class.

    The threshold is determined by the dominant evidence class:
    - If evidence is mostly CLAIM (OBS) → use PSI_MIN_OBS (0.99)
    - If evidence is mostly PLAUSIBLE/HYPOTHESIS (DER/INT) → use PSI_MIN_DER (0.85)
    - Otherwise → use PSI_MIN (0.70, fallback)
    """
    p = state.scalars.psi

    # Determine the appropriate F2 threshold from evidence composition
    evidence = state.evidence
    if not evidence:
        psi_threshold = PSI_MIN
        threshold_label = "FALLBACK (no evidence)"
    else:
        obs_count = sum(1 for e in evidence if e.uncertainty in ("CLAIM",))
        der_count = sum(1 for e in evidence if e.uncertainty in ("PLAUSIBLE", "HYPOTHESIS"))
        total = obs_count + der_count
        if total == 0:
            psi_threshold = PSI_MIN
            threshold_label = f"FALLBACK (PSI_MIN={PSI_MIN})"
        elif obs_count >= der_count:
            psi_threshold = PSI_MIN_OBS
            threshold_label = f"OBS (PSI_MIN_OBS={PSI_MIN_OBS})"
        else:
            psi_threshold = PSI_MIN_DER
            threshold_label = f"DER (PSI_MIN_DER={PSI_MIN_DER})"

    if p < psi_threshold:
        return TripwireResult(
            id="INTEGRITY",
            triggered=True,
            reason=(
                f"F2 TRUTH: Ψ={p:.3f} < {psi_threshold} ({threshold_label}). "
                f"Floor compliance or drift intolerable. "
                f"obs_evidence={obs_count if evidence else 0} "
                f"der_evidence={der_count if evidence else 0}"
            ),
            severity="DELAY",
        )
    return TripwireResult(
        id="INTEGRITY",
        triggered=False,
        reason=f"Ψ={p:.3f} ≥ {psi_threshold} ({threshold_label})",
        severity="WARN",
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


def _check_rasa_derita(state: GovernanceState) -> TripwireResult:
    """RASA DERITA Phase 3: cascade + consent for L3+/irreversible mutation."""
    try:
        from arifosmcp.kernel.rasa_derita_gates import evaluate_mutation_gates

        blast = getattr(state.risk, "blast_radius", None)
        verdict = evaluate_mutation_gates(
            mode=getattr(state, "action_mode", None),
            action_tier=getattr(state, "action_tier", None),
            reversible=state.reversible,
            blast_radius=str(blast) if blast is not None else None,
            causal_cascade=getattr(state, "causal_cascade", None),
            consent_lease=getattr(state, "consent_lease", None),
            require_consent=bool(getattr(state, "requires_consent", False)),
        )
        if not verdict.passed:
            return TripwireResult(
                id="RASA_DERITA",
                triggered=True,
                reason=" | ".join(verdict.reasons) or "RASA DERITA gate failed — 888_HOLD",
                severity="BLOCK",
            )
        return TripwireResult(
            id="RASA_DERITA",
            triggered=False,
            reason=verdict.reasons[0] if verdict.reasons else "RASA DERITA gates clear",
            severity="WARN",
        )
    except Exception as exc:
        # Fail-closed on gate module failure for irreversible paths
        if not state.reversible:
            return TripwireResult(
                id="RASA_DERITA",
                triggered=True,
                reason=f"RASA DERITA gate unavailable on irreversible path: {exc}",
                severity="BLOCK",
            )
        return TripwireResult(
            id="RASA_DERITA",
            triggered=False,
            reason=f"RASA DERITA gate soft-skip (reversible): {exc}",
            severity="WARN",
        )


def _check_floors(state: GovernanceState) -> TripwireResult:
    if not state.evidence:
        return TripwireResult(
            id="FLOOR",
            triggered=True,
            reason="F4 CLARITY: No evidence provided. Evidence required for SEAL.",
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
