"""
eval_telemetry.py — Optional telemetry hook to arifos_eval/apex

Phase 2: Light integration hook for v36.1Ω measurement layer.

This module provides an OPTIONAL bridge from arifos_core to arifos_eval.
It does NOT change existing verdict logic in APEX_PRIME.py.
It only logs telemetry for comparison and validation.

Usage:
    from arifos_core.eval_telemetry import log_eval_telemetry, EVAL_TELEMETRY_ENABLED

    if EVAL_TELEMETRY_ENABLED:
        log_eval_telemetry(dials, output_text, output_metrics)

Configuration:
    Set ARIFOS_EVAL_TELEMETRY=1 environment variable to enable.
    Default: disabled (no behavioral change).

Note:
    This module is designed to fail gracefully if arifos_eval is not available.
    It never affects core verdict logic.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

# Enable via environment variable (default: disabled)
EVAL_TELEMETRY_ENABLED: bool = os.environ.get("ARIFOS_EVAL_TELEMETRY", "0") == "1"

# Logger for telemetry output
_logger = logging.getLogger("arifos.eval_telemetry")

# Cached eval layer instance (lazy initialization)
_eval_instance: Optional[Any] = None
_eval_available: Optional[bool] = None


# =============================================================================
# LAZY LOADER
# =============================================================================

def _get_eval_instance() -> Optional[Any]:
    """
    Lazily load ApexMeasurement from arifos_eval.

    Returns None if arifos_eval is not available.
    This ensures arifos_core never hard-depends on arifos_eval.
    """
    global _eval_instance, _eval_available

    if _eval_available is False:
        return None

    if _eval_instance is not None:
        return _eval_instance

    try:
        from arifos_eval.apex import ApexMeasurement
        import os

        # Look for standards file in known locations
        standards_paths = [
            os.path.join(os.path.dirname(__file__), "..", "arifos_eval", "apex", "apex_standards_v36.json"),
            os.path.join(os.path.dirname(__file__), "..", "spec", "apex_standards_v36.json"),
        ]

        for path in standards_paths:
            if os.path.exists(path):
                _eval_instance = ApexMeasurement(path)
                _eval_available = True
                _logger.info(f"Eval telemetry loaded from {path}")
                return _eval_instance

        _logger.warning("apex_standards_v36.json not found, telemetry disabled")
        _eval_available = False
        return None

    except ImportError as e:
        _logger.debug(f"arifos_eval not available: {e}")
        _eval_available = False
        return None


# =============================================================================
# TELEMETRY FUNCTIONS
# =============================================================================

def log_eval_telemetry(
    dials: Dict[str, float],
    output_text: str,
    output_metrics: Dict[str, float],
    context: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Log telemetry from arifos_eval layer for comparison.

    This function is PURELY OBSERVATIONAL. It does not affect
    any verdict logic in APEX_PRIME or other core modules.

    Args:
        dials: A/P/E/X dial values
        output_text: Output text for Anti-Hantu check
        output_metrics: Metrics dict (delta_s, peace2, k_r, etc.)
        context: Optional context for logging

    Returns:
        Eval result dict if available, None otherwise.
        Result includes: verdict, G, C_dark, Psi, floors

    Example:
        result = log_eval_telemetry(
            dials={"A": 0.9, "P": 0.9, "E": 0.95, "X": 0.9},
            output_text="Based on the analysis...",
            output_metrics={
                "delta_s": 0.2, "peace2": 1.1, "k_r": 0.98,
                "rasa": 1.0, "amanah": 1.0, "entropy": 0.1
            }
        )
        if result:
            logger.info(f"Eval verdict: {result['verdict']}")
    """
    if not EVAL_TELEMETRY_ENABLED:
        return None

    eval_layer = _get_eval_instance()
    if eval_layer is None:
        return None

    try:
        result = eval_layer.judge(dials, output_text, output_metrics)

        # Log comparison data
        _logger.info(
            f"[EVAL TELEMETRY] verdict={result['verdict']} "
            f"G={result['G']:.3f} C_dark={result['C_dark']:.3f} Psi={result['Psi']:.3f}"
        )

        if context:
            _logger.debug(f"[EVAL TELEMETRY] context={context}")

        return result

    except Exception as e:
        _logger.warning(f"Eval telemetry failed: {e}")
        return None


def compare_verdicts(
    core_verdict: str,
    dials: Dict[str, float],
    output_text: str,
    output_metrics: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """
    Compare core APEX verdict with eval layer verdict.

    This is for validation during Phase 2. It logs any discrepancies
    for analysis but does NOT change the core verdict.

    Args:
        core_verdict: Verdict from arifos_core APEX_PRIME
        dials: A/P/E/X dial values
        output_text: Output text
        output_metrics: Metrics dict

    Returns:
        Comparison result with:
        - core_verdict: Original verdict
        - eval_verdict: Eval layer verdict
        - match: Whether they agree
        - eval_details: Full eval result
    """
    if not EVAL_TELEMETRY_ENABLED:
        return None

    eval_result = log_eval_telemetry(dials, output_text, output_metrics)
    if eval_result is None:
        return None

    eval_verdict = eval_result["verdict"]
    match = core_verdict == eval_verdict

    if not match:
        _logger.warning(
            f"[VERDICT MISMATCH] core={core_verdict} eval={eval_verdict} "
            f"G={eval_result['G']:.3f} C_dark={eval_result['C_dark']:.3f}"
        )

    return {
        "core_verdict": core_verdict,
        "eval_verdict": eval_verdict,
        "match": match,
        "eval_details": eval_result,
    }


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    "EVAL_TELEMETRY_ENABLED",
    "log_eval_telemetry",
    "compare_verdicts",
]
