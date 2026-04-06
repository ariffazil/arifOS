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
# 9 CANONICAL RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

CANONICAL_RESOURCE_SPECS: tuple[ResourceSpec, ...] = (
    # ═══ SYSTEM ENTRY ═══
    
    ResourceSpec(
        uri="arifos://bootstrap",
        name="arifOS Bootstrap",
        description=(
            "Getting started guide for arifOS. "
            "Startup path, canonical sequence, first session walkthrough. "
            "Read this first if you're new to the system."
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # ═══ GOVERNANCE ═══
    
    ResourceSpec(
        uri="arifos://governance/floors",
        name="arifOS Floors",
        description=(
            "Constitutional F1-F13 thresholds and doctrine. "
            "Immutable legal and physical criteria for all evaluations. "
            "Includes floor descriptions, thresholds, and enforcement rules."
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    
    ResourceSpec(
        uri="arifos://floors/{floor_id}/doctrine",
        name="arifOS Floor Doctrine",
        description=(
            "Detailed doctrine for a specific constitutional floor. "
            "Replace {floor_id} with F1, F2, ..., F13."
        ),
        mime_type="application/json",
        is_template=True,
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # ═══ SYSTEM STATUS ═══
    
    ResourceSpec(
        uri="arifos://status/vitals",
        name="arifOS Vitals",
        description=(
            "Current system health and deployment info. "
            "Real-time thermodynamic metrics: G-score, entropy, capacity. "
            "Versions, git SHA, uptime. Changes frequently."
        ),
        mime_type="application/json",
        dynamic=True,
        auth_required="anonymous",
    ),
    
    # ═══ SESSION-SPECIFIC ═══
    
    ResourceSpec(
        uri="arifos://sessions/{session_id}/vitals",
        name="arifOS Session Vitals",
        description=(
            "Real-time telemetry for a specific governed session. "
            "Replace {session_id} with your session ID. "
            "Includes authority level, available tools, constitutional metrics."
        ),
        mime_type="application/json",
        is_template=True,
        dynamic=True,
        auth_required="anchored",  # Must have a session
    ),
    
    # ═══ CAPABILITIES ═══
    
    ResourceSpec(
        uri="arifos://agents/skills",
        name="arifOS Skills",
        description=(
            "Consolidated guide for AI agents. "
            "Skills, behaviors, best practices, constitutional alignment. "
            "How agents should use arifOS tools and resources."
        ),
        mime_type="application/json",
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # ═══ TOOL SPECIFICATIONS ═══
    
    ResourceSpec(
        uri="arifos://tools/{tool_name}",
        name="arifOS Tool Spec",
        description=(
            "Detailed contract for a specific tool. "
            "Replace {tool_name} with: init_session_anchor, judge_verdict, etc. "
            "Includes inputs, outputs, auth requirements, examples."
        ),
        mime_type="application/json",
        is_template=True,
        dynamic=False,
        auth_required="anonymous",
    ),
    
    # ═══ VAULT (READ-ONLY) ═══
    
    ResourceSpec(
        uri="arifos://vault/recent",
        name="arifOS Vault Recent",
        description=(
            "Read-only summary of recent vault verdicts. "
            "Last 100 entries with verdicts, timestamps, anonymized metrics. "
            "For audit and transparency. No sensitive data."
        ),
        mime_type="application/json",
        dynamic=True,
        auth_required="anonymous",
    ),
    
    # ═══ CHATGPT WIDGET ═══
    
    ResourceSpec(
        uri="ui://arifos/vault-seal-widget.html",
        name="Vault Seal Widget",
        description=(
            "ChatGPT Apps SDK widget for displaying constitutional health. "
            "HTML resource served in iframe. "
            "Shows telemetry, verdict, and attestation status."
        ),
        mime_type="text/html",
        dynamic=False,
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
