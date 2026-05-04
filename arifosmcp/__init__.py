"""
arifosmcp — The Sovereign Constitutional Intelligence Kernel
═════════════════════════════════════════════════════════════

13 canonical MCP capability tools | 13 Floors (F1–F13) | Trinity ΔΩΨ
DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

__version__ = "2026.05.01"
__author__ = "Muhammad Arif bin Fazil"
__license__ = "AGPL-3.0-only"

try:
    import asyncio

    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
