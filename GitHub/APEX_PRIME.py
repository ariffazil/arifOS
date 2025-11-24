"""
apex_prime.py — APEX PRIME judiciary engine for arifOS v33Ω.

Implements the constitutional floors and Ψ vitality gate as defined in:
- spec/APEX_PRIME.md
- spec/APEX_PRIME.yaml

APEX PRIME never generates content; it audits candidate outputs and
returns SEAL / PARTIAL / VOID verdicts based on ΔΩΨ metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional

from .metrics import ConstitutionalMetrics  # adjust if your class name differs


class Verdict(Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    VOID = "VOID"


@dataclass
class ApexConfig:
    """Minimal config – can be wired to spec/APEX_PRIME.yaml later."""
    truth_min: float = 0.99
    delta_s_min: float = 0.0
    peace_sq_min: float = 1.0
    kappa_r_min: float = 0.95
    omega_min: float = 0.03
    omega_max: float = 0.05
    tri_witness_min: float = 0.95
    psi_seal: float = 1.0
    psi_partial_min: float = 0.85


class APEXPrime:
    """
    APEX PRIME – Soul-Governor / Judiciary.

    Usage:
        apex = APEXPrime()
        verdict, reason = apex.judge(metrics, high_stakes=True)
    """

    def __init__(self, config: Optional[ApexConfig] = None):
        self.config = config or ApexConfig()

    # ---------------------- core public API ---------------------- #

    def judge(
        self,
        metrics: ConstitutionalMetrics,
        high_stakes: bool = False,
        organ_vetoes: Optional[Dict[str, bool]] = None,
    ) -> (str, str):
        """
        Evaluate all floors + Ψ and return (verdict, reason).

        - SEAL: all floors green and Ψ ≥ 1.0
        - PARTIAL: floors mostly OK but Ψ in warning band
        - VOID: critical failure (floor or Ψ)
        """
        organ_vetoes = organ_vetoes or {}
        failures = self._check_floors(metrics, high_stakes, organ_vetoes)
        psi = self._compute_psi(metrics)

        # High-stakes Ψ gating
        if psi is None:
            failures.append("Psi vitality could not be computed")
        elif psi < self.config.psi_partial_min:
            failures.append(f"Ψ vitality {psi:.3f} < {self.config.psi_partial_min:.2f}")

        if failures:
            # VOID vs PARTIAL depends on severity of Ψ + floors
            if psi is not None and psi >= self.config.psi_partial_min:
                # borderline case – classify as PARTIAL
                return Verdict.PARTIAL.value, self._format_failures(failures, psi)
            return Verdict.VOID.value, self._format_failures(failures, psi)

        # All floors green and Ψ ≥ seal threshold
        if psi is not None and psi >= self.config.psi_seal:
            return Verdict.SEAL.value, "All constitutional floors satisfied; Ψ vitality sufficient."
        else:
            # Floors pass but Ψ < seal threshold → PARTIAL
            return Verdict.PARTIAL.value, f"Floors pass but Ψ vitality {psi:.3f} < {self.config.psi_seal:.2f}"

    # ---------------------- helpers ---------------------- #

    def _check_floors(
        self,
        m: ConstitutionalMetrics,
        high_stakes: bool,
        organ_vetoes: Dict[str, bool],
    ) -> list[str]:
        failures: list[str] = []

        if m.truth < self.config.truth_min:
            failures.append(f"Truth {m.truth:.3f} < {self.config.truth_min:.2f}")
        if m.delta_s < self.config.delta_s_min:
            failures.append(f"ΔS {m.delta_s:.3f} < {self.config.delta_s_min:.2f}")
        if m.peace_squared < self.config.peace_sq_min:
            failures.append(f"Peace² {m.peace_squared:.3f} < {self.config.peace_sq_min:.2f}")
        if m.kappa_r < self.config.kappa_r_min:
            failures.append(f"κᵣ {m.kappa_r:.3f} < {self.config.kappa_r_min:.2f}")
        if not (self.config.omega_min <= m.omega_0 <= self.config.omega_max):
            failures.append(f"Ω₀ {m.omega_0:.3f} outside [{self.config.omega_min:.2f}, {self.config.omega_max:.2f}]")
        if not m.rasa:
            failures.append("RASA protocol not satisfied")
        if not m.amanah:
            failures.append("Amanah lock is not set (integrity breach)")
        if high_stakes and m.tri_witness < self.config.tri_witness_min:
            failures.append(f"Tri-Witness {m.tri_witness:.3f} < {self.config.tri_witness_min:.2f} (high-stakes)")

        # W@W organ vetoes
        for organ, veto in organ_vetoes.items():
            if veto:
                failures.append(f"Organ veto: {organ} vetoed the output")

        return failures

    def _compute_psi(self, m: ConstitutionalMetrics, entropy: float = 0.0, shadow: float = 0.0) -> Optional[float]:
        """
        Compute Ψ vitality as in spec/APEX_PRIME.md.
        If any missing attribute, return None and let floors handle.
        """
        try:
            epsilon = 1.0e-6
            numerator = (
                max(m.delta_s, 0.0)
                * max(m.peace_squared, 0.0)
                * max(m.kappa_r, 0.0)
                * max(m.truth, 0.0)
                * (1.0 if m.rasa else 0.0)
                * (1.0 if m.amanah else 0.0)
            )
            denom = max(entropy + shadow + epsilon, epsilon)
            return numerator / denom
        except AttributeError:
            return None

    @staticmethod
    def _format_failures(failures: list[str], psi: Optional[float]) -> str:
        base = "APEX PRIME refusal/hedge: " + "; ".join(failures)
        if psi is not None:
            base += f" | Ψ={psi:.3f}"
        return base