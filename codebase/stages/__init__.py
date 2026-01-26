# canonical_core.stages

"""
Metabolic pipeline stages for canonical_core.
Stages 444-889 moved here for entropy reduction.
"""

from codebase.stages import stage_444
from codebase.stages import stage_555
from codebase.stages import stage_666
from codebase.stages import stage_777_forge
from codebase.stages import stage_888_judge
from codebase.stages import stage_889_proof

__all__ = [
    "stage_444",
    "stage_555",
    "stage_666",
    "stage_777_forge",
    "stage_888_judge",
    "stage_889_proof",
]
