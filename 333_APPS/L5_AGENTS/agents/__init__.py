"""
L5_AGENTS - The 4 Constitutional Agents

Architecture:
├── ARCHITECT (AGI/Mind) → Design & Planning
├── ENGINEER (ASI/Heart) → Implementation & Safety  
├── AUDITOR (EYE/Witness) → Verification & Facts
└── VALIDATOR (APEX/Soul) → Judgment & Sealing

Reference: 000-999 Metabolic Loop
"""

__version__ = "v55.0-stub"
__all__ = ["ARCHITECT", "ENGINEER", "AUDITOR", "VALIDATOR"]


class Agent:
    """Base agent stub."""
    name = "base"
    symbol = "?"
    
    async def execute(self, context):
        raise NotImplementedError(f"{self.name} not implemented")
