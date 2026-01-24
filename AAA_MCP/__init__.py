"""
AAA_MCP (v51.0.0) - Constitutional Intelligence Application Layer
Artifact · Authority · Architecture

The Body (Hands) - Application layer that speaks MCP protocol.
Imports arifos as a library (the Brain).

Tools:
  000_init    → Gate (Authority + Injection + Amanah)
  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)
  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
  apex_judge  → Soul (EUREKA → JUDGE → PROOF)
  999_vault   → Seal (Merkle + zkPC + Immutable Log)

Usage:
  python -m AAA_MCP              # stdio mode (default)
  python -m AAA_MCP sse          # SSE mode for Railway

DITEMPA BUKAN DIBERI
"""

__version__ = "51.0.0"

from AAA_MCP.bridge import (
    ENGINES_AVAILABLE,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
)

__all__ = [
    "ENGINES_AVAILABLE",
    "bridge_agi_router",
    "bridge_asi_router",
    "bridge_apex_router",
]
