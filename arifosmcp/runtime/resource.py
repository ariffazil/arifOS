"""Canonical resource authority for arifOS MCP."""

from __future__ import annotations

from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EVIDENCE_RESOURCES,
    register_resources,
)

__all__ = [
    "CANONICAL_RESOURCES",
    "EVIDENCE_RESOURCES",
    "register_resources",
    "manifest_resources",
]


def manifest_resources() -> list[str]:
    """Return the canonical and evidence resource URI manifests."""
    return list(CANONICAL_RESOURCES) + list(EVIDENCE_RESOURCES)
