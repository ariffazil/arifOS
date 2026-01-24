"""
Stage 888: JUDGE - Executive Veto (Free Won't)
Scientific Principle: Prefrontal Inhibition
Function: The final Energy Gate. Inhibits action if $Cost > Budget$ or $Risk > Floor$.
"""
from typing import Dict, Any
from arifos.core.engines.apex_engine import APEXEngine

APEX = APEXEngine()

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "888"
    
    eureka_result = context.get("forge_result")
    
    agi_output = {
        "floor_violations": context.get("thermodynamic_violation", False), # Adapter
        "think": context.get("reflect_result")
    }
    asi_output = {
        "align": context.get("align_result"),
        "evidence": context.get("evidence_result"),
        "empathy": context.get("empathize_result")
    }

    if not eureka_result:
        return context

    # Constitutional Judgment (Inhibition Check)
    result = APEX.judge(eureka_result, agi_output, asi_output)
    
    context["judge_result"] = result
    context["verdict"] = result.verdict.value
    
    return context
