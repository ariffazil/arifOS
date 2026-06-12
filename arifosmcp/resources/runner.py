"""
runner.py — Context Engine Runner Resources (F13-safe burn-in surface)
════════════════════════════════════════════════════════════════════════

Two read-only resources for the context_runner bridge:

  runner://receipt/{run_id}  — return a cached ContextRunReceipt
  runner://policy/v1         — the pinned policy of the bridge

F-binding:
  F2: deterministic; no LLM, no I/O, no canonical mutation.
  F11: read-only; receipts are the bridge's in-process LRU cache.
  F13: no canonical mutation, no policy change, no auto-compact enable.

These resources are separate from the canonical 13-tool surface.
Resources are a separate MCP concept; they do not count toward
the 13-tool assertion in arifosmcp.runtime.tools._CANONICAL_HANDLERS.

DITEMPA BUKAN DIBERI — the receipt is the trace, not the wall.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from arifosmcp.runtime.context_runner_bridge import (
    BRIDGE_POLICY_VERSION,
    BRIDGE_SOURCE_OF_TRUTH,
    cache_size,
    resource_policy,
    resource_receipt,
)

# Canonical URIs (F11 manifest)
RUNNER_RESOURCES = (
    "runner://receipt/{run_id}",
    "runner://policy/v1",
)


def register_runner_resources(mcp: FastMCP) -> list[str]:
    """Register 2 context-runner resources on the given FastMCP server.

    Returns the list of registered URIs (without path-param expansion).
    """
    registered: list[str] = []

    @mcp.resource("runner://receipt/{run_id}")
    def runner_receipt_resource(run_id: str) -> dict[str, Any]:
        """Return a cached ContextRunReceipt by run_id.

        F2: pure read. F11: returns the cached receipt or a not-found
        envelope. The cache is in-process; dies on restart (F13: no
        canonical write).
        """
        return resource_receipt(run_id)

    registered.append("runner://receipt/{run_id}")

    @mcp.resource("runner://policy/v1")
    def runner_policy_resource() -> dict[str, Any]:
        """The pinned policy of the context_runner bridge.

        F2: deterministic. F11: this is the SOT for what the bridge
        claims to honor; the resource is the auditable copy.
        """
        # Stamp in the cache size live so the policy always reflects
        # current burn-in state.
        pol = resource_policy()
        pol["cache"]["current_size"] = cache_size()
        return pol

    registered.append("runner://policy/v1")

    return registered


__all__ = [
    "RUNNER_RESOURCES",
    "register_runner_resources",
    "BRIDGE_POLICY_VERSION",
    "BRIDGE_SOURCE_OF_TRUTH",
]
