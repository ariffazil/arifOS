"""
AGI ROOM - ARIF Loop v52.1 Mind/Reflect Phase

DITEMPA BUKAN DIBERI - Forged, Not Given

This module implements the AGI (Mind/Δ) parallel room for the ARIF Loop.
AGI runs stages 111-222-333 in isolation, producing DELTA_BUNDLE.
ASI CANNOT see this output until 444 TRINITY_SYNC merges it.

Architecture:
    111 SENSE: Parse query → facts, detect intent
    222 THINK: Generate 3 hypotheses (conservative/exploratory/adversarial)
    333 REASON: Build reasoning tree, compute ΔS, floor scores, vote

Constitutional Floors (AGI owns):
    F2 Truth: ≥ 0.99 (factual accuracy)
    F4 Clarity: ΔS ≤ 0 (reduces confusion)
    F7 Humility: Ω₀ ∈ [0.03, 0.05] (uncertainty band)
    F13 Curiosity: ≥ 3 paths explored

Output:
    DELTA_BUNDLE (sealed, thermodynamically isolated from ASI)

Version: v52.1-CANONICAL
Author: Muhammad Arif bin Fazil
"""

from .executor import (
    AGIRoom,
    execute_agi_room,
)

from .stage_111_sense import (
    execute_stage_111,
    ParsedFact,
    SenseOutput,
)

from .stage_222_think import (
    execute_stage_222,
    HypothesisPath,
)

from .stage_333_reason import (
    execute_stage_333,
    ReasonOutput,
)

__all__ = [
    # Executor
    "AGIRoom",
    "execute_agi_room",
    # Stage 111
    "execute_stage_111",
    "ParsedFact",
    "SenseOutput",
    # Stage 222
    "execute_stage_222",
    "HypothesisPath",
    # Stage 333
    "execute_stage_333",
    "ReasonOutput",
]

__version__ = "v52.1-CANONICAL"
