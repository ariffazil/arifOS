"""
arifos/pipeline/context.py

PipelineContext - Shared state object that flows through stages

The context accumulates:
- Input data (query, user_id, metadata)
- Kernel verdicts (Delta, Omega, Psi)
- Intermediate computations (ΔS, metrics)
- Final verdict and reasoning

Immutable pattern: Each stage returns a new context (or modifies in-place for performance).

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from arifos.agi.delta_kernel import DeltaVerdict
from arifos.apex.psi_kernel import PsiVerdict, Verdict
from arifos.asi.omega_kernel import OmegaVerdict


@dataclass
class PipelineContext:
    """
    Pipeline context that flows through stages 000→999.

    Attributes:
        query: User input
        response: AI output (may be None in early stages)
        user_id: Optional user identifier
        session_id: Optional session identifier

        # Stage results
        hypervisor_passed: F10-F12 hypervisor result
        hypervisor_failures: Hypervisor failure reasons
        delta_verdict: DeltaKernel result (F1-F2)
        omega_verdict: OmegaKernel result (F3-F7, F9)
        psi_verdict: PsiKernel result (F8, final verdict)

        # Metrics
        delta_s: Computed entropy change
        genius_score: F8 genius score
        tri_witness: F3 consensus score
        peace_squared: F4 stability score
        kappa_r: F5 empathy score
        omega_0: F6 humility score
        rasa: F7 felt care
        c_dark: F9 dark cleverness score

        # Control flow
        stage_reached: Highest stage reached before short-circuit
        failures: Accumulated failure messages
        metadata: Additional context
    """
    # Input
    query: str
    response: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Hypervisor (Stage 000)
    hypervisor_passed: bool = True
    hypervisor_failures: List[str] = field(default_factory=list)

    # Trinity Verdicts
    delta_verdict: Optional[DeltaVerdict] = None
    omega_verdict: Optional[OmegaVerdict] = None
    psi_verdict: Optional[PsiVerdict] = None

    # Metrics (computed by stages or provided)
    delta_s: Optional[float] = None
    genius_score: float = 0.85  # Default F8
    tri_witness: float = 0.95   # Default F3
    peace_squared: float = 1.0  # Default F4
    kappa_r: float = 0.95       # Default F5
    omega_0: float = 0.04       # Default F6
    rasa: bool = True           # Default F7
    c_dark: float = 0.15        # Default F9

    # Control flow
    stage_reached: int = 0
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    # Execution flags
    reversible: bool = True
    within_mandate: bool = True

    @property
    def final_verdict(self) -> Optional[Verdict]:
        """Get final verdict from Psi if available."""
        return self.psi_verdict.verdict if self.psi_verdict else None

    @property
    def passed(self) -> bool:
        """Check if final verdict is SEAL."""
        return self.final_verdict == Verdict.SEAL if self.final_verdict else False

    def to_dict(self) -> Dict:
        """Serialize context to dict for logging/debugging."""
        return {
            "query": self.query,
            "response": self.response,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "stage_reached": self.stage_reached,
            "final_verdict": self.final_verdict.value if self.final_verdict else None,
            "passed": self.passed,
            "delta_s": self.delta_s,
            "failures": self.failures,
            "hypervisor_passed": self.hypervisor_passed,
            "delta_passed": self.delta_verdict.passed if self.delta_verdict else None,
            "omega_passed": self.omega_verdict.passed if self.omega_verdict else None,
            "psi_passed": self.psi_verdict.passed if self.psi_verdict else None,
        }


__all__ = ["PipelineContext"]
