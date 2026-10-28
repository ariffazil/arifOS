"""void_contract.py — a VOID verdict must carry its own work order.

WHY (2026-10-28)
    "Bare VOID is a shrug." A VOID that reaches a human as *"aku tak tahu"*
    charges the cost of a gap without handing back the way to close it. That is
    the same failure class as KX-010: a fact that exists (or a duty that exists)
    is declared somewhere and never coupled to the point of consequence.

    In arifOS grammar VOID is the HARDEST verdict, not the vaguest:
        UNKNOWN  — evidence insufficient for a claim
        HOLD     — action not yet authorized / precondition failed
        VOID     — this path is invalid within the current constitutional frame

    A path is invalidated by a specific invariant on specific evidence. So a
    VOID always knows more than "no": it knows WHICH invariant, WHICH evidence,
    and WHY repair cannot preserve the proposed path. A VOID that cannot say
    those things is not a verdict — it is an unfinished thought wearing a
    verdict's clothes.

THE FIVE FIELDS
    boundary         what exactly is unresolved / which invariant is violated
    set              the alternatives still possible, bounded where possible
    probe            the cheapest decision-changing test
    price            what the probe costs (time, money, compute, risk)
    decision_effect  which decision changes once the probe answers

    Rule adopted from the 2026-10-28 review: if no probe can change the
    decision, do not probe — stop verifying and either choose inside
    reversible scope or escalate the exact human decision.

COUPLING, NOT DECORATION
    A contract that is only written down is KX-010 again. This module is called
    from the runtime envelope chokepoint and its result is stamped on the
    envelope, so an incomplete VOID is visible at the boundary instead of
    arriving at a human as a clean-looking refusal.

    It does NOT change the verdict. It never upgrades VOID to HOLD and never
    suppresses a refusal — a wrong VOID is a different defect from a bare VOID,
    and conflating the two would teach the system to stop refusing.
"""

from __future__ import annotations

from typing import Any, Mapping

VOID_REQUIRED: tuple[str, ...] = (
    "boundary",
    "set",
    "probe",
    "price",
    "decision_effect",
)

# A field satisfies the contract if it carries real content. An empty string,
# an empty list, a bare None or a one-word shrug is not content.
_MIN_TEXT = 8


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) >= _MIN_TEXT
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    if isinstance(value, Mapping):
        return len(value) > 0
    return True


def validate_void(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return the VOID contract state for a payload. Never raises.

    Accepts the contract either flat on the payload or nested under
    `void_contract`, so callers are not forced to reshape an envelope.
    """
    try:
        payload = payload or {}
        nested = payload.get("void_contract")
        src: Mapping[str, Any] = nested if isinstance(nested, Mapping) else payload

        present = [f for f in VOID_REQUIRED if _is_filled(src.get(f))]
        missing = [f for f in VOID_REQUIRED if f not in present]
        complete = not missing
        return {
            "schema": "arifos.void_contract.v1",
            "complete": complete,
            "present": present,
            "missing": missing,
            "fields": list(VOID_REQUIRED),
            "note": (
                "complete VOID"
                if complete
                else "INCOMPLETE VOID — a refusal without probe and price is a shrug, not a verdict"
            ),
        }
    except Exception:  # never let the contract check break a verdict path
        return {
            "schema": "arifos.void_contract.v1",
            "complete": False,
            "present": [],
            "missing": list(VOID_REQUIRED),
            "fields": list(VOID_REQUIRED),
            "note": "contract check failed — treated as incomplete (fail closed)",
        }


def stamp_void_contract(envelope: Any) -> dict[str, Any] | None:
    """Attach the contract state to an envelope whose verdict is VOID.

    Returns the contract dict when stamped, None when the verdict is not VOID.
    Does not mutate the verdict.
    """
    verdict = getattr(envelope, "verdict", None)
    if str(getattr(verdict, "value", verdict) or "").upper() != "VOID":
        return None

    payload = getattr(envelope, "payload", None)
    if not isinstance(payload, dict):
        payload = {}
        try:
            envelope.payload = payload
        except Exception:
            return None

    contract = validate_void(payload)
    payload["void_contract"] = contract
    return contract
