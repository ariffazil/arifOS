"""
HardenedGeoxAgent — Constitutionally Hardened Agent
DITEMPA BUKAN DIBERI

An agent implementation with hardened constitutional enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .base_tool import GeoToolResult
from .geox_validator import GeoXValidator


@dataclass
class HardenedConfig:
    """Configuration for hardened agent."""

    strict_mode: bool = True
    max_uncertainty: float = 0.15
    require_provenance: bool = True


class HardenedGeoxAgent:
    """
    Constitutionally hardened GEOX agent.

    Enforces strict compliance with constitutional floors.
    """

    def __init__(self, config: HardenedConfig | None = None, session_id: str | None = None):
        from .geox_tools import ToolRegistry

        self.config = config or HardenedConfig()
        self.session_id = session_id or "default_session"
        self.validator = GeoXValidator(strict_mode=self.config.strict_mode)
        self.registry = ToolRegistry.default_registry()
        self._history: list[dict[str, Any]] = []

    async def process(self, input_data: Any) -> dict[str, Any]:
        """Process input with full constitutional enforcement."""
        validation = self.validator.validate(input_data)
        if validation.verdict == "contradicted" and self.config.strict_mode:
            return {
                "verdict": "VOID",
                "error": "Input validation failed",
                "issues": validation.floor_violations,
            }

        result = {
            "verdict": "SEAL",
            "data": input_data,
            "validation": validation.to_dict(),
        }
        self._history.append({"input": input_data, "result": result})
        return result

    def get_history(self) -> list[dict[str, Any]]:
        """Get processing history."""
        return self._history.copy()

    async def execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool by name."""
        tool = self.registry.get(tool_name)
        if tool is None:
            return {"error": f"Tool {tool_name} not found"}

        if hasattr(tool, "run"):
            result = await tool.run(params)
            if isinstance(result, GeoToolResult):
                return {
                    "success": result.success,
                    "tool_name": result.tool_name or tool_name,
                    "quantities": [q.model_dump(mode="json") for q in result.quantities],
                    "raw_output": result.raw_output,
                    "metadata": result.metadata,
                    "latency_ms": result.latency_ms,
                    "error": result.error,
                }
            return result
        return {"error": f"Tool {tool_name} has no run method"}


__all__ = ["HardenedGeoxAgent", "HardenedConfig"]
