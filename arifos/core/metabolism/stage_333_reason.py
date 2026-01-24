"""
Stage 333: REASON - Vector Analysis (ATLAS)
Scientific Principle: Orthogonal Decomposition
Function: Maps the logic landscape into independent vectors (Truth/Fact/Constraint).
"""
from typing import Dict, Any
from arifos.core.engines.agi_engine import AGIEngine

AGI = AGIEngine()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "333"
    sense_result = context.get("sense_result")
    think_result = context.get("reflect_result") # Used to be think_result
    
    if not (sense_result and think_result):
        return context
        
    # ATLAS: Map the vectors
    result = AGI.atlas(sense_result, think_result)
    
    context["reason_result"] = result
    
    return context
