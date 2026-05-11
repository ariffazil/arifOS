"""
core/paradox — Paradox detection and resolution engine for arifOS.

Implements the PARADOX_DOCTRINE_V1:
- Circuit Breakers (CB1-CB5) for epistemic failure modes
- Conflicting Verdicts resolution (Conservative Wins)
- Evidence vs Intent resolution (P1)
- Post-SEAL correction protocols (P8)

Author: Muhammad Arif bin Fazil
Status: EMBODIED v2026.05.11
"""

from __future__ import annotations

from core.paradox.circuit_breakers import (
    CircuitBreaker,
    CircuitBreakerState,
    check_godellock,
    check_single_witness,
    check_cheap_truth,
    check_recursive_stack,
    check_confidence_cascade,
    evaluate_all_breakers,
)
from core.paradox.conflict_resolver import (
    resolve_verdict_conflict,
    conservative_wins,
    ConflictResolution,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "check_godellock",
    "check_single_witness",
    "check_cheap_truth",
    "check_recursive_stack",
    "check_confidence_cascade",
    "evaluate_all_breakers",
    "resolve_verdict_conflict",
    "conservative_wins",
    "ConflictResolution",
]
