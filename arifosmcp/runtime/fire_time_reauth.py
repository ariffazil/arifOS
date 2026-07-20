"""
fire_time_reauth.py — WAJIB 5: Fire-Time Reauthorization (2026-07-19)
══════════════════════════════════════════════════════════════════════

Every deferred action must be re-judged at fire time, not just at
write time. Covers cron, queues, retries, Renovate, and long-running tasks.

reauthorize_at_fire() pattern per WAJIB 5 / FORGE-incident-triage SKILL.md.
5 required fire-time checks.

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReauthVerdict(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    VOID = "VOID"  # Authority revoked — action must be cancelled


@dataclass
class DeferredAction:
    """A queued/scheduled action that needs fire-time reauthorization."""

    action_id: str
    action_type: str  # cron, queue, retry, renovate, long_running
    queued_at: float
    fire_at: float
    original_authority: str
    original_session_id: str
    original_lease_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReauthResult:
    """Result of fire-time reauthorization check."""

    verdict: ReauthVerdict
    action_id: str
    reason: str = ""
    current_authority: str = "OBSERVE_ONLY"
    checked_at: float = field(default_factory=time.time)


def reauthorize_at_fire(
    action: DeferredAction,
    current_session_valid: bool = True,
    current_authority: str = "OBSERVE_ONLY",
    organ_healthy: bool = True,
    no_intervening_hold: bool = True,
    freshness_ok: bool = True,
) -> ReauthResult:
    """Execute the 5 WAJIB 5 fire-time reauthorization checks.

    Returns PROCEED only if ALL 5 checks pass.
    Any single check failure → HOLD or VOID.
    """
    failures: list[str] = []

    # Check 1: Session still valid at fire time?
    if not current_session_valid:
        failures.append("F1: Session expired or revoked since queuing")

    # Check 2: Authority not degraded since write time?
    if current_authority != action.original_authority:
        failures.append(
            f"F2: Authority degraded: was {action.original_authority}, now {current_authority}"
        )

    # Check 3: Target organ healthy?
    if not organ_healthy:
        failures.append("F3: Target organ is degraded or unhealthy")

    # Check 4: No intervening HOLD/VOID on this session?
    if not no_intervening_hold:
        failures.append("F4: Intervening HOLD or VOID on session")

    # Check 5: Fire-time freshness (action not stale)?
    age = time.time() - action.queued_at
    max_age = action.fire_at - action.queued_at + 300  # 5 min grace
    if not freshness_ok or age > max_age * 2:
        failures.append(f"F5: Action stale — queued {age:.0f}s ago")

    # ── Compute verdict ──────────────────────────────────────────
    if not failures:
        return ReauthResult(
            verdict=ReauthVerdict.PROCEED,
            action_id=action.action_id,
            current_authority=current_authority,
            reason="All 5 fire-time checks passed.",
        )

    # Authority revoked → VOID (action must be cancelled)
    authority_revoked = any("authority" in f.lower() and "degraded" in f.lower() for f in failures)

    if authority_revoked:
        return ReauthResult(
            verdict=ReauthVerdict.VOID,
            action_id=action.action_id,
            current_authority=current_authority,
            reason=f"Authority revoked: {'; '.join(failures)}",
        )

    return ReauthResult(
        verdict=ReauthVerdict.HOLD,
        action_id=action.action_id,
        current_authority=current_authority,
        reason=f"Fire-time checks failed: {'; '.join(failures)}",
    )
