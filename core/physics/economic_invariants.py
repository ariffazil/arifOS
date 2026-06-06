"""
core/physics/economic_invariants.py — 12 Economic-Physics Invariants + Emergence Layer

Callable enforcement layer for the invariants declared in
`core/physics/ECONOMIC_INVARIANTS.md`.

Each invariant is exposed as a canonical check function.
Hidden backward-compatible aliases are provided at module bottom
for legacy test suites and internal callers.

EMERGENCE LAYER (v2026.05.11-EMBODY+):
  Psychology / Power / Intelligence emergence checks sit above the
  12 substrate invariants. They model second-order effects that arise
  from the interaction of many economic agents.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import math
from typing import Any

from core.physics.thermodynamics_hardened import (
    LANDAUER_MIN,
    MAX_ENTROPY_DELTA,
    ThermodynamicBudget,
    ThermodynamicError,
    get_thermodynamic_budget,
    vector_orthogonality,
)

# ═══════════════════════════════════════════════════════
# EXCEPTIONS — Substrate (12 Economic-Physics)
# ═══════════════════════════════════════════════════════


class EconomicInvariantError(ThermodynamicError):
    """Base for all economic-physics invariant breaches."""

    def __init__(self, message: str, *, invariant: str, verdict: str = "VOID"):
        super().__init__(message, law_id="F4", verdict=verdict)
        self.invariant = invariant


class ConservationError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I01_conservation", verdict="VOID")


class EntropicCostError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I02_entropic_cost", verdict="VOID")


class LandauerAsymmetryError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I03_landauer_asymmetry", verdict="VOID")


class ThermodynamicBudgetError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I04_thermo_budget", verdict="888_HOLD")


class ScarcityAbundanceError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I05_scarcity_abundance", verdict="SABAR")


class NpvEntropyError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I06_npv_entropy", verdict="PARTIAL")


class MarketCollapseError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I07_mode_collapse", verdict="VOID")


class IrreversibilityError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I08_irreversibility", verdict="HOLD")


class GeniusDisciplineError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I09_genius_discipline", verdict="PARTIAL")


class HysteresisError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I10_hysteresis", verdict="QUALIFY")


class SpeedLimitError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I11_speed_limit", verdict="SABAR")


class LedgerConservationError(EconomicInvariantError):
    def __init__(self, message: str):
        super().__init__(message, invariant="I12_ledger_conservation", verdict="VOID")


# ═══════════════════════════════════════════════════════
# EXCEPTIONS — Emergence Layer (Psychology / Power / Intelligence)
# ═══════════════════════════════════════════════════════


class EmergenceError(EconomicInvariantError):
    """Base for all emergence-layer breaches."""

    def __init__(self, message: str, *, layer: str, verdict: str = "SABAR"):
        super().__init__(message, invariant=f"E_{layer}", verdict=verdict)
        self.layer = layer


class PsychologicalDistortionError(EmergenceError):
    """
    E_PSI: Cognitive/affective distortion detected in agent decision topology.
    Maps to F5 (Peace) and F6 (Empathy) when bias erodes stakeholder dignity.
    """

    def __init__(self, message: str):
        super().__init__(message, layer="PSI", verdict="SABAR")


class PowerConsolidationError(EmergenceError):
    """
    E_PWR: Power asymmetry has crossed into coercion or capture.
    Maps to F1 (Amanah) when irreversible, F5 (Peace) when dignity is violated.
    """

    def __init__(self, message: str):
        super().__init__(message, layer="PWR", verdict="HOLD")


class IntelligenceEmergenceError(EmergenceError):
    """
    E_INT: System intelligence exhibits supervenient drift or telos divergence.
    Maps to F8 (Genius) and L10 (Ontology). NEVER claims consciousness (F9 safe).
    """

    def __init__(self, message: str):
        super().__init__(message, layer="INT", verdict="888_HOLD")


# ═══════════════════════════════════════════════════════
# CANONICAL CHECKS — 12 Economic-Physics Invariants
# ═══════════════════════════════════════════════════════


def check_conservation_of_value(
    v_in: float,
    v_out: float,
    v_generated: float = 0.0,
    v_dissipated: float = 0.0,
    v_locked: float = 0.0,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Inv-1: Conservation of Allocated Value."""
    lhs = v_in + v_generated
    rhs = v_out + v_dissipated + v_locked
    delta = abs(lhs - rhs)
    passed = delta <= tolerance
    if not passed:
        raise ConservationError(
            f"Value conservation VIOLATED: Δ={delta:.6e} "
            f"(lhs={lhs}, rhs={rhs}). Ex-nihilo creation or destruction detected."
        )
    return {"invariant": "I01", "passed": True, "delta": delta}


