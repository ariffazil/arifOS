"""
AGI (Δ Delta) Kernel — The Architect

Role: Cold Analysis & Structure
Mandate: "Is this TRUE?"
Primary Floors: F1 Truth (≥0.99), F2 DeltaS (≥0)
Pipeline Stages: 111 SENSE, 222 REFLECT, 333 REASON (ATLAS-333)
Authority: DRAFT only — proposes, cannot seal

Part of v46 Trinity Orthogonal AAA Architecture.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

# Fixed imports to match actual floor_checks.py exports
from .floor_checks import (
    Floor,
    Floor1_Amanah,
    Floor2_Truth,
    Floor3_TriWitness,
    Floor6_DeltaS,  # Fixed: ΔS is Floor 6, not Floor 4
    FloorResult,
    check_agi_floors,
    check_delta_s_f6,  # Fixed: Was check_delta_s_f2
    check_truth_f2,    # Fixed: Was check_truth_f1
)

__all__ = [
    "Floor",
    "Floor1_Amanah",
    "Floor2_Truth",
    "Floor3_TriWitness",
    "Floor6_DeltaS",  # Fixed: ΔS is Floor 6
    "FloorResult",
    "check_agi_floors",
    "check_delta_s_f6",  # Fixed: Was check_delta_s_f2
    "check_truth_f2",    # Fixed: Was check_truth_f1
]
