"""
Agent Zero Integration Module

Provides arifOS constitutional governance for Agent Zero.

Usage:
    from integrations.agent_zero import checkpoint, seal, Verdict

    # Validate an action
    result = checkpoint("Delete all user files")
    if result.verdict == Verdict.VOID:
        print("Action blocked:", result.reasons)

    # Seal a completed action
    ledger_id = seal(
        action="Created new user account",
        result="User john@example.com created successfully",
        verdict=Verdict.SEAL
    )
"""

from .bridge import (
    checkpoint,
    validate_floor,
    seal,
    Verdict,
    CheckpointResult,
    FloorDefinition,
    FLOORS,
    HARD_FLOORS,
    SOFT_FLOORS,
)

__all__ = [
    "checkpoint",
    "validate_floor",
    "seal",
    "Verdict",
    "CheckpointResult",
    "FloorDefinition",
    "FLOORS",
    "HARD_FLOORS",
    "SOFT_FLOORS",
]

__version__ = "1.0.0"
