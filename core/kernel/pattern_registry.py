"""
core/kernel/pattern_registry.py — Registry for agentic execution patterns.

This module catalogs and manages reusable agentic patterns (e.g., ReAct, Reflection, Planning)
for selection and execution within the arifOS governed substrate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgenticPattern:
    """Definition of an agentic execution pattern."""
    name: str
    description: str
    schema: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

class PatternRegistry:
    """
    Catalog for reusable agentic patterns.
    Enables explicit, auditable selection of execution patterns.
    """

    def __init__(self):
        self._patterns: dict[str, AgenticPattern] = {}
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Register canonical arifOS patterns."""
        self.register_pattern(
            name="ReAct",
            description="Reasoning and Acting loop.",
            schema={
                "steps": ["Reason", "Act", "Observe"],
                "termination": "Final Answer or Max Steps",
            }
        )
        self.register_pattern(
            name="Reflection",
            description="Iterative self-correction and refinement.",
            schema={
                "steps": ["Generate", "Reflect", "Refine"],
                "termination": "Quality Threshold or Max Iterations",
            }
        )
        self.register_pattern(
            name="Chain-of-Thought",
            description="Step-by-step linear reasoning.",
            schema={
                "steps": ["Think", "Respond"],
                "termination": "End of Sequence",
            }
        )

    def register_pattern(self, name: str, description: str, schema: dict[str, Any], metadata: dict[str, Any] | None = None):
        """Register a new agentic pattern."""
        self._patterns[name] = AgenticPattern(
            name=name,
            description=description,
            schema=schema,
            metadata=metadata or {}
        )

    def get_pattern(self, name: str) -> AgenticPattern | None:
        """Retrieve a pattern by name."""
        return self._patterns.get(name)

    def list_patterns(self) -> list[str]:
        """List all registered pattern names."""
        return list(self._patterns.keys())

    def get_all_patterns(self) -> list[AgenticPattern]:
        """Retrieve all registered pattern objects."""
        return list(self._patterns.values())
