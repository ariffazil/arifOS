"""
Verdict Mapping Layer (v43-aligned).
Thin wrapper that imports semantic constants and provides backward-compatible API.

This file is the translation layer between arifOS core and aCLIP.
All logic is delegated to constants.py (source of truth).
"""

from arifos_clip.aclip.bridge.constants import (
    # Verdict labels
    VERDICT_PASS,
    VERDICT_FLAG,
    VERDICT_HOLD,
    VERDICT_VOID,
    VERDICT_SEALED,
    VERDICT_ERROR,
    # Exit codes
    EXIT_PASS,
    EXIT_FLAG,
    EXIT_HOLD,
    EXIT_VOID,
    EXIT_SEALED,
    EXIT_ERROR,
    # Mappings
    VERDICT_TO_EXIT_CODE,
    EXIT_CODE_TO_VERDICT,
    VERDICT_SEMANTICS,
    # Helper functions
    get_verdict_from_exit_code,
    get_exit_code_from_verdict,
    get_semantic_description,
    is_hard_floor_violation,
    is_soft_floor_violation,
)

# ============================================================================
# RE-EXPORT (backward compatibility)
# ============================================================================

__all__ = [
    # Verdict labels
    "VERDICT_PASS",
    "VERDICT_FLAG",
    "VERDICT_HOLD",
    "VERDICT_VOID",
    "VERDICT_SEALED",
    "VERDICT_ERROR",
    # Exit codes
    "EXIT_PASS",
    "EXIT_FLAG",
    "EXIT_HOLD",
    "EXIT_VOID",
    "EXIT_SEALED",
    "EXIT_ERROR",
    # Mappings (legacy names)
    "verdict_to_exit_code",
    "exit_code_to_verdict",
    # Helper functions
    "get_verdict_name",
    "get_exit_code",
    "get_semantic_description",
]

# Legacy dict API (backward-compatible)
verdict_to_exit_code = VERDICT_TO_EXIT_CODE
exit_code_to_verdict = EXIT_CODE_TO_VERDICT


# ============================================================================
# LEGACY FUNCTIONS (backward-compatible)
# ============================================================================


def get_verdict_name(exit_code: int) -> str:
    """
    (LEGACY) Convert exit code to verdict label.
    
    Deprecated: Use get_verdict_from_exit_code() instead.
    """
    try:
        return get_verdict_from_exit_code(exit_code)
    except ValueError:
        return VERDICT_ERROR


def get_exit_code(verdict: str) -> int:
    """
    (LEGACY) Convert verdict label to exit code.
    
    Deprecated: Use get_exit_code_from_verdict() instead.
    """
    try:
        return get_exit_code_from_verdict(verdict)
    except ValueError:
        return EXIT_ERROR
