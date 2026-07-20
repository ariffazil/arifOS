"""
arifosmcp/prl — Precedent Retrieval Layer
════════════════════════════════════════════

Cold geometric law enforcement for arifOS.  Not memory.  Not personality.
Pure vector geometry + structural payload filtering.

Modules:
  - vault_vectorizer.py:  VAULT999 → Qdrant embedding index
  - prl_gate.py:          Dual-Gate precedent enforcement

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from .prl_gate import (
    PrlConstraint,
    PrlGate,
    PrlGateResult,
    classify_blast_radius,
)
from .vault_vectorizer import (
    BLAST_RADIUS_VALUES,
    DEFAULT_BLAST_RADIUS,
    PRL_TAU_THRESHOLD,
    PrecedentVectorizer,
)

__all__ = [
    "PrlGate",
    "PrlGateResult",
    "PrlConstraint",
    "PrecedentVectorizer",
    "classify_blast_radius",
    "BLAST_RADIUS_VALUES",
    "DEFAULT_BLAST_RADIUS",
    "PRL_TAU_THRESHOLD",
]
