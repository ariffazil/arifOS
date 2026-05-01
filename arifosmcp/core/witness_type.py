"""
arifOS Constitutional Kernel — Witness Type
═══════════════════════════════════════════

Canonical enumeration of witness classes for F3/F13 enforcement.
Lives at core/witness_type.py to avoid circular imports between
authority_gate.py and floor_evaluator.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from enum import Enum


class WitnessType(Enum):
    """
    Witness class for multi-agent and human-in-the-loop governance.

    F3 (QuadWitness): Actions above certain thresholds require multiple
    witnesses of appropriate class.

    F13 (Sovereign): Human witness is always the final authority.
    """

    AI = "ai"
    HUMAN = "human"
    MULTI = "multi"
