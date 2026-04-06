"""
AgentZero Security Module

Constitutional defense mechanisms:
- PromptArmor: LLM-based injection detection (F12)
- Sandboxing: Code execution isolation
- Audit: VAULT999 logging
"""

from .prompt_armor import InjectionReport, PromptArmor

__all__ = ["PromptArmor", "InjectionReport"]
