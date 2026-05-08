"""
WEALTH — Sovereign Governance & Forge Laws
Codification of the 6 Forge Laws and Epistemic Metrics.
"""

import enum
from typing import Any, Dict, List

class ForgeLaw(enum.Enum):
    F1_REVERSIBILITY = "Reversible by default; permanent only by SEAL."
    F2_TRUTH = "Truth over consensus; data origin over metadata."
    F3_WITNESS = "Tri-witness validation: Human, AI, Earth."
    F4_LEGIBILITY = "No hand-wavy math; shadow prices only."
    F5_MARUAH = "Maintain sovereign dignity (Maruah)."
    F6_HUMILITY = "Bound arrogance via kappa_r (Reasoning Coherence)."

def compute_kappa_r(rasa_score: float, truth_consistency: float) -> float:
    """
    Computes Humility score (Reasoning coherence).
    [0.0, 1.0] where 1.0 is perfectly coherent and humble.
    """
    return round((rasa_score * 0.4) + (truth_consistency * 0.6), 4)

def compute_psi_le(legibility_entropy: float, complexity: float) -> float:
    """
    Computes psi_le (Legibility entropy).
    Measures the gap between model complexity and human-auditable legibility.
    """
    return round(legibility_entropy / (1.0 + complexity), 4)

def get_qdf_version() -> str:
    """Returns the current Quantitative Decision Framework version."""
    return "QDF-v2.0-TRINITY"
