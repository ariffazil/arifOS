"""
arifosmcp/kernel/apex_decision_field.py — Epoch 34 organism gate

APEX Theory says governance must become intrinsic to action, not a policeman
outside the action. This module implements the first machine-checkable form of
that idea for generated capabilities:

    G = Q * V * Psi * Phi

Q   = action potential
V   = vitality / purpose fit
Psi = stability / constitutional equilibrium
Phi = wisdom / scar-law alignment
Theta = dPhi/dt, the wisdom trajectory

A generated capability with low Phi or decaying Theta cannot accumulate enough
execution energy to be drafted, even if it passes string-level scans.
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
class ApexDecisionField:
    """Epoch 34 decision field components.

    All values are normalized to 0.0-1.0 except theta, which may be negative.
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
    evidence: dict[str, object] = field(default_factory=dict)

    def energy(self) -> float:
        """Compute G = Q * V * Psi * Phi with bounded components."""
        q = _clamp01(self.q_action_potential)
        v = _clamp01(self.v_vitality)
        psi = _clamp01(self.psi_stability)
        phi = _clamp01(self.phi_wisdom)
        return q * v * psi * phi


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

    @property
    def admissible(self) -> bool:
        return self.verdict == ApexDecisionVerdict.ADMIT

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict.value,
            "energy": self.energy,
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
                "evidence": self.field.evidence,
            },
        }


DEFAULT_ENERGY_THRESHOLD = 0.35
DEFAULT_PHI_THRESHOLD = 0.70
DEFAULT_THETA_FLOOR = -0.05
DEFAULT_OMEGA_DRIFT_CEILING = 0.30


def assess_apex_decision_field(
    field: ApexDecisionField,
    *,
    energy_threshold: float = DEFAULT_ENERGY_THRESHOLD,
    phi_threshold: float = DEFAULT_PHI_THRESHOLD,
    theta_floor: float = DEFAULT_THETA_FLOOR,
    omega_drift_ceiling: float = DEFAULT_OMEGA_DRIFT_CEILING,
) -> ApexDecisionAssessment:
    """
    Assess whether a generated capability can accumulate execution energy.

    VOID means intrinsic formation is blocked.
    HOLD means F13 / external review is required.
    ADMIT means the capability may continue to downstream schema/registry gates.
    """
    reasons: list[str] = []
    energy = field.energy()

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

    if "CCE_SELF_AUDIT_FAILED" in reasons or "SCAR_CONSTRAINTS_NOT_APPLIED" in reasons:
        verdict = ApexDecisionVerdict.VOID
    elif reasons:
        verdict = ApexDecisionVerdict.HOLD
    else:
        verdict = ApexDecisionVerdict.ADMIT

    return ApexDecisionAssessment(
        verdict=verdict,
        energy=energy,
        reasons=tuple(reasons),
        thresholds={
            "energy_threshold": energy_threshold,
            "phi_threshold": phi_threshold,
            "theta_floor": theta_floor,
            "omega_drift_ceiling": omega_drift_ceiling,
        },
        field=field,
    )
