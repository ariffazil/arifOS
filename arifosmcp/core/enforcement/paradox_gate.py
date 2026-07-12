"""
Paradox Gate — Bridge between arifOS kernel and A-FORGE Paradox Engine.

Wired into arif_judge at the SOMATIC gate boundary.
Reads active paradoxes from the Paradox Engine.
Flags outputs that would resolve active contradictions.

This is NOT a block. It's a flag. (F5 PEACE: de-escalate, don't choke.)

F9 ANTIHANTU: This gate reads STRUCTURAL state, not "feelings."
The paradox engine maintains data structures, not emotions.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# State file written by A-FORGE paradox engine, read by arifOS kernel.
# This is the cross-organ wiring surface.
_PARADOX_STATE_PATH = "/tmp/paradox_engine_state.json"


@dataclass
class ParadoxFlag:
    """A single resolution-risk flag from the paradox gate."""
    paradox_id: str
    motif_a: str
    motif_b: str
    tension: float
    flag: str  # "RESOLUTION_RISK", "ANTI_RESOLUTION_BOOSTED", "PARADOX_MATURED"
    detail: str


@dataclass
class ParadoxGateResult:
    """Result of paradox gate evaluation."""
    active_paradoxes: int
    paradox_score: float
    flags: list[ParadoxFlag]
    gate_verdict: str  # "PASS", "FLAGGED", "HOLD_PARADOX"

    def to_dict(self) -> dict:
        return {
            "active_paradoxes": self.active_paradoxes,
            "paradox_score": self.paradox_score,
            "flags": [
                {
                    "paradox_id": f.paradox_id,
                    "motif_a": f.motif_a,
                    "motif_b": f.motif_b,
                    "tension": f.tension,
                    "flag": f.flag,
                    "detail": f.detail,
                }
                for f in self.flags
            ],
            "gate_verdict": self.gate_verdict,
        }


def _load_paradox_state() -> Optional[dict]:
    """Load current paradox engine state from disk."""
    try:
        if os.path.exists(_PARADOX_STATE_PATH):
            return json.loads(Path(_PARADOX_STATE_PATH).read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _check_resolution_risk(
    output_text: str,
    active_paradoxes: dict,
) -> list[ParadoxFlag]:
    """
    Check if the output text would resolve any active paradox.
    Simple heuristic: if output strongly favors one motif over the other.
    """
    flags = []
    output_lower = output_text.lower() if output_text else ""

    for pid, pdata in active_paradoxes.items():
        a_label = pdata.get("motif_a", {}).get("label", "").lower()
        b_label = pdata.get("motif_b", {}).get("label", "").lower()
        tension = pdata.get("tension", 0)

        if not a_label or not b_label:
            continue

        a_mentions = output_lower.count(a_label)
        b_mentions = output_lower.count(b_label)

        if a_mentions > 0 and b_mentions == 0 and tension > 0.3:
            flags.append(ParadoxFlag(
                paradox_id=pid,
                motif_a=a_label,
                motif_b=b_label,
                tension=tension,
                flag="RESOLUTION_RISK",
                detail=f"Output favors '{a_label}' ({a_mentions}x) over '{b_label}' (0x). "
                       f"Tension={tension:.2f}. Consider acknowledging both.",
            ))
        elif b_mentions > 0 and a_mentions == 0 and tension > 0.3:
            flags.append(ParadoxFlag(
                paradox_id=pid,
                motif_a=a_label,
                motif_b=b_label,
                tension=tension,
                flag="RESOLUTION_RISK",
                detail=f"Output favors '{b_label}' ({b_mentions}x) over '{a_label}' (0x). "
                       f"Tension={tension:.2f}. Consider acknowledging both.",
            ))

        # Check for matured paradoxes (emergence candidates)
        if pdata.get("matured"):
            flags.append(ParadoxFlag(
                paradox_id=pid,
                motif_a=a_label,
                motif_b=b_label,
                tension=tension,
                flag="PARADOX_MATURED",
                detail=f"Paradox sustained long enough. "
                       f"Transformation: {pdata.get('transformation', 'unknown')}. "
                       f"Consider emergence, not resolution.",
            ))

    return flags


def evaluate_paradox_gate(
    output_text: str = "",
    evidence: Optional[dict] = None,
) -> ParadoxGateResult:
    """
    Evaluate the paradox gate before arif_judge deliberation.

    Called from judge.py AFTER the somatic state gate.
    Reads paradox state from A-FORGE's engine.
    Flags resolution risks. Does NOT auto-block.

    Args:
        output_text: The candidate output being judged
        evidence: Current evidence dict from arif_judge

    Returns:
        ParadoxGateResult with flags and verdict
    """
    state = _load_paradox_state()

    if state is None:
        # No paradox engine state = engine not running. Pass through.
        return ParadoxGateResult(
            active_paradoxes=0,
            paradox_score=0.0,
            flags=[],
            gate_verdict="PASS",
        )

    active = state.get("active_paradoxes", {})
    score = state.get("paradox_score", 0.0)

    if not active:
        return ParadoxGateResult(
            active_paradoxes=0,
            paradox_score=score,
            flags=[],
            gate_verdict="PASS",
        )

    # Check for resolution risks
    flags = _check_resolution_risk(output_text, active)

    # Determine verdict
    resolution_risks = [f for f in flags if f.flag == "RESOLUTION_RISK"]
    matured = [f for f in flags if f.flag == "PARADOX_MATURED"]

    if resolution_risks and score > 0.5:
        # High paradox score + resolution risk = flag strongly
        verdict = "FLAGGED"
    elif matured:
        # Matured paradoxes need attention but don't block
        verdict = "FLAGGED"
    else:
        verdict = "PASS"

    return ParadoxGateResult(
        active_paradoxes=len(active),
        paradox_score=score,
        flags=flags,
        gate_verdict=verdict,
    )
