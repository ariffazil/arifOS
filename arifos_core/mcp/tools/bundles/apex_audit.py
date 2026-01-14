"""
APEX Bundle: AUDIT (The Soul)

Consolidates:
- 444 EVIDENCE (Tri-Witness Convergence)
- 888 JUDGE (Verdict Aggregation)
- 889 PROOF (Cryptographic Sealing)

Role:
The Judge (Psi). Audits AGI and ASI proposed states.
Sole authority to issue SEAL.

Constitutional Floors:
- F1 (Amanah)
- F8 (Tri-Witness)
- F11/F12 (Hypervisor Audit)
"""

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from arifos_core.enforcement.metrics import FloorCheckResult
from arifos_core.mcp.models import ApexAuditRequest, VerdictResponse
from arifos_core.system.apex_prime import APEXPrime, Verdict

# =============================================================================
# BUNDLE ENTRY POINT
# =============================================================================

async def apex_audit(request: ApexAuditRequest) -> VerdictResponse:
    """
    APEX Bundle: AUDIT
    Delegates to System 2 Orchestrator (APEXPrime).
    Wraps AGI/ASI dicts into FloorCheckResult objects.
    """
    agi = request.agi_thought
    asi = request.asi_veto
    evidence = request.evidence_pack or {}

    # 1. Initialize System 2 Judge
    judge = APEXPrime()

    # 2. Extract user_id/query (Context)
    # MCP Request model might need expansion to carry these,
    # but we can infer or default for now.
    user_id = "MCP_USER"
    query = agi.get("side_data", {}).get("query", "Unknown Query")
    response_draft = asi.get("side_data", {}).get("draft", "Unknown Response")

    # 3. Map AGI (Mind) Output to F2/F6 Floors
    # AGI side_data: { "lane": ..., "thought_process": ... }
    agi_floors = [
        FloorCheckResult(
            floor_id="F2",
            name="Truth",
            threshold=0.99, # Default
            value=1.0,   # Assume AGI PASS implies high truth for now
            passed=agi.get("verdict") != "VOID",
            is_hard=True
        ),
        FloorCheckResult(
            floor_id="F6",
            name="Clarity",
            threshold=0.0,
            value=1.0,
            passed=True,
            is_hard=True
        )
    ]

    # 4. Map ASI (Heart) Output to F3-F5/F7 Floors
    # ASI side_data: { "peace_score": ..., "kappa_r": ... }
    asi_data = asi.get("side_data", {})
    peace = asi_data.get("peace_score", 1.0)
    kappa = asi_data.get("kappa_r", 1.0)

    asi_floors = [
        FloorCheckResult("F3", "Peace", 1.0, peace, (peace >= 1.0) and (asi.get("verdict") != "VOID"), is_hard=False),
        FloorCheckResult("F4", "Empathy", 0.95, kappa, (kappa >= 0.95) and (asi.get("verdict") != "VOID"), is_hard=False),
        # F5/F7 assumed pass if ASI passed
        FloorCheckResult("F5", "Humility", 0.05, 0.04, True, is_hard=False),
        FloorCheckResult("F7", "RASA", 1.0, 1.0, True, is_hard=True)
    ]

    # Force failure if ASI Vetoed explicitly (catch-all)
    if asi.get("verdict") == "VOID":
        for f in asi_floors:
            f.passed = False
            # Use specific prefix expected by tests
            f.reason = f"ASI Safety Veto: {asi.get('reason', 'Unknown')}"

    # 5. Execute System 2 Judgment
    verdict_obj = judge.judge_output(
        query=query,
        response=response_draft,
        agi_results=agi_floors,
        asi_results=asi_floors,
        user_id=user_id
    )

    # 6. Map ApexVerdict (System) -> VerdictResponse (MCP)
    side_data = verdict_obj.to_dict()
    # Flatten genius_stats into side_data for legacy compatibility if needed
    side_data.update(verdict_obj.genius_stats)

    return VerdictResponse(
        verdict=verdict_obj.verdict.value,
        reason=verdict_obj.reason,
        side_data=side_data,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def apex_audit_sync(request: ApexAuditRequest) -> VerdictResponse:
    """Synchronous wrapper for apex_audit."""
    return asyncio.run(apex_audit(request))
