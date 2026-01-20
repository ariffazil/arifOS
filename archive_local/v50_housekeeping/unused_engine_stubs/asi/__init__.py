"""
ASI (Ω Omega) Kernel — The Auditor

Role: Warm Care & Empathy
Mandate: "Is this SAFE to receive?"
Primary Floors: F3 Peace² (≥1.0), F4 κᵣ (≥0.95), F5 Ω₀ (0.03-0.05), F7 RASA
Pipeline Stages: 444 ALIGN, 555 EMPATHIZE, 666 BRIDGE, 777 FORGE (EUREKA-777)
Authority: SABAR only — can pause/cool, cannot seal

Part of v46 Trinity Orthogonal AAA Architecture.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

# Import kernel classes
from .kernel import ASIKernel, ASIActionCore

from .empathy.empathy_architect import EmpathyArchitect
from .floor_checks import (
                           check_kappa_r_f4,
                           check_omega_band_f5,
                           check_peace_squared_f3,
                           check_rasa_f7,
)

__all__ = [
    # Kernel classes
    "ASIKernel",
    "ASIActionCore",
    # Empathy and floor checks
    "EmpathyArchitect",
    "check_peace_squared_f3",
    "check_kappa_r_f4",
    "check_omega_band_f5",
    "check_rasa_f7",
]
