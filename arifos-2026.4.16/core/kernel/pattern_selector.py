"""
core/kernel/pattern_selector.py — Pattern Selection Engine.

Dynamically select and apply agentic execution patterns from the PatternRegistry
based on context, role, and task requirements.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from core.kernel.pattern_registry import PatternRegistry, AgenticPattern

class PatternSelector:
    """
    Engine to select the most appropriate agentic pattern for a task.
    Ensures safe and optimal execution by matching pattern to task complexity.
    """

    def __init__(self, registry: PatternRegistry):
        self.registry = registry

    def select(self, context: Dict[str, Any]) -> str:
        """
        Dynamically select the optimal pattern name based on context.
        Default: Chain-of-Thought (simplest)
        Complex tasks: ReAct (for tools)
        Verification/Refinement: Reflection
        """
        query = context.get("query", "").lower()
        has_tools = bool(context.get("available_tools"))
        requires_verification = context.get("requires_verification", False)

        if has_tools:
            # Tool usage typically requires reasoning and action
            return "ReAct"

        if requires_verification or "verify" in query or "check" in query:
            # Tasks requiring self-correction
            return "Reflection"

        # Default reasoning pattern
        return "Chain-of-Thought"

    def apply(self, pattern_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Instantiate a pattern's parameters with the given state.
        Ensures the right agentic pattern is applied per task.
        """
        pattern = self.registry.get_pattern(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_name}' not found in registry.")

        # Implementation logic for pattern application would go here.
        # For now, return pattern metadata and enriched state.
        applied_state = state.copy()
        applied_state["applied_pattern"] = {
            "name": pattern.name,
            "description": pattern.description,
            "schema": pattern.schema
        }
        return applied_state