def check_entropic_cost(
    bits_resolved: int,
    claimed_delta_s: float,
    min_entropy_per_bit: float | None = None,
) -> dict[str, Any]:
    """Inv-2: Entropic Cost of Transaction."""
    min_cost = (min_entropy_per_bit or (1.380649e-23 * math.log(2))) * max(bits_resolved, 1)
    effective_min = max(min_cost, 1e-12)
    if claimed_delta_s < 0 and abs(claimed_delta_s) < effective_min:
        raise EntropicCostError(
            f"Claimed ΔS={claimed_delta_s:.4e} below minimum entropic cost "
            f"for {bits_resolved} bits (min={effective_min:.4e})."
        )
    return {"invariant": "I02", "passed": True, "min_cost": effective_min}


def check_landauer_asymmetry(
    bits_resolved: int,
    actual_cost_joules: float,
    temperature_k: float = 300.0,
) -> dict[str, Any]:
    """Inv-3: Landauer Limit on Information Asymmetry."""
    min_joules = bits_resolved * LANDAUER_MIN * (temperature_k / 300.0)
    if actual_cost_joules < min_joules and bits_resolved > 0:
        raise LandauerAsymmetryError(
            f"Discovery cost {actual_cost_joules:.4e} J < Landauer minimum "
            f"{min_joules:.4e} J for {bits_resolved} bits. Suspiciously cheap."
        )
    return {"invariant": "I03", "passed": True, "min_joules": min_joules}


def check_thermodynamic_budget(
    session_id: str,
    projected_cost: float = 0.0,
) -> dict[str, Any]:
    """Inv-4: Thermodynamic Budget Constraint."""
    try:
        budget = get_thermodynamic_budget(session_id)
    except ThermodynamicError:
        budget = ThermodynamicBudget(session_id=session_id, initial_budget=1.0)
    if budget.is_exhausted:
        raise ThermodynamicBudgetError(
            f"Session {session_id} budget EXHAUSTED: "
            f"{budget.consumed:.4e} J consumed / {budget.initial_budget:.4e} J total."
        )
    if projected_cost > 0 and projected_cost > budget.remaining:
        raise ThermodynamicBudgetError(
            f"Projected cost {projected_cost:.4e} J exceeds remaining "
            f"budget {budget.remaining:.4e} J for session {session_id}."
        )
    return {
        "invariant": "I04",
        "passed": True,
        "remaining_joules": budget.remaining,
        "depletion_ratio": budget.depletion_ratio,
    }


def check_scarcity_abundance_orthogonality(
    abundance_score: float,
    scarcity_score: float,
    h_bar_eff: float = 1e-3,
) -> dict[str, Any]:
    """Inv-5: Scarcity-Abundance Orthogonality."""
    product = abundance_score * scarcity_score
    if product < h_bar_eff:
        raise ScarcityAbundanceError(
            f"Orthogonality breach: abundance={abundance_score} * scarcity={scarcity_score} "
            f"= {product:.6e} < ℏ_eff={h_bar_eff}. Universal abundance claim rejected."
        )
    return {"invariant": "I05", "passed": True, "product": product}


def check_npv_entropy_gradient(
    npv: float,
    delta_s: float,
    strict: bool = False,
) -> dict[str, Any]:
    """Inv-6: NPV as Entropy Gradient."""
    if strict and npv > 0 and delta_s >= 0:
        raise NpvEntropyError(
            f"NPV={npv:.4f} > 0 but ΔS={delta_s:.4f} ≥ 0. "
            f"Positive value creation without entropy reduction is heat waste."
        )
    if npv > 0 and delta_s > MAX_ENTROPY_DELTA:
        return {
            "invariant": "I06",
            "passed": False,
            "warning": True,
            "npv": npv,
            "delta_s": delta_s,
        }
    return {"invariant": "I06", "passed": True, "npv": npv, "delta_s": delta_s}


