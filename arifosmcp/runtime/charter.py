"""
arifosmcp/runtime/charter.py — arifOS MCP Manifest

Well-known charter for discovery and SDK generation.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.prompt import V2_PROMPT_SPECS
from arifosmcp.runtime.resource import SYSTEM_CAPABILITIES
from arifosmcp.runtime.tool_specs import V2_TOOLS


def build_charter_v2(
    public_base_url: str = "https://arifosmcp.arif-fazil.com",
) -> dict[str, Any]:
    """Build the canonical MCP v2 charter."""

    # Build tool entries
    tools = []
    for spec in V2_TOOLS:
        tools.append(
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
                "visibility": spec.visibility,
                "layer": spec.layer,
                "trinity": spec.trinity,
                "floors": list(spec.floors),
            }
        )

    # Build prompt entries
    prompts = []
    for spec in V2_PROMPT_SPECS:
        prompts.append(
            {
                "name": spec["name"],
                "description": spec["description"],
                "inputSchema": spec["input_schema"],
                "defaultTools": spec.get("default_tools", []),
                "toolChoice": spec.get("tool_choice", "auto"),
            }
        )

    # Build resource entries
    resources = [
        {
            "uri": "arifos://doctrine",
            "name": "Constitutional Doctrine",
            "description": "Immutable 13-floor constitution (F1–F13). All tools and agents must operate within these floors.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://trinity",
            "name": "AAA Trinity Lanes",
            "description": "AAA Trinity lane architecture: AGI(111) proposes, ASI(444) judges, APEX(888) authorizes, FORGE(010) executes, 999 seals.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://schema",
            "name": "Canonical Schema",
            "description": "Complete canonical blueprint of the arifOS MCP surface — tools, Trinity lanes, floors, separation of powers.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://civilization",
            "name": "Civilizational Ontology",
            "description": "Seven federation organs, three intelligence strata, constitutional boundaries, entropy responsibility model.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://seal-readiness",
            "name": "Seal Readiness & Vault Integrity",
            "description": "Vault integrity report, five disambiguated seal types, seven-floor seal gate.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://jurisdiction",
            "name": "Jurisdiction & Autonomy Bands",
            "description": "Five autonomy bands (GREEN→BLACK), CapabilityGrant registry, jurisdiction rules.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://identity",
            "name": "Sovereign Identity Manifest",
            "description": "Sovereign identity bound from identity.toml. Root of accountability — all attestation chains begin here.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://memory",
            "name": "Memory Architecture (L1–L6)",
            "description": "Six-layer memory architecture: L1 ephemeral → L6 immutable (VAULT999). Memory ≠ truth without provenance.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://vitals",
            "name": "Constitutional Vitals Reference",
            "description": "Metric definitions and thresholds (green/yellow/red). For LIVE values use arif_ops_measure.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://bootstrap",
            "name": "Federation Bootstrap Context",
            "description": "Complete federation knowledge-graph bootstrap. Full world-model in one call. v2026.06.14.",
            "mimeType": "text/plain",
        },
        {
            "uri": "tree777://index",
            "name": "TREE777 Index",
            "description": "TREE777 wiki full index — all skills, concepts, and scars in the canonical knowledge graph.",
            "mimeType": "text/plain",
        },
        {
            "uri": "runner://policy/v1",
            "name": "Runner Policy",
            "description": "Pinned policy of the context_runner bridge. F2 deterministic, F11 source-of-truth.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://human/metabolized",
            "name": "Human Metabolized Context",
            "description": "Metabolized sovereign context — compact human intelligence. The nutrient, not the full testimony.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://mcp-alignment",
            "name": "MCP Spec Conformance Matrix",
            "description": "Current conformance status vs. MCP 2025-11-25 — protocol compliance, extensions, deprecations, client compatibility.",
            "mimeType": "text/plain",
        },
        {
            "uri": "arifos://resources/index",
            "name": "Resource Catalog",
            "description": "Machine-readable JSON catalog of all registered arifOS MCP resources with URIs, MIME types, descriptions, and floor linkages.",
            "mimeType": "application/json",
        },
    ]

    return {
        "schema_version": "2025-11-25",
        "name": "ARIFOS MCP",
        "version": "2.0.0",
        "description": "Constitutional AI orchestration kernel — Sovereign 9-tool core with governance layer",
        "namespace": "arifos",
        "website_url": "https://arifosmcp.arif-fazil.com",
        "repository": "https://github.com/ariffazil/arifOS",
        "license": "AGPL-3.0-only",
        "contact": {
            "security": "security@arif-fazil.com",
            "support": "https://github.com/ariffazil/arifOS/issues",
        },
        "vendor": {
            "name": "Muhammad Arif bin Fazil",
            "url": "https://arif-fazil.com",
        },
        "server": {
            "url": public_base_url,
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "tools": "/tools",
                "prompts": "/prompts",
                "resources": "/resources",
                "manifest": "/.well-known/manifest.json",
            },
        },
        "capabilities": {
            "tools": True,
            "prompts": True,
            "resources": True,
            "streaming": True,
            "authentication": False,  # Public endpoint
        },
        "constitutional": {
            "floors": 13,
            "trinity_model": True,
            "verdict_system": ["SEAL", "PARTIAL", "VOID", "HOLD"],
        },
        "stats": {
            "tools_total": len(tools),
            "tools_public": sum(1 for t in tools if t["visibility"] == "public"),
            "tools_internal": sum(1 for t in tools if t["visibility"] == "internal"),
            "prompts": len(prompts),
            "resources": len(resources),
        },
        "tools": tools,
        "prompts": prompts,
        "resources": resources,
        "system": SYSTEM_CAPABILITIES,
    }


def build_well_known_charter(
    public_base_url: str = "https://arifosmcp.arif-fazil.com",
) -> dict[str, Any]:
    """Build the .well-known/manifest.json minimal charter format."""
    return {
        "schema_version": "2025-11-25",
        "name": "ARIFOS MCP",
        "version": "2.0.0",
        "description": "Constitutional AI orchestration kernel",
        "namespace": "arifos",
        "capabilities": ["tools", "prompts", "resources"],
        "contact": {
            "security": "security@arif-fazil.com",
        },
    }


__all__ = [
    "build_charter_v2",
    "build_well_known_charter",
]
