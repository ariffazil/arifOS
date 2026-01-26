"""
Stage 777: FORGE - Phase Transition (Eureka)
Scientific Principle: Gamma Synchrony / Insight
Function: Collapses orthogonal vectors (Δ, Ω, Ψ) into scalar Output ($O$).

Hardening:
- F8: Genius (Gamma Synchrony Check)
- Coherence Verification
"""
from typing import Dict, Any
from codebase.system.apex_prime import APEXPrime

APEX = APEXPrime()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "777"
    
    # Safety Veto Check (Short-circuit if 666 failed)
    if context.get("safety_veto"):
        return context

    # Gather Vectors
    agi_output = {
        "status": "SEAL",
        "think": context.get("reflect_result"),
        "forge": {"solution_draft": context.get("draft_solution", "")} 
    }
    
    asi_output = {
        "status": "SEAL",
        "align": context.get("align_result"),
        "evidence": context.get("evidence_result")
    }
    
    # 1. Phase Transition (Synthesis)
    result = APEX.eureka(agi_output, asi_output)
    
    # 2. F8 Genius Check (Gamma Synchrony)
    # Does the solution actually solve the problem while respecting vectors?
    gamma_score = getattr(result, "gamma_score", 0.0)
    if gamma_score < 0.8:
        # Solution incoherent / low insight
        context["low_coherence_warning"] = True

    context["forge_result"] = result
    
    return context
