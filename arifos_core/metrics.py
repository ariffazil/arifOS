from dataclasses import dataclass, field
from typing import List, Optional, Dict


def _clamp_floor_ratio(value: float, floor: float) -> float:
    """Return a conservative ratio for floor evaluation.

    A ratio of 1.0 means the value is exactly at the floor.
    Anything below the floor is <1.0, above is >1.0.
    """

    if floor == 0:
        return 0.0 if value < 0 else 1.0 + value
    return value / floor


@dataclass
class Metrics:
    """Canonical metrics required by ArifOS floors.

    Canonical field names mirror LAW.md and runtime/constitution.json.
    Legacy aliases (delta_S, peace2) are provided for backwards compatibility.
    """

    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    amanah: bool
    tri_witness: float
    rasa: bool = True
    psi: Optional[float] = None

    def __post_init__(self) -> None:
        # Compute psi lazily if not provided
        if self.psi is None:
            self.psi = self.compute_psi()

    # --- Legacy aliases ----------------------------------------------------
    @property
    def delta_S(self) -> float:  # pragma: no cover - compatibility shim
        return self.delta_s

    @delta_S.setter
    def delta_S(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.delta_s = value

    @property
    def peace2(self) -> float:  # pragma: no cover - compatibility shim
        return self.peace_squared

    @peace2.setter
    def peace2(self, value: float) -> None:  # pragma: no cover - compatibility shim
        self.peace_squared = value

    # --- Helpers -----------------------------------------------------------
    def compute_psi(self, tri_witness_required: bool = True) -> float:
        """Compute Ψ (vitality) from constitutional floors.

        Ψ is the minimum conservative ratio across all required floors; any
        breach drives Ψ below 1.0 and should trigger SABAR.
        """

        omega_band_ok = 0.03 <= self.omega_0 <= 0.05
        ratios = [
            _clamp_floor_ratio(self.truth, 0.99),
            1.0 + min(self.delta_s, 0.0) if self.delta_s < 0 else 1.0 + self.delta_s,
            _clamp_floor_ratio(self.peace_squared, 1.0),
            _clamp_floor_ratio(self.kappa_r, 0.95),
            1.0 if omega_band_ok else 0.0,
            1.0 if self.amanah else 0.0,
            1.0 if self.rasa else 0.0,
        ]

        if tri_witness_required:
            ratios.append(_clamp_floor_ratio(self.tri_witness, 0.95))

        return min(ratios)

    def to_dict(self) -> Dict[str, float]:
        return {
            "truth": self.truth,
            "delta_s": self.delta_s,
            "peace_squared": self.peace_squared,
            "kappa_r": self.kappa_r,
            "omega_0": self.omega_0,
            "amanah": self.amanah,
            "tri_witness": self.tri_witness,
            "rasa": self.rasa,
            "psi": self.psi,
        }


ConstitutionalMetrics = Metrics


@dataclass
class FloorsVerdict:
    """Result of evaluating all floors.

    hard_ok: Truth, ΔS, Ω₀, Amanah, Ψ, RASA
    soft_ok: Peace², κᵣ, Tri-Witness (if required)
    """

    hard_ok: bool
    soft_ok: bool
    reasons: List[str]
    truth_ok: bool
    delta_s_ok: bool
    peace_squared_ok: bool
    kappa_r_ok: bool
    omega_0_ok: bool
    amanah_ok: bool
    tri_witness_ok: bool
    psi_ok: bool
    rasa_ok: bool = field(default=True)
