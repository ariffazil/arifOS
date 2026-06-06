"""
core/kernel/tool_registry.py — Tool Contract Registry.

Central registry for tool schemas, contracts, and validation logic.
Ensures tools are discoverable, schema-validated, and safely callable.

Phase 2 addition: callability audit — distinguishes callable tools from
phantom tools (advertised but not actually invokable at runtime).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from typing import Any


@dataclass
class ToolContract:
    """Definition of a tool contract."""

    name: str
    description: str
    schema: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    # callability_status: callable | phantom | deprecated
    # phantom = advertised but not actually callable at runtime (surface/registry mismatch)
    callability_status: str = "callable"


class ToolContractRegistry:
    """
    Registry for managing tool contracts and schemas.
    Enables discoverability and safe execution of tool calls.
    """

    def __init__(self):
        self._tools: dict[str, ToolContract] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        schema: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ):
        """Register a new tool contract."""
        self._tools[name] = ToolContract(
            name=name, description=description, schema=schema, metadata=metadata or {}
        )

    def get_tool_contract(self, name: str) -> ToolContract | None:
        """Retrieve a tool's contract by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())

    def validate_call(self, name: str, params: dict[str, Any]) -> bool:
        """Validate a tool call against its registered schema."""
        contract = self.get_tool_contract(name)
        if not contract:
            raise ValueError(f"Tool '{name}' not found in registry.")

        # Simple schema validation logic for parameters
        expected_params = contract.schema.get("parameters", {}).get("properties", {})
        for param, _schema_info in expected_params.items():
            if param not in params and param in contract.schema.get("parameters", {}).get(
                "required", []
            ):
                return False
            # Further type-checking could be added here

        return True

    def get_all_contracts(self) -> list[ToolContract]:
        """Retrieve all registered tool contract objects."""
        return list(self._tools.values())

    # ── Phase 2: Callability audit ─────────────────────────────────────────────

    def mark_phantom(self, name: str) -> None:
        """Mark a tool as phantom — advertised in registry but not callable at runtime."""
        contract = self._tools.get(name)
        if contract:
            contract.callability_status = "phantom"

    def mark_callable(self, name: str) -> None:
        """Mark a tool as callable — verified to work at runtime."""
        contract = self._tools.get(name)
        if contract:
            contract.callability_status = "callable"

    def mark_deprecated(self, name: str) -> None:
        """Mark a tool as deprecated — exists but should not be called by new agents."""
        contract = self._tools.get(name)
        if contract:
            contract.callability_status = "deprecated"

    def audit_callability(self) -> dict[str, str]:
        """
        Return a callability map for all registered tools.

        Returns dict of tool_name → status (callable | phantom | deprecated).
        Phantom tools must be treated as a red build — surface mismatch is a
        governance failure because agents may plan around tools that don't exist.
        """
        return {name: contract.callability_status for name, contract in self._tools.items()}

    def list_phantom_tools(self) -> list[str]:
        """Return names of all tools marked as phantom."""
        return [
            name
            for name, contract in self._tools.items()
            if contract.callability_status == "phantom"
        ]

    def audit_surface_truth(
        self,
        probe_results: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Registry truth audit — Phase 2 callability verification.

        Compares the advertised tool surface against actual callability.
        If probe_results is provided (from a live dry-run probe), updates
        callability_status for each tool before computing the receipt.

        Args:
            probe_results: optional dict of {tool_name: status_str}
                           where status_str is "callable" | "phantom" | "broken" | "requires_args"
                           from an async probe that called each tool. If None, uses current status.

        Returns:
            Receipt with registry_truth, phantom_tools, callable_tools, broken_tools,
            deprecated_tools, and safe_surface_hash.

        Design note (L08): This auditor is a read-only mirror — it does not block calls.
        Each tool should independently validate session/receipt. The audit flags phantom
        tools so agents don't build workflows around tools that don't exist (F2 violation).
        """
        import hashlib
        import json
        from datetime import datetime

        # Apply probe results if provided
        if probe_results:
            for name, status in probe_results.items():
                if name in self._tools:
                    self._tools[name].callability_status = status

        callable_tools: list[str] = []
        phantom_tools: list[str] = []
        broken_tools: list[str] = []
        deprecated_tools: list[str] = []
        requires_args_tools: list[str] = []

        for name, contract in self._tools.items():
            s = contract.callability_status
            if s == "callable":
                callable_tools.append(name)
            elif s == "phantom":
                phantom_tools.append(name)
            elif s == "broken":
                broken_tools.append(name)
            elif s == "deprecated":
                deprecated_tools.append(name)
            elif s == "requires_args":
                requires_args_tools.append(name)
            else:
                callable_tools.append(name)  # unknown status treated as callable

        # Determine overall registry_truth
        if phantom_tools or broken_tools:
            registry_truth = "FAIL"
        elif deprecated_tools:
            registry_truth = "WARN"
        else:
            registry_truth = "PASS"

        # safe_surface_hash: SHA-256 of sorted callable tool names
        # Any change in the callable surface changes this hash — detectable drift
        safe_surface_data = json.dumps(sorted(callable_tools), sort_keys=True)
        safe_surface_hash = hashlib.sha256(safe_surface_data.encode()).hexdigest()[:32]

        return {
            "registry_truth": registry_truth,
            "total_advertised": len(self._tools),
            "callable_count": len(callable_tools),
            "callable_tools": sorted(callable_tools),
            "phantom_tools": sorted(phantom_tools),
            "broken_tools": sorted(broken_tools),
            "deprecated_tools": sorted(deprecated_tools),
            "requires_args_tools": sorted(requires_args_tools),
            "safe_surface_hash": safe_surface_hash,
            "timestamp": datetime.now(UTC).isoformat(),
            "f2_violation": bool(phantom_tools),  # phantom tools = agents plan around ghosts
            "f08_note": (
                "This audit is a read-only mirror. Each tool validates independently. "
                "No single chokepoint — distributed receipt chain architecture (L08)."
            ),
        }
