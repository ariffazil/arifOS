"""
Stage 333: REASON - Vector Analysis (ATLAS)
Scientific Principle: Orthogonal Decomposition
Function: Maps the logic landscape into independent vectors (Truth/Fact/Constraint).

Hardening:
- F4: Clarity (Vector Separation)
- Orthogonality Check: Ensure Fact != Value
"""
from typing import Dict, Any
from arifos.core.engines.agi_engine import AGIEngine

AGI = AGIEngine()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "333"
    sense_result = context.get("sense_result")
    think_result = context.get("reflect_result")
    
    if not (sense_result and think_result): return context
        
    # 1. F4 Clarity Check (Pre-processing)
    # Ensure inputs are distinct enough to solve partial differential equations of state
    if sense_result == think_result:
        # Tautology detected!
         context["floor_violations"] = context.get("floor_violations", []) + ["F4: Tautological Loop Detected"]
         return context

    # 2. ATLAS: Map the vectors
    result = AGI.atlas(sense_result, think_result)
    
    # 3. Orthogonality Verification
    # Do we have distinct vectors?
    if len(result.vectors) < 2:
         # Not enough dimensionality to reason safely
         result.is_orthogonal = False
    
    context["reason_result"] = result
    
    return context
