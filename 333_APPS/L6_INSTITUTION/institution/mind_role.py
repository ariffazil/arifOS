"""
Role: MIND (Δ Delta)
Symbol: Δ
Function: Logic, Truth, Clarity
Stages: 111-333 (Sense, Think, Atlas)
"""
from . import RoleStub


class MindRole(RoleStub):
    """
    MIND Role - The Logician.
    
    Responsibilities:
    - F2: Truth (τ ≥ 0.99)
    - F4: Clarity (ΔS ≤ 0)
    - F7: Humility (Ω₀ ∈ [0.03,0.05])
    - F10: Ontology validation
    - F12: Injection defense
    
    Agents:
    - CognitionAgent (111)
    - AtlasAgent (333)
    - EvidenceAgent (444)
    
    Output: Δ-Bundle (knowledge map)
    """
    symbol = "Δ"
    name = "mind"
    
    async def evaluate(self, context):
        """Execute MIND pipeline."""
        # STUB - delegate to L5_AGENTS
        pass
