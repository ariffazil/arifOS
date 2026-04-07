"""
arifosmcp/runtime/manifest_v2.py — arifOS MCP v2 Manifest

Well-known manifest for discovery and SDK generation.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.tool_specs_v2 import V2_TOOLS
from arifosmcp.runtime.prompts_v2 import V2_PROMPT_SPECS
from arifosmcp.runtime.resources_v2 import SYSTEM_CAPABILITIES


def build_manifest_v2(public_base_url: str = "https://arifosmcp.arif-fazil.com") -> dict[str, Any]:
    """Build the canonical MCP v2 manifest."""
    
    # Build tool entries
    tools = []
    for spec in V2_TOOLS:
        tools.append({
            "name": spec.name,
            "description": spec.description,
            "inputSchema": spec.input_schema,
            "visibility": spec.visibility,
            "layer": spec.layer,
            "trinity": spec.trinity,
            "floors": list(spec.floors),
        })
    
    # Build prompt entries
    prompts = []
    for spec in V2_PROMPT_SPECS:
        prompts.append({
            "name": spec["name"],
            "description": spec["description"],
            "inputSchema": spec["input_schema"],
            "defaultTools": spec.get("default_tools", []),
            "toolChoice": spec.get("tool_choice", "auto"),
        })
    
    # Build resource entries
    resources = [
        {
            "uri": "arifos.v2.governance.floors",
            "name": "Governance Floors",
            "description": "Constitutional F1-F13 thresholds and doctrine",
            "mimeType": "application/json",
        },
        {
            "uri": "arifos.v2.governance.verdict_spec",
            "name": "Verdict Specification",
            "description": "Verdict system and output schema",
            "mimeType": "application/json",
        },
        {
            "uri": "arifos.v2.system.capabilities",
            "name": "System Capabilities",
            "description": "Machine-readable capability map",
            "mimeType": "application/json",
        },
        {
            "uri": "arifos.v2.system.architecture",
            "name": "System Architecture",
            "description": "Architecture documentation and pipeline",
            "mimeType": "text/markdown",
        },
        {
            "uri": "arifos.v2.compliance.mapping",
            "name": "Compliance Mapping",
            "description": "Floor-to-standard compliance mapping",
            "mimeType": "application/json",
        },
    ]
    
    return {
        "schema_version": "2025-11-25",
        "name": "ARIFOS MCP",
        "version": "2.0.0",
        "description": "Constitutional AI orchestration kernel — Sovereign 9-tool core with governance layer",
        "namespace": "arifos.v2",
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


def build_well_known_manifest(public_base_url: str = "https://arifosmcp.arif-fazil.com") -> dict[str, Any]:
    """Build the .well-known/manifest.json minimal format."""
    return {
        "schema_version": "2025-11-25",
        "name": "ARIFOS MCP",
        "version": "2.0.0",
        "description": "Constitutional AI orchestration kernel",
        "namespace": "arifos.v2",
        "capabilities": ["tools", "prompts", "resources"],
        "contact": {
            "security": "security@arif-fazil.com",
        },
    }


__all__ = [
    "build_manifest_v2",
    "build_well_known_manifest",
]
