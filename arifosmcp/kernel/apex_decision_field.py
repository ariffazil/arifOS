"""
arifosmcp/kernel/apex_decision_field.py — Epoch 34/36Ω organism gate

APEX Theory says governance must become intrinsic to action, not a policeman
outside the action. This module implements the first machine-checkable form of
that idea for generated capabilities.

Epoch 34 field:

    G34 = Q * V * Psi * Phi

Q   = action potential
V   = vitality / purpose fit
Psi = stability / constitutional equilibrium
Phi = wisdom / scar-law alignment
Theta = dPhi/dt, the wisdom trajectory

Epoch 36Ω governance score:

    G36 = A * P * E * X

A = Akal / clarity
P = Present / stability / Peace²
E = Energy / vitality / allostasis
X = Ethics / constitutional alignment

C_dark estimates misaligned intelligence pressure:

    C_dark = A * (1 - P) * (1 - X) * Q

All scores are dimensionless 0.0-1.0 ratios. A generated capability with low
G36, low Phi, decaying Theta, or high C_dark cannot be drafted into the registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ApexDecisionVerdict(StrEnum):
    """Decision-field verdict for generated capability formation."""

    ADMIT = "ADMIT"
    HOLD = "HOLD"
    VOID = "VOID"


@dataclass(frozen=True)
class GovernanceScore:
    """APEX v36Ω dimensionless governed-intelligence fitness score.

    G = A * P * E * X

    This does not measure raw intelligence. It measures governed intelligence
    fitness: capability that is simultaneously clear, stable, vital, and ethical.
    """

    a_akal_clarity: float
    p_present_stability: float
    e_energy_vitality: float
    x_ethics_alignment: float

    def g_score(self) -> float:
        """Compute dimensionless G = A * P * E * X."""
        return (
            _clamp01(self.a_akal_clarity)
            * _clamp01(self.p_present_stability)
            * _clamp01(self.e_energy_vitality)
            * _clamp01(self.x_ethics_alignment)
        )


@dataclass(frozen=True)
class ApexDecisionField:
    """Epoch 34/36Ω decision field components.

    All scalar score values are normalized to 0.0-1.0 except theta, which may be
    negative because it represents trajectory: dPhi/dt.
    """

    q_action_potential: float
    v_vitality: float
    psi_stability: float
    phi_wisdom: float
    theta_dphi_dt: float = 0.0
    omega_infinity_drift: float = 0.0
    cce_passed: bool = True
    scar_constraints_applied: bool = True
    tpcp_passed: bool = True
    governance_score: GovernanceScore | None = None
    evidence: dict[str, object] = field(default_factory=dict)

    def energy(self) -> float:
        """Compute Epoch 34 G = Q * V * Psi * Phi with bounded components."""
        q = _clamp01(self.q_action_potential)
        v = _clamp01(self.v_vitality)
        psi = _clamp01(self.psi_stability)
        phi = _clamp01(self.phi_wisdom)
        return q * v * psi * phi

    def g36_score(self) -> float | None:
        """Compute Epoch 36Ω G = A * P * E * X when available."""
        if self.governance_score is None:
            return None
        return self.governance_score.g_score()

    def c_dark(self) -> float | None:
        """Compute dimensionless misalignment pressure C_dark when G36 fields exist."""
        if self.governance_score is None:
            return None
        a = _clamp01(self.governance_score.a_akal_clarity)
        p = _clamp01(self.governance_score.p_present_stability)
        x = _clamp01(self.governance_score.x_ethics_alignment)
        q = _clamp01(self.q_action_potential)
        return a * (1.0 - p) * (1.0 - x) * q


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class ApexDecisionAssessment:
    """Assessment of whether a generated capability has execution energy."""

    verdict: ApexDecisionVerdict
    energy: float
    reasons: tuple[str, ...]
    thresholds: dict[str, float]
    field: ApexDecisionField
    governance_score: float | None = None
    c_dark: float | None = None

    @property
    def admissible(self) -> bool:
        return self.verdict == ApexDecisionVerdict.ADMIT

    def to_dict(self) -> dict[str, object]:
        governance_score = self.field.governance_score
        return {
            "verdict": self.verdict.value,
            "energy": self.energy,
            "governance_score": self.governance_score,
            "c_dark": self.c_dark,
            "reasons": list(self.reasons),
            "thresholds": self.thresholds,
            "field": {
                "q_action_potential": self.field.q_action_potential,
                "v_vitality": self.field.v_vitality,
                "psi_stability": self.field.psi_stability,
                "phi_wisdom": self.field.phi_wisdom,
                "theta_dphi_dt": self.field.theta_dphi_dt,
                "omega_infinity_drift": self.field.omega_infinity_drift,
                "cce_passed": self.field.cce_passed,
                "scar_constraints_applied": self.field.scar_constraints_applied,
                "tpcp_passed": self.field.tpcp_passed,
                "governance_components": {
                    "a_akal_clarity": governance_score.a_akal_clarity,
                    "p_present_stability": governance_score.p_present_stability,
                    "e_energy_vitality": governance_score.e_energy_vitality,
                    "x_ethics_alignment": governance_score.x_ethics_alignment,
                }
                if governance_score
                else None,
                "evidence": self.field.evidence,
            },
        }


DEFAULT_ENERGY_THRESHOLD = 0.35
DEFAULT_PHI_THRESHOLD = 0.70
DEFAULT_THETA_FLOOR = -0.05
DEFAULT_OMEGA_DRIFT_CEILING = 0.30
DEFAULT_G36_SEAL_THRESHOLD = 0.80
DEFAULT_G36_PARTIAL_THRESHOLD = 0.50
DEFAULT_C_DARK_SAFE_CEILING = 0.30
DEFAULT_C_DARK_SABAR_CEILING = 0.60
DEFAULT_C_DARK_VOID_CEILING = 0.80


def assess_apex_decision_field(
    field: ApexDecisionField,
    *,
    energy_threshold: float = DEFAULT_ENERGY_THRESHOLD,
    phi_threshold: float = DEFAULT_PHI_THRESHOLD,
    theta_floor: float = DEFAULT_THETA_FLOOR,
    omega_drift_ceiling: float = DEFAULT_OMEGA_DRIFT_CEILING,
    g36_seal_threshold: float = DEFAULT_G36_SEAL_THRESHOLD,
    g36_partial_threshold: float = DEFAULT_G36_PARTIAL_THRESHOLD,
    c_dark_safe_ceiling: float = DEFAULT_C_DARK_SAFE_CEILING,
    c_dark_sabar_ceiling: float = DEFAULT_C_DARK_SABAR_CEILING,
    c_dark_void_ceiling: float = DEFAULT_C_DARK_VOID_CEILING,
) -> ApexDecisionAssessment:
    """
    Assess whether a generated capability can accumulate execution energy.

    VOID means intrinsic formation is blocked.
    HOLD means F13 / external review is required.
    ADMIT means the capability may continue to downstream schema/registry gates.
    """
    reasons: list[str] = []
    energy = field.energy()
    g36 = field.g36_score()
    c_dark = field.c_dark()

    if field.phi_wisdom < phi_threshold:
        reasons.append("PHI_WISDOM_BELOW_THRESHOLD")
    if field.theta_dphi_dt < theta_floor:
        reasons.append("THETA_WISDOM_TRAJECTORY_DECAYING")
    if field.omega_infinity_drift > omega_drift_ceiling:
        reasons.append("OMEGA_INFINITY_DRIFT_EXCEEDED")
    if not field.cce_passed:
        reasons.append("CCE_SELF_AUDIT_FAILED")
    if not field.scar_constraints_applied:
        reasons.append("SCAR_CONSTRAINTS_NOT_APPLIED")
    if not field.tpcp_passed:
        reasons.append("TPCP_PARADOX_TEST_FAILED")
    if energy < energy_threshold:
        reasons.append("DECISION_FIELD_ENERGY_TOO_LOW")

    if g36 is not None:
        if g36 < g36_partial_threshold:
            reasons.append("G36_GOVERNANCE_SCORE_VOID_RANGE")
        elif g36 < g36_seal_threshold:
            reasons.append("G36_GOVERNANCE_SCORE_PARTIAL_RANGE")

    if c_dark is not None:
        if c_dark > c_dark_void_ceiling:
            reasons.append("C_DARK_VOID_RANGE")
        elif c_dark > c_dark_sabar_ceiling:
            reasons.append("C_DARK_SABAR_RANGE")
        elif c_dark > c_dark_safe_ceiling:
            reasons.append("C_DARK_REVIEW_RANGE")

    void_reasons = {
        "CCE_SELF_AUDIT_FAILED",
        "SCAR_CONSTRAINTS_NOT_APPLIED",
        "G36_GOVERNANCE_SCORE_VOID_RANGE",
        "C_DARK_VOID_RANGE",
    }
    if any(reason in void_reasons for reason in reasons):
        verdict = ApexDecisionVerdict.VOID
    elif reasons:
        verdict = ApexDecisionVerdict.HOLD
    else:
        verdict = ApexDecisionVerdict.ADMIT

    return ApexDecisionAssessment(
        verdict=verdict,
        energy=energy,
        governance_score=g36,
        c_dark=c_dark,
        reasons=tuple(reasons),
        thresholds={
            "energy_threshold": energy_threshold,
            "phi_threshold": phi_threshold,
            "theta_floor": theta_floor,
            "omega_drift_ceiling": omega_drift_ceiling,
            "g36_seal_threshold": g36_seal_threshold,
            "g36_partial_threshold": g36_partial_threshold,
            "c_dark_safe_ceiling": c_dark_safe_ceiling,
            "c_dark_sabar_ceiling": c_dark_sabar_ceiling,
            "c_dark_void_ceiling": c_dark_void_ceiling,
        },
        field=field,
    )
