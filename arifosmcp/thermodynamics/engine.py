"""
arifOS Thermodynamics Engine — v37Ω-E

BIJAKSANA = thermodynamic wisdom = the ability to price present entropy
expenditure (ΔS_now) against future entropy reduction (ΔS_future).

Three entropy pathways:
  INVESTMENT:   ΔS_now ↑ → ΔS_future ↓  (spend disorder, buy order)
  MAINTENANCE:  ΔS_now ≈ ΔS_future      (manage, survive, no transformation)
  EXTRACTION:   ΔS_now ↑ → ΔS_future ↑  (spend order, create disorder)
  TERMINAL:     ΔS_now ↑ → ΔS_future ↑↑ (accelerating collapse, D_index > 1.0)

The BIJAKSANA dimension (B) is ORTHOGONAL to governance quality (G_governance).
B is not morality. B is the capacity to price entropy expenditure correctly.

DITEMPA BUKAN DIBERI — Forged, Not Given. 2026-08-01.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntropyPathway(Enum):
    """The thermodynamic trajectory of an action's entropy expenditure."""

    INVESTMENT = "INVESTMENT"
    MAINTENANCE = "MAINTENANCE"
    EXTRACTION = "EXTRACTION"
    TERMINAL_EXTRACTION = "TERMINAL_EXTRACTION"
    UNKNOWN = "UNKNOWN"

    def explanation(self) -> str:
        return {
            EntropyPathway.INVESTMENT: "ΔS_now ↑ → ΔS_future ↓ — entropy spent as capital",
            EntropyPathway.MAINTENANCE: "ΔS_now ≈ ΔS_future — no major harm, no transformation",
            EntropyPathway.EXTRACTION: "ΔS_now ↑ → ΔS_future ↑ — entropy spent on extraction",
            EntropyPathway.TERMINAL_EXTRACTION: "ΔS_now ↑ → ΔS_future ↑↑ — accelerating collapse",
            EntropyPathway.UNKNOWN: "entropy pathway not yet classified",
        }[self]


class ThermodynamicVerdict(Enum):
    """Constitutional verdict mapped to thermodynamic state."""

    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"

    def thermodynamic_meaning(self) -> str:
        return {
            ThermodynamicVerdict.SEAL: "Entropy expenditure is investment-grade. Governed execution.",
            ThermodynamicVerdict.SABAR: "Entropy pathway is neutral or actor lacks buffer. Wait, observe.",
            ThermodynamicVerdict.HOLD: "Entropy pathway is extractive or unsafe. Restructure or block.",
            ThermodynamicVerdict.VOID: "Entropy expenditure is terminal. Irreversible. Reject.",
        }[self]


class BufferStatus(Enum):
    SUFFICIENT = "SUFFICIENT"
    THIN = "THIN"
    EXHAUSTED = "EXHAUSTED"
    UNKNOWN = "UNKNOWN"


@dataclass
class EntropyReceipt:
    """Complete thermodynamic audit of an adjudicated action."""

    verdict: ThermodynamicVerdict
    entropy_pathway: EntropyPathway
    delta_s_now: str = "UNKNOWN"
    delta_s_future: str = "UNKNOWN"
    actor_B: float = 0.0
    actor_phi: float = 0.0
    buffer_status: BufferStatus = BufferStatus.UNKNOWN
    thermodynamic_reason: str = ""
    constitutional_floor_check: dict[str, Any] = field(default_factory=dict)
    required_action: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "entropy_pathway": self.entropy_pathway.value,
            "delta_s_now": self.delta_s_now,
            "delta_s_future": self.delta_s_future,
            "actor_B": self.actor_B,
            "actor_phi": self.actor_phi,
            "buffer_status": self.buffer_status.value,
            "thermodynamic_reason": self.thermodynamic_reason,
            "constitutional_floor_check": self.constitutional_floor_check,
            "required_action": self.required_action,
        }


# ── Core Compute Functions ──────────────────────────────────────────────────


