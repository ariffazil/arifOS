"""
arifOS v52.0.0 Constitutional Kernel
5-Tool Trinity Framework

Modules:
  arifos.mcp       - MCP Server (Trinity 5-tool)
  arifos.core      - AGI/ASI/APEX kernels
  arifos.protocol  - Protocol handlers

DITEMPA BUKAN DIBERI
"""

__version__ = "v52.0.0"

# Minimal exports to avoid circularity during initialization

from .mcp.mode_selector import MCPMode

from .core.system.types import Metrics, Verdict, ApexVerdict, FloorCheckResult
