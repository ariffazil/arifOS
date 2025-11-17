from dataclasses import dataclass
from typing import List

@dataclass
class Metrics:
    """Metrics required by ArifOS floors.

    - truth, tri_witness ∈ [0,1]
    - delta_S, peace2, psi use the same units as your governance config
    - omega_0 is expected around 0.03–0.05
    """
    truth: float
    delta_S: float
    peace2: float
    kappa_r: float
    omega_0: float
    amanah: bool
    tri_witness: float
    psi: float

@dataclass
class FloorsVerdict:
    """Result of evaluating all floors.

    hard_ok: Truth, ΔS, Ω₀, Amanah, Ψ
    soft_ok: Peace², κᵣ, Tri-Witness (if required)
    """
    hard_ok: bool
    soft_ok: bool
    reasons: List[str]
    truth_ok: bool
    delta_S_ok: bool
    peace2_ok: bool
    kappa_r_ok: bool
    omega_0_ok: bool
    amanah_ok: bool
    tri_witness_ok: bool
    psi_ok: bool
