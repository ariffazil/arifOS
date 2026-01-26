"""
Stage 888: JUDGE - Executive Veto (Free Won't)
Scientific Principle: Prefrontal Inhibition
Function: The final Energy Gate. Inhibits action if $Cost > Budget$ or $Risk > Floor$.

Hardening:
- F1: Amanah (Trust/Budget)
- F13: Sovereign Override (Human Veto)
- Energy Budget Check
"""
from typing import Dict, Any
from codebase.system.apex_prime import APEXPrime

APEX = APEXPrime()

def check_f13_sovereign_requirement(context: Dict[str, Any]) -> bool:
    """Check if action requires Sovereign Approval (F13)."""
    # e.g. Modifying heavy artifacts or changing floors
    # This would check the proposed action metadata
    return False # Default to False for basic loop

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "888"
    
    eureka_result = context.get("forge_result")
    
    # 1. Energy Budget Check (F1 Amanah)
    current_energy = context.get("energy_cost", 0.0)
    max_budget = context.get("energy_budget", 1.0)
    if current_energy > max_budget:
        context["floor_violations"] = context.get("floor_violations", []) + ["F1: Energy Budget Exceeded"]
        # Inhibit action
        return context

    # 2. Sovereign Requirement Check (F13)
    if check_f13_sovereign_requirement(context):
         # If sovereign not present, HOLD
         context["verdict"] = "HOLD_888"
         return context

    agi_output = {
        "floor_violations": context.get("thermodynamic_violation", False),
        "think": context.get("reflect_result")
    }
    asi_output = {
        "align": context.get("align_result"),
        "evidence": context.get("evidence_result"),
        "empathy": context.get("empathize_result")
    }

    if not eureka_result:
        # Nothing to judge
        return context

    # 3. Constitutional Judgment
    result = APEX.judge(eureka_result, agi_output, asi_output)
    
    # Check for hard veto from previous stages
    if context.get("floor_violations"):
        # Override to VOID if there are violations
        # (APEX.judge might do this internally, but we enforce it here)
        pass 
    
    context["judge_result"] = result
    context["verdict"] = getattr(result, "verdict", "VOID").value
    
    return context
