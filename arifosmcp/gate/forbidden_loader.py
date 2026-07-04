"""
forbidden_loader.py — Load sealed forbidden patterns into MCP Gate
==================================================================
Reads forge_work/offsec_governance/ToolHazardV1/forbidden_patterns.yaml
and returns structured data for mcp_gate_v0.py consumption.

Forged: 2026-06-29 — EHT Repo Audit
Sealed: 2026-06-29 — F13 SOVEREIGN (888)
"""
from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field

FORBIDDEN_PATTERNS_PATH = Path(
    "/root/arifOS/forge_work/offsec_governance/ToolHazardV1/forbidden_patterns.yaml"
)


@dataclass
class ForbiddenPattern:
    name: str
    kind: str
    eht_category: str
    upstream: str = ""
    note: str = ""
    block_level: str = "HARD"


@dataclass
class ForbiddenRegistry:
    tool_names: set[str] = field(default_factory=set)
    patterns: list[ForbiddenPattern] = field(default_factory=list)
    loaded: bool = False

    def is_forbidden(self, tool_name: str) -> bool:
        """Check if a tool name matches any forbidden pattern."""
        if not self.loaded:
            return False
        return tool_name.lower() in self.tool_names

    def get_block_reason(self, tool_name: str) -> str:
        """Return the constitutional reason for blocking a tool."""
        for p in self.patterns:
            if p.name.lower() == tool_name.lower():
                return (
                    f"HARD BLOCK: {p.name} — {p.kind}. "
                    f"Category: {p.eht_category}. "
                    f"Constitutional basis: F1 AMANAH + F5 PEACE + F10 ONTOLOGY."
                )
        return f"HARD BLOCK: '{tool_name}' matched forbidden patterns registry."


def load_forbidden_registry(path: Path | None = None) -> ForbiddenRegistry:
    """Load the sealed forbidden patterns YAML.

    Returns ForbiddenRegistry with tool_names populated for fast lookup.
    Returns empty registry (loaded=False) if file is missing or unreadable.
    """
    path = path or FORBIDDEN_PATTERNS_PATH
    registry = ForbiddenRegistry()

    if not path.exists():
        return registry

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, OSError):
        return registry

    if not data or "_meta" not in data:
        return registry

    meta = data["_meta"]
    if meta.get("status") != "SEALED":
        return registry

    # Collect all pattern names across all categories
    for section_key in data:
        if section_key.startswith("_"):
            continue
        section = data[section_key]
        if not isinstance(section, dict):
            continue
        block_level = section.get("block_level", "HARD")
        for pattern in section.get("patterns", []):
            p = ForbiddenPattern(
                name=pattern["name"],
                kind=pattern.get("kind", "unknown"),
                eht_category=pattern.get("eht_category", "unknown"),
                upstream=pattern.get("upstream", ""),
                note=pattern.get("note", ""),
                block_level=block_level,
            )
            registry.patterns.append(p)
            registry.tool_names.add(pattern["name"].lower())

    registry.loaded = True
    return registry


# Module-level singleton — loaded once at import time
_forbidden_registry: ForbiddenRegistry | None = None


def get_forbidden_registry() -> ForbiddenRegistry:
    """Return the module-level forbidden registry singleton."""
    global _forbidden_registry
    if _forbidden_registry is None:
        _forbidden_registry = load_forbidden_registry()
    return _forbidden_registry
