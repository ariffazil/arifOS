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

        # Probing arifOS tools from constitutional map
        try:
            from arifosmcp.constitutional_map import list_canonical_tools
            for tool_name in list_canonical_tools():
                self._capabilities.append(
                    SubstrateCapability(
                        name=tool_name,
                        kind="tool",
                        organ="arifOS",
                        available=True,
                        notes="arifOS cognitive tool"
                    )
                )
        except Exception as e:
            self._capabilities.append(
                SubstrateCapability(name="arifOS_tools", kind="tool", available=False, notes=str(e))
            )

        self._built = True
        return self

    def validate_tool_naming_invariants(self) -> dict[str, list[str]]:
        """
        Validate naming invariants for tools:
        - arifOS tools must have exactly 2 terms: arif_<cognitive_verb> (e.g., arif_init, arif_judge).
        - A-FORGE tools must have exactly 3 terms: forge_<component>_<verb> (e.g., forge_filesystem_read, forge_git_commit).
        """
        from arifosmcp.constitutional_map import list_canonical_tools

        violations = {
            "arifOS": [],
            "A-FORGE": []
        }

        # SDK long-name aliases are first-class aliases, not canonical tools,
        # so they are exempt from the strict 2-term invariant.
        SDK_LONG_NAME_ALIASES = {
            "arif_session_init",
            "arif_sense_observe",
            "arif_evidence_fetch",
            "arif_mind_reason",
            "arif_heart_critique",
            "arif_reply_compose",
            "arif_memory_recall",
            "arif_gateway_connect",
            "arif_ops_measure",
            "arif_judge_deliberate",
            "arif_vault_seal",
            "arif_forge_execute",
        }

        # Validate arifOS tools (Starts with 'arif_' and exactly 2 terms)
        for tool_name in list_canonical_tools():
            if not tool_name.startswith("arif_"):
                violations["arifOS"].append(f"Tool '{tool_name}' does not start with 'arif_' prefix")
                continue
            terms = tool_name.split("_")
            if len(terms) != 2:
                # Core primitives and SDK long-name aliases are grandfathered.
                if tool_name not in {
                    "arif_kernel_intercept",
                    "arif_bridge_connect",
                    "arif_conformance_report",
                    *SDK_LONG_NAME_ALIASES,
                }:
                    violations["arifOS"].append(
                        f"Tool '{tool_name}' violates the 2-term invariant (arif_<cognitive_verb>): has {len(terms)} terms"
                    )

        # Validate A-FORGE tools from A-FORGE source directory if available
        import os
        import re

        a_forge_mcp_dir = "/root/A-FORGE/src/interfaces/mcp"
        if os.path.exists(a_forge_mcp_dir):
            for filename in ("forgeTools.ts", "gatewayTools.ts", "proxyTools.ts"):
                filepath = os.path.join(a_forge_mcp_dir, filename)
                if os.path.exists(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Extract tools registered via server.tool("..." or server.registerTool("..."
                        tool_names = re.findall(r'server\.(?:tool|registerTool)\(\s*["\']([^"\']+)["\']', content)
                        for tool_name in tool_names:
                            if not tool_name.startswith("forge_"):
                                violations["A-FORGE"].append(f"A-FORGE tool '{tool_name}' does not start with 'forge_' prefix")
                                continue
                            terms = tool_name.split("_")
                            if len(terms) != 3:
                                # We allow direct command tools like forge_research or forge_search as exceptions, or flag them.
                                if tool_name not in ("forge_research", "forge_search"):
                                    violations["A-FORGE"].append(
                                        f"A-FORGE tool '{tool_name}' violates the 3-term invariant (forge_<component>_<verb>): has {len(terms)} terms"
                                    )
                    except Exception as e:
                        violations["A-FORGE"].append(f"Failed to read A-FORGE file '{filename}': {e}")
        else:
            violations["A-FORGE"].append("A-FORGE mcp source directory not found for validation")

        return violations

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

