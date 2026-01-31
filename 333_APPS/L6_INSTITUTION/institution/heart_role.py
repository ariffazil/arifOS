"""
Role: HEART (Ω Omega)
Symbol: Ω
Function: Safety, Care, Empathy
Stages: 444-666 (Evidence, Empathy, Align)
"""
from . import RoleStub


class HeartRole(RoleStub):
    """
    HEART Role - The Guardian.
    
    Responsibilities:
    - F1: Amanah (reversibility)
    - F5: Peace² (≥ 1.0)
    - F6: Empathy (κᵣ ≥ 0.70)
    - F9: Anti-Hantu (< 0.30)
    
    Agents:
    - EvidenceAgent (444)
    - DefendAgent (555)
    
    Output: Ω-Bundle (safety report)
    """
    symbol = "Ω"
    name = "heart"
    
    async def evaluate(self, context):
        """Execute HEART pipeline."""
        # STUB - delegate to L5_AGENTS
        pass
