# Bridge client to call arifOS law engine functions (v42-aware).
from typing import Any, Dict, Optional, Tuple

from arifos_clip.aclip.bridge import verdicts

_arifos_eval = None


def _load_arifos_evaluator() -> Optional[Any]:
    """Multi-path import to support v42 layout + legacy shim."""
    try:
        from arifos_core.bridge import evaluate_session  # type: ignore

        return evaluate_session
    except Exception:
        pass
    try:
        import arifos_core as arifos_core_pkg  # legacy root export

        if hasattr(arifos_core_pkg, "evaluate_session"):
            return arifos_core_pkg.evaluate_session
    except Exception:
        pass
    return None


def request_verdict(session) -> Dict[str, Any]:
    """
    Request a verdict from arifOS on whether the session can be sealed.

    Returns a dict:
    {
      "verdict": <string or None>,  # expected values in verdicts.* (SEAL/HOLD/VOID/PARTIAL/SABAR/PASS)
      "reason": <string or None>,   # human-friendly reason if available
      "details": <optional payload> # passthrough from arifOS if provided
    }

    If arifOS is unavailable or errors, returns HOLD-equivalent:
      {"verdict": verdicts.VERDICT_HOLD, "reason": "arifOS not available", "details": {}}
    """
    global _arifos_eval

    if _arifos_eval is None:
        _arifos_eval = _load_arifos_evaluator()

    if _arifos_eval is None:
        return {"verdict": verdicts.VERDICT_HOLD, "reason": "arifOS not available", "details": {}}

    try:
        result = _arifos_eval(session.data)
    except Exception as exc:  # safe-by-default: treat as HOLD
        return {"verdict": verdicts.VERDICT_HOLD, "reason": str(exc), "details": {}}

    # Normalize return shape
    if isinstance(result, dict):
        verdict_value = result.get("verdict")
        reason = result.get("reason")
        details = result.get("details", {})
    else:
        verdict_value = result
        reason = None
        details = {}

    # If arifOS returned nothing, treat as HOLD
    if verdict_value is None:
        return {"verdict": verdicts.VERDICT_HOLD, "reason": "no verdict returned", "details": details}

    return {"verdict": verdict_value, "reason": reason, "details": details}
