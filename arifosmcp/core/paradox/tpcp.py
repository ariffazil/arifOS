"""
tpcp.py — Thermodynamic Paradox Conductance Protocol (TPCP)

Implements the 4-phase paradox resolution pipeline from APEX Unified Theory:

  Phase 1: ΔP (Paradox Pressure)   — measure contradiction
  Phase 2: ΩP (Uncertainty Expand) — expand epistemic humility
  Phase 3: ΨP (Equilibrium Check)  — validate stability under floors
  Phase 4: Φ_P (Crown)             — compute wisdom metric → verdict

Core equation:
  Φ_P = (∫ΨP dt) / (ΔP × Ω₀)
  
  Φ_P ≥ 0.80 → SEAL
  Φ_P 0.40–0.79 → SABAR
  Φ_P 0.10–0.39 → HOLD
  Φ_P < 0.10 → VOID

Theory: arifOS/static/arifos/theory/000/APEX_THEORY.md
Spec:   arifOS/static/arifos/theory/000/CANONICAL_SPEC.yaml

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ── Phase Enum ───────────────────────────────────────────────────────────────

class TPCPPhase(Enum):
    """The 4 phases of the Paradox Containment Protocol."""
    DELTA_P = "delta_P"       # Phase 1: Paradox Pressure
    OMEGA_P = "omega_P"       # Phase 2: Uncertainty Expansion
    PSI_P = "psi_P"           # Phase 3: Equilibrium Validation
    PHI_P = "phi_P"           # Phase 4: Resolution Convergence


# ── State Dataclass ──────────────────────────────────────────────────────────

@dataclass
class TPCPState:
    """
    Full state of the TPCP pipeline.

    All fields are typed, ranged, and mathematically meaningful.
    """
    # Phase 1: Paradox Pressure
    delta_P: float = 0.0         # ΔP = H_contradictory - H_coherent
    h_contradictory: float = 0.0  # Shannon entropy of contradictory frame
    h_coherent: float = 0.0       # Shannon entropy of coherent frame

    # Phase 2: Uncertainty Expansion
    omega_0: float = 0.05         # Ω₀ baseline epistemic humility [0.03, 0.05]
    omega_P: float = 0.0          # ΩP expanded uncertainty
    alpha: float = 0.15            # Expansion rate constant [0.0, 1.0]

    # Phase 3: Equilibrium Validation
    psi_P: float = 0.0            # ΨP equilibrium stability [-1.0, 1.0]
    delta_s: float = 0.0          # ∂S/∂t — entropy change rate
    floors_compliance: float = 1.0  # Σ_floors_compliance — fraction of floors passed [0, 1]

    # Phase 4: Resolution Convergence
    phi_P: float = 0.0            # Φ_P crown metric [0.0, 1.0]
    integration_window: float = 1.0  # ∫ dt — integration window in arbitrary units

    # Metadata
    phase: TPCPPhase = TPCPPhase.DELTA_P
    cycle_count: int = 0
    history: list[dict] = field(default_factory=list)

    # ── Constants ─────────────────────────────────────────────────────
    OMEGA_0_MIN: float = 0.03
    OMEGA_0_MAX: float = 0.05
    ALPHA_DEFAULT: float = 0.15

    # ── Phase 1: Compute ΔP ──────────────────────────────────────────
    def compute_delta_P(self) -> float:
        """ΔP = H_contradictory - H_coherent (Paradox Pressure)."""
        self.delta_P = max(0.0, self.h_contradictory - self.h_coherent)
        self.phase = TPCPPhase.DELTA_P
        self._record_phase()
        return self.delta_P

    # ── Phase 2: Compute ΩP ──────────────────────────────────────────
    def compute_omega_P(self) -> float:
        """ΩP = Ω₀ + α × ΔP (Uncertainty Expansion)."""
        # Constrain omega_0 to canonical band
        self.omega_0 = max(self.OMEGA_0_MIN, min(self.OMEGA_0_MAX, self.omega_0))
        self.omega_P = self.omega_0 + self.alpha * self.delta_P
        self.phase = TPCPPhase.OMEGA_P
        self._record_phase()
        return self.omega_P

    # ── Phase 3: Compute ΨP ──────────────────────────────────────────
    def compute_psi_P(self) -> float:
        """ΨP = (∂S/∂t)⁻¹ × Σ_floors_compliance (Equilibrium Validation).

        If delta_s is 0 (no entropy change), ∂S/∂t → ∞ so ΨP → 0.
        If floors_compliance is 0, ΨP → 0.
        """
        if self.delta_s == 0.0:
            stability = 1.0  # No entropy change = stable
        else:
            stability = 1.0 / abs(self.delta_s)

        self.psi_P = stability * self.floors_compliance
        self.psi_P = max(-1.0, min(1.0, self.psi_P))  # Bound to [-1, 1]
        self.phase = TPCPPhase.PSI_P
        self._record_phase()
        return self.psi_P

    # ── Phase 4: Compute Φ_P ─────────────────────────────────────────
    def compute_phi_P(self) -> float:
        """Φ_P = (∫ΨP dt) / (ΔP × Ω₀) (Crown Metric).

        If ΔP or Ω₀ are 0, Φ_P is undefined → return 0.0.
        ∫ΨP dt ≈ psi_P × integration_window (Riemann approximation).
        """
        denominator = self.delta_P * self.omega_0
        if denominator == 0.0:
            self.phi_P = 0.0
        else:
            integral_psi = self.psi_P * self.integration_window
            self.phi_P = integral_psi / denominator

        # Bound to [0, 1]
        self.phi_P = max(0.0, min(1.0, self.phi_P))
        self.phase = TPCPPhase.PHI_P
        self.cycle_count += 1
        self._record_phase()
        return self.phi_P

    # ── Full Pipeline ────────────────────────────────────────────────
    def run_pipeline(
        self,
        h_contradictory: float | None = None,
        h_coherent: float | None = None,
        delta_s: float | None = None,
        floors_compliance: float | None = None,
        omega_0: float | None = None,
    ) -> dict:
        """
        Run the full 4-phase TPCP pipeline and return verdict.

        Args:
            h_contradictory: Shannon entropy of contradictory evidence
            h_coherent: Shannon entropy of coherent evidence
            delta_s: Entropy change rate (∂S/∂t)
            floors_compliance: Fraction of floors satisfied [0, 1]
            omega_0: Baseline epistemic uncertainty

        Returns:
            Dict with phi_P, verdict, all intermediate values
        """
        if h_contradictory is not None:
            self.h_contradictory = h_contradictory
        if h_coherent is not None:
            self.h_coherent = h_coherent
        if delta_s is not None:
            self.delta_s = delta_s
        if floors_compliance is not None:
            self.floors_compliance = floors_compliance
        if omega_0 is not None:
            self.omega_0 = max(self.OMEGA_0_MIN, min(self.OMEGA_0_MAX, omega_0))

        self.compute_delta_P()
        self.compute_omega_P()
        self.compute_psi_P()
        self.compute_phi_P()

        return self.summary()

    # ── Verdict from Φ_P ─────────────────────────────────────────────
    def verdict_from_phi(self) -> str:
        """Map Φ_P value to verdict per CANONICAL_SPEC.yaml thresholds."""
        if self.phi_P >= 0.80:
            return "SEAL"
        elif self.phi_P >= 0.40:
            return "SABAR"
        elif self.phi_P >= 0.10:
            return "HOLD"
        return "VOID"

    # ── Summary ──────────────────────────────────────────────────────
    def summary(self) -> dict:
        """Return full TPCP state as a dict for logging/telemetry."""
        return {
            "phi_P": round(self.phi_P, 4),
            "verdict": self.verdict_from_phi(),
            "pipeline_complete": self.phase == TPCPPhase.PHI_P,
            "phases": {
                "delta_P": {
                    "value": round(self.delta_P, 4),
                    "h_contradictory": round(self.h_contradictory, 4),
                    "h_coherent": round(self.h_coherent, 4),
                },
                "omega_P": {
                    "value": round(self.omega_P, 4),
                    "omega_0": round(self.omega_0, 4),
                    "alpha": self.alpha,
                },
                "psi_P": {
                    "value": round(self.psi_P, 4),
                    "delta_s": round(self.delta_s, 4),
                    "floors_compliance": round(self.floors_compliance, 4),
                },
                "phi_P": {
                    "value": round(self.phi_P, 4),
                    "integration_window": self.integration_window,
                },
            },
            "cycle_count": self.cycle_count,
        }

    # ── Internal: Record phase in history ────────────────────────────
    def _record_phase(self) -> None:
        self.history.append({
            "phase": self.phase.value,
            "timestamp_au": len(self.history),
        })
