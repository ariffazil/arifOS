"""
AGI (Mind/Δ) - The Thinker

Unified namespace for arifOS Mind engine.

Modules:
    executor.py     - AGI execution logic (AGIRoom entry point)
    kernel.py       - AGI neural kernel
    hardening.py    - AGI hardening protocols
    metrics.py      - Thermodynamic dashboard (v52.6.0)
    parallel.py     - Parallel hypothesis matrix (v52.6.0)
    evidence.py     - Live evidence injection (v52.6.0)
    stages/         - Metabolic stages (111, 222, 333)
        sense.py    - Stage 111: SENSE
        think.py    - Stage 222: THINK
        reason.py   - Stage 333: REASON
"""

# v52.6.0: Main entry point is AGIRoom
from .executor import AGIRoom, execute_agi_room
from .kernel import AGINeuralCore
from .metrics import ThermodynamicDashboard, get_dashboard
from .parallel import ParallelHypothesisMatrix
from .evidence import EvidenceKernel, get_evidence_kernel

__all__ = [
    "AGIRoom",
    "execute_agi_room",
    "AGINeuralCore",
    "ThermodynamicDashboard",
    "get_dashboard",
    "ParallelHypothesisMatrix",
    "EvidenceKernel",
    "get_evidence_kernel"
]
