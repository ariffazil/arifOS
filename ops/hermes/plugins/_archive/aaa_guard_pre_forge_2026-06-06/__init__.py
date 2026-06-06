"""
aaa_guard — AAA Runtime Enforcement Gate
DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

P0: Converts constitutional floors from text into runtime enforcement.
Intercepts every tool call before execution and applies F1-F13 policy.

Architecture:
- pre_tool_call: blocks/flags dangerous tools, enforces 888_HOLD for F13
- pre_llm_call: injects current floor constraints, risk class, session state
"""

from aaa_guard.aaa_guard import AAAGuardPlugin, FLOOR_CLASSES, RISK_TIERS

def register():
    """Placeholder for hermes plugin registration."""
    pass

__all__ = ["AAAGuardPlugin", "register", "FLOOR_CLASSES", "RISK_TIERS"]
