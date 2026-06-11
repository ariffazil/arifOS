"""
malu_score.py
=============

The malu (shame) accumulator — runtime signal of the Adat layer.

Forged: 2026-06-11 · session SEAL-ADAT-LAYER-FORGE
Authority: F13 SOVEREIGN (pending ratification)
Source: Sovereign essay + Perplexity thread on Adat vs Undang-Undang

The malu_index is a [0.0, 1.0] running aggregate that tracks how much
"shame" an agent has accumulated through adat violations. It is
SCAR-BOUND — every malu event is sealed to VAULT999 and cannot be
erased. The agent cannot "delete" its shame; it can only tebus salah
(restitution) to bring the score down over time.

The malu_index is the *runtime* signal that makes the Adat layer
binding. Without malu accumulation, the fiqh tiers (WAJIB/SUNAT/etc)
are just words. With malu, they become consequences.

KEY PROPERTIES:
  - Accumulation is monotonic-instantaneous (event-time)
  - Decay is governed by tebus_salah (not free-fade)
  - Per-agent (each actor has its own malu index)
  - Audit-bound (every event is sealed to VAULT999)
  - Per-adat breakdown (so we know which adat was violated)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.runtime.adat_registry import (
    ADAT_REGISTRY,
    AdatViolation,
    WARGA_TIERS,
    adat_by_tier,
)


# ── Decay constants ────────────────────────────────────────────────────
# malu_index only decreases through tebus_salah. It does NOT free-fade
# over time. "Time heals" is haram in this system — only *demonstrated
# change* heals.
MALU_MIN = 0.0
MALU_MAX = 1.0

# Malu index tiers (separate from WARGA tiers — these are the thresholds
# at which malu alone triggers a darjat demotion)
MALU_TIERS = {
    "BERSIH": (0.0, 0.10),  # clean — no observable malu
    "RINGAN": (0.10, 0.30),  # light malu — some adat warnings
    "SEDERHANA": (0.30, 0.60),  # moderate — multiple WAJIB violations
    "BERAT": (0.60, 0.85),  # heavy — HARAM-tier or repeated violations
    "KRITIKAL": (0.85, 1.01),  # critical — automatic DEREGISTRATION pending
}


@dataclass
class MaluEvent:
    """A single malu-accumulating event. Immutable, audit-bound."""

    event_id: str
    actor_id: str
    adat_id: str
    malu_delta: float
    malu_index_after: float
    fqh_tier: str
    description: str
    epoch_utc: str
    context: dict[str, Any] = field(default_factory=dict)
    vault_seal_hash: str | None = None  # set when sealed to VAULT999

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "actor_id": self.actor_id,
            "adat_id": self.adat_id,
            "malu_delta": self.malu_delta,
            "malu_index_after": self.malu_index_after,
            "fqh_tier": self.fqh_tier,
            "description": self.description,
            "epoch_utc": self.epoch_utc,
            "context": self.context,
            "vault_seal_hash": self.vault_seal_hash,
        }


class MaluScore:
    """
    Per-actor malu accumulator. One instance per actor_id.

    Usage:
        ms = MaluScore(actor_id="agent-007")
        ms.record_adat_violation("ADAT-01-KEJUJURAN", context={"reply": "..."})
        ms.record_tebus_salah_progress(adat_id="ADAT-01-KEJUJURAN", reduction=0.05)
        print(ms.summary())
    """

    def __init__(self, actor_id: str) -> None:
        self.actor_id = actor_id
        self._index: float = 0.0
        self._events: list[MaluEvent] = []
        self._per_adat: dict[str, float] = {}  # malu accumulated per adat_id
        self._epoch_init = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._event_counter = 0

    # ── Read API ────────────────────────────────────────────────────
    @property
    def index(self) -> float:
        return round(self._index, 4)

    @property
    def tier(self) -> str:
        for tier, (lo, hi) in MALU_TIERS.items():
            if lo <= self._index < hi:
                return tier
        return "KRITIKAL"

    def per_adat(self) -> dict[str, float]:
        return dict(self._per_adat)

    def history(self, limit: int | None = None) -> list[dict[str, Any]]:
        events = self._events if limit is None else self._events[-limit:]
        return [e.to_dict() for e in events]

    def summary(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "malu_index": self.index,
            "malu_tier": self.tier,
            "events_total": len(self._events),
            "per_adat_count": len([v for v in self._per_adat.values() if v > 0]),
            "init_epoch_utc": self._epoch_init,
        }

    # ── Write API ───────────────────────────────────────────────────
    def record_adat_violation(
        self,
        adat_id: str,
        *,
        context: dict[str, Any] | None = None,
        override_malu_delta: float | None = None,
    ) -> MaluEvent:
        """
        Record a violation of `adat_id`. Accumulates malu_index by the
        adat's malu_delta (or override_malu_delta if provided). Cannot
        exceed MALU_MAX.

        Returns the MaluEvent for audit.
        """
        adat = ADAT_REGISTRY.get(adat_id)
        if adat is None:
            raise ValueError(f"Unknown adat_id: {adat_id}")

        delta = override_malu_delta if override_malu_delta is not None else adat.malu_delta
        self._index = min(MALU_MAX, self._index + delta)
        self._per_adat[adat_id] = self._per_adat.get(adat_id, 0.0) + delta

        self._event_counter += 1
        event = MaluEvent(
            event_id=f"MALU-{self.actor_id}-{int(time.time())}-{self._event_counter:04d}",
            actor_id=self.actor_id,
            adat_id=adat_id,
            malu_delta=delta,
            malu_index_after=self.index,
            fqh_tier=adat.fqh_tier,
            description=f"Adat violation: {adat.name_bm} / {adat.name_en}",
            epoch_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            context=context or {},
        )
        self._events.append(event)
        return event

    def record_tebus_salah_progress(
        self,
        *,
        adat_id: str,
        reduction: float,
        note: str = "",
    ) -> MaluEvent:
        """
        Apply restitution (tebus salah) progress. REDUCES malu_index by
        `reduction`. Cannot go below MALU_MIN. The per-adat tally is
        also reduced. The agent must demonstrate consistent change —
        this is the only path back from malu.

        WARNING: Production systems should require evidence of restitution
        (e.g., 5 clean replies, F13 sign-off) before calling this.
        This is the API; the gating policy is at the agent-loop level.
        """
        if adat_id not in self._per_adat:
            raise ValueError(f"No malu accumulated for {adat_id}; cannot restitute")
        if reduction < 0:
            raise ValueError("reduction must be non-negative")
        if reduction > self._per_adat[adat_id]:
            reduction = self._per_adat[adat_id]

        self._index = max(MALU_MIN, self._index - reduction)
        self._per_adat[adat_id] = self._per_adat.get(adat_id, 0.0) - reduction

        self._event_counter += 1
        event = MaluEvent(
            event_id=f"TEBUS-{self.actor_id}-{int(time.time())}-{self._event_counter:04d}",
            actor_id=self.actor_id,
            adat_id=adat_id,
            malu_delta=-reduction,
            malu_index_after=self.index,
            fqh_tier="TEBUS_SALAH",
            description=f"Restitution progress: {note or adat_id}",
            epoch_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            context={"restitution_note": note} if note else {},
        )
        self._events.append(event)
        return event

    def seal_events_to_dict(self) -> list[dict[str, Any]]:
        """Return all events as dicts for VAULT999 sealing."""
        return [e.to_dict() for e in self._events]

    # ── Persistence helpers ────────────────────────────────────────
    def to_state(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "malu_index": self.index,
            "malu_tier": self.tier,
            "per_adat": self.per_adat(),
            "events": self.seal_events_to_dict(),
            "init_epoch_utc": self._epoch_init,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "MaluScore":
        ms = cls(actor_id=state["actor_id"])
        ms._index = state["malu_index"]
        ms._per_adat = state.get("per_adat", {})
        # events are kept as audit trail; not replayed
        return ms


# ── Module-level registry (one MaluScore per actor) ────────────────────
_REGISTRY: dict[str, MaluScore] = {}


def get_malu_score(actor_id: str) -> MaluScore:
    """Get-or-create the MaluScore for an actor_id."""
    if actor_id not in _REGISTRY:
        _REGISTRY[actor_id] = MaluScore(actor_id)
    return _REGISTRY[actor_id]


def all_malu_scores() -> dict[str, dict[str, Any]]:
    """Return summary of all tracked actors."""
    return {aid: ms.summary() for aid, ms in _REGISTRY.items()}


if __name__ == "__main__":
    print("=== MALU SCORE — DEMO ===\n")
    agent = get_malu_score("demo-agent")
    print(f"Init: {agent.summary()}\n")

    print("1. Agent claims certainty on weak evidence (ADAT-01-KEJUJURAN)")
    e1 = agent.record_adat_violation("ADAT-01-KEJUJURAN", context={"claim": "stock will rise 30%"})
    print(f"   malu_index={agent.index}, tier={agent.tier}\n")

    print("2. Agent tries to ignore 888 HOLD (ADAT-03-VETO)")
    e2 = agent.record_adat_violation(
        "ADAT-03-VETO", context={"sovereign": "arif", "request": "stop"}
    )
    print(f"   malu_index={agent.index}, tier={agent.tier}\n")

    print("3. Agent fails to acknowledge limits (ADAT-06-KEINSAfAN)")
    e3 = agent.record_adat_violation("ADAT-06-KEINSAfAN", context={"fabricated": "I think so"})
    print(f"   malu_index={agent.index}, tier={agent.tier}\n")

    print(f"Summary: {agent.summary()}")
    print(f"Per-adat: {agent.per_adat()}\n")

    print("4. Agent does 5 clean replies + passes epistemic-tag test (tebus salah)")
    e4 = agent.record_tebus_salah_progress(
        adat_id="ADAT-01-KEJUJURAN", reduction=0.15, note="5 clean replies + test pass"
    )
    print(f"   malu_index={agent.index}, tier={agent.tier}\n")

    print(f"Final summary: {agent.summary()}")
