"""
arifos_core/stages/stage_777_forge.py

Stage 777: FORGE (Output Forging)
Function: Final response construction.

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from typing import Any, Dict


def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute State 777.
    Forges the final response.
    """
    context["stage"] = "777"

    # Final polish of the content
    final_response = context.get("aligned_content", "")
    context["final_response"] = final_response

    return context
