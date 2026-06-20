"""
Namespace Guard — Linter that fails any tool name without organ prefix.

Per F13 directive: "name is the first act of creation"
Per SUBSTRATE_NAMESPACES.md: every MCP tool name must begin with `<organ>_`.

F2 TRUTH: a tool that fails this check is rejected at registration time.
F8 LAW: namespace discipline is enforced uniformly across organs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .substrate_namespace_registry import (
    CANONICAL_ORGAN_PREFIXES,
    SubstrateNamespaceRegistry,
    get_substrate_namespace_registry,
)


@dataclass
class NamespaceGuardResult:
    """Result of namespace validation."""

    tool_name: str
    valid: bool
    reason: str
    namespace: str | None = None
    canonical_name: str | None = None
    is_legacy: bool = False

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "valid": self.valid,
            "reason": self.reason,
            "namespace": self.namespace,
            "canonical_name": self.canonical_name,
            "is_legacy": self.is_legacy,
        }


class NamespaceGuard:
    """Linter that validates MCP tool names against the namespace discipline."""

    # Snake case pattern (lowercase letters, digits, underscores)
    VALID_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")

    def __init__(self, registry: SubstrateNamespaceRegistry | None = None):
        self.registry = registry or get_substrate_namespace_registry()

    def validate(self, tool_name: str) -> NamespaceGuardResult:
        """
        Validate a tool name against the namespace discipline.

        Returns NamespaceGuardResult with valid=True if the name:
        - Matches the snake_case pattern
        - Has a valid namespace prefix (or accepted sub-prefix)
        - Either is canonical or has a legacy alias
        """
        # Empty or non-string
        if not tool_name or not isinstance(tool_name, str):
            return NamespaceGuardResult(
                tool_name=tool_name or "",
                valid=False,
                reason="empty or non-string name",
            )

        # Snake case check
        if not self.VALID_NAME_PATTERN.match(tool_name):
            return NamespaceGuardResult(
                tool_name=tool_name,
                valid=False,
                reason="does not match snake_case pattern (lowercase letters, digits, underscores)",
            )

        # Must contain at least one underscore
        if "_" not in tool_name:
            return NamespaceGuardResult(
                tool_name=tool_name,
                valid=False,
                reason="missing namespace prefix (no underscore)",
            )

        # Namespace check (accept both canonical and arifos_ sub-namespace)
        namespace = tool_name.split("_")[0]
        valid_prefixes = set(CANONICAL_ORGAN_PREFIXES)
        if namespace not in valid_prefixes:
            return NamespaceGuardResult(
                tool_name=tool_name,
                valid=False,
                reason=f"unknown namespace '{namespace}' (must be one of {sorted(valid_prefixes)})",
            )

        # mcp_ namespace is legacy diagnostic exception (per WELL AGENTS.md "DEPRECATED")
        is_mcp_legacy = namespace == "mcp"

        # Map arifos_ → arif_ for organ resolution
        resolved_ns = "arif" if namespace == "arifos" else namespace

        # Legacy alias check
        canonical_name = self.registry.canonical_name(tool_name)
        is_legacy = canonical_name != tool_name

        # Organ resolution
        organ = self.registry.resolve_organ_for_tool(tool_name)

        if organ is None:
            return NamespaceGuardResult(
                tool_name=tool_name,
                valid=False,
                reason=f"namespace '{namespace}' declared but no organ registered for it",
                namespace=namespace,
            )

        # Double-prefix check (e.g. wealth_wealth_*)
        if tool_name.startswith(f"{resolved_ns}_{resolved_ns}_"):
            return NamespaceGuardResult(
                tool_name=tool_name,
                valid=False,
                reason=f"double namespace prefix detected ({resolved_ns}_{resolved_ns}_)",
                namespace=namespace,
            )

        return NamespaceGuardResult(
            tool_name=tool_name,
            valid=True,
            reason="valid" + (" (legacy alias resolved to canonical)" if is_legacy else "") + (" (mcp_ legacy diagnostic)" if is_mcp_legacy else ""),
            namespace=resolved_ns,
            canonical_name=canonical_name,
            is_legacy=is_legacy or is_mcp_legacy,
        )

    def validate_batch(self, tool_names: list[str]) -> list[NamespaceGuardResult]:
        """Validate a list of tool names."""
        return [self.validate(name) for name in tool_names]

    def filter_invalid(self, tool_names: list[str]) -> list[NamespaceGuardResult]:
        """Return only the invalid tool names."""
        return [r for r in self.validate_batch(tool_names) if not r.valid]
