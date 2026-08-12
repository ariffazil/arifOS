"""
arifosmcp/hib — Hangat Ingatan Balik (formerly Precedent Retrieval Layer)
════════════════════════════════════════════

Cold geometric law enforcement for arifOS.  Not memory.  Not personality.
Pure vector geometry + structural payload filtering.

Modules:
  - vault_vectorizer.py:  VAULT999 → Qdrant embedding index
  - hib_gate.py:          Dual-Gate precedent enforcement

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from .hib_gate import (
    HibConstraint,
    HibGate,
    HibGateResult,
    classify_blast_radius,
)
from .vault_vectorizer import (
    BLAST_RADIUS_VALUES,
    DEFAULT_BLAST_RADIUS,
    HIB_TAU_THRESHOLD,
    PrecedentVectorizer,
)

__all__ = [
    "HibGate",
    "HibGateResult",
    "HibConstraint",
    "PrecedentVectorizer",
    "classify_blast_radius",
    "BLAST_RADIUS_VALUES",
    "DEFAULT_BLAST_RADIUS",
    "HIB_TAU_THRESHOLD",
]
