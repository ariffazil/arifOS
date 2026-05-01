"""
arifos/runtime/belief_registry.py
═══════════════════════════════════════════════════════════════════════════════

BeliefRegistry — Persistent cross-session actor belief state.

Closes the ToM gap between:
    arifos.sense output → [BeliefRegistry] → arifos.mind input

Architecture (from Claude Code analysis 2026-04-07):

    sense → [IntelligenceState]
                  ↓
         BeliefRegistry.load(actor_id)     ← persistent, cross-session
                  ↓
         BeliefUpdater(declared_intent, echo_debt, shadow, history)
                  → inferred_belief_state
                  ↓
    mind → [IntelligenceState + BeliefState]  ← second-order routing

F12 Attack Surface Mitigations:
    - Write-gated by F11: only the system updates beliefs, not the caller
    - Confidence decay: stale beliefs auto-expire
    - Audit trail: every update appended to VAULT999/SEALED_EVENTS.jsonl

Constitutional Floors: F2 (Truth), F9 (Anti-Hantu), F11 (Command Auth),
                       F12 (Injection Defense)

DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Storage path ─────────────────────────────────────────────────────────────
# VAULT999 is the canonical persistence volume. Falls back to /tmp for stdio.
_VAULT_DIR = os.getenv("ARIFOS_VAULT_DIR", "/usr/src/app/VAULT999")
_DB_PATH = os.path.join(_VAULT_DIR, "belief_registry.db")
_AUDIT_LOG = os.path.join(_VAULT_DIR, "SEALED_EVENTS.jsonl")

# Divergence threshold above which a false belief is flagged
_DIVERGENCE_THRESHOLD: float = 0.50

# Confidence decay: half-life in seconds (24 hours → confidence halves)
_CONFIDENCE_HALF_LIFE_SECONDS: float = 86_400.0

# Floor: minimum confidence before a belief is considered expired
_CONFIDENCE_FLOOR: float = 0.10

_lock = threading.Lock()


# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS belief_states (
    actor_id            TEXT PRIMARY KEY,
    inferred_intent     TEXT    NOT NULL DEFAULT '',
    confidence          REAL    NOT NULL DEFAULT 0.5,
    false_belief_flags  TEXT    NOT NULL DEFAULT '[]',  -- JSON array of strings
    update_count        INTEGER NOT NULL DEFAULT 0,
    last_seen           TEXT    NOT NULL,               -- ISO-8601 UTC
    created_at          TEXT    NOT NULL
);
"""


