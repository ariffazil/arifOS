"""
Stage 222: REFLECT - Recursive Self-Reference
Scientific Principle: System 2 Cognitive Control / Gödelian Loop
Function: Serial reasoning cost (Thinking) to verify coherence.

Hardening:
- F7: Humility (Uncertainty Injection)
- Recursion Check: Depth Limit
"""
from typing import Dict, Any
from arifos.core.engines.agi_engine import AGIEngine

AGI = AGIEngine()
MAX_RECURSION_DEPTH = 3

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "222"
    sense_result = context.get("sense_result")
    depth = context.get("recursion_depth", 0)
    
    if not sense_result: return context
    
    # 1. Recursion Depth Check
    if depth > MAX_RECURSION_DEPTH:
        context["floor_violations"] = context.get("floor_violations", []) + ["222: Max Recursion Depth Exceeded"]
        return context

    # 2. F7 Humility Injection (Epistemic Doubt)
    # Ensure allow_uncertainty is propagated
    sense_result.allow_uncertainty = True 

    # 3. System 2 Thinking
    result = AGI.think(sense_result)
    
    # 4. Update Context
    context["reflect_result"] = result
    context["recursion_depth"] = depth + 1
    
    return context
