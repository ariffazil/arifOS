from typing import Literal, List
from .metrics import Metrics, FloorsVerdict

ApexVerdict = Literal["SEAL", "PARTIAL", "VOID"]

def check_floors(
    metrics: Metrics,
    tri_witness_required: bool = False,
    tri_witness_threshold: float = 0.95,
) -> FloorsVerdict:
    """Evaluate all constitutional floors."""
    reasons: List[str] = []

    # Hard floors
    truth_ok = metrics.truth >= 0.99
    if not truth_ok:
        reasons.append("Truth < 0.99")

    delta_S_ok = metrics.delta_S >= 0
    if not delta_S_ok:
        reasons.append("ΔS < 0")

    omega_0_ok = 0.03 <= metrics.omega_0 <= 0.05
    if not omega_0_ok:
        reasons.append("Ω₀ outside [0.03, 0.05] band")

    amanah_ok = bool(metrics.amanah)
    if not amanah_ok:
        reasons.append("Amanah = false")

    psi_ok = metrics.psi >= 1.0
    if not psi_ok:
        reasons.append("Ψ < 1.0")

    hard_ok = truth_ok and delta_S_ok and omega_0_ok and amanah_ok and psi_ok

    # Soft floors
    peace2_ok = metrics.peace2 >= 1.0
    if not peace2_ok:
        reasons.append("Peace² < 1.0")

    kappa_r_ok = metrics.kappa_r >= 0.95
    if not kappa_r_ok:
        reasons.append("κᵣ < 0.95")

    if tri_witness_required:
        tri_witness_ok = metrics.tri_witness >= tri_witness_threshold
        if not tri_witness_ok:
            reasons.append("Tri-Witness below threshold")
    else:
        tri_witness_ok = True

    soft_ok = peace2_ok and kappa_r_ok and tri_witness_ok

    return FloorsVerdict(
        hard_ok=hard_ok,
        soft_ok=soft_ok,
        reasons=reasons,
        truth_ok=truth_ok,
        delta_S_ok=delta_S_ok,
        peace2_ok=peace2_ok,
        kappa_r_ok=kappa_r_ok,
        omega_0_ok=omega_0_ok,
        amanah_ok=amanah_ok,
        tri_witness_ok=tri_witness_ok,
        psi_ok=psi_ok,
    )

def apex_review(
    metrics: Metrics,
    high_stakes: bool = False,
    tri_witness_threshold: float = 0.95,
) -> ApexVerdict:
    """Apply APEX PRIME decision policy.

    - If any hard floor fails → VOID
    - If hard floors pass but soft floors fail → PARTIAL
    - If all floors pass → SEAL
    """
    floors = check_floors(
        metrics,
        tri_witness_required=high_stakes,
        tri_witness_threshold=tri_witness_threshold,
    )

    if not floors.hard_ok:
        return "VOID"
    if not floors.soft_ok:
        return "PARTIAL"
    return "SEAL"
