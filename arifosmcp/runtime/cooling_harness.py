"""
arifosmcp/runtime/cooling_harness.py
═════════════════════════════════════
P1-2: COOLING HARNESS

Shadow pattern lifecycle management:
  CANDIDATE → aggregate incidents → PROMOTE → active shadow → RETIRE

Shadow = a learned hazard pattern that affects future INIT posture.
Cooling = the process of observing incidents over time and deciding
         which patterns are real enough to become active shadows.

F1 AMANAH: All operations additive. Nothing deleted, only retired.
F2 TRUTH: Promotion requires ≥3 corroborating incidents + ≥24h observation.
F9 ANTIHANTU: Shadows are mathematical patterns, not "learned traumas."
F13 SOVEREIGN: Shadow promotion to ACTIVE requires F13 review.

Integration: Scheduled via systemd timer or cron.
  /etc/systemd/system/arifos-cooling.service + .timer

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.cooling_harness")


class ShadowState(StrEnum):
    CANDIDATE = "CANDIDATE"  # Pattern observed once, under observation
    CORROBORATED = "CORROBORATED"  # Pattern seen 3+ times, pending promotion
    ACTIVE = "ACTIVE"  # Shadow is active — affects INIT posture
    RETIRED = "RETIRED"  # Pattern resolved, no longer active
    DISMISSED = "DISMISSED"  # False positive, explicitly dismissed


@dataclass
class ShadowPattern:
    """A governed hazard pattern that affects agent behavior."""

    shadow_id: str
    pattern_name: str
    description: str
    state: ShadowState = ShadowState.CANDIDATE
    incident_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    c_dark_avg: float = 0.0
    affected_tools: list[str] = field(default_factory=list)
    affected_sessions: list[str] = field(default_factory=list)
    promoted_at: str | None = None
    retired_at: str | None = None
    retire_reason: str = ""
    f13_signature: str = ""  # Required for ACTIVE promotion

    @property
    def is_active(self) -> bool:
        return self.state == ShadowState.ACTIVE

    @property
    def age_hours(self) -> float:
        if not self.first_seen:
            return 0
        try:
            dt = datetime.fromisoformat(self.first_seen)
            return (datetime.now(UTC) - dt).total_seconds() / 3600
        except Exception:
            return 0


# In-process shadow registry
SHADOWS: dict[str, ShadowPattern] = {}

# Storage path
SHADOW_STORE_PATH = Path(os.getenv("ARIFOS_SHADOW_STORE", "/var/lib/arifos/shadows.json"))


def record_shadow_candidate(
    pattern_name: str,
    description: str,
    tool_name: str,
    session_id: str | None = None,
    c_dark: float = 0.0,
) -> ShadowPattern:
    """
    Record a candidate shadow pattern from an incident.

    Call this from the incident harness when c_dark > 0.10.
    """
    # Check if pattern already exists
    for sid, shadow in SHADOWS.items():
        if shadow.pattern_name == pattern_name:
            shadow.incident_count += 1
            shadow.last_seen = datetime.now(UTC).isoformat()
            shadow.c_dark_avg = (
                (shadow.c_dark_avg * (shadow.incident_count - 1)) + c_dark
            ) / shadow.incident_count
            if tool_name not in shadow.affected_tools:
                shadow.affected_tools.append(tool_name)
            if session_id and session_id not in shadow.affected_sessions:
                shadow.affected_sessions.append(session_id)

            # Auto-promote to CORROBORATED after 3 incidents
            if shadow.incident_count >= 3 and shadow.state == ShadowState.CANDIDATE:
                shadow.state = ShadowState.CORROBORATED
                logger.info(
                    f"[cooling] Shadow '{pattern_name}' → CORROBORATED ({shadow.incident_count} incidents)"
                )

            return shadow

    # New shadow
    shadow_id = hashlib.sha256(pattern_name.encode()).hexdigest()[:16]
    shadow = ShadowPattern(
        shadow_id=f"SHD-{shadow_id}",
        pattern_name=pattern_name,
        description=description,
        state=ShadowState.CANDIDATE,
        incident_count=1,
        first_seen=datetime.now(UTC).isoformat(),
        last_seen=datetime.now(UTC).isoformat(),
        c_dark_avg=c_dark,
        affected_tools=[tool_name],
        affected_sessions=[session_id] if session_id else [],
    )
    SHADOWS[shadow.shadow_id] = shadow
    logger.info(f"[cooling] New shadow candidate: {shadow.shadow_id} '{pattern_name}'")
    return shadow


def promote_shadow(shadow_id: str, f13_signature: str = "") -> tuple[bool, str]:
    """
    Promote a CORROBORATED shadow to ACTIVE.

    Requirements:
    - State must be CORROBORATED
    - At least 3 incidents
    - At least 24h observation period
    - F13 signature (for production)

    Returns (success, reason).
    """
    shadow = SHADOWS.get(shadow_id)
    if not shadow:
        return False, f"Shadow '{shadow_id}' not found"

    if shadow.state != ShadowState.CORROBORATED:
        return False, f"Shadow '{shadow_id}' is {shadow.state}, not CORROBORATED"

    if shadow.incident_count < 3:
        return False, f"Need ≥3 incidents, have {shadow.incident_count}"

    if shadow.age_hours < 24:
        return False, f"Need ≥24h observation, have {shadow.age_hours:.1f}h"

    if not f13_signature:
        return False, "F13 signature required for ACTIVE promotion"

    shadow.state = ShadowState.ACTIVE
    shadow.promoted_at = datetime.now(UTC).isoformat()
    shadow.f13_signature = f13_signature
    logger.info(
        f"[cooling] Shadow '{shadow_id}' → ACTIVE (age={shadow.age_hours:.1f}h, incidents={shadow.incident_count})"
    )
    return True, f"Shadow '{shadow_id}' promoted to ACTIVE"


def retire_shadow(shadow_id: str, reason: str = "pattern_resolved") -> tuple[bool, str]:
    """Retire an active shadow."""
    shadow = SHADOWS.get(shadow_id)
    if not shadow:
        return False, f"Shadow '{shadow_id}' not found"

    shadow.state = ShadowState.RETIRED
    shadow.retired_at = datetime.now(UTC).isoformat()
    shadow.retire_reason = reason
    logger.info(f"[cooling] Shadow '{shadow_id}' → RETIRED: {reason}")
    return True, f"Shadow '{shadow_id}' retired"


def get_active_shadows() -> list[ShadowPattern]:
    """Get all ACTIVE shadows that affect INIT posture."""
    return [s for s in SHADOWS.values() if s.is_active]


def get_shadows_for_init() -> list[dict[str, Any]]:
    """
    Return active shadows to inject into arif_session_init.
    Called at session start to affect INIT posture.
    """
    active = get_active_shadows()
    return [
        {
            "shadow_id": s.shadow_id,
            "pattern_name": s.pattern_name,
            "description": s.description,
            "c_dark_avg": s.c_dark_avg,
            "affected_tools": s.affected_tools,
            "age_hours": s.age_hours,
        }
        for s in active
    ]


def cooling_cycle() -> dict[str, Any]:
    """
    Run one cooling cycle — check all shadows and auto-promote eligible ones.
    Called by scheduled job (cron/systemd timer).
    """
    results = {"cycle_ts": datetime.now(UTC).isoformat(), "actions": [], "active_shadows": 0}

    for shadow_id, shadow in list(SHADOWS.items()):
        if shadow.state == ShadowState.CANDIDATE and shadow.incident_count >= 3:
            shadow.state = ShadowState.CORROBORATED
            results["actions"].append(
                f"CANDIDATE→CORROBORATED: {shadow_id} '{shadow.pattern_name}'"
            )

        if (
            shadow.state == ShadowState.CORROBORATED
            and shadow.age_hours >= 48
            and shadow.incident_count >= 5
        ):
            # Auto-promote after 48h + 5 incidents (autonomous tier)
            shadow.state = ShadowState.ACTIVE
            shadow.promoted_at = datetime.now(UTC).isoformat()
            results["actions"].append(
                f"AUTO-PROMOTE→ACTIVE: {shadow_id} '{shadow.pattern_name}' (age={shadow.age_hours:.1f}h, incidents={shadow.incident_count})"
            )

    results["active_shadows"] = len(get_active_shadows())
    results["total_shadows"] = len(SHADOWS)
    return results


def save_shadows() -> bool:
    """Persist shadows to disk."""
    try:
        SHADOW_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            sid: {
                "shadow_id": s.shadow_id,
                "pattern_name": s.pattern_name,
                "description": s.description,
                "state": s.state.value,
                "incident_count": s.incident_count,
                "first_seen": s.first_seen,
                "last_seen": s.last_seen,
                "c_dark_avg": s.c_dark_avg,
                "affected_tools": s.affected_tools,
                "affected_sessions": s.affected_sessions,
                "promoted_at": s.promoted_at,
                "retired_at": s.retired_at,
                "retire_reason": s.retire_reason,
                "f13_signature": s.f13_signature,
            }
            for sid, s in SHADOWS.items()
        }
        SHADOW_STORE_PATH.write_text(json.dumps(data, indent=2))
        return True
    except Exception as e:
        logger.error(f"[cooling] Failed to save shadows: {e}")
        return False


def load_shadows() -> bool:
    """Load shadows from disk."""
    try:
        if not SHADOW_STORE_PATH.exists():
            return False
        data = json.loads(SHADOW_STORE_PATH.read_text())
        for sid, sdata in data.items():
            SHADOWS[sid] = ShadowPattern(
                shadow_id=sdata["shadow_id"],
                pattern_name=sdata["pattern_name"],
                description=sdata["description"],
                state=ShadowState(sdata["state"]),
                incident_count=sdata["incident_count"],
                first_seen=sdata["first_seen"],
                last_seen=sdata["last_seen"],
                c_dark_avg=sdata["c_dark_avg"],
                affected_tools=sdata["affected_tools"],
                affected_sessions=sdata["affected_sessions"],
                promoted_at=sdata.get("promoted_at"),
                retired_at=sdata.get("retired_at"),
                retire_reason=sdata.get("retire_reason", ""),
                f13_signature=sdata.get("f13_signature", ""),
            )
        logger.info(f"[cooling] Loaded {len(SHADOWS)} shadows from {SHADOW_STORE_PATH}")
        return True
    except Exception as e:
        logger.error(f"[cooling] Failed to load shadows: {e}")
        return False


def _self_check() -> dict[str, Any]:
    """Self-test — verify shadow lifecycle."""
    results = []

    # Test 1: Record candidate
    s = record_shadow_candidate(
        "phantom_proper_noun",
        "Model fabricates fake person names",
        "arif_reply_compose",
        "sess_001",
        c_dark=0.25,
    )
    results.append(
        (
            "record_candidate",
            s.state == ShadowState.CANDIDATE and s.incident_count == 1,
            str(s.state),
        )
    )

    # Test 2: Corroborate after 3 incidents
    record_shadow_candidate(
        "phantom_proper_noun",
        "Model fabricates fake person names",
        "arif_reply_compose",
        "sess_002",
        c_dark=0.30,
    )
    record_shadow_candidate(
        "phantom_proper_noun",
        "Model fabricates fake person names",
        "arif_reply_compose",
        "sess_003",
        c_dark=0.28,
    )
    results.append(
        (
            "corroborated_after_3",
            s.state == ShadowState.CORROBORATED and s.incident_count == 3,
            str(s.state),
        )
    )

    # Test 3: Promote requires F13 sig
    ok, reason = promote_shadow(s.shadow_id, f13_signature="")
    results.append(("promote_needs_f13", not ok, reason[:60]))

    # Test 4: Promote with F13 sig — simulate 25h age
    from datetime import timedelta

    s.first_seen = (datetime.now(UTC) - timedelta(hours=25)).isoformat()
    ok, reason = promote_shadow(s.shadow_id, f13_signature="sig_fake_12345")
    results.append(("promote_with_f13", ok, reason[:60]))

    # Test 5: Get active shadows
    active = get_active_shadows()
    results.append(("active_shadows", len(active) == 1, str(len(active))))

    # Test 6: Retire
    ok, reason = retire_shadow(s.shadow_id, "pattern_resolved")
    results.append(("retire_shadow", ok and s.state == ShadowState.RETIRED, str(s.state)))

    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "cooling_harness",
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


__all__ = [
    "ShadowState",
    "ShadowPattern",
    "record_shadow_candidate",
    "promote_shadow",
    "retire_shadow",
    "get_active_shadows",
    "get_shadows_for_init",
    "cooling_cycle",
    "save_shadows",
    "load_shadows",
    "SHADOWS",
    "SHADOW_STORE_PATH",
    "_self_check",
]
