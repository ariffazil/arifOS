"""
arifOS Registry Layer — MCP tool capability manifest.

Per executive verdict:
"Create these in arifOS before adding more tools:
  mcp_tool_policy:
    default: deny
    allow_requires: [signed_tool_manifest, schema_hash, source_repository, ...]"

This package provides:
- mcp_tool_registry.py: canonical MCP tool capability manifest
- capability_manifest.py: per-tool capability matrix
- tool_scorecard.py: per-tool OpenSSF-style score
"""

from .mcp_tool_registry import MCPToolRegistry, ToolManifest, ToolLane
from .capability_manifest import CapabilityManifest
from .tool_scorecard import ToolScorecard

__all__ = ["MCPToolRegistry", "ToolManifest", "ToolLane", "CapabilityManifest", "ToolScorecard"]
