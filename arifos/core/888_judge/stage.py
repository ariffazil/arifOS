"""
arifos_core/888_judge/stage.py

Stage 888: JUDGE (Verdict Rendering)
Function: Final Judgment via APEX Prime (System 2 Orchestrator).
Kernel: APEX Prime
"""

from typing import Any, Dict

from arifos.core.system.apex_prime import APEXPrime, Verdict

# Initialize Single Execution Spine
ORCHESTRATOR = APEXPrime()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Stage 888 (Judge).
    Delegates final verdict to APEX Prime.
    """
    context["stage"] = "888"

    # Extract Inputs from Context
    query = context.get("query", "")
    response = context.get("response", "") # The draft to judge
    user_id = context.get("user_id")

    # Extract upstream kernel traces if available in metabolic state
    # Assuming context['trace'] or similar holds results
    trace = context.get("trace", {})
    agi_results = trace.get("agi_results", [])
    asi_results = trace.get("asi_results", [])

    # Execute APEX Prime
    verdict_obj = ORCHESTRATOR.judge_output(
        query=query,
        response=response,
        agi_results=agi_results,
        asi_results=asi_results,
        user_id=user_id
    )

    # Update Context with Verdict
    context["apex_verdict"] = {
        "verdict": verdict_obj.verdict.value,
        "reason": verdict_obj.reason,
        "violated_floors": verdict_obj.violated_floors,
        "metrics": verdict_obj.genius_stats,
        "compass_alignment": verdict_obj.compass_alignment,
        "proof_hash": verdict_obj.proof_hash
    }

    # If VOID, we might want to flag the context to stop pipeline
    if verdict_obj.verdict == Verdict.VOID:
        context["stop_pipeline"] = True
        context["error"] = verdict_obj.reason

    return context
