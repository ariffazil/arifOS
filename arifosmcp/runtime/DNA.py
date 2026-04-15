"""
arifosmcp/runtime/DNA.py — The arifOS Genome (v2026.04)
IMMUTABLE CONSTITUTIONAL CONSTANTS.
"""

from typing import Final, List, Tuple

# --- VERSIONING ---
VERSION: Final[str] = "2026.04.16"
CODENAME: Final[str] = "REFORGE_EARTH_WITNESS"

# --- F7 HUMILITY BAND (OMNIPRESENT) ---
OMEGA_BAND: Final[Tuple[float, float]] = (0.03, 0.05)
OMEGA_CENTER: Final[float] = 0.04

# --- THE 13 CONSTITUTIONAL FLOORS ---
FLOORS: Final[List[str]] = [
    "F1_AMANAH",      # Reversibility
    "F2_TRUTH",       # Thermodynamic Cost
    "F3_JUSTICE",     # Proportionality
    "F4_CLARITY",     # ΔS ≤ 0
    "F5_EMPATHY",     # Stakeholder consequences
    "F6_ANTI_HANTU",  # Direct > Clever
    "F7_HUMILITY",    # Uncertainty Band [0.03-0.05]
    "F8_GENIUS",      # G† Calculation
    "F9_ETHICS",      # Anti-Manipulation
    "F10_REFLECTION", # Self-Audit
    "F11_CONTINUITY", # Auth Lineage
    "F12_DEFENSE",    # Input Hardening
    "F13_SOVEREIGN",  # 888_JUDGE Veto
]

# --- METABOLIC LIMITS ---
DENSITY_TARGET: Final[float] = 300.0  # LOC / File
MAX_ENTROPY_DRIFT: Final[float] = 0.15 # Max ΔS before SABAR trigger

# --- TELOS DEFAULTS ---
TELOS_AXES: Final[List[str]] = [
    "performance", "understanding", "stability", "harmony",
    "exploration", "preservation", "agency", "integration"
]

MOTTO: Final[str] = "DITEMPA BUKAN DIBERI — Forged, Not Given"
