"""
arifos_core/stages/stage_333_reason.py

Stage 333: REASON (Logic Generation)
Function: Reasoning, Exploration, Structured Logic.
Kernel: AGI (Δ) - Axis 1

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from typing import Any, Dict

from arifos_core.agi.kernel import AGIKernel, AGIVerdict

# Initialize Kernel (Singleton pattern or per-request?)
# For Phase 2, simple instantiation.
KERNEL = AGIKernel()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute State 333.
    Uses AGI Kernel to structure reasoning.
    """
    context["stage"] = "333"

    query = context.get("parsed_query", "")

    # Placeholder for reasoning generation (e.g., calling an LLM)
    # In a real impl, we'd generate a 'draft_response' here.
    draft_reasoning = f"Reasoning about: {query}"
    context["draft_reasoning"] = draft_reasoning

    # Evaluate with AGI Kernel (Initial Check)
    # We verify if the generated reasoning is Clear (F4) and Truthful (F2).
    verdict: AGIVerdict = KERNEL.evaluate(
        query=query,
        response=draft_reasoning
    )

    context["agi_verdict"] = {
        "passed": verdict.passed,
        "reason": verdict.reason,
        "failures": verdict.failures,
        "delta_s": verdict.f4_delta_s
    }

    if not verdict.passed:
        context["warnings"] = context.get("warnings", []) + verdict.failures
        # In a non-linear pipeline, we might loop back here.

    return context
