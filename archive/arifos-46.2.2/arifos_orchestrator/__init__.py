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

from arifos_orchestrator.core.orchestrator import run_orchestration

__all__ = ["run_orchestration"]
