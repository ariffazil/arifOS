"""
arifOS Multi-Agent Orchestrator

Constitutional governance orchestration system synchronizing:
- Claude (Reasoning/Truth layer)
- ChatGPT Codex (Code generation)
- AntiGravity (Validation)

DITEMPA BUKAN DIBERI — Forged, not given.
"""

__version__ = "0.1.0"
__author__ = "arifOS Project"

# Component 4: Metabolizer (Human-Optimized Output)
# Import these first as they have no dependencies on arifos.core
try:
    from arifos.orchestrator.metabolizer import (
        AAAMetabolizer,
        Decoder,
        Encoder,
        Metabolizer,
        PresentationStrategy,
        Semantics,
        UserProfile,
    )
    _METABOLIZER_AVAILABLE = True
except ImportError:
    # Fallback for development mode
    AAAMetabolizer = None
    Decoder = None
    Encoder = None
    Metabolizer = None
    PresentationStrategy = None
    Semantics = None
    UserProfile = None
    _METABOLIZER_AVAILABLE = False

# MCP Gateway
try:
    from arifos.orchestrator.mcp_gateway import MCPGateway, TransportClient, gateway
    _GATEWAY_AVAILABLE = True
except ImportError:
    MCPGateway = None
    TransportClient = None
    gateway = None
    _GATEWAY_AVAILABLE = False

# Legacy orchestrator (may require arifos.core dependencies)
try:
    from arifos.orchestrator.core.orchestrator import run_orchestration
    _ORCHESTRATOR_AVAILABLE = True
except ImportError:
    run_orchestration = None
    _ORCHESTRATOR_AVAILABLE = False

__all__ = [
    "AAAMetabolizer",
    "Decoder",
    "Encoder",
    "Metabolizer",
    "PresentationStrategy",
    "Semantics",
    "UserProfile",
    "MCPGateway",
    "TransportClient",
    "gateway",
    "run_orchestration",
]
