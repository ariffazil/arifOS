# arifosmcp/mcp/tools/_111_sense.py
from typing import Any, Dict, Optional


async def execute(query: str, intent_type: Optional[str] = None) -> Dict[str, Any]:
    """
    arifos.111_sense: Intent classification and perception grounding.
    Consolidates fetch logic and perception grounding floors.
    """
    # Intent classification logic
    classification = intent_type or (
        "COMMAND"
        if any(v in query.lower() for v in ["run", "execute", "start"])
        else "INQUIRY"
    )

    # Grounding check (entropy reduction simulation)
    grounding_score = 1.0 - (len(query.split()) / 1000.0)

    report = {
        "ok": True,
        "classification": classification,
        "grounding_score": max(0.0, grounding_score),
        "metabolic_stage": "111_SENSE",
        "sensing_report": {
            "raw_query": query,
            "pre_check_floors": ["F1", "F2", "F4"],
            "intent_detected": classification,
        },
    }

    return report
