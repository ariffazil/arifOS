"""
L6_INSTITUTION - Trinity Multi-Agent System
Stub package for future implementation.

Canonical implementation will use codebase/ + L5_AGENTS
"""

__version__ = "v56.0-stub"
__all__ = [
    "ConstitutionalOrchestrator",
    "MindRole",
    "HeartRole",
    "SoulRole",
    "TriWitnessGate",
    "Phoenix72",
]


class RoleStub:
    """Base stub for Trinity roles."""
    symbol = "?"
    name = "stub"
    
    async def evaluate(self, bundle):
        """To be implemented."""
        raise NotImplementedError(f"{self.name} role not yet implemented")
