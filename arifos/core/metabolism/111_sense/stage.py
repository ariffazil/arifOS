"""
arifos.core/stages/stage_111_sense.py

Stage 111: SENSE (Context Gathering)
Function: Input sensing, intent parsing, raw data collection.

DITEMPA BUKAN DIBERI - Forged v46.2
"""

from typing import Any, Dict


def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute State 111.
    Senses raw input and gathers context.
    """
    context["stage"] = "111"

    raw_input = context.get("user_input", "")
    if not raw_input:
        context["status"] = "EMPTY_INPUT"
        return context

    # Basic sensing (in production this would call parsers)
    context["parsed_query"] = raw_input.strip()
    context["input_length"] = len(raw_input)

    return context
