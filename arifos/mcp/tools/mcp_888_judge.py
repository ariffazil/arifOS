"""
MCP Tool 888: JUDGE

Final verdict aggregation via System 2 Orchestrator (APEX Prime).

Constitutional role:
- Aggregates verdicts from all active kernels (AGI, ASI).
- Applies APEX Kernel constraints (F1, F8-F12).
- Emits final verdict: SEAL, PARTIAL, VOID, SABAR, HOLD.

Layer: APEX (Judge) - F1, F8, F9, F11, F12
Authority: arifos_core/system/apex_prime.py
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from arifos.mcp.models import FloorCheckResult, VerdictResponse
from arifos.core.system.apex_prime import APEXPrime, Verdict


def _synthesize_floor_results_from_verdicts(verdicts_dict: Dict[str, str]) -> tuple:
    """
    Synthesize FloorCheckResult objects from verdicts dict (test compatibility).

    Args:
        verdicts_dict: Dict mapping stage names to verdict strings (e.g., {"222": "PASS"})

    Returns:
        Tuple of (agi_results, asi_results) as Lists of FloorCheckResult
    """
    # Map stage numbers to floor IDs and engines
    stage_to_floor = {
        "222": ("F6", "AGI", "Clarity"),      # Reflect → F6 ΔS
        "333": ("F2", "AGI", "Truth"),        # Reason → F2 Truth
        "444": ("F2", "AGI", "Truth"),        # Evidence → F2 Truth
        "555": ("F4", "ASI", "Empathy"),      # Empathize → F4 κᵣ
        "666": ("F1", "ASI", "Amanah"),       # Align → F1 Amanah
        "777": ("F6", "AGI", "Clarity"),      # Forge → F6 ΔS
    }

    agi_results = []
    asi_results = []

    for stage_id, verdict_str in verdicts_dict.items():
        if stage_id not in stage_to_floor:
            continue

        floor_id, engine, name = stage_to_floor[stage_id]

        # Convert verdict string to passed boolean and value
        passed = verdict_str in ["PASS", "SEAL"]
        value = 1.0 if passed else 0.5 if verdict_str == "PARTIAL" else 0.0

        floor_result = FloorCheckResult(
            floor_id=floor_id,
            name=name,
            threshold=0.99 if floor_id == "F2" else 0.95,
            value=value,
            passed=passed,
            reason=f"Stage {stage_id} returned {verdict_str}",
            is_hard=(floor_id in ["F1", "F2", "F6"])  # Hard floors
        )

        if engine == "AGI":
            agi_results.append(floor_result)
        else:
            asi_results.append(floor_result)

    return agi_results, asi_results


async def mcp_888_judge(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 888: JUDGE - Final Verdict via APEX Prime.

    Delegates to System 2 Orchestrator.
    """
    # 1. Initialize System 2 Orchestrator
    judge = APEXPrime()

    # 2. Extract inputs
    # The request is expected to contain the accumulated state or explicit verdicts
    # Trace of previous tool outputs usually passed in metabolic loop
    query = request.get("query", "")
    response = request.get("response", "") # The draft being judged

    # Extract upstream kernel results if available
    # (In a real metabolic loop, these trace objects would be passed)
    agi_results = request.get("agi_results", [])
    asi_results = request.get("asi_results", [])

    # If using simplified "verdicts" dict (legacy/simple mode), we synthesize floor results
    verdicts_dict = request.get("verdicts", {})
    if verdicts_dict and not (agi_results or asi_results):
        # Fallback mapping for simple integration (test compatibility)
        # Convert verdicts dict to FloorCheckResult objects with synthetic metrics
        agi_results, asi_results = _synthesize_floor_results_from_verdicts(verdicts_dict)

    # 3. Execute System 2 Judgment
    # judge_output runs the full Trinity check (G, C_dark, Psi) + Hypervisor
    verdict_obj = judge.judge_output(
        query=query,
        response=response,
        agi_results=agi_results, # Type: List[FloorCheckResult]
        asi_results=asi_results, # Type: List[FloorCheckResult]
        user_id=request.get("user_id")
    )

    # 4. Map ApexVerdict -> VerdictResponse
    side_data = verdict_obj.to_dict()
    # Flatten genius_stats into side_data
    side_data.update(verdict_obj.genius_stats)

    return VerdictResponse(
        verdict=verdict_obj.verdict.value,
        reason=verdict_obj.reason,
        side_data=side_data,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def mcp_888_judge_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_888_judge."""
    return asyncio.run(mcp_888_judge(request))
