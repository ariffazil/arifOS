"""
arifOS Unified Constitutional Kernel (v50.5.25)

The True Core - Master Orchestrator for AGI, ASI, APEX engines.

111-888 Metabolic Pipeline:
    000 INIT     → Gate (Ignition + Authority)
    111 SENSE    → AGI Δ
    222 REFLECT  → AGI Δ
    333 ATLAS    → AGI Δ
    444 EVIDENCE → ASI Ω
    555 EMPATHIZE → ASI Ω
    666 ALIGN    → ASI Ω
    777 FORGE    → EUREKA (AGI + ASI → APEX)
    888 JUDGE    → APEX Ψ
    889 PROOF    → APEX Ψ
    999 SEAL     → Vault

DITEMPA BUKAN DIBERI - Forged, not given.
"""

# Master Kernel Orchestrator (v50.5.25)
from .kernel import (
    Kernel,
    KernelStage,
    KernelVerdict,
    KernelOutput,
    StageResult,
    Lane,
    get_kernel,
    execute_pipeline,
)

# Constitutional Kernel (legacy, still functional)
from .constitutional import ConstitutionalKernel

# Export all kernels
__all__ = [
    # Master Orchestrator
    "Kernel",
    "KernelStage",
    "KernelVerdict",
    "KernelOutput",
    "StageResult",
    "Lane",
    "get_kernel",
    "execute_pipeline",
    # Legacy Constitutional
    "ConstitutionalKernel",
    "UnifiedConstitutionalKernel",
]

class UnifiedConstitutionalKernel:
    """
    Unified entry point for all constitutional governance operations.

    Now delegates to the new Kernel orchestrator while maintaining
    backwards compatibility with the ConstitutionalKernel.

    Usage:
        kernel = UnifiedConstitutionalKernel()

        # New way: Use execute() for full AGI→ASI→APEX pipeline
        result = kernel.execute("Explain quantum entanglement")

        # Legacy way: Use run_constitutional_pipeline()
        result = kernel.run_constitutional_pipeline(query, response)
    """

    def __init__(self, session_id: str = None):
        # New Master Orchestrator (v50.5.24)
        self.kernel = Kernel(session_id)

        # Legacy Constitutional Kernel (still functional)
        self.constitutional = ConstitutionalKernel()

    def execute(self, query: str, context: dict = None,
                proposed_action: str = None, user_id: str = None) -> dict:
        """
        Execute full AGI→ASI→APEX pipeline via Kernel orchestrator.

        This is the NEW preferred method.

        Returns:
            KernelOutput as dict with verdict, proof_hash, etc.
        """
        result = self.kernel.execute(query, context, proposed_action, user_id)
        return result.as_dict()

    def get_health(self) -> dict:
        """Get kernel health status."""
        return {
            "kernel": "operational",
            "constitutional": self.constitutional.health_check(),
            "engines": {
                "agi": self.kernel._agi is not None,
                "asi": self.kernel._asi is not None,
                "apex": self.kernel._apex is not None,
            },
            "status": "full_implementation",
            "version": "50.5.25"
        }

    def run_constitutional_pipeline(self, query: str, response: str, user_id: str = None) -> dict:
        """
        Run the legacy 000→999 constitutional pipeline.

        NOTE: For new code, use execute() instead.
        """
        return self.constitutional.run_pipeline(query, response, user_id)

    def get_constitutional_metrics(self, content: str) -> dict:
        """
        Calculate all 13 constitutional floor metrics.

        Uses ASI (Ω) engine for metric computation with heuristic-based scoring.
        """
        from ..enforcement.eval.asi import ASI

        # Use ASI to compute metrics from content
        asi = ASI()
        result = asi.assess(content)
        metrics = result.metrics

        # Return metrics as dict for MCP compatibility
        return {
            "truth": metrics.truth,
            "delta_s": metrics.delta_s,
            "peace_squared": metrics.peace_squared,
            "kappa_r": metrics.kappa_r,
            "omega_0": metrics.omega_0,
            "amanah": metrics.amanah,
            "tri_witness": metrics.tri_witness,
            "rasa": metrics.rasa,
            "anti_hantu": metrics.anti_hantu,
            "psi": metrics.psi,
            "mode": result.mode.value,
            "uncertainty_calibration": result.uncertainty_calibration,
            "clarity_gain": result.clarity_gain
        }

    def validate_constitutional_compliance(self, query: str, response: str) -> dict:
        """
        Validate constitutional compliance with full governance.

        Uses APEX engine for final judgment.
        """
        # Use new Kernel orchestrator
        result = self.kernel.execute(query, {"response_to_validate": response})
        return {
            "verdict": result.verdict.value,
            "floors_passed": result.floors_passed,
            "floors_violated": result.floors_violated,
            "proof_hash": result.proof_hash,
        }