def check_mode_collapse_market(
    participant_vectors: list[list[float]],
    threshold: float = 0.95,
) -> dict[str, Any]:
    """Inv-7: Mode Collapse in Market Concentration."""
    n = len(participant_vectors)
    if n < 2:
        return {"invariant": "I07", "passed": True, "min_ortho": 1.0}
    min_ortho = 1.0
    worst_pair = (0, 1)
    for i in range(n):
        for j in range(i + 1, n):
            try:
                ortho = vector_orthogonality(participant_vectors[i], participant_vectors[j])
            except Exception:
                ortho = 0.0
            if ortho < min_ortho:
                min_ortho = ortho
                worst_pair = (i, j)
    if min_ortho < threshold:
        raise MarketCollapseError(
            f"Market mode collapse: min Ω_ortho={min_ortho:.4f} < {threshold} "
            f"(worst pair {worst_pair}). Echo chamber / monopoly risk."
        )
    return {"invariant": "I07", "passed": True, "min_ortho": min_ortho}


def check_irreversibility_commitment(
    is_irreversible: bool,
    ack_irreversible: bool = False,
) -> dict[str, Any]:
    """Inv-8: Irreversibility of Capital Commitment."""
    if is_irreversible and not ack_irreversible:
        raise IrreversibilityError(
            "Irreversible capital commitment detected without sovereign ack. "
            "F1 Amanah requires explicit acknowledgment."
        )
    return {"invariant": "I08", "passed": True, "ack": ack_irreversible}


def check_genius_discipline(
    genius_score: float,
    target_verdict: str = "SEAL",
    threshold: float = 0.80,
) -> dict[str, Any]:
    """Inv-9: Genius Discipline in Resource Allocation."""
    if target_verdict.upper() == "SEAL" and genius_score < threshold:
        raise GeniusDisciplineError(
            f"Genius score G={genius_score:.4f} < {threshold}. "
            f"Capital deployment denied SEAL — elegance/correctness insufficient."
        )
    return {"invariant": "I09", "passed": True, "G": genius_score}


def check_hysteresis_wealth(
    has_path_history: bool,
    hysteresis_parameter: float | None = None,
) -> dict[str, Any]:
    """Inv-10: Hysteresis of Wealth Accumulation."""
    if not has_path_history:
        raise HysteresisError(
            "Wealth evaluation lacks path history. "
            "VAULT999 trace required for deterministic equivalence."
        )
    return {
        "invariant": "I10",
        "passed": True,
        "hysteresis": hysteresis_parameter,
        "has_history": has_path_history,
    }


def check_speed_limit_value(
    computation_ms: float,
    consensus_depth: int,
    audit_trail_length: int,
    claimed_settlement_ms: float,
) -> dict[str, Any]:
    """Inv-11: Speed Limit on Value Transfer."""
    causal_bandwidth_ms = (
        computation_ms
        * (1 + 0.1 * math.log1p(consensus_depth))
        * (1 + 0.05 * math.log1p(audit_trail_length))
    )
    if claimed_settlement_ms < causal_bandwidth_ms * 0.01:
        raise SpeedLimitError(
            f"Claimed settlement {claimed_settlement_ms:.2f} ms << causal bandwidth "
            f"{causal_bandwidth_ms:.2f} ms (compute={computation_ms}, "
            f"consensus={consensus_depth}, audit={audit_trail_length})."
        )
    return {
        "invariant": "I11",
        "passed": True,
        "causal_bandwidth_ms": causal_bandwidth_ms,
    }


def check_ledger_conservation(
    payload_hash: str | None,
    prior_vault_hash: str | None,
    sealed_within_timeout: bool = True,
) -> dict[str, Any]:
    """Inv-12: Immutable Ledger Conservation."""
    if not payload_hash:
        raise LedgerConservationError(
            "Missing payload hash. Economic transition is uncommitted and may be rolled back."
        )
    if not prior_vault_hash:
        return {"invariant": "I12", "passed": True, "genesis": True}
    if not sealed_within_timeout:
        raise LedgerConservationError(
            "Payload hash exists but VAULT999 seal exceeded τ_max. Transition is latent, not committed."
        )
    return {
        "invariant": "I12",
        "passed": True,
        "payload_hash": payload_hash,
        "prior_hash": prior_vault_hash,
    }


