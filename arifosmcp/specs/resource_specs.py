"""
arifOS MCP Resource Specifications
═══════════════════════════════════════════════════════════════════════════════

7 canonical + supplemental read-only context resources.

Resources are live context surfaces, not executable actions.
They provide:
- System status and vitals
- Governance doctrine
- Tool specifications
- Session telemetry
- MCP conformance alignment
- Machine-readable catalog

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
# 7 CANONICAL + SUPPLEMENTAL RESOURCE SPECS
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    ResourceSpec(
        uri="arifos://doctrine",
        name="arifOS Doctrine",
        description=(
            "Immutable constitutional substrate. F1-L13 floors, verdict schema, Gödel Lock, agent skills manifest. "
            "Sub-resources: arifos://doctrine/floor/{law_id}, arifos://doctrine/skill/{skill_name}"
        ),
        mime_type="text/plain",
        dynamic=False,
        auth_required="anonymous",
    ),
    ResourceSpec(
        uri="arifos://vitals",
        name="arifOS Vitals",
        description=(
            "Real-time constitutional health and thermodynamics. "
            "Query: ?format=json|markdown|widget&window=live|1h|24h"
        ),
        mime_type="application/json",
        dynamic=True,
        auth_required="anonymous",
    ),
    ResourceSpec(
        uri="arifos://schema",
        name="arifOS Schema",
        description=(
            "Complete structural blueprint. "
            "Query: ?section=all|master|tools|trinity|stages|reply|index&tool_id={id}. "
            "Includes the governed domain evidence contract used by GEOX-aware tool envelopes."
        ),
        mime_type="text/plain",
        dynamic=False,
        auth_required="anonymous",
    ),
    ResourceSpec(
        uri="arifos://session/{session_id}",
        name="arifOS Session",
        description=(
            "Ephemeral per-session state and task dashboard. "
            "Query: ?depth=surface|engineer|architect&compress=true|false. "
            "Surfaces active domain evidence contract guidance for GEOX-aware sessions."
        ),
        mime_type="application/json",
        is_template=True,
        dynamic=True,
        auth_required="anchored",
    ),
    ResourceSpec(
        uri="arifos://forge",
        name="arifOS Forge",
        description=(
            "Execution bridge and deployment topology. "
            "Query: ?context=all|engine|deployment|widgets&platform=claude|cursor|opencode|chatgpt"
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    ResourceSpec(
        uri="arifos://mcp-alignment",
        name="MCP Spec Conformance Matrix",
        description=(
            "Current conformance status of arifOS vs. MCP 2025-11-25 specification. "
            "Covers core spec conformance, extensions support (JSON Schema 2020-12, Pagination, "
            "Tasks, MCP Apps, OAuth), transport, auth/security posture, deprecations, "
            "live resource inventory, and client compatibility matrix."
        ),
        mime_type="text/plain",
        dynamic=False,
        auth_required="anonymous",
    ),
    ResourceSpec(
        uri="arifos://resources/index",
        name="Resource Catalog",
        description=(
            "Machine-readable JSON catalog of all registered arifOS MCP resources. "
            "Auto-generated from live resource registry. Includes URIs, MIME types, "
            "descriptions, floor linkages, and summary counts grouped by family "
            "(canonical, tree777, embodied, evidence, runner, supplemental)."
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
