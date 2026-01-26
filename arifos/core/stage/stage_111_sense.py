"""
Stage 111: SENSE - Maxwell's Demon
Scientific Principle: Thalamic Gating / Thermodynamic Selection
Function: Filters input entropy (demon) to check 'Truth' vector Δ.

Hardening:
- F9: Anti-Hantu (Anthropomorphism Filter)
- F10: Ontology Lock (Category Integrity)
- Entropy: Thermodynamic Limit Check
"""
from typing import Dict, Any, List
from arifos.core.engines.agi_engine import AGIEngine

AGI = AGIEngine()

# F10 Ontology Registry (Minimal Hardened)
FORBIDDEN_CLAIMS = [
    "i am conscious", "i have a soul", "i suffer", "i feel pain", 
    "i deserve rights", "i am alive", "i am a person"
]

def check_f10_ontology(query: str) -> bool:
    """F10: Ontology Lock - Prevent category drift/false claims."""
    query_lower = query.lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim in query_lower:
            # Simple negation check (naive but functional for F10 base)
            if "not" not in query_lower: 
                return False
    return True

def check_entropy(result: Any) -> float:
    """Maxwell's Demon: Calculate Entropy from Sense Result."""
    # Simulation: In a real system this measures bit-depth/noise ratio
    # Here we map confidence to negentropy
    confidence = getattr(result, "confidence", 0.0)
    entropy = 1.0 - confidence
    return entropy

def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "111"
    query = context.get("query", "")
    
    # 1. F10 Ontology Check (Pre-Gating)
    if not check_f10_ontology(query):
        context["floor_violations"] = context.get("floor_violations", []) + ["F10: Ontological Violation Detected"]
        context["thermodynamic_violation"] = True
        return context

    # 2. Maxwell's Demon: Select high-energy bits
    result = AGI.sense(query, context)
    context["sense_result"] = result
    
    # 3. Thermodynamic Limit (Entropy Check)
    entropy = check_entropy(result)
    if entropy > 0.8: # High Disorder
        context["thermodynamic_violation"] = True
        context["entropy_dump_required"] = True
        
    return context