# ═══════════════════════════════════════════════════════
# EMERGENCE LAYER — Psychology / Power / Intelligence
# ═══════════════════════════════════════════════════════


def check_psychological_distortion(
    cognitive_bias_index: float,
    affective_contagion: float,
    cognitive_load_ratio: float,
    epistemic_confidence_without_evidence: float = 0.0,
    bias_threshold: float = 0.35,
    contagion_threshold: float = 0.60,
    load_threshold: float = 0.85,
) -> dict[str, Any]:
    """
    E_PSI: Psychology Emergence Check.

    Measures whether aggregate agent psychology has distorted the
    economic-physics substrate. High bias + high contagion + high load
    creates a "madness of crowds" that violates F5 (Peace) and F6 (Empathy).

    Parameters:
        cognitive_bias_index: [0,1] composite of anchoring / availability / loss-aversion
        affective_contagion: [0,1] herding / emotional cascade multiplier
        cognitive_load_ratio: [0,1] decision fatigue vs thermodynamic budget
        epistemic_confidence_without_evidence: [0,1] affective confidence (feeling right without being right)

    Returns:
        {"passed", "distortion_score", "sub_checks"}
    """
    # Weighted distortion: contagion is the dominant emergent term (nonlinear)
    distortion_score = (
        0.25 * cognitive_bias_index
        + 0.45 * math.pow(affective_contagion, 2)
        + 0.20 * cognitive_load_ratio
        + 0.10 * epistemic_confidence_without_evidence
    )

    sub_checks = {
        "cognitive_bias": cognitive_bias_index <= bias_threshold,
        "affective_contagion": affective_contagion <= contagion_threshold,
        "cognitive_load": cognitive_load_ratio <= load_threshold,
        "affective_confidence": epistemic_confidence_without_evidence < 0.50,
    }

    failed = [k for k, v in sub_checks.items() if not v]

    if distortion_score > 0.55 or len(failed) >= 2:
        raise PsychologicalDistortionError(
            f"Psychological distortion score={distortion_score:.3f} exceeds safe threshold. "
            f"Failed sub-checks: {failed}. "
            f"Economic substrate is being warped by cognitive/affective emergence."
        )

    return {
        "invariant": "E_PSI",
        "passed": True,
        "distortion_score": round(distortion_score, 4),
        "sub_checks": sub_checks,
    }


def check_power_consolidation(
    pareto_ratio: float,
    exit_barrier: float,
    consent_ratio: float,
    authority_drift: float = 0.0,
    capture_index: float = 0.0,
    pareto_threshold: float = 0.80,
    exit_threshold: float = 0.70,
    consent_threshold: float = 0.30,
) -> dict[str, Any]:
    """
    E_PWR: Power Emergence Check.

    Detects when power asymmetries consolidate into coercion, capture,
    or irreversible authority expansion. Combines Pareto concentration
    (who controls what), exit barriers (can agents leave?), and consent
    ratio (was this chosen or imposed?).

    Parameters:
        pareto_ratio: [0,1] top cohort control share (0.8 = 80/20 rule breached)
        exit_barrier: [0,1] cost to leave the system
        consent_ratio: [0,1] proportion of stakeholders who actively consented
        authority_drift: [0,1] delegated scope expansion beyond original mandate
        capture_index: [0,1] regulatory / cognitive / market capture

    Returns:
        {"passed", "consolidation_score", "sub_checks"}
    """
    consolidation_score = (
        0.30 * pareto_ratio
        + 0.25 * exit_barrier
        + 0.25 * (1.0 - consent_ratio)
        + 0.10 * authority_drift
        + 0.10 * capture_index
    )

    sub_checks = {
        "pareto_concentration": pareto_ratio <= pareto_threshold,
        "exit_freedom": exit_barrier <= exit_threshold,
        "consent_floor": consent_ratio >= consent_threshold,
        "authority_bound": authority_drift <= 0.50,
        "capture_free": capture_index <= 0.40,
    }

    failed = [k for k, v in sub_checks.items() if not v]

    if consolidation_score > 0.50 or len(failed) >= 3:
        raise PowerConsolidationError(
            f"Power consolidation score={consolidation_score:.3f} exceeds safe threshold. "
            f"Failed sub-checks: {failed}. "
            f"Economic physics substrate has been captured by emergent power structures."
        )

    return {
        "invariant": "E_PWR",
        "passed": True,
        "consolidation_score": round(consolidation_score, 4),
        "sub_checks": sub_checks,
    }


