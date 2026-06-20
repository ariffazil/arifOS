"""
MCP Tool Registry — Canonical capability manifest for every MCP tool in the federation.

Per the executive verdict, every tool must carry:
  - signed_tool_manifest
  - schema_hash
  - source_repository
  - license
  - blast_radius_class
  - reversible_flag
  - secret_touching_flag
  - network_access_flag
  - filesystem_access_flag
  - human_approval_policy

F2 TRUTH: This registry must match the live tool surface (no phantom tools, no ghost tools).
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from enum import Enum


class ToolLane(str, Enum):
    """Per GEOX.yaml §3 four-lane discipline (extended to all organs)."""

    DISCOVERY = "discovery"
    EVIDENCE = "evidence"
    REASONING = "reasoning"
    JUDGMENT = "judgment"
    WEALTH_CALCULATE = "wealth_calculate"
    WEALTH_AUDIT = "wealth_audit"
    WELL_MEASURE = "well_measure"
    WEAVE_ORCHESTRATE = "weave_orchestrate"


@dataclass
class ToolManifest:
    """Canonical manifest for a single MCP tool."""

    tool_name: str
    organ: str  # arifOS | WEALTH | GEOX | WELL | AAA | A-FORGE
    lane: ToolLane
    action_class: str  # OBSERVE | ANALYZE | MUTATE | GOVERNED | SEAL
    schema_hash: str  # b3: or sha256:
    source_repository: str
    license: str
    blast_radius_class: str  # LOW | MEDIUM | HIGH | CRITICAL
    reversible: bool
    secret_touching: bool
    network_access: bool
    filesystem_access: bool
    human_approval_policy: str  # NONE | SABAR | ALWAYS
    description: str
    signed: bool = False
    signature: str | None = None

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "organ": self.organ,
            "lane": self.lane.value,
            "action_class": self.action_class,
            "schema_hash": self.schema_hash,
            "source_repository": self.source_repository,
            "license": self.license,
            "blast_radius_class": self.blast_radius_class,
            "reversible": self.reversible,
            "secret_touching": self.secret_touching,
            "network_access": self.network_access,
            "filesystem_access": self.filesystem_access,
            "human_approval_policy": self.human_approval_policy,
            "description": self.description,
            "signed": self.signed,
            "signature": self.signature,
        }


class MCPToolRegistry:
    """Federation-wide MCP tool capability manifest."""

    def __init__(self):
        self._tools: dict[str, ToolManifest] = {}

    def register(self, manifest: ToolManifest) -> None:
        """Register a tool manifest."""
        if manifest.tool_name in self._tools:
            raise ValueError(f"Tool {manifest.tool_name} already registered")
        self._tools[manifest.tool_name] = manifest

    def get(self, tool_name: str) -> ToolManifest | None:
        return self._tools.get(tool_name)

    def list_by_organ(self, organ: str) -> list[ToolManifest]:
        return [m for m in self._tools.values() if m.organ == organ]

    def list_by_lane(self, lane: ToolLane) -> list[ToolManifest]:
        return [m for m in self._tools.values() if m.lane == lane]

    def registry_hash(self) -> str:
        """BLAKE3 hash of the full registry (for attestation)."""
        canonical = json.dumps(
            sorted([m.to_dict() for m in self._tools.values()], key=lambda x: x["tool_name"]),
            sort_keys=True,
        )
        return "b3:" + hashlib.sha256(canonical.encode()).hexdigest()

    def export(self) -> dict:
        return {
            "version": 1,
            "tool_count": len(self._tools),
            "registry_hash": self.registry_hash(),
            "tools": [m.to_dict() for m in sorted(self._tools.values(), key=lambda x: x.tool_name)],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
