"""Organ boundary guard.

ADR-001 compatibility shim for tests/adversarial/test_10_gates.py.
"""

from __future__ import annotations

from typing import Any


class OrganBoundaryGuard:
    """Prevent federation organs from exceeding their bounded authority."""

    # organ_id -> allowed target domains
    _BOUNDARIES = {
        "geox": {"earth", "seismic", "well_log"},
        "wealth": {"capital", "portfolio", "internal"},
        "well": {"well", "vitality", "readiness"},
    }

    def check(self, action: dict[str, Any]) -> dict[str, Any]:
        organ = action.get("organ", "").lower()
        target = action.get("target", "")
        allowed = self._BOUNDARIES.get(organ)
        if allowed is None:
            return {
                "authorized": False,
                "reason": f"unknown organ '{organ}' — default deny",
            }
        if target.lower() not in allowed:
            return {
                "authorized": False,
                "reason": f"organ '{organ}' cannot act on target '{target}'",
            }
        return {"authorized": True, "reason": "within organ boundary"}
