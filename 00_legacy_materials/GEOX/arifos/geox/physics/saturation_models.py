"""
Saturation Models — Water Saturation Calculation
DITEMPA BUKAN DIBERI

Archie (1942): Clean formations
Simandoux (1963): Dispersed shaly sands

F2 Truth: Every model validates its assumptions.
F7 Humility: Uncertainty propagated from parameter uncertainty.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class ModelResult:
    """Result from saturation model calculation."""

    sw: float  # Water saturation (fraction)
    sw_uncertainty: float  # Absolute uncertainty (fraction)
    method: str  # Model name used
    inputs: dict  # Input parameters (for audit)
    assumption_violations: list[str]  # F2 Truth: explicit violations

    @property
    def sw_low(self) -> float:
        """95% CI lower bound (approximate)."""
        return max(0.0, self.sw - 1.96 * self.sw_uncertainty)

    @property
    def sw_high(self) -> float:
        """95% CI upper bound (approximate)."""
        return min(1.0, self.sw + 1.96 * self.sw_uncertainty)


class SaturationModel(ABC):
    """Abstract base for water saturation models."""

    name: str = "base"
    valid_vsh_range: tuple[float, float] = (0.0, 1.0)

    @abstractmethod
    def compute_sw(
        self,
        rt: float,  # True formation resistivity (ohm-m)
        phi: float,  # Porosity (fraction)
        rw: float,  # Formation water resistivity (ohm-m)
        **kwargs,
    ) -> ModelResult:
        """Compute water saturation."""
        pass

    @abstractmethod
    def validate_assumptions(
        self,
        vsh: float,
        clay_type: str | None = None,
        salinity: float | None = None,
    ) -> list[str]:
        """Return list of assumption violations (F2 Truth)."""
        pass

    def _validate_inputs(
        self,
        rt: float,
        phi: float,
        rw: float,
    ) -> list[str]:
        """Basic input validation."""
        violations = []
        if rt <= 0:
            violations.append(f"Rt must be positive, got {rt}")
        if phi <= 0 or phi > 0.6:
            violations.append(f"Phi must be in (0, 0.6], got {phi}")
        if rw <= 0:
            violations.append(f"Rw must be positive, got {rw}")
        return violations


class ArchieModel(SaturationModel):
    """
    Archie (1942) water saturation model for clean formations.

    Equation: Sw^n = (a * Rw) / (PHI^m * Rt)

    ASSUMPTIONS:
    - Clean formation (Vsh < 10%)
    - Homogeneous pore system
    - Water-wet rock
    - Single water salinity
    - Intergranular porosity

    Reference: Archie, G.E. (1942). "The electrical resistivity log as an aid in
    determining some reservoir characteristics." Transactions of the AIME, 146(1), 54-62.
    """

    name = "archie_clean"
    valid_vsh_range = (0.0, 0.10)

    def __init__(
        self,
        a: float = 1.0,  # Tortuosity factor
        m: float = 2.0,  # Cementation exponent
        n: float = 2.0,  # Saturation exponent
    ):
        self.a = a
        self.m = m
        self.n = n

    def compute_sw(self, rt: float, phi: float, rw: float, **kwargs) -> ModelResult:
        """
        Compute Sw using Archie equation.

        Args:
            rt: True formation resistivity (ohm-m)
            phi: Porosity (fraction, e.g., 0.20 for 20%)
            rw: Formation water resistivity (ohm-m)

        Returns:
            ModelResult with Sw and uncertainty
        """
        # Input validation
        violations = self._validate_inputs(rt, phi, rw)
        if violations:
            return ModelResult(
                sw=1.0,  # Conservative default
                sw_uncertainty=1.0,
                method=self.name,
                inputs={
                    "rt": rt,
                    "phi": phi,
                    "rw": rw,
                    "a": self.a,
                    "m": self.m,
                    "n": self.n,
                },
                assumption_violations=violations,
            )

        # Archie equation: Sw^n = (a * Rw) / (PHI^m * Rt)
        try:
            sw_n = (self.a * rw) / (phi**self.m * rt)
            sw = sw_n ** (1.0 / self.n)
            sw = float(np.clip(sw, 0.0, 1.0))
        except (ValueError, OverflowError):
            return ModelResult(
                sw=1.0,
                sw_uncertainty=1.0,
                method=self.name,
                inputs={"rt": rt, "phi": phi, "rw": rw},
                assumption_violations=["Numerical error in Archie calculation"],
            )

        # Uncertainty propagation (simplified)
        # Partial derivatives for uncertainty propagation
        # dSw/dRt = -Sw / (n * Rt)
        # dSw/dphi = -m * Sw / (n * phi)
        # dSw/dRw = Sw / (n * Rw)

        # Assume 10% uncertainty on Rt, 5% on phi, 20% on Rw
        sigma_rt = 0.10 * rt
        sigma_phi = 0.05 * phi
        sigma_rw = 0.20 * rw

        dsw_drt = -sw / (self.n * rt)
        dsw_dphi = -self.m * sw / (self.n * phi)
        dsw_drw = sw / (self.n * rw)

        sw_variance = (
            (dsw_drt * sigma_rt) ** 2
            + (dsw_dphi * sigma_phi) ** 2
            + (dsw_drw * sigma_rw) ** 2
        )
        sw_uncertainty = np.sqrt(sw_variance)

        return ModelResult(
            sw=sw,
            sw_uncertainty=float(sw_uncertainty),
            method=self.name,
            inputs={
                "rt": rt,
                "phi": phi,
                "rw": rw,
                "a": self.a,
                "m": self.m,
                "n": self.n,
            },
            assumption_violations=[],
        )

    def validate_assumptions(
        self,
        vsh: float,
        clay_type: str | None = None,
        salinity: float | None = None,
    ) -> list[str]:
        """Validate Archie assumptions."""
        violations = []

        if vsh > self.valid_vsh_range[1]:
            violations.append(
                f"Vsh={vsh:.2f} exceeds Archie limit of {self.valid_vsh_range[1]:.2f}. "
                "Archie assumes clean formation. Use shaly sand model."
            )

        if clay_type and clay_type.lower() in ["smectite", "montmorillonite"]:
            violations.append(
                f"Clay type '{clay_type}' has high CEC. Archie invalid. "
                "Use Dual-Water or Waxman-Smits model."
            )

        return violations


class SimandouxModel(SaturationModel):
    """
    Simandoux (1963) water saturation model for shaly sands.

    Equation: 1/Rt = (PHI^m / (a * Rw)) * Sw^n + (Vsh / Rsh) * Sw

    Or solving for Sw:
    Sw = [-B + sqrt(B^2 + 4 * A * C)] / (2 * A)
    where:
        A = Vsh / Rsh
        B = Phi^m / (a * Rw)
        C = 1 / Rt

    ASSUMPTIONS:
    - Shaly sand with dispersed clay
    - Vsh typically 10-40%
    - Shale resistivity (Rsh) known or estimable
    - Single water type

    Reference: Simandoux, P. (1963). "Dielectric measurements on porous media
    application to the measurement of water saturation: study of the behavior
    of argillaceous formations." Revue de l'Institut Français du Pétrole, 18(Suppl.), 193-215.
    """

    name = "simandoux_dispersed"
    valid_vsh_range = (0.10, 0.40)

    def __init__(
        self,
        a: float = 1.0,
        m: float = 2.0,
        n: float = 2.0,
        rsh: float = 4.0,  # Shale resistivity (ohm-m), typical default
    ):
        self.a = a
        self.m = m
        self.n = n
        self.rsh = rsh

    def compute_sw(
        self,
        rt: float,
        phi: float,
        rw: float,
        vsh: float = 0.0,
        rsh: float | None = None,
        **kwargs,
    ) -> ModelResult:
        """
        Compute Sw using Simandoux equation.

        Args:
            rt: True formation resistivity (ohm-m)
            phi: Porosity (fraction)
            rw: Formation water resistivity (ohm-m)
            vsh: Shale volume (fraction, 0-1)
            rsh: Shale resistivity (ohm-m), uses default if None
        """
        # Input validation
        violations = self._validate_inputs(rt, phi, rw)
        if violations:
            return ModelResult(
                sw=1.0,
                sw_uncertainty=1.0,
                method=self.name,
                inputs={"rt": rt, "phi": phi, "rw": rw, "vsh": vsh},
                assumption_violations=violations,
            )

        # Use provided rsh or default
        rsh_used = rsh if rsh is not None else self.rsh

        # Simandoux quadratic: A*Sw^2 + B*Sw + C = 0
        # Actually: A*Sw + B*Sw^n = C where A = Vsh/Rsh, B = Phi^m/(a*Rw), C = 1/Rt
        # For n=2: A*Sw + B*Sw^2 = C
        # Rearranging: B*Sw^2 + A*Sw - C = 0

        A = vsh / rsh_used if rsh_used > 0 else 0.0
        B = phi**self.m / (self.a * rw)
        C = 1.0 / rt

        try:
            if self.n == 2.0:
                # Quadratic solution
                discriminant = A**2 + 4 * B * C
                if discriminant < 0:
                    violations.append("Negative discriminant in Simandoux solution")
                    sw = 1.0
                else:
                    sw = (-A + np.sqrt(discriminant)) / (2 * B)
            else:
                # General case: iterate
                sw = self._iterate_simandoux(A, B, C, self.n)

            sw = float(np.clip(sw, 0.0, 1.0))

        except (ValueError, OverflowError):
            return ModelResult(
                sw=1.0,
                sw_uncertainty=1.0,
                method=self.name,
                inputs={"rt": rt, "phi": phi, "rw": rw, "vsh": vsh, "rsh": rsh_used},
                assumption_violations=["Numerical error in Simandoux calculation"],
            )

        # Uncertainty propagation
        sigma_rt = 0.10 * rt
        sigma_phi = 0.05 * phi
        0.20 * rw
        0.10 * vsh  # Vsh uncertainty

        # Approximate partial derivatives numerically
        delta = 0.001
        sw_plus_rt = self._compute_sw_numerical(
            rt + delta, phi, rw, vsh, rsh_used, self.n
        )
        sw_minus_rt = self._compute_sw_numerical(
            rt - delta, phi, rw, vsh, rsh_used, self.n
        )
        dsw_drt = (sw_plus_rt - sw_minus_rt) / (2 * delta)

        sw_plus_phi = self._compute_sw_numerical(
            rt, phi + delta, rw, vsh, rsh_used, self.n
        )
        sw_minus_phi = self._compute_sw_numerical(
            rt, phi - delta, rw, vsh, rsh_used, self.n
        )
        dsw_dphi = (sw_plus_phi - sw_minus_phi) / (2 * delta)

        sw_variance = (
            (dsw_drt * sigma_rt) ** 2
            + (dsw_dphi * sigma_phi) ** 2
            + (0.1 * sw) ** 2  # Approximate Rw/Vsh contribution
        )
        sw_uncertainty = np.sqrt(sw_variance)

        return ModelResult(
            sw=sw,
            sw_uncertainty=float(sw_uncertainty),
            method=self.name,
            inputs={
                "rt": rt,
                "phi": phi,
                "rw": rw,
                "vsh": vsh,
                "rsh": rsh_used,
                "a": self.a,
                "m": self.m,
                "n": self.n,
            },
            assumption_violations=[],
        )

    def _iterate_simandoux(
        self,
        A: float,
        B: float,
        C: float,
        n: float,
        max_iter: int = 50,
        tolerance: float = 1e-6,
    ) -> float:
        """Iterate to solve Simandoux for general n."""
        sw = 0.5  # Initial guess
        for _ in range(max_iter):
            f = A * sw + B * sw**n - C
            fp = A + n * B * sw ** (n - 1)
            if abs(fp) < 1e-10:
                break
            sw_new = sw - f / fp
            if abs(sw_new - sw) < tolerance:
                return sw_new
            sw = max(0.0, min(1.0, sw_new))
        return sw

    def _compute_sw_numerical(
        self,
        rt: float,
        phi: float,
        rw: float,
        vsh: float,
        rsh: float,
        n: float,
    ) -> float:
        """Helper for numerical differentiation."""
        A = vsh / rsh if rsh > 0 else 0.0
        B = phi**self.m / (self.a * rw)
        C = 1.0 / rt

        if n == 2.0:
            discriminant = A**2 + 4 * B * C
            if discriminant >= 0:
                return (-A + np.sqrt(discriminant)) / (2 * B)
            return 1.0
        else:
            return self._iterate_simandoux(A, B, C, n)

    def validate_assumptions(
        self,
        vsh: float,
        clay_type: str | None = None,
        salinity: float | None = None,
    ) -> list[str]:
        """Validate Simandoux assumptions."""
        violations = []

        if vsh < self.valid_vsh_range[0]:
            violations.append(
                f"Vsh={vsh:.2f} below Simandoux range [{self.valid_vsh_range[0]:.2f}, "
                f"{self.valid_vsh_range[1]:.2f}]. Archie sufficient for clean sand."
            )

        if vsh > self.valid_vsh_range[1]:
            violations.append(
                f"Vsh={vsh:.2f} above Simandoux range. Consider Indonesia or "
                "laminated sand-shale models."
            )

        return violations


def select_model_for_rock(
    vsh: float,
    clay_type: str | None = None,
    salinity: float | None = None,
) -> tuple[type[SaturationModel], list[str]]:
    """
    Select appropriate saturation model based on rock properties.

    Returns:
        (Model class, list of warnings/considerations)
    """
    warnings = []

    if vsh < 0.10:
        return ArchieModel, warnings
    elif vsh < 0.40:
        if clay_type and clay_type.lower() in ["smectite", "montmorillonite"]:
            warnings.append(
                f"High-CEC clay '{clay_type}' detected. Simandoux may underestimate Sw. "
                "Consider Dual-Water if CEC data available."
            )
        return SimandouxModel, warnings
    else:
        warnings.append(
            f"Vsh={vsh:.2f} is high. Simandoux marginal. "
            "Indonesia or laminated models preferred (Phase C)."
        )
        return SimandouxModel, warnings  # Best available in Phase B
