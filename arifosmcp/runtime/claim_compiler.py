"""
arifosmcp/runtime/claim_compiler.py — Evidence-State Enforcement
═══════════════════════════════════════════════════════════════

Implements Gap 6: Claim-State Compiler.
Forces strict labeling of claims based on evidence level and provenance.
Prevents speculation from being treated as verification.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from enum import Enum
from typing import Any, Dict, List

class ClaimState(str, Enum):
    OBSERVED = "OBSERVED"     # Directly seen in raw data
    MEASURED = "MEASURED"     # Computed from sensor data
    INFERRED = "INFERRED"     # Reasoned from evidence
    ABDUCED = "ABDUCED"       # Best explanation, requires test
    HYPOTHESIS = "HYPOTHESIS" # Plausible but weak
    NORMATIVE = "NORMATIVE"   # Value judgment
    SPECULATIVE = "SPECULATIVE" # Possible, no evidence
    VOID = "VOID"             # Unsafe or invalid
    VERIFIED = "VERIFIED"     # Confirmed by independent witness
    SEALED = "SEALED"         # Finalized by human authority

def compile_claim_state(
    raw_claim: str,
    evidence_level: str,
    provenance: str,
    uncertainty: float
) -> ClaimState:
    """
    Law 6.3 Invariant: Claim state must match evidence state.
    """
    if evidence_level == "L0" or uncertainty > 0.8:
        return ClaimState.SPECULATIVE
    
    if "L4" in evidence_level and uncertainty < 0.1:
        return ClaimState.VERIFIED
        
    if "L1" in evidence_level:
        return ClaimState.OBSERVED
        
    if provenance == "abduction":
        return ClaimState.ABDUCED
        
    return ClaimState.HYPOTHESIS

def validate_claim_transition(current: ClaimState, proposed: ClaimState) -> bool:
    """
    Prevents illegal escalation of authority.
    Example: ABDUCED cannot become VERIFIED without a test receipt.
    """
    forbidden_escalations = [
        (ClaimState.ABDUCED, ClaimState.VERIFIED),
        (ClaimState.SPECULATIVE, ClaimState.INFERRED),
        (ClaimState.HYPOTHESIS, ClaimState.SEALED)
    ]
    
    if (current, proposed) in forbidden_escalations:
        return False
        
    return True
