"""
AC_Risk Calculation Engine — Theory of Anomalous Contrast (ToAC)
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI

The core equation:
    AC_Risk = U_phys × D_transform × B_cog

Where:
    U_phys = Physical ambiguity [0.0, 1.0]
    D_transform = Display distortion factor [1.0, 3.0]
    B_cog = Cognitive bias factor [0.2, 0.42]

Verdict thresholds:
    < 0.15 → SEAL
    < 0.35 → QUALIFY
    < 0.60 → HOLD (888_HOLD triggered)
    ≥ 0.60 → VOID
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AC_RiskResult:
    """Result of AC_Risk calculation."""

    ac_risk: float
    verdict: str
    explanation: str
    u_phys: float
    d_transform: float
    b_cog: float


def compute_ac_risk(
    u_phys: float,
    transform_stack: List[str],
    bias_scenario: str = "ai_vision_only",
    custom_b_cog: float = None,
) -> AC_RiskResult:
    """
    Calculate Theory of Anomalous Contrast (ToAC) risk score.

    Args:
        u_phys: Physical ambiguity [0.0, 1.0]
        transform_stack: List of applied transforms
        bias_scenario: Cognitive bias scenario
        custom_b_cog: Override B_cog value

    Returns:
        AC_RiskResult with score, verdict, and explanation
    """
    # Validate inputs
    u_phys = max(0.0, min(1.0, u_phys))

    # Calculate D_transform (display distortion factor)
    transform_risk_map = {
        "linear_scaling": 1.0,
        "contrast_stretch": 1.05,
        "agc_rms": 1.15,
        "agc_inst": 1.25,
        "clahe": 1.35,
        "spectral_balance": 1.20,
        "vlm_inference": 1.50,
        "ai_segmentation": 1.40,
        "depth_conversion": 1.30,
    }

    d_transform = 1.0
    for transform in transform_stack:
        d_transform *= transform_risk_map.get(transform, 1.25)
    d_transform = min(d_transform, 3.0)  # Cap at 3x

    # Calculate B_cog (cognitive bias factor)
    bias_map = {
        "unaided_expert": 0.35,
        "multi_interpreter": 0.28,
        "physics_validated": 0.20,
        "ai_vision_only": 0.42,
        "ai_with_physics": 0.30,
    }
    b_cog = (
        custom_b_cog if custom_b_cog is not None else bias_map.get(bias_scenario, 0.42)
    )
    b_cog = max(0.0, min(1.0, b_cog))

    # Calculate AC_Risk
    ac_risk = u_phys * d_transform * b_cog
    ac_risk = max(0.0, min(1.0, ac_risk))

    # Determine verdict
    if ac_risk < 0.15:
        verdict = "SEAL"
        explanation = f"AC_Risk={ac_risk:.3f}: Low risk. Physical grounding strong. Proceed with standard QC."
    elif ac_risk < 0.35:
        verdict = "QUALIFY"
        explanation = f"AC_Risk={ac_risk:.3f}: Moderate risk. Proceed with caveats. Document assumptions per F2 Truth."
    elif ac_risk < 0.60:
        verdict = "HOLD"
        explanation = f"AC_Risk={ac_risk:.3f}: Elevated risk. Human review required per 888_HOLD. Escalate to qualified interpreter."
    else:
        verdict = "VOID"
        explanation = f"AC_Risk={ac_risk:.3f}: Critical risk. Interpretation unsafe. Acquire better data or ground-truth validation."

    return AC_RiskResult(
        ac_risk=round(ac_risk, 4),
        verdict=verdict,
        explanation=explanation,
        u_phys=round(u_phys, 4),
        d_transform=round(d_transform, 4),
        b_cog=round(b_cog, 4),
    )