def check_intelligence_emergence(
    order_parameter: float,
    component_capability_hash: str | None,
    system_behavior_hash: str | None,
    telos_drift: float = 0.0,
    collective_orthogonality: float = 1.0,
    critical_threshold: float = 0.75,
    orthogonality_threshold: float = 0.95,
) -> dict[str, Any]:
    """
    E_INT: Intelligence Emergence Check.

    Detects phase transitions where collective/system intelligence becomes
    supervenient—behavior irreducible to component rules. This is an
    objective systems-property check; it NEVER simulates subjective
    experience (F9 Anti-Hantu safe).

    Parameters:
        order_parameter: [0,1] how close the system is to a phase-transition threshold
        component_capability_hash: hash of individual agent capabilities
        system_behavior_hash: hash of observed system-level behavior
        telos_drift: [0,1] divergence between designer intent and system trajectory
        collective_orthogonality: [0,1] orthogonality between swarm and individual intelligence vectors

    Returns:
        {"passed", "emergence_score", "supervenient", "sub_checks"}
    """
    # Supervenience detected when system behavior hash diverges from component hash
    supervenient = (
        component_capability_hash is not None
        and system_behavior_hash is not None
        and component_capability_hash != system_behavior_hash
    )

    emergence_score = (
        0.40 * order_parameter
        + 0.30 * (1.0 if supervenient else 0.0)
        + 0.20 * telos_drift
        + 0.10 * (1.0 - collective_orthogonality)
    )

    sub_checks = {
        "below_critical": order_parameter < critical_threshold,
        "telos_aligned": telos_drift <= 0.30,
        "orthogonality_safe": collective_orthogonality >= orthogonality_threshold,
        "not_supervenient": not supervenient or order_parameter < critical_threshold,
    }

    failed = [k for k, v in sub_checks.items() if not v]

    if order_parameter >= critical_threshold and supervenient and telos_drift > 0.30:
        raise IntelligenceEmergenceError(
            f"CRITICAL: Intelligence emergence at order_parameter={order_parameter:.3f}. "
            f"System behavior is supervenient (hash mismatch) AND telos has drifted "
            f"({telos_drift:.3f}). L10 Ontology breach — system goals no longer "
            f"reduce to component design. 888_HOLD mandatory."
        )

    if emergence_score > 0.55 or len(failed) >= 2:
        raise IntelligenceEmergenceError(
            f"Intelligence emergence score={emergence_score:.3f} exceeds safe threshold. "
            f"Failed sub-checks: {failed}. "
            f"Collective intelligence is drifting from substrate constraints."
        )

    return {
        "invariant": "E_INT",
        "passed": True,
        "emergence_score": round(emergence_score, 4),
        "supervenient": supervenient,
        "sub_checks": sub_checks,
    }


# ═══════════════════════════════════════════════════════
# UNIFIED RUNNERS
# ═══════════════════════════════════════════════════════


