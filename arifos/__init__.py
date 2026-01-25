"""
arifOS v52.5.1-SEAL Constitutional Kernel
5-Tool Trinity Framework + ATLAS-333 Smart Routing

A filter that stops AI from lying, harming, or being overconfident.
- 5 rules (TEACH): Truth, Empathy, Amanah, Clarity, Humility
- 4 verdicts: SEAL, SABAR, VOID, 888_HOLD
- 4 lanes: CRISIS, FACTUAL, CARE, SOCIAL

Modules:
  arifos.mcp       - MCP Server (Trinity 5-tool)
  arifos.core      - AGI/ASI/APEX kernels
  arifos.protocol  - Protocol handlers

DITEMPA BUKAN DIBERI
"""

__version__ = "52.5.1"

# Minimal exports to avoid circularity during initialization

from .mcp.mode_selector import MCPMode

from .core.system.types import Metrics, Verdict, ApexVerdict, FloorCheckResult