def compute_entropy_pathway(
    actor_B: float,
    actor_phi: float,
    delta_s_now: str,
    delta_s_future: str,
    d_index: float = 0.0,
) -> EntropyPathway:
    """
    Classify the entropy pathway of an action.

    Parameters:
        actor_B: BIJAKSANA score (0.0-1.0) — entropy-pricing capacity
        actor_phi: Cumulative scar pressure (0.0-∞)
        delta_s_now: "UP" | "FLAT" | "DOWN"
        delta_s_future: "UP" | "FLAT" | "DOWN"
        d_index: Composite darkness index (D_index > 1.0 = black hole)

    Returns:
        EntropyPathway classification
    """
    # Terminal: black hole zone
    if d_index > 1.0:
        return EntropyPathway.TERMINAL_EXTRACTION

    # Investment: spend now, reduce later
    if delta_s_now == "UP" and delta_s_future == "DOWN":
        return EntropyPathway.INVESTMENT

    # Extraction: spend now, increase or maintain later
    if delta_s_now == "UP" and delta_s_future in ("UP", "FLAT"):
        return EntropyPathway.EXTRACTION

    # Maintenance: no change
    if delta_s_now in ("FLAT", "DOWN") and delta_s_future in ("FLAT", "DOWN"):
        return EntropyPathway.MAINTENANCE

    # Unknown
    return EntropyPathway.UNKNOWN


def classify_actor_buffer(
    actor_B: float,
    actor_phi: float,
) -> BufferStatus:
    """
    Classify the actor's entropy buffer capacity.

    Thresholds (heuristic, Ω₀=0.05):
        B >= 0.70 AND phi < 1.0 → SUFFICIENT
        B >= 0.55 OR phi < 0.80 → THIN
        B < 0.55 AND phi > 1.0 → EXHAUSTED
    """
    if actor_B >= 0.70 and actor_phi < 1.0:
        return BufferStatus.SUFFICIENT
    if actor_B >= 0.55 or actor_phi < 0.80:
        return BufferStatus.THIN
    if actor_B < 0.55 and actor_phi > 1.0:
        return BufferStatus.EXHAUSTED
    return BufferStatus.UNKNOWN


# ── Thermodynamic Verdict Matrix ────────────────────────────────────────────


def thermodynamic_judge(
    entropy_pathway: EntropyPathway,
    actor_B: float,
    actor_phi: float,
    buffer_status: BufferStatus,
    floors_pass: bool = True,
) -> ThermodynamicVerdict:
    """
    Map entropy pathway + actor state to constitutional verdict.

    Verdict Matrix:
    ┌──────────────────┬──────────────────────┬──────────────────────┐
    │ Actor State      │ INVESTMENT           │ EXTRACTION           │
    ├──────────────────┼──────────────────────┼──────────────────────┤
    │ High B, Low Φ    │ SEAL                 │ HOLD                 │
    │ Low B, High Φ    │ SABAR                │ VOID                 │
    │ High B, High Φ   │ SABAR                │ HOLD                 │
    │ Low B, Low Φ     │ SABAR                │ HOLD                 │
    ├──────────────────┼──────────────────────┼──────────────────────┤
    │ MAINTENANCE      │ SABAR (always)       │                      │
    │ TERMINAL         │ VOID (always)         │                      │
    └──────────────────┴──────────────────────┴──────────────────────┘
    """
    # Constitutional floor failure → VOID regardless
    if not floors_pass:
        return ThermodynamicVerdict.VOID

    # Terminal extraction → VOID regardless
    if entropy_pathway == EntropyPathway.TERMINAL_EXTRACTION:
        return ThermodynamicVerdict.VOID

    # Maintenance → SABAR regardless
    if entropy_pathway == EntropyPathway.MAINTENANCE:
        return ThermodynamicVerdict.SABAR

    # Unknown → HOLD (fail-closed)
    if entropy_pathway == EntropyPathway.UNKNOWN:
        return ThermodynamicVerdict.HOLD

    # Investment pathway
    if entropy_pathway == EntropyPathway.INVESTMENT:
        if buffer_status == BufferStatus.SUFFICIENT:
            return ThermodynamicVerdict.SEAL
        return ThermodynamicVerdict.SABAR

    # Extraction pathway
    if entropy_pathway == EntropyPathway.EXTRACTION:
        if buffer_status == BufferStatus.EXHAUSTED:
            return ThermodynamicVerdict.VOID
        return ThermodynamicVerdict.HOLD

    # Fallback: fail-closed
    return ThermodynamicVerdict.HOLD


