"""
arifOS v53.1.0-SEAL Constitutional Kernel
5-Tool Trinity Framework + ATLAS-333 Smart Routing

A filter that stops AI from lying, harming, or being overconfident.
- 5 rules (TEACH): Truth, Empathy, Amanah, Clarity, Humility
- 4 verdicts: SEAL, SABAR, VOID, 888_HOLD
- 4 lanes: CRISIS, FACTUAL, CARE, SOCIAL

Modules:
  arifos.mcp       - MCP Server (Trinity 5-tool)
  arifos.core      - AGI/ASI/APEX kernels
  arifos.protocol  - Protocol handlers

Note: Heavy imports are done lazily to avoid startup delays.
Import specific modules when needed:
  from arifos.core.system.apex_prime import APEXPrime
  from arifos.core.system.types import Metrics, Verdict

DITEMPA BUKAN DIBERI
"""

__version__ = "53.1.0"

# Minimal exports - no heavy imports at package level
__all__ = ["__version__"]
