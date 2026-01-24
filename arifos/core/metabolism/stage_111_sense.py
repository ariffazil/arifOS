"""
Stage 111: SENSE - Maxwell's Demon
Scientific Principle: Thalamic Gating / Thermodynamic Selection
Function: Filters input entropy (demon) to check 'Truth' vector Δ.
"""
from typing import Dict, Any
from arifos.core.engines.agi_engine import AGIEngine

AGI = AGIEngine()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "111"
    query = context.get("query", "")
    
    # Maxwell's Demon: Select high-energy bits (relevant), block noise
    result = AGI.sense(query, context)
    
    context["sense_result"] = result
    
    # Check for "Injection" (High Entropy Spike)
    if result.floor_F12_risk > 0.8:
        context["thermodynamic_violation"] = True
        
    return context
