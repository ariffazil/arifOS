"""
AAA_MCP (v51.2.0) - Constitutional Intelligence Application Layer
Artifact · Authority · Architecture

Aligned with v51 Unified Core Architecture:
  - AGINeuralCore (Mind - Δ)
  - ASIActionCore (Heart - Ω)
  - APEXJudicialCore (Soul - Ψ)

The Body (Hands) - Application layer that speaks MCP protocol.
Imports arifos as a library (the Brain).

Tools:
  000_init    → Gate (Session management)
  agi_genius  → Mind (SENSE → REFLECT → ATLAS)
  asi_act     → Heart (EVIDENCE → EMPATHIZE → BRIDGE)
  apex_judge  → Soul (FORGE → JUDGE → PROOF)
  999_vault   → Seal (Hash + Immutable Log)

Usage:
  python -m AAA_MCP              # stdio mode (default)
  python -m AAA_MCP sse          # SSE mode for Railway

DITEMPA BUKAN DIBERI
"""

import os

# Read version from single source of truth
_version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")
try:
    with open(_version_file) as f:
        __version__ = f.read().strip()
except FileNotFoundError:
    __version__ = "51.2.0"

from AAA_MCP.bridge import (
    ENGINES_AVAILABLE,
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)

__all__ = [
    # Availability Flag
    "ENGINES_AVAILABLE",
    # Routers
    "bridge_init_router",
    "bridge_agi_router",
    "bridge_asi_router",
    "bridge_apex_router",
    "bridge_vault_router",
]
