# -*- coding: utf-8 -*-
"""
Enforcement Package - Re-exports canonical validators from arifos.core.
Maintains backward compatibility while enforcing single source of truth.
"""

from arifos.core.floor_validators import (
                                          validate_f1_amanah,
                                          validate_f2_truth,
                                          validate_f3_triwitness,
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
]