def render_entropy_receipt(
    pathway: EntropyPathway,
    actor_B: float,
    actor_phi: float,
    floors_pass: bool = True,
) -> EntropyReceipt:
    """Full thermodynamic adjudication pipeline."""
    buffer = classify_actor_buffer(actor_B, actor_phi)
    verdict = thermodynamic_judge(pathway, actor_B, actor_phi, buffer, floors_pass)

    if not floors_pass:
        reason = "Constitutional floor violation. Thermodynamic assessment moot."
    elif verdict == ThermodynamicVerdict.SEAL and pathway == EntropyPathway.INVESTMENT:
        reason = "Entropy expenditure is investment-grade. Actor has capacity and buffer. Governed execution authorised."
    elif verdict == ThermodynamicVerdict.SABAR and pathway == EntropyPathway.INVESTMENT:
        reason = "Investment thesis may be sound, but actor lacks sufficient buffer or B-score. Wait, build capacity."
    elif verdict == ThermodynamicVerdict.SABAR and pathway == EntropyPathway.MAINTENANCE:
        reason = "Entropy pathway is neutral. No harm, no transformation. Do not pretend maintenance is reform."
    elif verdict == ThermodynamicVerdict.HOLD and pathway == EntropyPathway.EXTRACTION:
        reason = "Entropy pathway is extractive. Restructure the action before execution. The disorder is not priced correctly."
    elif verdict == ThermodynamicVerdict.VOID and pathway == EntropyPathway.TERMINAL_EXTRACTION:
        reason = (
            "Entropy expenditure is terminal. Irreversible collapse trajectory. Reject outright."
        )
    else:
        reason = f"Thermodynamic verdict: {verdict.value}. Pathway: {pathway.value}. Buffer: {buffer.value}."

    delta_s_now = {
        EntropyPathway.INVESTMENT: "UP",
        EntropyPathway.EXTRACTION: "UP",
        EntropyPathway.TERMINAL_EXTRACTION: "UP",
        EntropyPathway.MAINTENANCE: "FLAT",
        EntropyPathway.UNKNOWN: "UNKNOWN",
    }[pathway]

    delta_s_future = {
        EntropyPathway.INVESTMENT: "DOWN",
        EntropyPathway.EXTRACTION: "UP",
        EntropyPathway.TERMINAL_EXTRACTION: "UP",
        EntropyPathway.MAINTENANCE: "FLAT",
        EntropyPathway.UNKNOWN: "UNKNOWN",
    }[pathway]

    required_action = {
        ThermodynamicVerdict.SEAL: "EXECUTE",
        ThermodynamicVerdict.SABAR: "WAIT",
        ThermodynamicVerdict.HOLD: "RESTRUCTURE",
        ThermodynamicVerdict.VOID: "REJECT",
    }[verdict]

    return EntropyReceipt(
        verdict=verdict,
        entropy_pathway=pathway,
        delta_s_now=delta_s_now,
        delta_s_future=delta_s_future,
        actor_B=actor_B,
        actor_phi=actor_phi,
        buffer_status=buffer,
        thermodynamic_reason=reason,
        constitutional_floor_check={"F1_F13": "PASS" if floors_pass else "FAIL"},
        required_action=required_action,
    )


# ── Backpropagation Through the Φ Chain ────────────────────────────────────


def compute_phi_delta(
    actor_A: float,
    actor_P: float,
    actor_E: float,
    actor_X: float,
) -> float:
    """
    Compute the entropy contribution of a governance action.

    ΔΦ(action) = C_dark(action) + S_shadow(action)
               = A·(1-P)·(1-X) + (1-E)·A

    This is the forward propagation step in the Φ chain.
    """
    c_dark = actor_A * (1 - actor_P) * (1 - actor_X)
    s_shadow = (1 - actor_E) * actor_A
    return c_dark + s_shadow


