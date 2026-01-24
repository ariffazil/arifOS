"""
Stage 444: EVIDENCE - Bayesian Update
Scientific Principle: Free Energy Principle / Error Minimization
Function: Grounds internal predictions against external evidence ($P(H|E)$).

Hardening:
- F2: Truth (P >= 0.99)
- Bayesian Confidence Floor
"""
from typing import Dict, Any
from arifos.core.engines.asi_engine import ASIEngine

ASI = ASIEngine()
TRUTH_THRESHOLD = 0.99

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "444"
    
    # Construct AGI Prior
    agi_output = {
        "sense": context.get("sense_result"),
        "think": context.get("reflect_result"),
        "atlas": context.get("reason_result")
    }
    
    # 1. Seek Evidence (Posterior verification)
    result = ASI.evidence(agi_output, context)
    
    # 2. F2 Truth Check
    truth_score = getattr(result, "truth_score", 0.0)
    if truth_score < TRUTH_THRESHOLD:
        # Downgrade certainty, maybe trigger SABAR
        context["low_truth_warning"] = True
        context["truth_vector"] = truth_score
    
    context["evidence_result"] = result
    
    return context
