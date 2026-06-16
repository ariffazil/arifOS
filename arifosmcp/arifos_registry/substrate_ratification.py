"""
Substrate Namespace Ratification — Run NamespaceGuard against every live MCP tool.

Probes each organ's MCP endpoint, lists its tools, validates against the
namespace discipline, and produces a ratification report.

F2 TRUTH: The report is OBS (observed from live probes) + DER (derived from
guard logic). Anchored to live state at ratification time.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from .namespace_guard import NamespaceGuard
from .substrate_namespace_registry import (
    SubstrateNamespaceRegistry,
    get_substrate_namespace_registry,
)


@dataclass
class OrganToolSurface:
    """Tool surface for one organ."""

    organ: str
    namespace: str
    endpoint: str
    tools: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)
    legacy_redirects: list[str] = field(default_factory=list)
    probe_latency_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "organ": self.organ,
            "namespace": self.namespace,
            "endpoint": self.endpoint,
            "tool_count": len(self.tools),
            "tools": self.tools,
            "invalid_count": len(self.invalid),
            "invalid": self.invalid,
            "legacy_redirects": self.legacy_redirects,
            "probe_latency_ms": self.probe_latency_ms,
            "error": self.error,
        }


class SubstrateNamespaceRatification:
    """Probe all organ MCP endpoints and ratify the namespace discipline."""

    def __init__(
        self,
        registry: Optional[SubstrateNamespaceRegistry] = None,
        guard: Optional[NamespaceGuard] = None,
        timeout: float = 5.0,
    ):
        self.registry = registry or get_substrate_namespace_registry()
        self.guard = guard or NamespaceGuard(registry=self.registry)
        self.timeout = timeout

    def probe_organ(self, namespace: str) -> OrganToolSurface:
        """Probe a single organ's MCP endpoint and return its tool surface."""
        ns = self.registry.get(namespace)
        if not ns:
            return OrganToolSurface(
                organ=namespace,
                namespace=namespace,
                endpoint="unknown",
                error=f"namespace '{namespace}' not in registry",
            )

        surface = OrganToolSurface(
            organ=ns.organ,
            namespace=namespace,
            endpoint=ns.endpoint,
        )

        t0 = time.time()
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                # MCP streamable-http transport requires specific Accept header
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                }
                resp = client.post(
                    ns.endpoint,
                    json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                tools = [t.get("name", "") for t in data.get("result", {}).get("tools", [])]
                surface.tools = sorted(tools)
        except Exception as e:
            surface.error = str(e)
        surface.probe_latency_ms = (time.time() - t0) * 1000

        # Validate namespace discipline
        results = self.guard.validate_batch(surface.tools)
        surface.invalid = sorted([r.tool_name for r in results if not r.valid])
        surface.legacy_redirects = sorted([r.tool_name for r in results if r.is_legacy])

        return surface

    def ratify_all(self) -> dict:
        """Probe all organs and produce a ratification report."""
        surfaces = []
        for namespace in self.registry.list_namespaces():
            surfaces.append(self.probe_organ(namespace.name))

        total_tools = sum(len(s.tools) for s in surfaces)
        total_invalid = sum(len(s.invalid) for s in surfaces)
        total_legacy = sum(len(s.legacy_redirects) for s in surfaces)

        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "registry_hash": self.registry.registry_hash(),
            "organs_probed": len(surfaces),
            "total_tools": total_tools,
            "total_invalid": total_invalid,
            "total_legacy_redirects": total_legacy,
            "namespace_discipline": "VALID" if total_invalid == 0 else "VIOLATIONS_FOUND",
            "surfaces": [s.to_dict() for s in surfaces],
        }