def forward_propagate_phi(
    current_phi: float,
    actor_A: float,
    actor_P: float,
    actor_E: float,
    actor_X: float,
) -> float:
    """
    Forward propagate the Φ chain through one governance action.

    Φ(t+1) = Φ(t) + ΔΦ(action)
    """
    delta = compute_phi_delta(actor_A, actor_P, actor_E, actor_X)
    return current_phi + delta


def backpropagate_entropy_gradient(
    actor_B: float,
    delta_s_now: float,
    lambda_discount: float = 0.5,
) -> dict[str, float | str]:
    """
    Compute the gradient of future entropy with respect to current action.

    ∂L/∂action = ΔS_now + λ·∂Φ_future/∂action

    The BIJAKSANA score (B) is the actor's ability to compute this gradient.
    B ≥ 0.70 → gradient is accurate
    B < 0.55 → gradient is noisy
    B < 0.30 → gradient is unknown

    Returns:
        dict with:
        - gradient: estimated ∂L/∂action
        - gradient_accuracy: B (the BIJAKSANA score itself)
        - immediate_entropy: ΔS_now
        - discounted_future_entropy: λ·∂Φ_future/∂action (estimated)
        - loss: estimated total governance loss
    """
    # The gradient accuracy IS the BIJAKSANA score
    gradient_accuracy = actor_B

    # Immediate entropy cost
    immediate_entropy = delta_s_now

    # Future entropy: approximated as λ·(1/actor_B - 1)
    # Higher B → lower future entropy (better pricing)
    # Lower B → higher future entropy (worse pricing)
    if actor_B > 0:
        discounted_future_entropy = lambda_discount * max(0, (1 / actor_B) - 1)
    else:
        discounted_future_entropy = float("inf")

    # Total governance loss
    loss = immediate_entropy + discounted_future_entropy

    return {
        "gradient": loss,
        "gradient_accuracy": gradient_accuracy,
        "immediate_entropy": immediate_entropy,
        "discounted_future_entropy": discounted_future_entropy,
        "loss": loss,
        "bijaksana_verdict": _bijaksana_verdict_from_gradient(actor_B, loss, lambda_discount),
    }


def _bijaksana_verdict_from_gradient(
    actor_B: float,
    loss: float,
    lambda_discount: float,
) -> str:
    """Classify the actor's gradient computation ability."""
    if actor_B >= 0.70:
        if loss < 0.5:
            return "INVESTMENT_GRADE — gradient is accurate, loss is acceptable"
        return "INVESTMENT_GRADE — gradient is accurate, loss is high but priced"
    elif actor_B >= 0.55:
        return "MAINTENANCE_GRADE — gradient is noisy, proceed with caution"
    elif actor_B >= 0.30:
        return "EXTRACTION_GRADE — gradient is unreliable, HOLD"
    else:
        return "TERMINAL_GRADE — gradient is unknown, VOID"


def compute_governance_loss(
    delta_s_now: float,
    current_phi: float,
    actor_A: float,
    actor_P: float,
    actor_E: float,
    actor_X: float,
    lambda_discount: float = 0.5,
) -> dict[str, float]:
    """
    Compute the full governance loss function.

    L = ΔS_now + λ·Φ_future
      = ΔS_now + λ·(Φ_now + ΔΦ(action))

    Returns:
        dict with loss, phi_now, phi_future, delta_phi, lambda
    """
    delta_phi = compute_phi_delta(actor_A, actor_P, actor_E, actor_X)
    phi_future = current_phi + delta_phi
    loss = delta_s_now + lambda_discount * phi_future

    return {
        "loss": loss,
        "phi_now": current_phi,
        "phi_future": phi_future,
        "delta_phi": delta_phi,
        "lambda": lambda_discount,
        "delta_s_now": delta_s_now,
    }
