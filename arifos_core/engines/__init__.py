"""
arifos_core.engines - AAA Engines Facade (v35Omega)

Provides clean facades for the AAA Trinity:
- ARIFEngine (Delta) - Mind/Cold Logic - clarity, structure, reasoning
- ADAMEngine (Omega) - Heart/Warm Logic - empathy, tone, stability
- ApexEngine (Psi) - Judiciary - judgment, veto, seal

These facades wrap existing pipeline logic without changing behavior.
See: docs/AAA_ENGINES_FACADE_PLAN_v35Omega.md for design contract.

Zero-break contract:
- No changes to floor thresholds or APEX_PRIME behavior
- Facades are internal implementation detail
- All production usage flows via pipeline.py
"""

from .arif_engine import ARIFEngine
from .adam_engine import ADAMEngine
from .apex_engine import ApexEngine

__all__ = [
    "ARIFEngine",
    "ADAMEngine",
    "ApexEngine",
]