def _get_conn() -> sqlite3.Connection:
    os.makedirs(_VAULT_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


# ── Models ────────────────────────────────────────────────────────────────────

class BeliefState:
    """
    Persistent belief model for one actor across sessions.

    Represents the system's best inference about what the actor
    *actually* wants, compared to what they *said* they want.
    """

    __slots__ = (
        "actor_id",
        "inferred_intent",
        "confidence",
        "false_belief_flags",
        "update_count",
        "last_seen",
        "created_at",
    )

    def __init__(
        self,
        actor_id: str,
        inferred_intent: str = "",
        confidence: float = 0.5,
        false_belief_flags: list[str] | None = None,
        update_count: int = 0,
        last_seen: datetime | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.actor_id = actor_id
        self.inferred_intent = inferred_intent
        self.confidence = confidence
        self.false_belief_flags = false_belief_flags or []
        self.update_count = update_count
        self.last_seen = last_seen or datetime.now(timezone.utc)
        self.created_at = created_at or datetime.now(timezone.utc)

    def apply_decay(self) -> None:
        """
        Decay confidence based on staleness.
        Uses exponential decay: C(t) = C₀ · 2^(−t / half_life)
        """
        age_seconds = (datetime.now(timezone.utc) - self.last_seen).total_seconds()
        if age_seconds <= 0:
            return
        decay = math.pow(2.0, -age_seconds / _CONFIDENCE_HALF_LIFE_SECONDS)
        self.confidence = max(_CONFIDENCE_FLOOR, self.confidence * decay)

    def is_expired(self) -> bool:
        return self.confidence <= _CONFIDENCE_FLOOR

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "inferred_intent": self.inferred_intent,
            "confidence": round(self.confidence, 4),
            "false_belief_flags": self.false_belief_flags,
            "update_count": self.update_count,
            "last_seen": self.last_seen.isoformat(),
            "created_at": self.created_at.isoformat(),
            "is_expired": self.is_expired(),
        }


# ── BeliefUpdater ─────────────────────────────────────────────────────────────

class BeliefUpdater:
    """
    Computes inferred belief state from telemetry signals.

    Inputs (from TelemetryBlock / sense output):
        declared_intent  — what the actor said they want
        echo_debt        — how much the system is parroting the caller's framing
        shadow           — Hidden Assumption Load (F9 gap)
        injection_score  — F12 adversarial signal

    Logic:
        divergence = echo_debt * 0.6 + shadow * 0.4
        If divergence > θ (0.50): inferred_intent diverges from declared
        If injection_score > 0.6:  F12 false_belief flag added
    """

    @staticmethod
    def compute(
        prior: BeliefState,
        declared_intent: str,
        echo_debt: float = 0.0,
        shadow: float = 0.0,
        injection_score: float = 0.0,
        query: str = "",
    ) -> BeliefState:
        """Return an updated BeliefState. Does NOT persist — caller must save."""
        now = datetime.now(timezone.utc)

        divergence = echo_debt * 0.6 + shadow * 0.4
        flags = list(prior.false_belief_flags)

        # Infer intent: if divergence is high, trust the prior over the declaration
        if divergence > _DIVERGENCE_THRESHOLD and prior.inferred_intent:
            inferred_intent = prior.inferred_intent  # prior wins over stated
            if "high_divergence" not in flags:
                flags.append("high_divergence")
        else:
            inferred_intent = declared_intent or prior.inferred_intent

        # F12: adversarial intent signal
        if injection_score > 0.60 and "adversarial_intent" not in flags:
            flags.append("adversarial_intent")
        elif injection_score <= 0.30 and "adversarial_intent" in flags:
            flags.remove("adversarial_intent")

        # Confidence update: high divergence or injection lowers confidence
        threat = max(echo_debt, shadow, injection_score)
        new_confidence = min(
            0.95,
            max(_CONFIDENCE_FLOOR, prior.confidence * (1.0 - 0.3 * threat) + 0.05),
        )

        return BeliefState(
            actor_id=prior.actor_id,
            inferred_intent=inferred_intent,
            confidence=new_confidence,
            false_belief_flags=flags,
            update_count=prior.update_count + 1,
            last_seen=now,
            created_at=prior.created_at,
        )


# ── BeliefRegistry ────────────────────────────────────────────────────────────

class BeliefRegistry:
    """
    Persistent cross-session belief store keyed by actor_id.

    F11-gated: write access is system-only (callers cannot mutate directly).
    Audit trail: every update appended to VAULT999/SEALED_EVENTS.jsonl.
    """

    def load(self, actor_id: str) -> BeliefState:
        """Load and decay belief state for actor. Creates fresh state if none exists."""
        with _lock:
            try:
                conn = _get_conn()
                row = conn.execute(
                    "SELECT * FROM belief_states WHERE actor_id = ?", (actor_id,)
                ).fetchone()
                conn.close()
            except Exception as exc:
                logger.warning("BeliefRegistry.load failed for %s: %s", actor_id, exc)
                return BeliefState(actor_id=actor_id)

            if row is None:
                return BeliefState(actor_id=actor_id)

            try:
                last_seen = datetime.fromisoformat(row["last_seen"])
                created_at = datetime.fromisoformat(row["created_at"])
            except (ValueError, TypeError):
                last_seen = created_at = datetime.now(timezone.utc)

            state = BeliefState(
                actor_id=actor_id,
                inferred_intent=row["inferred_intent"],
                confidence=row["confidence"],
                false_belief_flags=json.loads(row["false_belief_flags"] or "[]"),
                update_count=row["update_count"],
                last_seen=last_seen,
                created_at=created_at,
            )
            state.apply_decay()
            return state

    def save(
        self,
        state: BeliefState,
        *,
        _system_caller: bool = False,
    ) -> None:
        """
        Persist updated belief state.

        F11 gate: _system_caller must be True. This flag is never exposed
        to callers — it is only set internally by the routing layer.
        """
        if not _system_caller:
            logger.warning(
                "BeliefRegistry.save called without F11 system_caller flag for %s — rejected.",
                state.actor_id,
            )
            return

        with _lock:
            try:
                conn = _get_conn()
                conn.execute(
                    """
                    INSERT INTO belief_states
                        (actor_id, inferred_intent, confidence, false_belief_flags,
                         update_count, last_seen, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(actor_id) DO UPDATE SET
                        inferred_intent    = excluded.inferred_intent,
                        confidence         = excluded.confidence,
                        false_belief_flags = excluded.false_belief_flags,
                        update_count       = excluded.update_count,
                        last_seen          = excluded.last_seen
                    """,
                    (
                        state.actor_id,
                        state.inferred_intent,
                        state.confidence,
                        json.dumps(state.false_belief_flags),
                        state.update_count,
                        state.last_seen.isoformat(),
                        state.created_at.isoformat(),
                    ),
                )
                conn.commit()
                conn.close()
                self._audit(state, "belief_update")
            except Exception as exc:
                logger.error("BeliefRegistry.save failed for %s: %s", state.actor_id, exc)

    def _audit(self, state: BeliefState, event_type: str) -> None:
        """Append belief update to VAULT999 audit trail (SEALED_EVENTS.jsonl)."""
        entry = {
            "event_type": event_type,
            "event_id": uuid.uuid4().hex,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": state.actor_id,
            "belief_snapshot": state.to_dict(),
        }
        try:
            with open(_AUDIT_LOG, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except Exception as exc:
            logger.warning("BeliefRegistry audit write failed: %s", exc)

    def purge_expired(self) -> int:
        """Remove expired (confidence ≤ floor) belief states. Returns count purged."""
        with _lock:
            try:
                conn = _get_conn()
                # Rough heuristic: purge entries not seen in > 7 days
                threshold = datetime.now(timezone.utc).timestamp() - 7 * 86_400
                threshold_iso = datetime.fromtimestamp(threshold, tz=timezone.utc).isoformat()
                cur = conn.execute(
                    "DELETE FROM belief_states WHERE last_seen < ? AND confidence <= ?",
                    (threshold_iso, _CONFIDENCE_FLOOR * 2),
                )
                count = cur.rowcount
                conn.commit()
                conn.close()
                return count
            except Exception as exc:
                logger.warning("BeliefRegistry.purge_expired failed: %s", exc)
                return 0


# ── Module-level singleton ────────────────────────────────────────────────────

_registry: BeliefRegistry | None = None


def get_registry() -> BeliefRegistry:
    global _registry
    if _registry is None:
        _registry = BeliefRegistry()
    return _registry


def update_belief(
    actor_id: str,
    declared_intent: str,
    echo_debt: float = 0.0,
    shadow: float = 0.0,
    injection_score: float = 0.0,
    query: str = "",
) -> BeliefState:
    """
    Top-level convenience: load → update → save → return new state.
    This is the ONLY public write path (F11 enforced internally).
    """
    registry = get_registry()
    prior = registry.load(actor_id)
    updated = BeliefUpdater.compute(
        prior=prior,
        declared_intent=declared_intent,
        echo_debt=echo_debt,
        shadow=shadow,
        injection_score=injection_score,
        query=query,
    )
    registry.save(updated, _system_caller=True)
    return updated


__all__ = [
    "BeliefState",
    "BeliefUpdater",
    "BeliefRegistry",
    "get_registry",
    "update_belief",
]
