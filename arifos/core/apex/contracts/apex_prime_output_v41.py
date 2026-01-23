from __future__ import annotations

from typing import Optional, Literal, Dict, Any

Verdict = Literal["SEAL", "SABAR", "VOID"]

_ALLOWED_REASON_PREFIXES = (
    "F1(", "F2(", "F3(", "F4(", "F5(", "F6(", "F7(", "F8(", "F9("
)

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _round2(x: float) -> float:
    return round(x + 1e-12, 2)

def validate_reason_code(reason_code: Optional[str]) -> Optional[str]:
    if reason_code is None:
        return None
    rc = reason_code.strip()
    if not rc:
        return None
    if any(ch.isspace() for ch in rc):
        raise ValueError("reason_code must be a single token (no whitespace).")
    if not rc.startswith(_ALLOWED_REASON_PREFIXES) or not rc.endswith(")"):
        raise ValueError("reason_code must look like F1(...)..F9(...).")
    if len(rc) > 32:
        raise ValueError("reason_code too long.")
    return rc

def compute_apex_pulse(psi_internal: float, verdict: Verdict) -> float:
    """
    Hard verdict-gated bands:
      VOID  -> 0.00–0.94
      SABAR -> 0.95–0.99
      SEAL  -> 1.00–1.10
    Then clamp to 0.00–1.10 and round(2).
    """
    v = _round2(_clamp(float(psi_internal), 0.00, 1.10))

    if verdict == "VOID":
        return min(v, 0.94)
    if verdict == "SABAR":
        return _round2(_clamp(v, 0.95, 0.99))
    if verdict == "SEAL":
        return max(v, 1.00)
    raise ValueError(f"Unknown verdict: {verdict}")

def serialize_public(
    *,
    verdict: Verdict,
    psi_internal: Optional[float],
    response: str,
    reason_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Public output contract.
    If psi_internal is missing -> apex_pulse = null (Amanah-safe).
    """
    rc = validate_reason_code(reason_code)

    payload: Dict[str, Any] = {
        "verdict": verdict,
        "response": response,
    }

    if psi_internal is None:
        payload["apex_pulse"] = None
    else:
        payload["apex_pulse"] = compute_apex_pulse(psi_internal, verdict)

    if rc:
        payload["reason_code"] = rc

    return payload