"""
arifos.core.stage
-----------------
Orthogonal Metabolic Loop (Hardened 11-File Structure)

Exports the 11 key stages for the Metabolizer to drive the loop.
"""

# Stage 000 now uses canonical_core (The Great Purge)
from codebase.stage_000 import execute_stage as void_000
from .stage_111_sense import execute_stage as sense_111
from .stage_222_reflect import execute_stage as reflect_222
from .stage_333_reason import execute_stage as reason_333
from .stage_444_evidence import execute_stage as evidence_444
from .stage_555_empathize import execute_stage as empathize_555
from .stage_666_align import execute_stage as align_666
from .stage_777_forge import execute_stage as forge_777
from .stage_888_judge import execute_stage as judge_888
from .stage_889_proof import execute_stage as proof_889
# Stage 999 now uses SEAL999 (The Great Purge - Code/Storage Separation)
# SEAL999 = Code (Algorithm), VAULT999 = Storage (Data)
from SEAL999 import execute_stage as vault_999

__all__ = [
    "void_000",
    "sense_111",
    "reflect_222",
    "reason_333",
    "evidence_444",
    "empathize_555",
    "align_666",
    "forge_777",
    "judge_888",
    "proof_889",
    "vault_999"
]
