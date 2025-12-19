"""
Bridge Constants: v43 Semantic Exit Codes and Verdict Mapping
Canonical source of truth for aCLIP <-> arifOS vocabulary alignment.

Doctrine: Ditempa, Bukan Diberi (Forged, Not Given)
Authority: Constitutional Floors (F1-F9) enforced architecturally
Humility Band: Omega_0 in [0.03, 0.05]
"""

from typing import Dict

# ============================================================================
# SEMANTIC EXIT CODES (v43 - POSIX-aligned, governance-aware)
# ============================================================================

EXIT_PASS = 0        # Stage OK; continue
EXIT_FLAG = 1        # Soft floor violation; review recommended
EXIT_HOLD = 88       # Governance issue; must resolve
EXIT_VOID = 89       # Hard floor violation; must redesign
EXIT_SEALED = 100    # Decision sealed; immutable
EXIT_ERROR = 255     # System crash (non-governance)

# ============================================================================
# VERDICT LABELS (human-facing; map to exit codes)
# ============================================================================

VERDICT_PASS = "PASS"        # exit 0
VERDICT_FLAG = "FLAG"        # exit 1
VERDICT_HOLD = "HOLD"        # exit 88
VERDICT_VOID = "VOID"        # exit 89
VERDICT_SEALED = "SEALED"    # exit 100
VERDICT_ERROR = "ERROR"      # exit 255

# ============================================================================
# BIDIRECTIONAL MAPPING (verdicts <-> exit codes)
# ============================================================================

VERDICT_TO_EXIT_CODE: Dict[str, int] = {
    VERDICT_PASS: EXIT_PASS,
    VERDICT_FLAG: EXIT_FLAG,
    VERDICT_HOLD: EXIT_HOLD,
    VERDICT_VOID: EXIT_VOID,
    VERDICT_SEALED: EXIT_SEALED,
    VERDICT_ERROR: EXIT_ERROR,
}

EXIT_CODE_TO_VERDICT: Dict[int, str] = {v: k for k, v in VERDICT_TO_EXIT_CODE.items()}

# ============================================================================
# CONSTITUTIONAL FLOOR ENFORCEMENT (F1-F9)
# ============================================================================

# Hard floors (cannot override; trigger EXIT_VOID)
HARD_FLOORS = {
    "F1_AMANAH": {
        "name": "Amanah (Grounded in Verified Facts)",
        "level": "hard",
        "exit_code": EXIT_VOID,
    },
    "F9_ANTI_HANTU": {
        "name": "Anti-Hantu (No AI Consciousness Claims)",
        "level": "hard",
        "exit_code": EXIT_VOID,
    },
}

# Soft floors (can flag; may override with token)
SOFT_FLOORS = {
    "F4_CLARITY": {
        "name": "Clarity (Output Reduces Confusion)",
        "level": "soft",
        "exit_code": EXIT_FLAG,
    },
    "F5_PEACE2": {
        "name": "Peace² (No Escalation Language)",
        "level": "soft",
        "exit_code": EXIT_FLAG,
    },
    "F7_HUMILITY": {
        "name": "Humility (Uncertainties Acknowledged)",
        "level": "soft",
        "exit_code": EXIT_FLAG,
    },
}

# ============================================================================
# AUTHORITY & TOKENS
# ============================================================================

TOKEN_PREFIX = "CLIP1"
DEFAULT_TTL_SECONDS = 15 * 60  # 15 minutes per-session
DEFAULT_HUMILITY_BAND = (0.03, 0.05)  # Omega_0

# ============================================================================
# LEDGER & AUDIT
# ============================================================================

LEDGER_DIR = "cooling_ledger"
SESSION_ARTIFACT_DIR = ".arifos_clip"
LEDGER_FILE_DECISIONS = f"{LEDGER_DIR}/decisions.jsonl"
LEDGER_FILE_AUDIT = f"{LEDGER_DIR}/audit.jsonl"

# ============================================================================
# VERDICT SEMANTICS (for UI/logging)
# ============================================================================

VERDICT_SEMANTICS: Dict[str, str] = {
    VERDICT_PASS: "Continue",
    VERDICT_FLAG: "Review recommended",
    VERDICT_HOLD: "Stop and review",
    VERDICT_VOID: "Invalid by design; redesign required",
    VERDICT_SEALED: "Final and immutable",
    VERDICT_ERROR: "System failure (non-governance)",
}

# ============================================================================
# HELPER FUNCTIONS (utility layer)
# ============================================================================


def get_verdict_from_exit_code(exit_code: int) -> str:
    """
    Convert exit code to verdict label.
    
    Args:
        exit_code: Integer exit code (0, 1, 88, 89, 100, 255)
    
    Returns:
        Verdict label (PASS, FLAG, HOLD, VOID, SEALED, ERROR)
    
    Raises:
        ValueError if exit_code is unknown
    """
    if exit_code not in EXIT_CODE_TO_VERDICT:
        raise ValueError(f"Unknown exit code: {exit_code}")
    return EXIT_CODE_TO_VERDICT[exit_code]


def get_exit_code_from_verdict(verdict: str) -> int:
    """
    Convert verdict label to exit code.
    
    Args:
        verdict: Verdict label (PASS, FLAG, HOLD, VOID, SEALED, ERROR)
    
    Returns:
        Integer exit code (0, 1, 88, 89, 100, 255)
    
    Raises:
        ValueError if verdict is unknown
    """
    if verdict not in VERDICT_TO_EXIT_CODE:
        raise ValueError(f"Unknown verdict: {verdict}")
    return VERDICT_TO_EXIT_CODE[verdict]


def get_semantic_description(verdict: str) -> str:
    """
    Get human-friendly description of a verdict.
    
    Args:
        verdict: Verdict label (PASS, FLAG, HOLD, VOID, SEALED, ERROR)
    
    Returns:
        Human-readable description
    
    Raises:
        ValueError if verdict is unknown
    """
    if verdict not in VERDICT_SEMANTICS:
        raise ValueError(f"Unknown verdict: {verdict}")
    return VERDICT_SEMANTICS[verdict]


def is_hard_floor_violation(floor_code: str) -> bool:
    """
    Check if a floor code represents a hard floor (cannot override).
    
    Args:
        floor_code: Floor code (e.g., F1_AMANAH, F9_ANTI_HANTU)
    
    Returns:
        True if hard floor; False otherwise
    """
    return floor_code in HARD_FLOORS


def is_soft_floor_violation(floor_code: str) -> bool:
    """
    Check if a floor code represents a soft floor (can flag/override).
    
    Args:
        floor_code: Floor code (e.g., F4_CLARITY, F5_PEACE2)
    
    Returns:
        True if soft floor; False otherwise
    """
    return floor_code in SOFT_FLOORS


# ============================================================================
# VERSION & METADATA
# ============================================================================

BRIDGE_VERSION = "v43"
BRIDGE_STATUS = "PRODUCTION-GRADE"
LAST_UPDATED = "2025-12-19"
DOCTRINE = "Ditempa, Bukan Diberi"