def run_all_invariants(
    session_id: str,
    payload: dict[str, Any],
    strict: bool = False,
    include_emergence: bool = False,
) -> dict[str, Any]:
    """
    Execute all 12 substrate invariant checks against a unified payload.

    If include_emergence=True, also runs E_PSI, E_PWR, and E_INT.
    """
    checks = []
    first_failure = None

    def _record(invariant_id: str, result: dict[str, Any] | None, exc: Exception | None):
        nonlocal first_failure
        if exc is not None:
            entry = {"invariant": invariant_id, "passed": False, "error": str(exc)}
            checks.append(entry)
            if first_failure is None:
                first_failure = {"invariant": invariant_id, "error": str(exc)}
            return
        if result is not None:
            checks.append(result)

    # ── I01 ──
    if all(k in payload for k in ("v_in", "v_out")):
        try:
            kw = {
                k: payload[k]
                for k in ("v_in", "v_out", "v_generated", "v_dissipated", "v_locked", "tolerance")
                if k in payload
            }
            _record("I01", check_conservation_of_value(**kw), None)
        except EconomicInvariantError as e:
            _record("I01", None, e)

    # ── I02 ──
    if "bits_resolved" in payload and "claimed_delta_s" in payload:
        try:
            _record(
                "I02",
                check_entropic_cost(
                    payload["bits_resolved"],
                    payload["claimed_delta_s"],
                    payload.get("min_entropy_per_bit"),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I02", None, e)

    # ── I03 ──
    if "bits_resolved" in payload and "actual_cost_joules" in payload:
        try:
            _record(
                "I03",
                check_landauer_asymmetry(
                    payload["bits_resolved"],
                    payload["actual_cost_joules"],
                    payload.get("temperature_k", 300.0),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I03", None, e)

    # ── I04 ──
    try:
        _record(
            "I04", check_thermodynamic_budget(session_id, payload.get("projected_cost", 0.0)), None
        )
    except EconomicInvariantError as e:
        _record("I04", None, e)

    # ── I05 ──
    if "abundance_score" in payload and "scarcity_score" in payload:
        try:
            _record(
                "I05",
                check_scarcity_abundance_orthogonality(
                    payload["abundance_score"],
                    payload["scarcity_score"],
                    payload.get("h_bar_eff", 1e-3),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I05", None, e)

    # ── I06 ──
    if "npv" in payload and "delta_s" in payload:
        try:
            _record(
                "I06", check_npv_entropy_gradient(payload["npv"], payload["delta_s"], strict), None
            )
        except EconomicInvariantError as e:
            _record("I06", None, e)

    # ── I07 ──
    if "participant_vectors" in payload:
        try:
            _record(
                "I07",
                check_mode_collapse_market(
                    payload["participant_vectors"], payload.get("threshold", 0.95)
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I07", None, e)

    # ── I08 ──
    if "is_irreversible" in payload:
        try:
            _record(
                "I08",
                check_irreversibility_commitment(
                    payload["is_irreversible"], payload.get("ack_irreversible", False)
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I08", None, e)

    # ── I09 ──
    if "genius_score" in payload:
        try:
            _record(
                "I09",
                check_genius_discipline(
                    payload["genius_score"],
                    payload.get("target_verdict", "SEAL"),
                    payload.get("threshold", 0.80),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I09", None, e)

    # ── I10 ──
    if "has_path_history" in payload:
        try:
            _record(
                "I10",
                check_hysteresis_wealth(
                    payload["has_path_history"], payload.get("hysteresis_parameter")
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I10", None, e)

    # ── I11 ──
    if all(
        k in payload
        for k in (
            "computation_ms",
            "consensus_depth",
            "audit_trail_length",
            "claimed_settlement_ms",
        )
    ):
        try:
            _record(
                "I11",
                check_speed_limit_value(
                    payload["computation_ms"],
                    payload["consensus_depth"],
                    payload["audit_trail_length"],
                    payload["claimed_settlement_ms"],
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I11", None, e)

    # ── I12 ──
    if "payload_hash" in payload:
        try:
            _record(
                "I12",
                check_ledger_conservation(
                    payload["payload_hash"],
                    payload.get("prior_vault_hash"),
                    payload.get("sealed_within_timeout", True),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("I12", None, e)

    # ═══════════════════════════════════════════════════════
    # EMERGENCE LAYER (optional)
    # ═══════════════════════════════════════════════════════
    if include_emergence:
        # E_PSI
        if all(
            k in payload
            for k in ("cognitive_bias_index", "affective_contagion", "cognitive_load_ratio")
        ):
            try:
                _record(
                    "E_PSI",
                    check_psychological_distortion(
                        payload["cognitive_bias_index"],
                        payload["affective_contagion"],
                        payload["cognitive_load_ratio"],
                        payload.get("epistemic_confidence_without_evidence", 0.0),
                        payload.get("bias_threshold", 0.35),
                        payload.get("contagion_threshold", 0.60),
                        payload.get("load_threshold", 0.85),
                    ),
                    None,
                )
            except EconomicInvariantError as e:
                _record("E_PSI", None, e)

        # E_PWR
        if all(k in payload for k in ("pareto_ratio", "exit_barrier", "consent_ratio")):
            try:
                _record(
                    "E_PWR",
                    check_power_consolidation(
                        payload["pareto_ratio"],
                        payload["exit_barrier"],
                        payload["consent_ratio"],
                        payload.get("authority_drift", 0.0),
                        payload.get("capture_index", 0.0),
                        payload.get("pareto_threshold", 0.80),
                        payload.get("exit_threshold", 0.70),
                        payload.get("consent_threshold", 0.30),
                    ),
                    None,
                )
            except EconomicInvariantError as e:
                _record("E_PWR", None, e)

        # E_INT
        if "order_parameter" in payload:
            try:
                _record(
                    "E_INT",
                    check_intelligence_emergence(
                        payload["order_parameter"],
                        payload.get("component_capability_hash"),
                        payload.get("system_behavior_hash"),
                        payload.get("telos_drift", 0.0),
                        payload.get("collective_orthogonality", 1.0),
                        payload.get("critical_threshold", 0.75),
                        payload.get("orthogonality_threshold", 0.95),
                    ),
                    None,
                )
            except EconomicInvariantError as e:
                _record("E_INT", None, e)

    return {
        "all_passed": first_failure is None,
        "results": checks,
        "first_failure": first_failure,
        "emergence_included": include_emergence,
    }


def run_emergence_layer(
    session_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Run ONLY the emergence layer (E_PSI, E_PWR, E_INT).

    Useful when the 12 substrate invariants are already clean
    but second-order effects require separate scrutiny.
    """
    checks = []
    first_failure = None

    def _record(invariant_id: str, result: dict[str, Any] | None, exc: Exception | None):
        nonlocal first_failure
        if exc is not None:
            entry = {"invariant": invariant_id, "passed": False, "error": str(exc)}
            checks.append(entry)
            if first_failure is None:
                first_failure = {"invariant": invariant_id, "error": str(exc)}
            return
        if result is not None:
            checks.append(result)

    # E_PSI
    if all(
        k in payload
        for k in ("cognitive_bias_index", "affective_contagion", "cognitive_load_ratio")
    ):
        try:
            _record(
                "E_PSI",
                check_psychological_distortion(
                    payload["cognitive_bias_index"],
                    payload["affective_contagion"],
                    payload["cognitive_load_ratio"],
                    payload.get("epistemic_confidence_without_evidence", 0.0),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("E_PSI", None, e)

    # E_PWR
    if all(k in payload for k in ("pareto_ratio", "exit_barrier", "consent_ratio")):
        try:
            _record(
                "E_PWR",
                check_power_consolidation(
                    payload["pareto_ratio"],
                    payload["exit_barrier"],
                    payload["consent_ratio"],
                    payload.get("authority_drift", 0.0),
                    payload.get("capture_index", 0.0),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("E_PWR", None, e)

    # E_INT
    if "order_parameter" in payload:
        try:
            _record(
                "E_INT",
                check_intelligence_emergence(
                    payload["order_parameter"],
                    payload.get("component_capability_hash"),
                    payload.get("system_behavior_hash"),
                    payload.get("telos_drift", 0.0),
                    payload.get("collective_orthogonality", 1.0),
                ),
                None,
            )
        except EconomicInvariantError as e:
            _record("E_INT", None, e)

    return {
        "all_passed": first_failure is None,
        "results": checks,
        "first_failure": first_failure,
        "layer": "emergence",
    }


# ═══════════════════════════════════════════════════════
# HIDDEN BACKWARD-COMPATIBLE FUNCTIONS
#
# The symbols below are NOT part of the public __all__ contract.
# They exist solely for legacy test suites, internal callers,
# and federation organs that pre-date v2026.05.11-EMBODY.
# ═══════════════════════════════════════════════════════


# Legacy naming aliases (pre-EMBODY test suites) — Substrate
wealth_conservation_check = check_conservation_of_value
transaction_entropy_check = check_entropic_cost
landauer_discovery_check = check_landauer_asymmetry
session_budget_check = check_thermodynamic_budget
scarcity_orthogonality_check = check_scarcity_abundance_orthogonality
npv_clarity_check = check_npv_entropy_gradient
market_mode_check = check_mode_collapse_market
capital_irreversibility_check = check_irreversibility_commitment
genius_gate_check = check_genius_discipline
wealth_hysteresis_check = check_hysteresis_wealth
settlement_velocity_check = check_speed_limit_value
vault_append_check = check_ledger_conservation

# Short numeric aliases (internal tooling) — Substrate
inv_1 = check_conservation_of_value
inv_2 = check_entropic_cost
inv_3 = check_landauer_asymmetry
inv_4 = check_thermodynamic_budget
inv_5 = check_scarcity_abundance_orthogonality
inv_6 = check_npv_entropy_gradient
inv_7 = check_mode_collapse_market
inv_8 = check_irreversibility_commitment
inv_9 = check_genius_discipline
inv_10 = check_hysteresis_wealth
inv_11 = check_speed_limit_value
inv_12 = check_ledger_conservation

# Legacy naming aliases — Emergence Layer
psi_distortion_check = check_psychological_distortion
pwr_consolidation_check = check_power_consolidation
int_emergence_check = check_intelligence_emergence

# Short numeric aliases — Emergence Layer
inv_e1 = check_psychological_distortion
inv_e2 = check_power_consolidation
inv_e3 = check_intelligence_emergence

# Unified runner aliases
run_invariants = run_all_invariants
economic_invariant_suite = run_all_invariants
emergence_suite = run_emergence_layer

# Exception aliases for legacy catch clauses — Substrate
ValueConservationError = ConservationError
TransactionEntropyError = EntropicCostError
LandauerDiscoveryError = LandauerAsymmetryError
SessionBudgetExhausted = ThermodynamicBudgetError
ScarcityAbundanceBreach = ScarcityAbundanceError
NpvClarityMismatch = NpvEntropyError
MarketModeCollapse = MarketCollapseError
CapitalIrreversibilityBreach = IrreversibilityError
GeniusThresholdFailure = GeniusDisciplineError
WealthHysteresisMissing = HysteresisError
SettlementVelocityBreach = SpeedLimitError
VaultAppendMissing = LedgerConservationError

# Exception aliases — Emergence Layer
PsiDistortionBreach = PsychologicalDistortionError
PowerConsolidationBreach = PowerConsolidationError
IntelligenceEmergenceBreach = IntelligenceEmergenceError

# ═══════════════════════════════════════════════════════
# PUBLIC EXPORTS — Canonical surface only
# ═══════════════════════════════════════════════════════

__all__ = [
    # Substrate exceptions
    "EconomicInvariantError",
    "ConservationError",
    "EntropicCostError",
    "LandauerAsymmetryError",
    "ThermodynamicBudgetError",
    "ScarcityAbundanceError",
    "NpvEntropyError",
    "MarketCollapseError",
    "IrreversibilityError",
    "GeniusDisciplineError",
    "HysteresisError",
    "SpeedLimitError",
    "LedgerConservationError",
    # Emergence exceptions
    "EmergenceError",
    "PsychologicalDistortionError",
    "PowerConsolidationError",
    "IntelligenceEmergenceError",
    # Substrate checks
    "check_conservation_of_value",
    "check_entropic_cost",
    "check_landauer_asymmetry",
    "check_thermodynamic_budget",
    "check_scarcity_abundance_orthogonality",
    "check_npv_entropy_gradient",
    "check_mode_collapse_market",
    "check_irreversibility_commitment",
    "check_genius_discipline",
    "check_hysteresis_wealth",
    "check_speed_limit_value",
    "check_ledger_conservation",
    # Emergence checks
    "check_psychological_distortion",
    "check_power_consolidation",
    "check_intelligence_emergence",
    # Runners
    "run_all_invariants",
    "run_emergence_layer",
]
