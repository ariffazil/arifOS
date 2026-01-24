"""
Stage 444: EVIDENCE - Bayesian Update
Scientific Principle: Free Energy Principle / Error Minimization
Function: Grounds internal predictions against external evidence ($P(H|E)$).
"""
from typing import Dict, Any
from arifos.core.engines.asi_engine import ASIEngine

ASI = ASIEngine()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "444"
    
    # Construct AGI Prior
    agi_output = {
        "sense": context.get("sense_result"),
        "think": context.get("reflect_result"),
        "atlas": context.get("reason_result")
    }
    
    # Seek Evidence (Posterior verification)
    result = ASI.evidence(agi_output, context)
    
    context["evidence_result"] = result
    
    return context
