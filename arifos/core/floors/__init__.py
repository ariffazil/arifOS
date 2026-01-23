"""
arifOS Constitutional Floors Package

12 floors implementing AGI/ASI/APEX separation of powers.

Version: v46.1-APEX-THEORY
Status: SEALED
"""

from .floor_01_input_validation import (
    sanitize_input,
    contains_sql_injection,
    contains_xss,
    contains_command_injection,
    compute_psi
)

# Floor 04-06 stub implementations (v46.1)
from .floor_04_data_persistence import validate_vault_consistency
from .floor_05_pattern_recognition import detect_anomalies
from .floor_06_semantic_understanding import analyze_coherence

__all__ = [
    # Floor 01
    "sanitize_input",
    "contains_sql_injection",
    "contains_xss",
    "contains_command_injection",
    "compute_psi",
    # Floor 04-06 (stubs)
    "validate_vault_consistency",
    "detect_anomalies",
    "analyze_coherence",
]

__version__ = "v46.1"
__status__ = "SEALED"
