"""
arifOS APEX Module - The Soul Engine (Tools + Resources)

v54.0: 9-PARADOX CONSTITUTIONAL MATRIX

Architecture:
- Trinity Alpha: Core Virtues (Truth·Care, Clarity·Peace, Humility·Justice)
- Trinity Beta: Implementation (Precision·Rev, Hierarchy·Consent, Agency·Protection)
- Trinity Gamma: Temporal/Meta (Urgency·Sustain, Certainty·Doubt, Unity·Diversity)

Equilibrium Point:
E* = argmin_E [(GM(E) - 0.85)² + σ(E)²]

Where:
- GM(E) = geometric mean of 9 paradox scores
- σ(E) = standard deviation

Verdicts:
- EQUILIBRIUM: All conditions met (GM≥0.85, σ≤0.10, all≥0.70)
- SEAL: High score but not perfect equilibrium
- VOID: Constitutional breach
- SABAR: Unbalanced
- 888_HOLD: Needs human review

Exports:
- TrinityNine: Main 9-paradox synchronization engine
- EquilibriumFinder: Finds equilibrium points
- PerturbationAnalyzer: Tests resilience

DITEMPA BUKAN DIBERI
"""

from .trinity_nine import (
    TrinityNine,
    NineFoldBundle,
    NineParadox,
    EquilibriumState,
    EquilibriumSolver,
    TrinityTier,
    create_nine_paradoxes,
    trinity_nine_sync,
    check_equilibrium,
    EQUILIBRIUM_THRESHOLD,
    BALANCE_TOLERANCE,
    MIN_PARADOX_SCORE
)

from .equilibrium_finder import (
    EquilibriumFinder,
    EquilibriumPoint,
    PerturbationAnalyzer,
    demonstrate_equilibrium
)

__version__ = "v54.0-9PARADOX"
__all__ = [
    # Trinity Nine
    "TrinityNine",
    "NineFoldBundle",
    "NineParadox",
    "EquilibriumState",
    "EquilibriumSolver",
    "TrinityTier",
    "create_nine_paradoxes",
    "trinity_nine_sync",
    "check_equilibrium",
    
    # Equilibrium
    "EquilibriumFinder",
    "EquilibriumPoint",
    "PerturbationAnalyzer",
    "demonstrate_equilibrium",
    
    # Constants
    "EQUILIBRIUM_THRESHOLD",
    "BALANCE_TOLERANCE",
    "MIN_PARADOX_SCORE",
]
