"""
GEOX 1D Rock Physics — Gassmann fluid substitution.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field

from .canon9_profile import DepthSample


class FluidProperties(BaseModel):
    """Fluid property calculator."""

    water_density: float = Field(default=1000.0, description="Brine density [kg/m³]")
    oil_density: float = Field(default=800.0, description="Oil density [kg/m³]")
    gas_density: float = Field(default=200.0, description="Gas density [kg/m³]")

    water_bulk_mod: float = Field(default=2.5e9, description="Brine bulk modulus [Pa]")
    oil_bulk_mod: float = Field(default=1.5e9, description="Oil bulk modulus [Pa]")
    gas_bulk_mod: float = Field(default=0.1e9, description="Gas bulk modulus [Pa]")

    def mixture_density(self, sw: float, so: float = 0.0, sg: float = 0.0) -> float:
        """Compute fluid mixture density."""
        if abs(sw + so + sg - 1.0) > 0.01:
            raise ValueError("Saturations must sum to 1")
        return sw * self.water_density + so * self.oil_density + sg * self.gas_density

    def mixture_bulk_mod(self, sw: float, so: float = 0.0, sg: float = 0.0) -> float:
        """
        Compute fluid mixture bulk modulus using Reuss average.
        1/Kf = Sw/Kw + So/Ko + Sg/Kg
        """
        if abs(sw + so + sg - 1.0) > 0.01:
            raise ValueError("Saturations must sum to 1")
        inv_kf = (
            sw / self.water_bulk_mod + so / self.oil_bulk_mod + sg / self.gas_bulk_mod
        )
        return 1.0 / inv_kf


class MineralProperties(BaseModel):
    """Mineral/matrix properties."""

    quartz: dict = Field(
        default_factory=lambda: {"density": 2650, "k": 37e9, "mu": 44e9}
    )
    calcite: dict = Field(
        default_factory=lambda: {"density": 2710, "k": 71e9, "mu": 30e9}
    )
    dolomite: dict = Field(
        default_factory=lambda: {"density": 2870, "k": 95e9, "mu": 45e9}
    )
    clay: dict = Field(default_factory=lambda: {"density": 2600, "k": 25e9, "mu": 9e9})

    def voigt_matrix_moduli(self, fractions: dict[str, float]) -> tuple[float, float]:
        """
        Voigt average for matrix moduli.
        Returns: (K_matrix, mu_matrix)
        """
        k_avg = sum(
            fractions.get(m, 0) * getattr(self, m)["k"]
            for m in ["quartz", "calcite", "dolomite", "clay"]
        )
        mu_avg = sum(
            fractions.get(m, 0) * getattr(self, m)["mu"]
            for m in ["quartz", "calcite", "dolomite", "clay"]
        )
        return k_avg, mu_avg

    def matrix_density(self, fractions: dict[str, float]) -> float:
        """Voigt average for matrix density."""
        return sum(
            fractions.get(m, 0) * getattr(self, m)["density"]
            for m in ["quartz", "calcite", "dolomite", "clay"]
        )


class GassmannModel:
    """
    Gassmann's equations for fluid substitution.

    Forward: dry-frame + fluid → saturated elastic moduli
    Inverse: saturated moduli → dry-frame moduli
    """

    def __init__(self):
        self.fluids = FluidProperties()
        self.minerals = MineralProperties()

    def fluid_substitution(
        self,
        k_sat_initial: float,
        k_matrix: float,
        k_fluid_initial: float,
        k_fluid_new: float,
        porosity: float,
    ) -> float:
        """
        Gassmann fluid substitution for bulk modulus.

        K_sat_new = K_matrix + (1 - K_matrix/K_sat_initial +
                    φ*(K_matrix/K_fluid_initial - K_matrix/K_fluid_new))⁻¹
        """
        if porosity <= 0:
            return k_sat_initial

        # Gassmann equation
        term1 = k_sat_initial / (k_matrix - k_sat_initial)
        term2 = k_fluid_initial / (porosity * (k_matrix - k_fluid_initial))
        term3 = k_fluid_new / (porosity * (k_matrix - k_fluid_new))

        k_sat_new = k_matrix / (1 + 1 / (term1 - term2 + term3))

        return k_sat_new

    def saturated_density(
        self, rho_matrix: float, rho_fluid: float, porosity: float
    ) -> float:
        """
        Bulk density of fluid-saturated rock.
        ρ_sat = (1 - φ) × ρ_matrix + φ × ρ_fluid
        """
        return (1 - porosity) * rho_matrix + porosity * rho_fluid

    def moduli_to_velocities(
        self, k_sat: float, mu_sat: float, rho_sat: float
    ) -> tuple[float, float]:
        """
        Convert elastic moduli to seismic velocities.
        Vp = √((K + 4/3 μ) / ρ)
        Vs = √(μ / ρ)
        """
        vp = np.sqrt((k_sat + (4 / 3) * mu_sat) / rho_sat)
        vs = np.sqrt(mu_sat / rho_sat)
        return vp, vs

    def velocities_to_moduli(
        self, vp: float, vs: float, rho: float
    ) -> tuple[float, float]:
        """
        Convert seismic velocities to elastic moduli.
        μ = ρ × Vs²
        K = ρ × Vp² - 4/3 μ
        """
        mu = rho * vs**2
        k = rho * vp**2 - (4 / 3) * mu
        return k, mu

    def forward(
        self,
        sample: DepthSample,
        mineral_fractions: dict[str, float],
        sw_new: float | None = None,
    ) -> DepthSample:
        """
        Forward rock physics: compute saturated elastic properties.

        Args:
            sample: Input CANON_9 sample
            mineral_fractions: {quartz: 0.7, calcite: 0.1, clay: 0.2}
            sw_new: Optional new water saturation for fluid substitution

        Returns:
            Updated sample with computed Vp, Vs, density
        """
        # Matrix properties
        k_matrix, mu_matrix = self.minerals.voigt_matrix_moduli(mineral_fractions)
        rho_matrix = self.minerals.matrix_density(mineral_fractions)

        # Porosity
        phi = sample.porosity

        # Fluid properties
        sw = sw_new if sw_new is not None else sample.sw
        so = 0.0  # Simplified - oil fraction
        sg = max(0, 1 - sw - so)  # Gas fraction

        k_fluid = self.fluids.mixture_bulk_mod(sw, so, sg)
        rho_fluid = self.fluids.mixture_density(sw, so, sg)

        # Compute saturated moduli
        # Simplified: assume mu is fluid-independent (valid for most rocks)
        k_sat = self.fluid_substitution(
            k_sat_initial=k_matrix * 0.8,  # Approximation
            k_matrix=k_matrix,
            k_fluid_initial=self.fluids.water_bulk_mod,
            k_fluid_new=k_fluid,
            porosity=phi,
        )
        mu_sat = mu_matrix * (1 - phi)  # Simplified

        # Saturated density
        rho_sat = self.saturated_density(rho_matrix, rho_fluid, phi)

        # Convert to velocities
        vp, vs = self.moduli_to_velocities(k_sat, mu_sat, rho_sat)

        return DepthSample(
            depth=sample.depth,
            density=rho_sat,
            vp=vp,
            vs=vs,
            resistivity=sample.resistivity,  # Would need Archie here
            magnetic_suscept=sample.magnetic_suscept,
            thermal_conduct=sample.thermal_conduct,
            pressure=sample.pressure,
            temperature=sample.temperature,
            porosity=sample.porosity,
            sw=np.clip(sw, 0.0, 1.0),
            salinity=sample.salinity,
            sources={
                "rock_physics": "Gassmann",
                "fluid_sub": f"Sw={np.clip(sw,0,1):.2f}",
            },
        )

    def inverse_solve_porosity(
        self,
        vp: float,
        vs: float,
        rho: float,
        mineral_fractions: dict[str, float],
        sw: float = 1.0,
    ) -> float:
        """
        Inverse: solve for porosity given velocities and density.
        Uses iterative Gassmann solve.
        """
        k_matrix, mu_matrix = self.minerals.voigt_matrix_moduli(mineral_fractions)
        rho_matrix = self.minerals.matrix_density(mineral_fractions)

        k_fluid = self.fluids.mixture_bulk_mod(sw)
        rho_fluid = self.fluids.mixture_density(sw)

        # Observed moduli
        k_obs, mu_obs = self.velocities_to_moduli(vp, vs, rho)

        # Iterate to find phi
        def residual(phi):
            rho_pred = (1 - phi) * rho_matrix + phi * rho_fluid
            # Simplified - full Gassmann iteration needed
            k_pred = k_matrix * (1 - phi) + phi * k_fluid
            return (k_pred - k_obs) ** 2 + (rho_pred - rho) ** 2

        # Simple grid search
        phis = np.linspace(0, 0.5, 100)
        residuals = [residual(p) for p in phis]
        return phis[np.argmin(residuals)]
