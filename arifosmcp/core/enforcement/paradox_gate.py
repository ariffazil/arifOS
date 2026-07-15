"""
Paradox Gate — Bridge between arifOS kernel and ATLAS-333 paradox geometry.

Two modes:
  1. LEGACY: Reads /tmp/paradox_engine_state.json (deprecated paradox_engine.py)
  2. GPV-NATIVE: Accepts GPV directly, uses paradox_axes for routing (ATLAS333 Bridge §4)

Wired into arif_judge at the SOMATIC gate boundary.
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
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from core.shared.types import GPV


# State file written by A-FORGE paradox engine, read by arifOS kernel.
# LEGACY — prefer GPV-native mode. This is the cross-organ wiring surface.
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
            flags.append(
                ParadoxFlag(
                    paradox_id=pid,
                    motif_a=a_label,
                    motif_b=b_label,
                    tension=tension,
                    flag="RESOLUTION_RISK",
                    detail=f"Output favors '{a_label}' ({a_mentions}x) over '{b_label}' (0x). "
                    f"Tension={tension:.2f}. Consider acknowledging both.",
                )
            )
        elif b_mentions > 0 and a_mentions == 0 and tension > 0.3:
            flags.append(
                ParadoxFlag(
                    paradox_id=pid,
                    motif_a=a_label,
                    motif_b=b_label,
                    tension=tension,
                    flag="RESOLUTION_RISK",
                    detail=f"Output favors '{b_label}' ({b_mentions}x) over '{a_label}' (0x). "
                    f"Tension={tension:.2f}. Consider acknowledging both.",
                )
            )

        # Check for matured paradoxes (emergence candidates)
        if pdata.get("matured"):
            flags.append(
                ParadoxFlag(
                    paradox_id=pid,
                    motif_a=a_label,
                    motif_b=b_label,
                    tension=tension,
                    flag="PARADOX_MATURED",
                    detail=f"Paradox sustained long enough. "
                    f"Transformation: {pdata.get('transformation', 'unknown')}. "
                    f"Consider emergence, not resolution.",
                )
            )

    return flags


def _try_create_gpv(output_text: str) -> Any | None:
    """Attempt to create a GPV from output text (ATLAS333-native).

    Falls back to None if Φ() or GPV is not importable (circular import guard).
    This is the bridge from legacy /tmp path to GPV-native routing.
    """
    try:
        from core.shared.atlas import Φ

        return Φ(output_text)
    except (ImportError, Exception):
        return None


def evaluate_paradox_gate(
    output_text: str = "",
    evidence: Optional[dict] = None,
) -> ParadoxGateResult:
    """
    Evaluate the paradox gate before arif_judge deliberation.

    Called from judge.py AFTER the somatic state gate.
    PREFERS GPV-native mode (ATLAS333 Bridge §4) — creates a GPV from
    the output text and routes through evaluate_paradox_gate_gpv().

    Falls back to legacy /tmp/paradox_engine_state.json path only if
    GPV creation fails (import guard for circular deps).

    This is a FLAG, not a BLOCK. (F5 PEACE: de-escalate, don't choke.)

    Args:
        output_text: The candidate output being judged
        evidence: Current evidence dict from arif_judge

    Returns:
        ParadoxGateResult with flags and verdict
    """
    # ATLAS333-native path: try creating GPV from output text
    _gpv = _try_create_gpv(output_text)
    if _gpv is not None:
        # Determine action_class from evidence if available
        _action_class = None
        if evidence:
            _mode = evidence.get("mode", "")
            _tier = evidence.get("action_tier", "")
            if _mode in ("seal", "irreversible") or _tier == "sovereign":
                _action_class = "SEAL"
            elif _mode in ("mutate", "forge", "write", "commit"):
                _action_class = "MUTATE"

        return evaluate_paradox_gate_gpv(
            gpv=_gpv,
            output_text=output_text,
            action_class=_action_class,
        )

    # LEGACY FALLBACK: read from /tmp/paradox_engine_state.json
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
        verdict = "FLAGGED"
    elif matured:
        verdict = "FLAGGED"
    else:
        verdict = "PASS"

    return ParadoxGateResult(
        active_paradoxes=len(active),
        paradox_score=score,
        flags=flags,
        gate_verdict=verdict,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GPV-NATIVE MODE — ATLAS333 Bridge §4
# ═══════════════════════════════════════════════════════════════════════════════
# Uses GPV.paradox_axes (resolved by atlas.py's PARADOX_GPV_MAP) instead of
# reading from /tmp. Stateless, no file I/O, no deprecated engine dependency.


# Zone → paradox ID mapping (from 333_MIND_ATLAS.md §1)
_ZONE_MAP: dict[str, list[int]] = {
    "TRUTH": [1, 2, 3, 4, 5],
    "GOVERNANCE": [6, 7, 8, 9, 10],
    "AGENT": [11, 12, 13, 14, 15],
    "GROWTH": [16, 17, 18, 19, 20],
    "CONNECTION": [21, 22, 23, 24, 25],
    "SYSTEM": [26, 27, 28, 29, 30],
    "WITNESS": [31, 32, 33],
}


def _paradox_ids_to_zones(paradox_ids: list[int]) -> dict[str, list[int]]:
    """Map paradox IDs to their zones."""
    zones: dict[str, list[int]] = {}
    for zone_name, zone_ids in _ZONE_MAP.items():
        active_in_zone = [pid for pid in paradox_ids if pid in zone_ids]
        if active_in_zone:
            zones[zone_name] = active_in_zone
    return zones


def evaluate_paradox_gate_gpv(
    gpv: Any,
    output_text: str = "",
    action_class: str | None = None,
) -> ParadoxGateResult:
    """Evaluate paradox gate using GPV state (ATLAS333-native).

    This is the GPV-native replacement for evaluate_paradox_gate().
    Uses GPV.paradox_axes instead of reading /tmp/paradox_engine_state.json.

    Args:
        gpv: GPV object with paradox_axes field (from atlas.py Φ function)
        output_text: The candidate output being judged
        action_class: Optional action class ("SEAL", "MUTATE", "READ")

    Returns:
        ParadoxGateResult with flags and verdict
    """
    paradox_ids = list(gpv.paradox_axes) if gpv.paradox_axes else []

    # Action-class gates (from bridge map §3 — not in GPV, added at judge time)
    if action_class == "SEAL":
        # Zone VII mandatory for irreversible actions
        for pid in [31, 32, 33]:
            if pid not in paradox_ids:
                paradox_ids.append(pid)
    elif action_class == "MUTATE":
        # Zone VI check for any mutation
        for pid in [26, 27, 28, 29, 30]:
            if pid not in paradox_ids:
                paradox_ids.append(pid)

    if not paradox_ids:
        return ParadoxGateResult(
            active_paradoxes=0,
            paradox_score=0.0,
            flags=[],
            gate_verdict="PASS",
        )

    # Compute paradox score from active zones
    zones = _paradox_ids_to_zones(paradox_ids)
    # Score: more zones active = higher tension
    paradox_score = min(1.0, len(zones) * 0.15)

    # Check for resolution risks in output text
    flags: list[ParadoxFlag] = []
    output_lower = output_text.lower() if output_text else ""

    if output_lower:
        # Import quote map for resolution risk checking
        try:
            from constitution.paradox_quotes import PARADOX_QUOTE_MAP, ALL_PARADOX_QUOTES

            for pid in paradox_ids:
                quote_ids = PARADOX_QUOTE_MAP.get(pid, [])
                if len(quote_ids) < 2:
                    continue  # Need at least 2 quotes to check resolution bias

                # Check if output favors one pole over the other
                q_a = ALL_PARADOX_QUOTES.get(quote_ids[0])
                q_b = ALL_PARADOX_QUOTES.get(quote_ids[1]) if len(quote_ids) > 1 else None

                if not q_a or not q_b:
                    continue

                # Simple heuristic: check if output mentions one axis pole more
                axis_words_a = set(q_a.axis_label.split(" vs. ")[0].lower().split())
                axis_words_b = (
                    set(q_a.axis_label.split(" vs. ")[1].lower().split())
                    if " vs. " in q_a.axis_label
                    else set()
                )

                a_hits = sum(1 for w in axis_words_a if w in output_lower)
                b_hits = sum(1 for w in axis_words_b if w in output_lower)

                if a_hits > 0 and b_hits == 0 and paradox_score > 0.3:
                    flags.append(
                        ParadoxFlag(
                            paradox_id=str(pid),
                            motif_a=q_a.axis_label.split(" vs. ")[0]
                            if " vs. " in q_a.axis_label
                            else q_a.axis_label,
                            motif_b=q_a.axis_label.split(" vs. ")[1]
                            if " vs. " in q_a.axis_label
                            else "",
                            tension=paradox_score,
                            flag="RESOLUTION_RISK",
                            detail=f"Output favors '{q_a.axis_label.split(' vs. ')[0]}' pole. "
                            f"Paradox #{pid} active. Consider acknowledging both poles.",
                        )
                    )
                elif b_hits > 0 and a_hits == 0 and paradox_score > 0.3:
                    flags.append(
                        ParadoxFlag(
                            paradox_id=str(pid),
                            motif_a=q_a.axis_label.split(" vs. ")[0]
                            if " vs. " in q_a.axis_label
                            else q_a.axis_label,
                            motif_b=q_a.axis_label.split(" vs. ")[1]
                            if " vs. " in q_a.axis_label
                            else "",
                            tension=paradox_score,
                            flag="RESOLUTION_RISK",
                            detail=f"Output favors '{q_a.axis_label.split(' vs. ')[1]}' pole. "
                            f"Paradox #{pid} active. Consider acknowledging both poles.",
                        )
                    )
        except ImportError:
            # If paradox_quotes not available, skip resolution risk check
            pass

    # Determine verdict
    resolution_risks = [f for f in flags if f.flag == "RESOLUTION_RISK"]

    if resolution_risks and paradox_score > 0.5:
        verdict = "FLAGGED"
    elif len(zones) >= 4:
        # Many zones active = high tension, flag even without resolution risk
        verdict = "FLAGGED"
    else:
        verdict = "PASS"

    return ParadoxGateResult(
        active_paradoxes=len(paradox_ids),
        paradox_score=paradox_score,
        flags=flags,
        gate_verdict=verdict,
    )
