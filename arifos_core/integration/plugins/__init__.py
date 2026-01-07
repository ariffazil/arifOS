"""
arifOS Constitutional Plugin System

This module provides constitutional governance for Claude Code plugins.
All plugin agents, skills, and tools flow through F1-F9 floor validation,
000-999 pipeline stages, and receive verdicts (SEAL/PARTIAL/VOID/SABAR/888_HOLD).

Modules:
    governance_engine: Core governance orchestration
    floor_validator: F1-F9 constitutional floor checks
    entropy_tracker: ΔS monitoring and SABAR-72 enforcement
    verdict_generator: Verdict generation (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
"""

__version__ = "1.0.0"
__all__ = [
    "governance_engine",
    "floor_validator",
    "entropy_tracker",
    "verdict_generator",
]
