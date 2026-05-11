"""
Porosity Solvers — Vsh and Porosity Calculation
DITEMPA BUKAN DIBERI

Vsh from Gamma Ray
Porosity from Density-Neutron crossover

F2 Truth: Environmental corrections explicit.
F7 Humility: Uncertainty from matrix/fluid assumptions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass
class PorosityResult:
    """Result from porosity calculation."""

    phi: float  # Porosity (fraction)
    phi_uncertainty: float  # Absolute uncertainty (fraction)
    method: str  # Calculation method
    inputs: dict  # Input parameters
    environmental_corrections: list[str]  # Corrections applied

    @property
    def phi_low(self) -> float:
        """95% CI lower bound."""
        return max(0.0, self.phi - 1.96 * self.phi_uncertainty)

    @property
    def phi_high(self) -> float:
        """95% CI upper bound."""
        return min(0.6, self.phi + 1.96 * self.phi_uncertainty)


@dataclass
class VshResult:
    """Result from Vsh calculation."""

    vsh: float  # Shale volume (fraction)
    vsh_uncertainty: float  # Absolute uncertainty
    method: str  # Linear, Clavier-Fertl, etc.
    gr_clean: float  # Clean sand GR value used
    gr_shale: float  # Shale GR value used

    @property
    def vsh_low(self) -> float:
        """95% CI lower bound."""
        return max(0.0, self.vsh - 1.96 * self.vsh_uncertainty)

    @property
    def vsh_high(self) -> float:
        """95% CI upper bound."""
        return min(1.0, self.vsh + 1.96 * self.vsh_uncertainty)


class PorositySolver(ABC):
    """Abstract base for porosity solvers."""

    @abstractmethod
    def compute_phi(self, **kwargs) -> PorosityResult:
        """Compute porosity."""
        pass


class VshSolver:
    """
    Shale volume (Vsh) calculation from Gamma Ray.

    Methods:
    - Linear: Simple linear interpolation between clean and shale endpoints
    - Clavier-Fertl: Non-linear correction for low Vsh

    F4 Clarity: GR endpoints must be explicit and documented.
    """

    def __init__(
        self,
        gr_clean: float = 30.0,  # API units
        gr_shale: float = 120.0,  # API units
    ):
        self.gr_clean = gr_clean
        self.gr_shale = gr_shale

        if gr_shale <= gr_clean:
            raise ValueError(f"gr_shale ({gr_shale}) must be > gr_clean ({gr_clean})")

    def compute_linear(
        self,
        gr: float,  # Gamma ray reading (API)
    ) -> VshResult:
        """
        Linear Vsh calculation: Vsh = (GR - GR_clean) / (GR_shale - GR_clean)

        Simple but overestimates Vsh at low values.
        """
        igr = (gr - self.gr_clean) / (self.gr_shale - self.gr_clean)
        igr = np.clip(igr, 0.0, 1.0)

        # Linear Vsh equals IGR
        vsh = igr

        # Uncertainty: approximately 10% of reading due to GR statistics + endpoint uncertainty
        sigma_gr = 5.0  # API units
        sigma_endpoints = 10.0  # API units (combined clean + shale uncertainty)

        d_igr_d_gr = 1.0 / (self.gr_shale - self.gr_clean)
        vsh_uncertainty = np.sqrt(
            (d_igr_d_gr * sigma_gr) ** 2 + (d_igr_d_gr * sigma_endpoints) ** 2
        )

        return VshResult(
            vsh=float(vsh),
            vsh_uncertainty=float(vsh_uncertainty),
            method="linear",
            gr_clean=self.gr_clean,
            gr_shale=self.gr_shale,
        )

    def compute_clavier_fertl(
        self,
        gr: float,  # Gamma ray reading (API)
    ) -> VshResult:
        """
        Clavier-Fertl (1984) Vsh calculation.

        Better for low Vsh values. Uses nonlinear correction.

        Vsh = 1.7 - sqrt(3.38 - (IGR + 0.7)^2)

        Or equivalently from some formulations:
        Vsh = IGR / (3 - 2*IGR)  # Steiber

        Using Larionov (1969) for Tertiary rocks:
        Vsh = 0.083 * (2^(3.7*IGR) - 1)
        """
        igr = (gr - self.gr_clean) / (self.gr_shale - self.gr_clean)
        igr = np.clip(igr, 0.0, 1.0)

        # Larionov (Tertiary) - good for young basins like Malay
        if igr <= 0.0:
            vsh = 0.0
        else:
            vsh = 0.083 * (2 ** (3.7 * igr) - 1)

        vsh = np.clip(vsh, 0.0, 1.0)

        # Uncertainty higher for nonlinear transforms
        sigma_gr = 5.0
        sigma_endpoints = 10.0

        # Approximate derivative numerically
        delta = 0.001
        igr_plus = np.clip(igr + delta, 0, 1)
        igr_minus = np.clip(igr - delta, 0, 1)

        if igr_plus > 0:
            vsh_plus = 0.083 * (2 ** (3.7 * igr_plus) - 1)
        else:
            vsh_plus = 0.0

        if igr_minus > 0:
            vsh_minus = 0.083 * (2 ** (3.7 * igr_minus) - 1)
        else:
            vsh_minus = 0.0

        d_vsh_d_igr = (vsh_plus - vsh_minus) / (2 * delta)
        d_igr_d_gr = 1.0 / (self.gr_shale - self.gr_clean)

        vsh_uncertainty = np.sqrt(
            (d_vsh_d_igr * d_igr_d_gr * sigma_gr) ** 2
            + (d_vsh_d_igr * d_igr_d_gr * sigma_endpoints) ** 2
        )

        return VshResult(
            vsh=float(vsh),
            vsh_uncertainty=float(vsh_uncertainty),
            method="clavier_fertl_larionov",
            gr_clean=self.gr_clean,
            gr_shale=self.gr_shale,
        )


class DensityNeutronSolver(PorositySolver):
    """
    Porosity from density-neutron crossover.

    Crossover detection indicates gas or bad data.
    Average of density and neutron porosity is typical for liquid-filled zones.

    F2 Truth: Matrix and fluid densities must be explicit.
    """

    # Default matrix densities (g/cm³)
    RHO_MATRIX_QUARTZ = 2.65
    RHO_MATRIX_LIMESTONE = 2.71
    RHO_MATRIX_DOLOMITE = 2.87

    # Default fluid density (g/cm³)
    RHO_FLUID_WATER = 1.0
    RHO_FLUID_OIL = 0.8
    RHO_FLUID_GAS = 0.1  # Highly variable

    def __init__(
        self,
        rho_matrix: float = 2.65,  # g/cm³
        rho_fluid: float = 1.0,  # g/cm³
        lithology: Literal["sandstone", "limestone", "dolomite"] = "sandstone",
    ):
        self.rho_matrix = rho_matrix
        self.rho_fluid = rho_fluid
        self.lithology = lithology

    def compute_phi(
        self,
        rhob: float,  # Bulk density (g/cm³)
        nphi: float | None = None,  # Neutron porosity (fraction or %)
        **kwargs,
    ) -> PorosityResult:
        """
        Compute porosity from density-neutron.

        Args:
            rhob: Bulk density from log (g/cm³)
            nphi: Neutron porosity (fraction, e.g., 0.20 for 20 pu)

        Returns:
            PorosityResult with phi and uncertainty
        """
        # Density porosity
        # phi_d = (rho_matrix - rho_bulk) / (rho_matrix - rho_fluid)
        phi_density = (self.rho_matrix - rhob) / (self.rho_matrix - self.rho_fluid)
        phi_density = np.clip(phi_density, 0.0, 1.0)

        # Neutron porosity (if available)
        if nphi is not None:
            # Handle percent vs fraction
            if nphi > 1.0:
                nphi = nphi / 100.0

            phi_neutron = np.clip(nphi, 0.0, 0.6)

            # Check for crossover (gas indicator)
            crossover = phi_neutron - phi_density

            # Average for liquid-filled zones
            # For gas, density is more reliable (neutron reads low)
            if crossover < -0.05:  # Significant crossover, possible gas
                phi = phi_density  # Prefer density in gas
                method = "density_preferred_gas"
                corrections = ["crossover_detected_gas_possible"]
            elif crossover > 0.05:  # Reverse crossover, possible bad data
                phi = (phi_density + phi_neutron) / 2
                method = "average_with_warning"
                corrections = ["reverse_crossover_check_data"]
            else:
                # Normal liquid-filled zone
                phi = (phi_density + phi_neutron) / 2
                method = "density_neutron_average"
                corrections = []
        else:
            # Density only
            phi = phi_density
            method = "density_only"
            corrections = ["neutron_unavailable"]

        # Uncertainty estimation
        # Density uncertainty: tool precision ~0.01 g/cm³
        sigma_rhob = 0.01
        d_phi_d_rhob = -1.0 / (self.rho_matrix - self.rho_fluid)
        phi_unc_density = abs(d_phi_d_rhob * sigma_rhob)

        # Matrix density uncertainty (lithology uncertainty)
        sigma_rho_matrix = 0.05  # g/cm³
        d_phi_d_matrix = (rhob - self.rho_fluid) / (
            self.rho_matrix - self.rho_fluid
        ) ** 2
        phi_unc_matrix = abs(d_phi_d_matrix * sigma_rho_matrix)

        # Combine uncertainties
        phi_uncertainty = np.sqrt(phi_unc_density**2 + phi_unc_matrix**2)

        # Add neutron uncertainty if used
        if nphi is not None:
            sigma_nphi = 0.02  # ~2 pu absolute
            phi_uncertainty = np.sqrt(phi_uncertainty**2 + (sigma_nphi / 2) ** 2)

        return PorosityResult(
            phi=float(phi),
            phi_uncertainty=float(phi_uncertainty),
            method=method,
            inputs={
                "rhob": rhob,
                "nphi": nphi,
                "rho_matrix": self.rho_matrix,
                "rho_fluid": self.rho_fluid,
                "lithology": self.lithology,
            },
            environmental_corrections=corrections,
        )

    def compute_effective_porosity(
        self,
        phi_total: float,
        vsh: float,
        phi_shale: float = 0.30,  # Shale porosity (fraction)
    ) -> PorosityResult:
        """
        Convert total porosity to effective porosity.

        phi_e = phi_t - Vsh * phi_shale

        Args:
            phi_total: Total porosity (fraction)
            vsh: Shale volume (fraction)
            phi_shale: Porosity of adjacent shale (fraction)
        """
        phi_e = phi_total - vsh * phi_shale
        phi_e = max(0.0, phi_e)

        # Uncertainty from Vsh uncertainty (~10% relative)
        sigma_vsh = 0.10 * vsh if vsh > 0 else 0.05
        sigma_phi_shale = 0.05  # 5 pu absolute

        unc_vsh_term = (sigma_vsh * phi_shale) ** 2
        unc_phi_shale_term = (vsh * sigma_phi_shale) ** 2

        phi_uncertainty = np.sqrt(unc_vsh_term + unc_phi_shale_term)

        return PorosityResult(
            phi=float(phi_e),
            phi_uncertainty=float(phi_uncertainty),
            method="effective_from_total",
            inputs={
                "phi_total": phi_total,
                "vsh": vsh,
                "phi_shale": phi_shale,
            },
            environmental_corrections=["vsh_correction_applied"],
        )


def compute_bvw(
    phi: float,
    sw: float,
    phi_uncertainty: float = 0.0,
    sw_uncertainty: float = 0.0,
) -> tuple[float, float]:
    """
    Compute Bulk Volume Water (BVW = phi * Sw) with uncertainty.

    Returns:
        (bvw, bvw_uncertainty)
    """
    bvw = phi * sw

    # Uncertainty propagation
    # BVW = phi * Sw
    # sigma_BVW = sqrt((Sw * sigma_phi)^2 + (phi * sigma_Sw)^2)
    bvw_uncertainty = np.sqrt((sw * phi_uncertainty) ** 2 + (phi * sw_uncertainty) ** 2)

    return float(bvw), float(bvw_uncertainty)


def compute_permeability_proxy(
    phi: float,
    sw: float | None = None,
    method: Literal["timur_coates", "simple_power"] = "simple_power",
) -> tuple[float, str]:
    """
    Compute permeability proxy (order of magnitude only).

    Args:
        phi: Effective porosity (fraction)
        sw: Water saturation (fraction), optional
        method: Permeability estimation method

    Returns:
        (k_proxy_mD, method_description)
    """
    if method == "simple_power":
        # k ∝ phi^3 — Kozeny-Carman order-of-magnitude proxy
        # phi=0.10 → ~1 mD, phi=0.25 → ~16 mD
        k = 1000 * (phi**3)  # mD
        description = f"k = 1000 * phi^6 = {k:.2f} mD (order of magnitude only)"
    elif method == "timur_coates":
        # Timur/Coates: k = (100 * phi^2 / (1-phi))^2 * ((1-Sw)/Sw)^2
        if sw is not None and sw < 1.0:
            k = (100 * phi**2 / (1 - phi)) ** 2 * ((1 - sw) / sw) ** 2
            description = f"Timur-Coates: k = {k:.2f} mD"
        else:
            k = 1000 * (phi**6)
            description = "Timur-Coates requires Sw < 1, using fallback"
    else:
        k = 1000 * (phi**6)
        description = "Unknown method, using fallback"

    return float(k), description
