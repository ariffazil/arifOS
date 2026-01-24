"""
Safe Type Conversions - F1 (Amanah) Type Safety

Prevents crashes from unexpected types in metrics.get() and similar operations.

Design Principles:
1. **Fail-Safe**: Return safe default instead of crashing
2. **Explicit**: Log conversion failures for debugging
3. **Defensive**: Handle None, empty strings, malformed data

Usage:
    >>> metrics = {"truth": "0.95", "tri_witness": None}
    >>> truth = safe_float(metrics.get("truth"), 0.0)
    0.95
    >>> tri_witness = safe_float(metrics.get("tri_witness"), 0.0)
    0.0  # Safe default, no crash

DITEMPA BUKAN DIBERI - Type safety forged into the foundation
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with fallback default.

    Args:
        value: Value to convert (can be int, float, str, None, etc.)
        default: Default value if conversion fails (default 0.0)

    Returns:
        float: Converted value or default if conversion fails

    Examples:
        >>> safe_float(0.95, 0.0)
        0.95
        >>> safe_float("0.95", 0.0)
        0.95
        >>> safe_float(None, 0.0)
        0.0
        >>> safe_float("invalid", 0.0)
        0.0
        >>> safe_float([1, 2, 3], 0.0)
        0.0
    """
    # Handle None explicitly
    if value is None:
        return default

    # Already a float
    if isinstance(value, float):
        return value

    # Try conversion
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        logger.debug(
            f"safe_float: Failed to convert {type(value).__name__} to float: {e}. "
            f"Returning default={default}"
        )
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int with fallback default.

    Args:
        value: Value to convert (can be int, float, str, None, etc.)
        default: Default value if conversion fails (default 0)

    Returns:
        int: Converted value or default if conversion fails

    Examples:
        >>> safe_int(42, 0)
        42
        >>> safe_int("42", 0)
        42
        >>> safe_int(3.14, 0)
        3
        >>> safe_int(None, 0)
        0
        >>> safe_int("invalid", 0)
        0
    """
    # Handle None explicitly
    if value is None:
        return default

    # Already an int
    if isinstance(value, int) and not isinstance(value, bool):
        return value

    # Try conversion
    try:
        return int(value)
    except (TypeError, ValueError) as e:
        logger.debug(
            f"safe_int: Failed to convert {type(value).__name__} to int: {e}. "
            f"Returning default={default}"
        )
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """
    Safely convert value to bool with fallback default.

    Handles common boolean representations in config/metrics:
    - Truthy: True, "true", "yes", "1", 1, "on"
    - Falsy: False, "false", "no", "0", 0, "off", None

    Args:
        value: Value to convert (can be bool, str, int, None, etc.)
        default: Default value if conversion fails (default False)

    Returns:
        bool: Converted value or default if conversion fails

    Examples:
        >>> safe_bool(True, False)
        True
        >>> safe_bool("true", False)
        True
        >>> safe_bool("yes", False)
        True
        >>> safe_bool("1", False)
        True
        >>> safe_bool(1, False)
        True
        >>> safe_bool(None, False)
        False
        >>> safe_bool("invalid", False)
        False
    """
    # Handle None explicitly
    if value is None:
        return default

    # Already a bool
    if isinstance(value, bool):
        return value

    # Try common boolean string representations
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in {"true", "yes", "1", "on"}:
            return True
        elif value_lower in {"false", "no", "0", "off"}:
            return False
        else:
            logger.debug(
                f"safe_bool: Unrecognized string '{value}'. Returning default={default}"
            )
            return default

    # Try int conversion (0 = False, non-zero = True)
    try:
        return bool(int(value))
    except (TypeError, ValueError) as e:
        logger.debug(
            f"safe_bool: Failed to convert {type(value).__name__} to bool: {e}. "
            f"Returning default={default}"
        )
        return default


__all__ = ["safe_float", "safe_int", "safe_bool"]
