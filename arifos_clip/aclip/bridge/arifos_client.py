# Bridge client to call arifOS law engine functions
from typing import Any, Optional

arifos_core: Optional[Any] = None
try:
    import arifos_core as _arifos_core  # assuming arifOS core is accessible in the environment
    arifos_core = _arifos_core
except ImportError:
    pass

def request_verdict(session):
    """
    Request a verdict from arifOS on whether the session can be sealed.
    Returns a tuple (verdict_value, reason). If arifOS is not available or an error occurs,
    returns (None, <error reason>).
    """
    if arifos_core is None:
        return (None, "arifOS not available")
    try:
        # We assume arifOS provides a function to evaluate the session's readiness to seal.
        if hasattr(arifos_core, "evaluate_session"):
            verdict = arifos_core.evaluate_session(session.data)
        else:
            # If no direct function, assume verdict is not available
            verdict = None
    except Exception as e:
        return (None, str(e))
    # If verdict is returned (e.g., "SEAL", "HOLD", etc.), no error reason
    return (verdict, None)
