# arifos_core/dream_forge/__init__.py
"""
arifOS Dream Forge: Offline Generative Replay System

Module: arifos_core.dream_forge
Version: v36.2 PHOENIX
Purpose: O-TASK Cadence implementation for healing from past failures (scars)

Components:
    - crucible.py: O-ALIGN classification (FACT, PARADOX, ANOMALY, NOISE)
    - anvil.py: O-FORGE generative replay + O-STRIKE validation

Motto: "Learn by cooling, not by burning."

Usage:
    from arifos_core.dream_forge.crucible import OAlignCrucible, OreType
    from arifos_core.dream_forge.anvil import OForgeAnvil

Safety: This is a LAB-ONLY tool. Outputs are quarantined.
"""

from arifos_core.dream_forge.crucible import OAlignCrucible, OreType
from arifos_core.dream_forge.anvil import OForgeAnvil

__all__ = ["OAlignCrucible", "OreType", "OForgeAnvil"]
__version__ = "36.2.0"
