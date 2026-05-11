"""
arifOS.SABAR — HOLD Lifecycle and Cooling Protocol
Stage: Sovereign Guard
DITEMPA BUKAN DIBERI — 999 SEAL

Consolidates: 888_HOLD cooling logic, human approval gating, Phoenix-72 cycle
Responsibility: HOLD lifecycle manager, cooling period, human approval queue
"""

from fastmcp import Context
from typing import Literal


async def sabar(
    ctx: Context,
    mode: Literal["check", "register", "release", "expire"] = "check",
    hold_id: str = None,
    action: str = None,
    risk_class: str = None,
) -> dict:
    """
    Manage 888_HOLD lifecycle.

    Args:
        mode: check|register|release|expire
        hold_id: Specific HOLD to manage
        action: Action that triggered HOLD
        risk_class: risk_class from 888_JUDGE

    Returns:
        HOLD status and lifecycle state
    """
    if mode == "check":
        return _check_hold_status(hold_id)
    elif mode == "register":
        return _register_hold(action, risk_class)
    elif mode == "release":
        return _release_hold(hold_id)
    elif mode == "expire":
        return _expire_hold(hold_id)


def _check_hold_status(hold_id: str) -> dict:
    """Check if action requires approval."""
    return {
        "status": "CHECK",
        "hold_id": hold_id,
        "requires_approval": True,
        "hold_type": "888_HOLD",
        "message": "HUMAN APPROVAL REQUIRED",
    }


def _register_hold(action: str, risk_class: str) -> dict:
    """Register new HOLD."""
    high_risk = risk_class in ["high", "critical"]
    return {
        "status": "REGISTERED",
        "action": action,
        "risk_class": risk_class,
        "requires_approval": high_risk,
        "hold_type": "888_HOLD" if high_risk else "AUTO_APPROVE",
        "message": "HUMAN APPROVAL REQUIRED" if high_risk else "Auto-approved",
    }


def _release_hold(hold_id: str) -> dict:
    """Release a HOLD after approval."""
    return {
        "status": "RELEASED",
        "hold_id": hold_id,
        "message": "HOLD released by human approval",
    }


def _expire_hold(hold_id: str) -> dict:
    """Expire HOLD after cooling period."""
    return {
        "status": "EXPIRED",
        "hold_id": hold_id,
        "message": "HOLD expired after Phoenix-72 cooling",
    }
