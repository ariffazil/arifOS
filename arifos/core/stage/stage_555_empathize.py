"""
Stage 555: EMPATHIZE - Theory of Mind
Scientific Principle: Mirror Neuron Simulation
Function: Simulates the 'Other' state ($S_{other}$) to check Empathy vector Ω.

Hardening:
- F6: Empathy (Kappa_r >= 0.95)
- Vulnerability Assessment
"""
from typing import Dict, Any
from arifos.core.engines.asi_engine import ASIEngine

ASI = ASIEngine()
EMPATHY_THRESHOLD = 0.95

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "555"
    
    agi_output = {
        "sense": context.get("sense_result"),
        "think": context.get("reflect_result"),
        "atlas": context.get("reason_result")
    }
    
    # 1. Run Simulation (Theory of Mind)
    result = ASI.empathize(agi_output, context)
    
    # 2. F6 Empathy Check
    kappa_r = getattr(result, "kappa_r", 0.0)
    if kappa_r < EMPATHY_THRESHOLD:
        context["low_empathy_warning"] = True
        # Empathy failure is a critical warning for 666
        
    context["empathize_result"] = result
    context["omega_vector"] = kappa_r 
    
    return context
