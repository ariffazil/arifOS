"""
TRL — Tensor Representation Layer for RASA DERITA v2 (geometric).

Status: DESIGN_LANDED · computation PARTIAL (ER seeds only) · 888_HOLD for full geometry

v1.0 DERITA: narrative → constitutional (labels ↔ floors)
v2.0 DERITA: constitutional → geometric (coordinates, geodesics, topology)

This package lands:
  - M_trauma coordinate model (5 axes as coordinates, not mere labels)
  - Diagonal metric placeholder g_ij (config, not estimated curvature)
  - ER1–ER5 scalar seeds (proportionality / cascade / bilinear / kinetics / Ω₀)
  - Φ-witnessing protocol constraints (F9/F10 — never claim lived experience)
  - Explicit NOT_IMPLEMENTED for geodesic, bifurcation, persistent homology

F13 remains absolute: geometric precision without sovereign veto = weapon.
Geometric precision WITH F13 = governed intelligence.

DITEMPA BUKAN DIBERI
"""

from arifosmcp.kernel.trl.coordinates import (
    AXIS_BOUNDS,
    TraumaCoordinates,
    axis_index,
    clamp_coordinates,
)
from arifosmcp.kernel.trl.er_seeds import (
    er1_betrayal_ratio,
    er2_cascade_depth,
    er3_power_consent_harm,
    er4_naming_metabolization,
    er5_omega_zero_band,
)
from arifosmcp.kernel.trl.phi_witness import PhiWitness, phi_witness, forbidden_phi_phrases
from arifosmcp.kernel.trl.geometry_status import (
    GeometryCapability,
    geometry_capability_matrix,
    geodesic_not_implemented,
    bifurcation_not_implemented,
    homology_not_implemented,
)

__all__ = [
    "AXIS_BOUNDS",
    "TraumaCoordinates",
    "axis_index",
    "clamp_coordinates",
    "er1_betrayal_ratio",
    "er2_cascade_depth",
    "er3_power_consent_harm",
    "er4_naming_metabolization",
    "er5_omega_zero_band",
    "PhiWitness",
    "phi_witness",
    "forbidden_phi_phrases",
    "GeometryCapability",
    "geometry_capability_matrix",
    "geodesic_not_implemented",
    "bifurcation_not_implemented",
    "homology_not_implemented",
]
