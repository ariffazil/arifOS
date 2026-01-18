"""
arifos_core/pipeline/stage_333_reason.py

Stage 333: Reason (AGI - DeltaKernel)

Evaluates F1 (Amanah) and F2 (Truth/ΔS) using DeltaKernel.
- F1: Integrity check (reversibility, mandate boundaries)
- F2: Clarity check (entropy must not increase beyond threshold)

If Delta fails → accumulate failures, continue to Omega (soft floor handling)

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from arifos.agi.delta_kernel import DeltaKernel

from .context import PipelineContext


def stage_333_reason(context: PipelineContext) -> PipelineContext:
    """
    Stage 333: Reason - AGI evaluation via DeltaKernel.

    Evaluates F1 (Amanah) and F2 (Clarity/ΔS).

    Args:
        context: Pipeline context with query + response

    Returns:
        Updated context with Delta verdict

    Raises:
        ValueError: If query or response is missing
    """
    context.stage_reached = 333
    context.metadata["stage_333"] = "Reason (DeltaKernel F1-F2)"

    if not context.query:
        raise ValueError("Stage 333: query is required")
    if not context.response:
        raise ValueError("Stage 333: response is required for Delta evaluation")

    # Initialize DeltaKernel
    kernel = DeltaKernel(
        clarity_threshold=0.0,  # Strict: no confusion increase
        require_amanah=True,
        tokenization_mode="word"
    )

    # Evaluate F1 + F2
    verdict = kernel.evaluate(
        query=context.query,
        response=context.response,
        reversible=context.reversible,
        within_mandate=context.within_mandate
    )

    # Store results
    context.delta_verdict = verdict
    context.delta_s = verdict.delta_s

    # Accumulate failures
    if not verdict.passed:
        context.failures.extend(verdict.failures)
        context.metadata["stage_333_result"] = f"FAIL ({len(verdict.failures)} failures)"
    else:
        context.metadata["stage_333_result"] = "PASS"

    return context


__all__ = ["stage_333_reason"]
