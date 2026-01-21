"""
Floor Validators - Import Redirect (v50)

This module exists for backward compatibility.
All floor validators are now consolidated in the canonical source:
    arifos/core/floor_validators.py

AUTHORITY: Δ (Architect) per F4 (Clarity/Entropy Reduction)
VERSION: v50.0.0
"""

# Redirect all imports to canonical source
from arifos.core.floor_validators import (
                                          validate_all_floors,
                                          validate_f1_amanah,
                                          validate_f2_truth,
                                          validate_f3_tri_witness,
                                          validate_f3_triwitness,  # Backward compat alias
                                          validate_f4_clarity,
                                          validate_f5_peace,
                                          validate_f6_empathy,
                                          validate_f7_humility,
                                          validate_f8_genius,
                                          validate_f9_cdark,
                                          validate_f10_ontology,
                                          validate_f11_command_auth,
                                          validate_f12_injection_defense,
                                          validate_f13_curiosity,
)

__all__ = [
    "validate_f1_amanah",
    "validate_f2_truth",
    "validate_f3_tri_witness",
    "validate_f3_triwitness",
    "validate_f4_clarity",
    "validate_f5_peace",
    "validate_f6_empathy",
    "validate_f7_humility",
    "validate_f8_genius",
    "validate_f9_cdark",
    "validate_f10_ontology",
    "validate_f11_command_auth",
    "validate_f12_injection_defense",
    "validate_f13_curiosity",
    "validate_all_floors",
]
