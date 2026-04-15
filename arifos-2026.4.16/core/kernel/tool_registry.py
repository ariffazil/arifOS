"""
core/kernel/tool_registry.py — Tool Contract Registry.

Central registry for tool schemas, contracts, and validation logic.
Ensures tools are discoverable, schema-validated, and safely callable.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class ToolContract:
    """Definition of a tool contract."""
    name: str
    description: str
    schema: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

class ToolContractRegistry:
    """
    Registry for managing tool contracts and schemas.
    Enables discoverability and safe execution of tool calls.
    """

    def __init__(self):
        self._tools: Dict[str, ToolContract] = {}

    def register_tool(self, name: str, description: str, schema: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """Register a new tool contract."""
        self._tools[name] = ToolContract(
            name=name,
            description=description,
            schema=schema,
            metadata=metadata or {}
        )

    def get_tool_contract(self, name: str) -> Optional[ToolContract]:
        """Retrieve a tool's contract by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())

    def validate_call(self, name: str, params: Dict[str, Any]) -> bool:
        """Validate a tool call against its registered schema."""
        contract = self.get_tool_contract(name)
        if not contract:
            raise ValueError(f"Tool '{name}' not found in registry.")

        # Simple schema validation logic for parameters
        expected_params = contract.schema.get("parameters", {}).get("properties", {})
        for param, schema_info in expected_params.items():
            if param not in params and param in contract.schema.get("parameters", {}).get("required", []):
                return False
            # Further type-checking could be added here
        
        return True

    def get_all_contracts(self) -> List[ToolContract]:
        """Retrieve all registered tool contract objects."""
        return list(self._tools.values())
