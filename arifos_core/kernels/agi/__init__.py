"""
arifOS AGI Kernel — Delta Engine (F1-F2)

v47 Stage 333_atlas per L1_THEORY/canon/333_atlas/310_AGI_DELTA_ARCHITECT_v46.md

Floors:
- F1: Truth floor (per L1/333_atlas/340_TRUTH_F1_v46.md)
- F2: Clarity floor (per L1/333_atlas/350_CLARITY_F2_v46.md)

Delta (Δ) responsibility:
  Propose truth and clarity in the constitution.
  Exploration before judgment.

DITEMPA BUKAN DIBERI
"""

from .truth_floor import check_truth_f1, F1TruthResult
from .clarity_floor import check_delta_s_f2, F2DeltaSResult

__all__ = [
    "check_truth_f1",
    "F1TruthResult",
    "check_delta_s_f2",
    "F2DeltaSResult",
]
