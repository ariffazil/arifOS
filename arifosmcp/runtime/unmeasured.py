"""
arifosmcp/runtime/unmeasured.py — UNMEASURED sentinel type.

A4 compliance: UNMEASURED may never satisfy a floor, never render as 0.0,
never coerce to pass. It is a type, not a string. Any attempt to treat it
as a boolean, float, or comparable value raises UnmeasuredError.

Usage:
    from arifosmcp.runtime.unmeasured import UNMEASURED, UnmeasuredError

    G = UNMEASURED
    if G > 0.5:   # raises UnmeasuredError
        ...

    value = float(G)  # raises UnmeasuredError

    if G:  # raises UnmeasuredError
        ...

Safe patterns:
    if G is UNMEASURED:  # identity check — always safe
        ...
    if G is not UNMEASURED:  # also safe
        ...
"""

from __future__ import annotations

from typing import Any, NoReturn


class UnmeasuredError(TypeError):
    """Raised when UNMEASURED is coerced to a truth value, number, or comparison."""


class _Unmeasured:
    """Sentinel for values that have not been measured.

    Singleton. Identity-check with `is UNMEASURED` (safe). Any attempt
    to coerce to bool, float, int, or compare numerically raises.
    """

    _instance: _Unmeasured | None = None

    def __new__(cls) -> _Unmeasured:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNMEASURED"

    def __str__(self) -> str:
        return "UNMEASURED"

    def __hash__(self) -> int:
        return hash("UNMEASURED")

    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return True

    def __bool__(self) -> NoReturn:
        raise UnmeasuredError("UNMEASURED has no truth value")

    def __float__(self) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not a number")

    def __int__(self) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not a number")

    def __lt__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not ordered")

    def __le__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not ordered")

    def __gt__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not ordered")

    def __ge__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED is not ordered")

    def __add__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __sub__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __mul__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __truediv__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __radd__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __rsub__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __rmul__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def __rtruediv__(self, other: object) -> NoReturn:
        raise UnmeasuredError("UNMEASURED cannot be used in arithmetic")

    def as_string_safe(self) -> str:
        """Explicit opt-in for serialization contexts where 'UNMEASURED' is
        the correct wire representation (JSON, SCT claims, health output).
        This is NOT coercion — it is an explicit serialization method.
        """
        return "UNMEASURED"


UNMEASURED = _Unmeasured()


def is_unmeasured(value: Any) -> bool:
    """Safe check: returns True ONLY if value IS the UNMEASURED sentinel."""
    return value is UNMEASURED


def coerce_legacy(value: Any) -> Any:
    """Convert legacy string 'UNMEASURED' to the sentinel.

    Safe for use in SCT parsing and session hydration where old tokens
    carry the string 'UNMEASURED'. Returns the sentinel for the string,
    passes through the sentinel unchanged, returns other values as-is.
    """
    if value is UNMEASURED:
        return UNMEASURED
    if value == "UNMEASURED":
        return UNMEASURED
    return value


def unmeasured_apex_dict() -> dict[str, _Unmeasured]:
    """Return apex dict with UNMEASURED sentinels (not strings).

    Replacement for sct.unmeasured_apex() which returns string values.
    Consumers that check `is UNMEASURED` will see sentinels;
    consumers that check `== 'UNMEASURED'` will see False (as intended).
    """
    return {"G": UNMEASURED, "C_dark": UNMEASURED, "W3": UNMEASURED, "h": UNMEASURED}
