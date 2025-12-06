"""
arifos_core.waw.bridges - Synergy Link Layer

This package contains the bridges that connect arifOS W@W organs to
external detection libraries ("muscles").

Protocol:
- Bridges MUST be optional (try/except imports).
- Bridges MUST return arifOS-native metrics (0.0–1.0, or deltas).
- Bridges MUST NOT crash the pipeline if an external lib fails.

In all cases, organs remain sovereign: they interpret bridge outputs
under arifOS floors (Peace², κᵣ, Amanah, Anti-Hantu), and fall back to
their internal heuristics when bridges are unavailable.
"""

from .well_bridge import WellBridge
from .geox_bridge import GeoxBridge
from .rif_bridge import RifBridge
from .wealth_bridge import WealthBridge
from .prompt_bridge import PromptBridge

__all__ = ["WellBridge", "GeoxBridge", "RifBridge", "WealthBridge", "PromptBridge"]
