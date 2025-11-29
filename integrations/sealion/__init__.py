"""
arifOS SEA-LION Integration

Constitutional AI for Southeast Asia.
Wraps SEA-LION regional models with arifOS v34Omega governance.

Usage:
    from integrations.sealion import GovernedSEALION

    client = GovernedSEALION(api_key="your-key")
    result = client.chat("What is AI governance?")
"""

from .arifos_sealion import (
    GovernedSEALION,
    FloorComputer,
    StandaloneCoolingLedger,
    Metrics,
    SEALION_MODELS,
    THRESHOLDS,
    create_client,
    quick_chat,
)

__version__ = "34Omega"
__all__ = [
    "GovernedSEALION",
    "FloorComputer",
    "StandaloneCoolingLedger",
    "Metrics",
    "SEALION_MODELS",
    "THRESHOLDS",
    "create_client",
    "quick_chat",
]
