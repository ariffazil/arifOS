"""
stages/ — arifOS v38 Pipeline Stage Modules

This package contains modular implementations of pipeline stages.
Each stage is a distinct module with:
- compute_*() function for measurable signal extraction
- stage_*() function for state transformation

Stages:
- stage_000_amanah: Risk gate + Amanah lock (F1)
- stage_555_empathy: Empathy measurement (F6 kappa_r)

Author: arifOS Project
Version: v38.0
"""

# Stage 000 Amanah now uses canonical_core (The Great Purge)
from canonical_core.stage_000 import (
    compute_amanah_score,
    AmanahSignals,
)
# Backward compatibility alias
stage_000_amanah = None  # Deprecated, use Stage000VOID.execute() instead
from .stage_555_empathy import (
    compute_kappa_r,
    stage_555_empathy,
    EmpathySignals,
)

__all__ = [
    # Stage 000
    "compute_amanah_score",
    "stage_000_amanah",
    "AmanahSignals",
    # Stage 555
    "compute_kappa_r",
    "stage_555_empathy",
    "EmpathySignals",
]
