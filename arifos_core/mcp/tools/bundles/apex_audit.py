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

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from arifos_core.mcp.models import ApexAuditRequest, VerdictResponse

# =============================================================================
# CONSTANTS
# =============================================================================

CONVERGENCE_SEAL = 0.95
CONVERGENCE_PARTIAL = 0.90
CONVERGENCE_VOID = 0.80

# =============================================================================
# LOGIC: EVIDENCE (444)
# =============================================================================

def check_tri_witness(evidence: Dict[str, Any]) -> Tuple[float, str]:
    """Check Tri-Witness convergence (Simplified from 444)."""
    if not evidence:
        return 0.70, "No evidence provided." # Baseline for single source

    sources = evidence.get("sources", [])
    if not sources:
        return 0.70, "No sources found."

    # Mock convergence logic based on source count/score
    # In full implementation, this uses Source Ranker logic
    score = 0.92 # Default high for now
    if len(sources) >= 3:
        score = 0.98
    elif len(sources) == 2:
        score = 0.90

    return score, f"Convergence: {score:.2f} (Sources: {len(sources)})"

# =============================================================================
# LOGIC: PROOF (889)
# =============================================================================

def generate_merkle_proof(items: List[str]) -> str:
    """Generate simple hash proof for the chain."""
    if not items:
        return hashlib.sha256(b"").hexdigest()

    # Combined hash of all inputs (Simplified Merkle Root)
    # Full Merkle tree logic in state.merkle if needed, here we just need a deterministic hash
    combined = "".join(sorted(items))
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

# =============================================================================
# BUNDLE ENTRY POINT
# =============================================================================

async def apex_audit(request: ApexAuditRequest) -> VerdictResponse:
    """
    APEX Bundle: AUDIT
    Executes Intersection (AGI ∩ ASI) -> Evidence Audit -> Proof Seal.
    """
    agi = request.agi_thought
    asi = request.asi_veto
    evidence = request.evidence_pack or {}

    # 1. INTERSECTION CHECK (AGI ∩ ASI)
    # Both must be valid (PASS or compatible state)
    # Assuming AGI returns dict with "lane", "thought_process" etc.
    # Assuming ASI returns dict with "verdict", "peace_score" etc.

    # Note: request fields are Dicts as per model, but likely were converted from VerdictResponse.dict()
    # AGI usually returns PASS. ASI returns PASS or VOID.

    # Check if AGI failed (unlikely for think, but possible)
    agi_verdict = agi.get("verdict", "PASS")
    # Check if ASI vetoed
    asi_verdict = asi.get("verdict", "PASS")

    if agi_verdict == "VOID":
        return VerdictResponse(
            verdict="VOID",
            reason=f"AGI Login Failure: {agi.get('reason')}",
            side_data={"bundle": "APEX_AUDIT", "stage": "AGI_FAIL"}
        )

    if asi_verdict == "VOID":
        return VerdictResponse(
            verdict="VOID",
            reason=f"ASI Safety Veto: {asi.get('reason')}",
            side_data={"bundle": "APEX_AUDIT", "stage": "ASI_FAIL"}
        )

    # 2. EVIDENCE AUDIT (F8)
    convergence, evidence_reason = check_tri_witness(evidence)
    if convergence < CONVERGENCE_VOID:
        return VerdictResponse(
            verdict="VOID",
            reason=f"Tri-Witness Failure: {evidence_reason}",
            side_data={"bundle": "APEX_AUDIT", "stage": "EVIDENCE_FAIL"}
        )

    # 3. SEAL GENERATION (F1 Proof)
    # Proof Chain: [QueryHash, ResponseHash, PeaceScore, Convergence]
    # We construct a verifiable chain string
    chain_elements = [
        str(agi.get("side_data", {}).get("thought_process", "")),
        str(asi.get("side_data", {}).get("peace_score", 0.0)),
        str(convergence),
        datetime.now(timezone.utc).isoformat()
    ]
    proof_hash = generate_merkle_proof(chain_elements)

    # Final Verdict Determination
    # If convergence is Partial but not Void -> PARTIAL or SEAL?
    # F8 requires >= 0.95 for SEAL.
    final_verdict = "SEAL" if convergence >= CONVERGENCE_SEAL else "PARTIAL"

    return VerdictResponse(
        verdict=final_verdict,
        reason=f"APEX Audit Complete. AGI+ASI Agreed. {evidence_reason}",
        side_data={
            "proof_hash": proof_hash,
            "convergence": convergence,
            "bundle": "APEX_AUDIT",
            "nodes_verified": 3 # AGI, ASI, EVIDENCE
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )

def apex_audit_sync(request: ApexAuditRequest) -> VerdictResponse:
    """Synchronous wrapper for apex_audit."""
    return asyncio.run(apex_audit(request))
