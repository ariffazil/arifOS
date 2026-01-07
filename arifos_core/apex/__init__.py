"""
APEX (Ψ Psi) Kernel — The Judge

Role: Constitutional Judge & Law
Mandate: "Is this LAWFUL?"
Primary Floors: F6 Amanah (LOCK), F8 Tri-Witness (≥0.95), F9 Anti-Hantu (0 violations)
Pipeline Stages: 000 VOID, 888 JUDGE, 999 SEAL
Authority: FINAL VERDICT — sole SEAL power

Part of v46 Trinity Orthogonal AAA Architecture.

CRITICAL: APEX does NOT generate content; it judges.
Verdict authority resides ONLY in apex_prime.py.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

from .floor_checks import (
    check_amanah_f6,
    check_tri_witness_f8,
    check_anti_hantu_f9,
)

__all__ = [
    "check_amanah_f6",
    "check_tri_witness_f8",
    "check_anti_hantu_f9",
]
