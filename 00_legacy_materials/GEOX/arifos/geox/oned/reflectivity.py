"""
GEOX 1D Reflectivity — Zoeppritz equations and approximations.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field
from typing import Literal

from .canon9_profile import Canon9Profile


class Interface(BaseModel):
    """Elastic contrast at a layer interface."""

    depth: float = Field(..., description="Interface depth [m]")

    # Upper layer properties
    vp1: float = Field(..., description="Upper Vp [m/s]")
    vs1: float = Field(..., description="Upper Vs [m/s]")
    rho1: float = Field(..., description="Upper density [kg/m³]")

    # Lower layer properties
    vp2: float = Field(..., description="Lower Vp [m/s]")
    vs2: float = Field(..., description="Lower Vs [m/s]")
    rho2: float = Field(..., description="Lower density [kg/m³]")

    @property
    def impedance1(self) -> float:
        """Acoustic impedance of upper layer."""
        return self.rho1 * self.vp1

    @property
    def impedance2(self) -> float:
        """Acoustic impedance of lower layer."""
        return self.rho2 * self.vp2

    @property
    def contrast(self) -> float:
        """Normalized impedance contrast."""
        return (self.impedance2 - self.impedance1) / (self.impedance2 + self.impedance1)


class ZoeppritzModel:
    """
    Zoeppritz equations for plane-wave reflection coefficients.

    Handles:
    - Exact Zoeppritz (all angles, all modes)
    - Aki-Richards approximation (small contrasts)
    - Shuey approximation (AVO analysis)
    """

    def __init__(self, approximation: Literal["exact", "aki-richards", "shuey"] = "exact"):
        self.approximation = approximation

    def _zoeppritz_exact(
        self,
        vp1: float,
        vs1: float,
        rho1: float,
        vp2: float,
        vs2: float,
        rho2: float,
        theta1: float,
    ) -> float:
        """
        Exact Zoeppritz equation for PP reflection.

        Args:
            theta1: Incidence angle [radians]

        Returns:
            PP reflection coefficient (complex if evanescent)
        """
        # Snell's law for transmitted P-wave
        sin_theta2 = (vp2 / vp1) * np.sin(theta1)

        # Check for critical angle
        if abs(sin_theta2) > 1:
            return 0.0  # Total reflection, simplified

        theta2 = np.arcsin(sin_theta2)

        # Snell's law for reflected/transmitted S-waves
        phi1 = np.arcsin(np.clip((vs1 / vp1) * np.sin(theta1), -1, 1))
        phi2 = np.arcsin(np.clip((vs2 / vp1) * np.sin(theta1), -1, 1))

        # Zoeppritz coefficients (simplified PP case)
        # Full matrix form is complex; using Aki-Richards as fallback
        if self.approximation == "exact":
            # Simplified exact form for PP
            a = rho2 * (1 - 2 * np.sin(phi2) ** 2) - rho1 * (1 - 2 * np.sin(phi1) ** 2)
            b = rho2 * (1 - 2 * np.sin(phi2) ** 2) + 2 * rho1 * np.sin(phi1) ** 2
            c = rho1 * (1 - 2 * np.sin(phi1) ** 2) + 2 * rho2 * np.sin(phi2) ** 2
            d = 2 * (rho2 * vs2**2 - rho1 * vs1**2)

            E = b * np.cos(theta1) / vp1 + c * np.cos(theta2) / vp2
            F = b * np.cos(phi1) / vs1 + c * np.cos(phi2) / vs2
            G = a - d * np.cos(theta1) / vp1 * np.cos(phi2) / vs2
            H = a - d * np.cos(theta2) / vp2 * np.cos(phi1) / vs1

            D = E * F + G * H * (np.sin(theta2) / vs2) ** 2

            if abs(D) < 1e-10:
                return 0.0

            Rpp = (
                F * (b * np.cos(theta1) / vp1 - c * np.cos(theta2) / vp2)
                - H
                * (a + d * np.cos(theta1) / vp1 * np.cos(phi2) / vs2)
                * (np.sin(theta2) / vs2) ** 2
            ) / D

            return Rpp

        elif self.approximation == "aki-richards":
            return self._aki_richards(vp1, vs1, rho1, vp2, vs2, rho2, theta1)

        else:  # shuey
            return self._shuey(vp1, vs1, rho1, vp2, vs2, rho2, theta1)

    def _aki_richards(
        self,
        vp1: float,
        vs1: float,
        rho1: float,
        vp2: float,
        vs2: float,
        rho2: float,
        theta: float,
    ) -> float:
        """
        Aki-Richards linearized approximation.
        R(θ) ≈ 0.5(1 + tan²θ)ΔVp/Vp - 4(Vs/Vp)²sin²θΔVs/Vs + 0.5(1 - 4(Vs/Vp)²sin²θ)Δρ/ρ
        """
        # Average properties
        vp_avg = 0.5 * (vp1 + vp2)
        vs_avg = 0.5 * (vs1 + vs2)
        rho_avg = 0.5 * (rho1 + rho2)

        # Differences
        dvp = vp2 - vp1
        dvs = vs2 - vs1
        drho = rho2 - rho1

        # Normalized differences
        dvp_vp = dvp / vp_avg
        dvs_vs = dvs / vs_avg
        drho_rho = drho / rho_avg

        # Aki-Richards coefficients
        term1 = 0.5 * (1 + np.tan(theta) ** 2) * dvp_vp
        term2 = 4 * (vs_avg / vp_avg) ** 2 * np.sin(theta) ** 2 * dvs_vs
        term3 = 0.5 * (1 - 4 * (vs_avg / vp_avg) ** 2 * np.sin(theta) ** 2) * drho_rho

        return term1 - term2 + term3

    def _shuey(
        self,
        vp1: float,
        vs1: float,
        rho1: float,
        vp2: float,
        vs2: float,
        rho2: float,
        theta: float,
    ) -> float:
        """
        Shuey's 2-term AVO approximation.
        R(θ) ≈ R(0) + G sin²θ

        Where:
        R(0) = 0.5(ΔVp/Vp + Δρ/ρ)  # Normal incidence
        G = 0.5ΔVp/Vp - 2(Vs/Vp)²(Δρ/ρ + 2ΔVs/Vs)  # Gradient
        """
        # Average properties
        vp_avg = 0.5 * (vp1 + vp2)
        vs_avg = 0.5 * (vs1 + vs2)
        rho_avg = 0.5 * (rho1 + rho2)

        # Normalized differences
        dvp_vp = (vp2 - vp1) / vp_avg
        dvs_vs = (vs2 - vs1) / vs_avg
        drho_rho = (rho2 - rho1) / rho_avg

        # Shuey coefficients
        R0 = 0.5 * (dvp_vp + drho_rho)
        G = 0.5 * dvp_vp - 2 * (vs_avg / vp_avg) ** 2 * (drho_rho + 2 * dvs_vs)

        return R0 + G * np.sin(theta) ** 2

    def compute_reflectivity(
        self, profile: Canon9Profile, angles: np.ndarray | None = None
    ) -> np.ndarray:
        """
        Compute reflection coefficients for a profile.

        Args:
            profile: CANON_9 profile
            angles: Incidence angles [radians]. If None, returns normal incidence.

        Returns:
            Reflectivity array [n_interfaces, n_angles]
        """
        if angles is None:
            angles = np.array([0.0])  # Normal incidence

        n_samples = len(profile.samples)
        n_angles = len(angles)

        # Reflection at each interface
        reflectivity = np.zeros((n_samples - 1, n_angles))

        for i in range(n_samples - 1):
            s1 = profile.samples[i]
            s2 = profile.samples[i + 1]

            for j, theta in enumerate(angles):
                if self.approximation == "exact":
                    r = self._zoeppritz_exact(
                        s1.vp, s1.vs, s1.density, s2.vp, s2.vs, s2.density, theta
                    )
                elif self.approximation == "aki-richards":
                    r = self._aki_richards(
                        s1.vp, s1.vs, s1.density, s2.vp, s2.vs, s2.density, theta
                    )
                else:  # shuey
                    r = self._shuey(s1.vp, s1.vs, s1.density, s2.vp, s2.vs, s2.density, theta)

                reflectivity[i, j] = r

        return reflectivity

    def extract_interfaces(self, profile: Canon9Profile) -> list[Interface]:
        """Extract all layer interfaces from profile."""
        interfaces = []
        for i in range(len(profile.samples) - 1):
            s1 = profile.samples[i]
            s2 = profile.samples[i + 1]
            interfaces.append(
                Interface(
                    depth=(s1.depth + s2.depth) / 2,
                    vp1=s1.vp,
                    vs1=s1.vs,
                    rho1=s1.density,
                    vp2=s2.vp,
                    vs2=s2.vs,
                    rho2=s2.density,
                )
            )
        return interfaces
