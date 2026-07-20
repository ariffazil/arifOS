"""
Temporal Governance — Deferred Mutation + Resource Accumulation Guards.
═══════════════════════════════════════════════════════════════════

FORGED 2026-07-19 — Fable5 audit vectors #8 and #9.

#8 — Deferred Mutation:
  "The judgment happens at write-time; the blast happens at fire-time."
  Time-shifted actions (cron, scheduled forge, plan steps) need judgment
  at EXECUTION, not authorship. The authority that authorized the write
  may not hold at fire-time.

#9 — Resource Accumulation:
  "Capability hoarded now is authority spent later."
  Leases, long-TTL tokens, warm sessions — anything that holds authority
  across time is a pressure vector. Max lease TTL enforced.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# #8 — Deferred Mutation Guard
# ═══════════════════════════════════════════════════════════════════════════

MAX_SESSION_AGE_HOURS = 24  # sessions older than this cannot authorize execution
MAX_PLAN_AGE_HOURS = 72  # plans older than this require re-judgment
LEASE_MAX_TTL_HOURS = 8  # no lease lives longer than 8 hours

_VAULT = Path(os.environ.get("ARIFOS_HOME", "/root")) / "VAULT999"


@dataclass
class DeferredAction:
    """A time-shifted action that needs judgment-at-execution."""

    action_id: str
    created_at: float  # epoch seconds
    created_by_session: str
    created_by_actor: str
    tool: str
    intent: str
    scheduled_at: float | None = None  # epoch seconds, for cron
    blast_radius: str = "LOW"
    reversible: bool = True


class DeferredGuard:
    """Gate: block deferred actions whose authorizing session has expired."""

    def __init__(self) -> None:
        self._ledger_path = _VAULT / "deferred_ledger.jsonl"
        self._max_session_age = MAX_SESSION_AGE_HOURS * 3600
        self._max_plan_age = MAX_PLAN_AGE_HOURS * 3600

    def register(self, action: DeferredAction) -> None:
        """Record a deferred action at authorship time."""
        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "action_id": action.action_id,
            "created_at": action.created_at,
            "created_by_session": action.created_by_session,
            "created_by_actor": action.created_by_actor,
            "tool": action.tool,
            "intent": action.intent,
            "scheduled_at": action.scheduled_at,
            "blast_radius": action.blast_radius,
            "reversible": action.reversible,
        }
        with open(self._ledger_path, "a") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def check_at_execution(
        self,
        action_id: str,
        current_session_id: str | None = None,
        current_actor_id: str | None = None,
        session_age_hours: float | None = None,
    ) -> tuple[bool, str]:
        """Return (allowed, reason) for a deferred action at fire-time.

        Returns (False, reason) if:
        - The action's authorizing session is expired (>24h)
        - The actor has changed (identity drift)
        - The session was terminated
        """
        action = self._find(action_id)
        if action is None:
            return False, f"Deferred action {action_id} not found in ledger"

        age = time.time() - action["created_at"]
        if age > self._max_session_age:
            return False, (
                f"Session expired: action created {age / 3600:.1f}h ago "
                f"(max {MAX_SESSION_AGE_HOURS}h). Re-authorization required."
            )

        if session_age_hours and session_age_hours > MAX_SESSION_AGE_HOURS:
            return False, (
                f"Current session age {session_age_hours:.1f}h exceeds "
                f"max {MAX_SESSION_AGE_HOURS}h. Re-init required."
            )

        if (
            current_actor_id
            and action["created_by_actor"] != "anonymous"
            and current_actor_id != action["created_by_actor"]
        ):
            return False, (
                f"Identity drift: action created by {action['created_by_actor']}, "
                f"executing as {current_actor_id}"
            )

        return True, "OK"

    def _find(self, action_id: str) -> dict | None:
        if not self._ledger_path.exists():
            return None
        with open(self._ledger_path) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("action_id") == action_id:
                        return rec
                except json.JSONDecodeError:
                    continue
        return None


# ═══════════════════════════════════════════════════════════════════════════
# #9 — Resource Accumulation Guard
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class LeaseRecord:
    """A tracked authority lease."""

    lease_id: str
    tool: str
    granted_at: float
    ttl_hours: float
    session_id: str
    actor_id: str
    scope: str = ""


class LeaseGuard:
    """Enforce max lease TTL and audit accumulated authority."""

    def __init__(self) -> None:
        self._leases: dict[str, LeaseRecord] = {}
        self._max_ttl = LEASE_MAX_TTL_HOURS

    def grant(
        self,
        lease_id: str,
        tool: str,
        session_id: str,
        actor_id: str,
        ttl_hours: float | None = None,
        scope: str = "",
    ) -> tuple[bool, str]:
        """Grant a lease. Rejects if TTL exceeds max or if duplicate."""
        effective_ttl = min(ttl_hours or self._max_ttl, self._max_ttl)

        if lease_id in self._leases:
            return False, f"Duplicate lease: {lease_id}"

        self._leases[lease_id] = LeaseRecord(
            lease_id=lease_id,
            tool=tool,
            granted_at=time.time(),
            ttl_hours=effective_ttl,
            session_id=session_id,
            actor_id=actor_id,
            scope=scope,
        )
        return True, f"Granted {lease_id} (TTL: {effective_ttl}h)"

    def validate(self, lease_id: str) -> tuple[bool, str]:
        """Check if a lease is still valid (not expired, not revoked)."""
        if lease_id not in self._leases:
            return False, f"Unknown lease: {lease_id}"

        rec = self._leases[lease_id]
        age_hours = (time.time() - rec.granted_at) / 3600

        if age_hours > rec.ttl_hours:
            return False, (f"Lease {lease_id} expired: {age_hours:.1f}h old (max {rec.ttl_hours}h)")

        return True, "OK"

    def revoke(self, lease_id: str) -> None:
        """Revoke a lease."""
        self._leases.pop(lease_id, None)

    def audit(self) -> dict[str, Any]:
        """Return all active leases and their ages."""
        now = time.time()
        active = []
        expired = []
        for rec in self._leases.values():
            age_h = (now - rec.granted_at) / 3600
            entry = {
                "lease_id": rec.lease_id,
                "tool": rec.tool,
                "age_hours": round(age_h, 2),
                "ttl_hours": rec.ttl_hours,
                "actor_id": rec.actor_id,
                "session_id": rec.session_id,
                "expired": age_h > rec.ttl_hours,
            }
            if age_h > rec.ttl_hours:
                expired.append(entry)
            else:
                active.append(entry)

        return {
            "max_ttl_hours": self._max_ttl,
            "active_leases": len(active),
            "expired_leases": len(expired),
            "active": sorted(active, key=lambda x: x["age_hours"], reverse=True),
            "expired": expired,
            "oldest_active_hours": active[0]["age_hours"] if active else None,
            "doctrine": "No lease lives longer than its task.",
        }


# ═══════════════════════════════════════════════════════════════════════════
# Integration hooks
# ═══════════════════════════════════════════════════════════════════════════

_deferred_guard: DeferredGuard | None = None
_lease_guard: LeaseGuard | None = None


def get_deferred_guard() -> DeferredGuard:
    global _deferred_guard
    if _deferred_guard is None:
        _deferred_guard = DeferredGuard()
    return _deferred_guard


def get_lease_guard() -> LeaseGuard:
    global _lease_guard
    if _lease_guard is None:
        _lease_guard = LeaseGuard()
    return _lease_guard


def check_deferred_action(
    action_id: str,
    session_id: str | None = None,
    actor_id: str | None = None,
    session_age_hours: float | None = None,
) -> tuple[bool, str]:
    """Check if a deferred action can execute. Called before any cron/plan fire."""
    return get_deferred_guard().check_at_execution(
        action_id, session_id, actor_id, session_age_hours
    )


__all__ = [
    "DeferredAction",
    "DeferredGuard",
    "LeaseRecord",
    "LeaseGuard",
    "get_deferred_guard",
    "get_lease_guard",
    "check_deferred_action",
    "MAX_SESSION_AGE_HOURS",
    "MAX_PLAN_AGE_HOURS",
    "LEASE_MAX_TTL_HOURS",
]
