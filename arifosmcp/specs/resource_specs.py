"""
arifOS MCP Resource Specifications
═══════════════════════════════════════════════════════════════════════════════

9 read-only context resources.

Resources are live context surfaces, not executable actions.
They provide:
- System status and vitals
- Governance doctrine
- Tool specifications
- Session telemetry

All resources are read-only. Mutations happen through tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ResourceSpec:
    """
    Clean resource specification following MCP protocol.
    
    Resources are read-only context accessed by URI.
    
    Fields:
        uri: Unique resource identifier (arifos://...)
        name: Human-readable name
        description: Clear purpose
        mime_type: Content type
        is_template: True if URI has {variables}
        dynamic: True if content changes (requires fetch)
        auth_required: Minimum authority level
    """
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"
    is_template: bool = False
    dynamic: bool = False
    auth_required: str = "anonymous"


# ═══════════════════════════════════════════════════════════════════════════════
# 5 CANONICAL RESOURCES (CONSOLIDATED)
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    # 1. arifos://doctrine — The Eternal Law (Ψ Sovereignty)
    ResourceSpec(
        uri="arifos://doctrine",
        name="arifOS Doctrine",
        description=(
            "The Eternal Law: Immutable constitutional substrate. "
            "Includes F1-F13 floor definitions, Verdict schemas (SEAL/VOID), "
            "Gödel Lock specification, and the Foundational 000/ROOT doctrine."
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # 2. arifos://vitals — The Living Pulse (Ω Stability)
    ResourceSpec(
        uri="arifos://vitals",
        name="arifOS Vitals",
        description=(
            "The Living Pulse: Real-time thermodynamic state (G-score, ΔS, Ψ). "
            "Includes versioning, health status, capacity metrics, and a "
            "recent vault summary of anonymized verdicts."
        ),
        mime_type="application/json",
        dynamic=True,
        auth_required="anonymous",
    ),
    
    # 3. arifos://schema — The Complete Blueprint (Δ Discernment)
    ResourceSpec(
        uri="arifos://schema",
        name="arifOS Schema Blueprint",
        description=(
            "The Complete Blueprint: All structural intelligence in one stable prefix. "
            "Includes Master schema, Tool context packets, Trinity definitions, "
            "Routing guides, and AGI Reply Protocol v3 schemas."
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # 4. arifos://session — The Ephemeral Self (Consciousness)
    ResourceSpec(
        uri="arifos://session/{session_id}",
        name="arifOS Session context",
        description=(
            "The Ephemeral Self: Session-bound runtime context. "
            "Includes authority level, available tools, active floors, "
            "and the Reply context-pack delta state."
        ),
        mime_type="application/json",
        is_template=True,
        dynamic=True,
        auth_required="anchored",
    ),
    
    # 5. arifos://forge — The Execution Bridge (Work/Energy)
    ResourceSpec(
        uri="arifos://forge",
        name="arifOS Forge Operational",
        description=(
            "The Execution Bridge: Operational bridge from governance to build. "
            "Includes AF-FORGE context, execution manifests, tool contracts, "
            "and widget definitions."
        ),
        mime_type="application/json",
        dynamic=True,
        auth_required="anonymous",
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# LOOKUP UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

RESOURCE_URIS: tuple[str, ...] = tuple(spec.uri for spec in CANONICAL_RESOURCE_SPECS)


def get_resource_spec(uri: str) -> ResourceSpec | None:
    """Get resource spec by URI."""
    for spec in CANONICAL_RESOURCE_SPECS:
        if spec.uri == uri:
            return spec
    return None


def resource_spec_to_mcp_schema(spec: ResourceSpec) -> dict[str, Any]:
    """Convert ResourceSpec to MCP resources/list schema."""
    if spec.is_template:
        return {
            "uriTemplate": spec.uri,
            "name": spec.name,
            "description": spec.description,
            "mimeType": spec.mime_type,
        }
    return {
        "uri": spec.uri,
        "name": spec.name,
        "description": spec.description,
        "mimeType": spec.mime_type,
    }


__all__ = [
    "ResourceSpec",
    "CANONICAL_RESOURCE_SPECS",
    "RESOURCE_URIS",
    "get_resource_spec",
    "resource_spec_to_mcp_schema",
]
