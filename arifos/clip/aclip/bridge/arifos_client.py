# Bridge client to call arifOS law engine functions (v42-aware).
from typing import Any, Dict, Optional, Tuple

from arifos.clip.aclip.bridge import verdicts

_arifos_eval = None


def _load_arifos_evaluator() -> Optional[Any]:
    """Multi-path import to support v49 single-body layout."""
    try:
        # v49: Primary Path (arifos package)
        from arifos.integration.bridge import evaluate_session
        return evaluate_session
    except ImportError:
        pass

    # v49: Core Path (arifos.core) - REMOVED (Redundant)

    try:
        # Legacy: Fallback (should be removed in v50)
        import arifos.integration.bridge as legacy_bridge  # type: ignore
        return legacy_bridge.evaluate_session
    except ImportError:
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
