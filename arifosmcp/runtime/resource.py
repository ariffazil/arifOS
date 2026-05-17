"""Canonical resource authority for arifOS MCP."""

from __future__ import annotations

import json

from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EMBODIED_RESOURCES,
    EVIDENCE_RESOURCES,
    TREE777_RESOURCES,
    register_resources,
)

__all__ = [
    "CANONICAL_RESOURCES",
    "EVIDENCE_RESOURCES",
    "TREE777_RESOURCES",
    "EMBODIED_RESOURCES",
    "register_resources",
    "manifest_resources",
    "read_resource_content",
    "apex_tools_markdown_table",
]


def manifest_resources() -> list[str]:
    """
    Return the canonical and evidence resource URI manifests.

    Includes all 5 URI families:
      - CANONICAL (arifos://doctrine, vitals, schema, forge, civilization)
      - TREE777 (tree777://index, search, skills/{cat}/{name}, concepts/{name}, scars/{name})
      - EMBODIED (arifos://tools/self-model/{view}, witness/{filter}, boundaries/{domain})
      - EVIDENCE (source://{hash}, receipt://..., contrast://..., void://...)
    """
    return (
        list(CANONICAL_RESOURCES)
        + list(TREE777_RESOURCES)
        + list(EMBODIED_RESOURCES)
        + list(EVIDENCE_RESOURCES)
    )


async def read_resource_content(uri: str) -> str:
    """
    Resolve a resource URI and return its content.

    Handles:
      - tree777:// URIs         → TREE777 wiki pages
      - arifos:// URIs          → arifOS canonical resources
      - source://, receipt://,
        contrast://, void://    → F-WEB evidence resources

    Returns the resource content as a string, or an error message
    if the URI cannot be resolved.
    """
    from arifosmcp.resources.tree777 import handle_resource

    result = handle_resource(uri)
    body = result.get("body", "")

    # Distinguish between a resolved resource and an error
    if isinstance(body, str) and ("ERROR" in body or "error" in result.get("error", "").lower()):
        return f"ERROR: {result.get('error', result.get('body', 'Unknown error'))}"

    # For JSON bodies (index, search results), return the JSON string
    if isinstance(body, dict):
        return json.dumps(body, indent=2)

    return str(body)


def apex_tools_markdown_table() -> str:
    """Stub for the apex tools markdown table (was in deleted resources.py)."""
    return ""
