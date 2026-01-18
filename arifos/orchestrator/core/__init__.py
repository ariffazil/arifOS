"""
Orchestrator core components

Main orchestration logic coordinating multi-agent workflow:
Claude → Codex → AntiGravity
"""

from arifos.orchestrator.core.orchestrator import run_orchestration

__all__ = ["run_orchestration"]
