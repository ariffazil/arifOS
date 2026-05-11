"""
skills/well/readiness.py — Biological Readiness Check

Readiness logic ported from arifosmcp/runtime/well_bridge.py
(get_biological_readiness) and arifosmcp/tools_canonical.py
(arifos_oracle_bio[readiness_check]).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

WELL_STATE_PATH = Path(os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))


def readiness_check() -> dict[str, Any]:
    """Evaluate biological readiness from WELL state."""
    try:
        _exists = WELL_STATE_PATH.exists()
    except (PermissionError, OSError):
        _exists = False

    if not _exists:
        return {
            "ok": False,
            "verdict": "UNKNOWN",
            "well_score": 50.0,
            "bandwidth": "NORMAL",
            "message": "WELL substrate offline or state missing.",
            "sabar_advisory": False,
        }

    try:
        with open(WELL_STATE_PATH, "r") as f:
            state = json.load(f)

        score = state.get("well_score", 50.0)
        violations = state.get("floors_violated", [])

        if violations:
            verdict = "DEGRADED"
            bandwidth = "RESTRICTED"
            sabar_advisory = True
        elif score >= 80:
            verdict = "OPTIMAL"
            bandwidth = "FULL"
            sabar_advisory = False
        elif score >= 60:
            verdict = "FUNCTIONAL"
            bandwidth = "NORMAL"
            sabar_advisory = False
        else:
            verdict = "LOW_CAPACITY"
            bandwidth = "REDUCED"
            sabar_advisory = True

        return {
            "ok": True,
            "verdict": verdict,
            "well_score": score,
            "bandwidth": bandwidth,
            "violations": violations,
            "sabar_advisory": sabar_advisory,
            "timestamp": state.get("timestamp"),
        }
    except Exception as e:
        return {
            "ok": False,
            "verdict": "ERROR",
            "error": str(e),
            "well_score": 0.0,
            "bandwidth": "RESTRICTED",
            "sabar_advisory": True,
        }
