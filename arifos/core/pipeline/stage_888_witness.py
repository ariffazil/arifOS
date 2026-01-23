"""
arifos.core/pipeline/stage_888_witness.py

Stage 888: Witness (APEX - PsiKernel)

Final judgment stage:
- Evaluates F8 (Genius)
- Integrates F10-F12 (Hypervisor results)
- Aggregates Delta + Omega failures
- Renders final verdict: SABAR > VOID > HOLD_888 > PARTIAL > SEAL

This is the judiciary - the final decision point.

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from arifos.core.apex.psi_kernel import PsiKernel

from .context import PipelineContext


def stage_888_witness(context: PipelineContext) -> PipelineContext:
    """
    Stage 888: Witness - APEX final judgment via PsiKernel.

    Evaluates F8 (Genius), integrates Hypervisor (F10-F12),
    and renders final verdict based on Trinity evaluation.

    Args:
        context: Pipeline context with Delta + Omega verdicts

    Returns:
        Updated context with Psi verdict (final judgment)

    Raises:
        ValueError: If Delta or Omega verdicts are missing
    """
    context.stage_reached = 888
    context.metadata["stage_888"] = "Witness (PsiKernel F8 + verdict)"

    if not context.delta_verdict:
        raise ValueError("Stage 888: Delta verdict is required")
    if not context.omega_verdict:
        raise ValueError("Stage 888: Omega verdict is required")

    # Initialize PsiKernel
    kernel = PsiKernel(genius_threshold=0.80)

    # Evaluate F8 + render final verdict
    verdict = kernel.evaluate(
        delta_verdict=context.delta_verdict,
        omega_verdict=context.omega_verdict,
        genius=context.genius_score,
        hypervisor_passed=context.hypervisor_passed,
        hypervisor_failures=context.hypervisor_failures
    )

    # Store results
    context.psi_verdict = verdict

    # Accumulate any additional failures
    if not verdict.passed:
        # Failures already accumulated in verdict
        context.metadata["stage_888_result"] = f"VERDICT: {verdict.verdict.value}"
    else:
        context.metadata["stage_888_result"] = f"VERDICT: SEAL"

    return context


__all__ = ["stage_888_witness"]
