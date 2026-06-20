"""
Substrate Index — Inventory of all substrate capabilities in the federation.

The Eureka Agent reads the substrate index to know:
- What tools are available (per organ, per lane)
- What policies are loaded
- What receipts are sealed
- What memory is available
- What enforcement is active

This is the "substrate intelligence" layer — knowing what substrate exists
without claiming any substrate is conscious or sovereign.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass


@dataclass
class SubstrateCapability:
    """A single substrate capability (tool, library, service)."""

    name: str
    kind: str  # tool | library | service | policy | memory
    organ: str | None = None
    lane: str | None = None
    version: str | None = None
    available: bool = True
    notes: str = ""


class SubstrateIndex:
    """
    Index of substrate capabilities.

    Built lazily on first call to `build()`; cached for the agent's lifetime.
    """

    def __init__(self):
        self._capabilities: list[SubstrateCapability] = []
        self._built = False

    def build(self) -> SubstrateIndex:
        """Build the substrate index by probing the live environment."""
        if self._built:
            return self

        # arifOS substrate libraries
        self._probe("pydantic", kind="library")
        self._probe("pydantic_ai", kind="library")
        self._probe("fastmcp", kind="library")
        self._probe("opentelemetry", kind="library")
        self._probe("blake3", kind="library")
        self._probe("networkx", kind="library")
        self._probe("opa", kind="library")
        self._probe("opa_python_client", kind="library")
        self._probe("sigstore", kind="library")
        self._probe("openlineage", kind="library")
        self._probe("duckdb", kind="library")
        self._probe("polars", kind="library")
        self._probe("pandera", kind="library")
        self._probe("pyportfolioopt", kind="library")
        self._probe("langgraph", kind="library")

        # arifOS organ substrate
        self._probe_module("arifOS.arifosmcp.arifos_policy", "OPA bridge")
        self._probe_module("arifOS.arifosmcp.arifos_attestation", "Sigstore/SLSA/SBOM")
        self._probe_module("arifOS.arifosmcp.arifos_observability", "OTel tracer")
        self._probe_module("arifOS.arifosmcp.arifos_registry", "Tool registry")
        self._probe_module("arifOS.arifosmcp.arifos_vault", "Receipts")

        # WEALTH substrate
        self._probe_module("WEALTH.internal.wealth_contracts", "WEALTH envelopes")
        self._probe_module("WEALTH.internal.wealth_adapters", "WEALTH adapters")
        self._probe_module("WEALTH.internal.wealth_security", "WEALTH security")
        self._probe_module("WEALTH.internal.wealth_observability", "WEALTH OTel")

        self._built = True
        return self

    def _probe(self, module_name: str, kind: str = "library", organ: str | None = None) -> None:
        try:
            mod = importlib.import_module(module_name)
            version = getattr(mod, "__version__", None)
            self._capabilities.append(
                SubstrateCapability(name=module_name, kind=kind, version=version, organ=organ, available=True)
            )
        except ImportError:
            self._capabilities.append(
                SubstrateCapability(name=module_name, kind=kind, organ=organ, available=False)
            )

    def _probe_module(self, dotted: str, display_name: str) -> None:
        try:
            importlib.import_module(dotted)
            self._capabilities.append(
                SubstrateCapability(name=display_name, kind="module", available=True)
            )
        except ImportError:
            self._capabilities.append(
                SubstrateCapability(name=display_name, kind="module", available=False)
            )

    def capabilities(self) -> list[SubstrateCapability]:
        return list(self._capabilities)

    def available(self) -> list[SubstrateCapability]:
        return [c for c in self._capabilities if c.available]

    def missing(self) -> list[SubstrateCapability]:
        return [c for c in self._capabilities if not c.available]

    def summary(self) -> dict:
        caps = self.capabilities()
        return {
            "total": len(caps),
            "available": len(self.available()),
            "missing": len(self.missing()),
            "missing_names": [c.name for c in self.missing()],
        }
