"""
arifos_core/pipeline

Pipeline Stages (000→999) - The arifOS Execution Flow

The 9 Stages orchestrate the Trinity Kernels (Δ, Ω, Ψ) through
constitutional evaluation from input to verdict.

Stages:
    000 - Hypervisor: F10-F12 preprocessing gates
    111 - Sense: Parse and validate input
    333 - Reason: Delta kernel (F1-F2) evaluation
    888 - Witness: Psi kernel (F8 + final verdict)
    999 - Seal: Write to cooling ledger

Architecture:
    Context flows through stages → accumulates verdicts → renders final judgment

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from .context import PipelineContext
from .orchestrator import PipelineOrchestrator

__all__ = [
    "PipelineContext",
    "PipelineOrchestrator",
]
