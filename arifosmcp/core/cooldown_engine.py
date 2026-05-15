"""
arifosmcp/core/cooldown_engine.py — SABAR Cooldown Protocol
═══════════════════════════════════════════════════════════

Internal hardening module. No new MCP tools. No "phoenix" in any output.

The SABAR cooldown protocol enforces a mandatory cooling window before any
insight, artifact, or decision can be sealed into permanent storage (VAULT999).

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ PROPOSE  │───▶│   COOL   │───▶│ WITNESS  │───▶│ SEAL     │
│ (PARTIAL)│    │ (SABAR)  │    │ (SABAR)  │    │ (SEAL)   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                      │                               ▲
                      ▼                               │
                ┌──────────┐                          │
                │  VOID    │ (expired/unwitnessed)     │
                └──────────┘                          │

Design invariants:
  - No insight enters permanent storage without cooldown.
  - SABAR is the DEFAULT during cooling.
  - Resource budget exhaustion → forced VOID.
  - Cooldown default: 72 hours (3 circadian cycles).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════

COOLDOWN_DEFAULT_HOURS: int = 72
COOLDOWN_MIN_HOURS: int = 24
COOLDOWN_MAX_HOURS: int = 720  # 30 days
COOLDOWN_RISK_TIERS: dict[str, int] = {
    "low": 24,
    "medium": 72,
    "high": 168,
    "critical": 720,
}

# ═══════════════════════════════════════════════════════════
# Data Models (internal — not exposed as MCP schemas)
# ═══════════════════════════════════════════════════════════


class TriWitness(BaseModel):
    """Tri-Witness validation status. All three must be True for SEAL."""

    human: bool = False
    ai_audit: bool = False
    reality_check: bool = False

    @property
    def is_complete(self) -> bool:
        return self.human and self.ai_audit and self.reality_check

    @property
    def count(self) -> int:
        return sum([self.human, self.ai_audit, self.reality_check])


class SabarResourceBudget(BaseModel):
    """Resource budget consumed during SABAR cooldown. Exhaustion → VOID."""

    disk_bytes_allocated: int = 0
    disk_bytes_peak: int = 0
    compute_seconds: float = 0.0
    memory_mb_seconds: float = 0.0
    token_count: int = 0

    # Hard limits — exceeding any triggers budget exhaustion
    disk_limit_bytes: int = 50_000_000_000  # 50 GB
    compute_limit_seconds: float = 3_600.0  # 1 hour
    memory_limit_mb_seconds: float = 1_000_000.0  # ~16GB * 60s
    token_limit: int = 1_000_000

    def consume_disk(self, bytes_used: int) -> None:
        self.disk_bytes_allocated += bytes_used
        if self.disk_bytes_allocated > self.disk_bytes_peak:
            self.disk_bytes_peak = self.disk_bytes_allocated

    def consume_compute(self, seconds: float) -> None:
        self.compute_seconds += seconds

    def consume_memory(self, mb_seconds: float) -> None:
        self.memory_mb_seconds += mb_seconds

    def consume_tokens(self, count: int) -> None:
        self.token_count += count

    @property
    def is_exhausted(self) -> bool:
        """Budget exhausted — artifact must be VOIDed."""
        return (
            self.disk_bytes_allocated > self.disk_limit_bytes
            or self.compute_seconds > self.compute_limit_seconds
            or self.memory_mb_seconds > self.memory_limit_mb_seconds
            or self.token_count > self.token_limit
        )

    def summary(self) -> dict:
        return {
            "disk_mb": round(self.disk_bytes_allocated / 1_000_000, 2),
            "disk_peak_mb": round(self.disk_bytes_peak / 1_000_000, 2),
            "compute_seconds": round(self.compute_seconds, 1),
            "memory_mb_seconds": round(self.memory_mb_seconds, 1),
            "tokens": self.token_count,
            "exhausted": self.is_exhausted,
        }


class CooldownEntry(BaseModel):
    """A single entry in the SABAR cooldown band."""

    entry_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_session_id: str | None = None
    artifact_ref: str | None = None  # e.g., docker image SHA, evidence hash
    description: str = ""
    risk_tier: Literal["low", "medium", "high", "critical"] = "medium"

    proposed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    cooldown_expiry: datetime | None = None
    cooldown_hours: int = COOLDOWN_DEFAULT_HOURS

    verdict: str = "SABAR"  # SABAR during cooling → SEAL or VOID at resolution
    tri_witness: TriWitness = Field(default_factory=TriWitness)
    resource_budget: SabarResourceBudget = Field(default_factory=SabarResourceBudget)

    sealed_at: datetime | None = None
    voided_at: datetime | None = None
    void_reason: str | None = None

    def model_post_init(self, __context) -> None:
        if self.cooldown_expiry is None:
            hours = COOLDOWN_RISK_TIERS.get(self.risk_tier, self.cooldown_hours)
            self.cooldown_hours = hours
            self.cooldown_expiry = self.proposed_at + timedelta(hours=hours)

    @property
    def is_expired(self) -> bool:
        if self.cooldown_expiry is None:
            return False
        return datetime.now(UTC) > self.cooldown_expiry

    @property
    def remaining_hours(self) -> float:
        if self.cooldown_expiry is None:
            return 0.0
        remaining = (self.cooldown_expiry - datetime.now(UTC)).total_seconds() / 3600.0
        return max(0.0, remaining)

    @property
    def is_resolved(self) -> bool:
        return self.verdict in ("SEAL", "VOID")

    @property
    def can_seal(self) -> bool:
        """Can this entry be SEALed? Requires: not expired, tri-witness complete, budget OK."""
        return (
            not self.is_expired
            and self.tri_witness.is_complete
            and not self.resource_budget.is_exhausted
        )

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "artifact_ref": self.artifact_ref,
            "description": self.description,
            "risk_tier": self.risk_tier,
            "proposed_at": self.proposed_at.isoformat(),
            "cooldown_expiry": self.cooldown_expiry.isoformat() if self.cooldown_expiry else None,
            "cooldown_hours": self.cooldown_hours,
            "remaining_hours": round(self.remaining_hours, 1),
            "verdict": self.verdict,
            "tri_witness": {
                "human": self.tri_witness.human,
                "ai_audit": self.tri_witness.ai_audit,
                "reality_check": self.tri_witness.reality_check,
                "complete": self.tri_witness.is_complete,
                "count": self.tri_witness.count,
            },
            "resource_budget": self.resource_budget.summary(),
            "is_expired": self.is_expired,
            "can_seal": self.can_seal,
        }


# Pydantic v2: rebuild after Literal type resolution
CooldownEntry.model_rebuild()


# ═══════════════════════════════════════════════════════════
# Cooldown Engine
# ═══════════════════════════════════════════════════════════


class CooldownEngine:
    """
    SABAR Cooldown Protocol Engine.

    In-memory cooldown band. For production, extend with Postgres/Redis persistence
    via the existing vault999-writer path.

    Usage:
        engine = CooldownEngine()
        entry = engine.propose(artifact_ref="sha256:abc123", description="arifos build v2")
        # ... 72 hours pass ...
        engine.witness(entry.entry_id, "human", True)
        engine.witness(entry.entry_id, "ai_audit", True)
        engine.witness(entry.entry_id, "reality_check", True)
        verdict = engine.resolve(entry.entry_id)  # → SEAL or VOID
    """

    def __init__(self) -> None:
        self._entries: dict[str, CooldownEntry] = {}
        self._sealed_count: int = 0
        self._voided_count: int = 0
        self._active_count: int = 0
        self._bypass_count: int = 0  # Legacy path: vault seals without cooldown

    # ── Core Operations ──

    def propose(
        self,
        artifact_ref: str | None = None,
        description: str = "",
        risk_tier: Literal["low", "medium", "high", "critical"] = "medium",
        session_id: str | None = None,
        cooldown_hours: int | None = None,
    ) -> CooldownEntry:
        """Register a new artifact/insight in the SABAR cooldown band."""
        entry = CooldownEntry(
            artifact_ref=artifact_ref,
            description=description,
            risk_tier=risk_tier,
            parent_session_id=session_id,
        )
        if cooldown_hours is not None:
            entry.cooldown_hours = max(COOLDOWN_MIN_HOURS, min(cooldown_hours, COOLDOWN_MAX_HOURS))
            entry.cooldown_expiry = entry.proposed_at + timedelta(hours=entry.cooldown_hours)

        self._entries[entry.entry_id] = entry
        self._active_count += 1
        return entry

    def check(self, entry_id: str) -> CooldownEntry | None:
        """Query cooldown state. Auto-transitions expired entries to VOID."""
        entry = self._entries.get(entry_id)
        if entry is None:
            return None

        # Auto-VOID on expiry
        if entry.is_expired and not entry.is_resolved:
            self._void(entry, "cooldown expired (auto-VOID)")
            return entry

        # Auto-VOID on budget exhaustion
        if entry.resource_budget.is_exhausted and not entry.is_resolved:
            self._void(entry, "resource budget exhausted")
            return entry

        return entry

    def witness(self, entry_id: str, witness_type: str, value: bool = True) -> bool:
        """Submit Tri-Witness evidence for a cooldown entry."""
        entry = self._entries.get(entry_id)
        if entry is None:
            return False
        if entry.is_resolved:
            return False

        if witness_type == "human":
            entry.tri_witness.human = value
        elif witness_type == "ai_audit":
            entry.tri_witness.ai_audit = value
        elif witness_type == "reality_check":
            entry.tri_witness.reality_check = value
        else:
            return False

        return True

    def seal(self, entry_id: str) -> tuple[bool, str]:
        """
        Attempt to SEAL a cooldown entry.
        Returns (success, reason).
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            return False, "entry not found"
        if entry.is_resolved:
            return False, f"already resolved: {entry.verdict}"

        # Expiry check (don't seal expired entries)
        entry = self.check(entry_id)
        if entry is None:
            return False, "entry vanished"
        if entry.is_resolved:
            return False, f"auto-resolved during check: {entry.verdict}"

        if entry.is_expired:
            self._void(entry, "expired before seal")
            return False, "cooldown expired"

        if not entry.tri_witness.is_complete:
            return False, f"tri-witness incomplete ({entry.tri_witness.count}/3)"

        if entry.resource_budget.is_exhausted:
            self._void(entry, "resource budget exhausted")
            return False, "resource budget exhausted"

        entry.verdict = "SEAL"
        entry.sealed_at = datetime.now(UTC)
        self._sealed_count += 1
        self._active_count = max(0, self._active_count - 1)
        return True, "sealed"

    def void(self, entry_id: str, reason: str = "manual void") -> tuple[bool, str]:
        """Manually VOID a cooldown entry."""
        entry = self._entries.get(entry_id)
        if entry is None:
            return False, "entry not found"
        if entry.is_resolved:
            return False, f"already resolved: {entry.verdict}"

        self._void(entry, reason)
        return True, "voided"

    def resolve(self, entry_id: str) -> CooldownEntry | None:
        """
        Resolve a cooldown entry: SEAL if conditions met, VOID otherwise.
        This is the primary decision point after cooldown completes.
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            return None
        if entry.is_resolved:
            return entry

        # Check expiry and budget first
        entry = self.check(entry_id)
        if entry is None:
            return None
        if entry.is_resolved:
            return entry

        success, _ = self.seal(entry_id)
        if not success:
            self._void(entry, "failed seal — conditions not met")
        return entry

    # ── Housekeeping ──

    def record_bypass(self) -> int:
        """Record a legacy bypass (vault seal without cooldown). Returns new count."""
        self._bypass_count += 1
        return self._bypass_count

    def expire_all(self) -> int:
        """VOID all expired entries. Returns count of voided entries."""
        count = 0
        for entry_id in list(self._entries.keys()):
            entry = self._entries.get(entry_id)
            if entry and entry.is_expired and not entry.is_resolved:
                self._void(entry, "batch expiry")
                count += 1
        return count

    def prune_voided(self) -> int:
        """Remove VOIDed entries from memory. Returns count removed."""
        to_remove = [eid for eid, e in self._entries.items() if e.verdict == "VOID"]
        for eid in to_remove:
            del self._entries[eid]
        return len(to_remove)

    # ── Queries ──

    def get_active(self) -> list[CooldownEntry]:
        """Return all active (unresolved) cooldown entries."""
        return [e for e in self._entries.values() if not e.is_resolved]

    def get_sealed(self) -> list[CooldownEntry]:
        """Return all SEALed entries."""
        return [e for e in self._entries.values() if e.verdict == "SEAL"]

    def get_voided(self) -> list[CooldownEntry]:
        """Return all VOIDed entries."""
        return [e for e in self._entries.values() if e.verdict == "VOID"]

    def vitals(self) -> dict:
        """Return engine vitals for ops_measure integration."""
        active = self.get_active()
        return {
            "cooldown_active_count": len(active),
            "cooldown_sealed_count": self._sealed_count,
            "cooldown_voided_count": self._voided_count,
            "cooldown_bypass_count": self._bypass_count,
            "cooldown_total_entries": len(self._entries),
            "cooldown_active_entries": [
                {
                    "entry_id": e.entry_id,
                    "description": e.description[:60],
                    "remaining_hours": round(e.remaining_hours, 1),
                    "witness_count": e.tri_witness.count,
                    "risk_tier": e.risk_tier,
                    "verdict": e.verdict,
                }
                for e in active[:10]  # Cap at 10 for telemetry size
            ],
            "cooldown_oldest_remaining_hours": (
                round(min(e.remaining_hours for e in active), 1) if active else None
            ),
            "cooldown_sabar_budget_exhausted_any": any(
                e.resource_budget.is_exhausted for e in active
            ),
        }

    # ── Internal ──

    def _void(self, entry: CooldownEntry, reason: str) -> None:
        entry.verdict = "VOID"
        entry.voided_at = datetime.now(UTC)
        entry.void_reason = reason
        self._voided_count += 1
        self._active_count = max(0, self._active_count - 1)


# ═══════════════════════════════════════════════════════════
# Module-level singleton (lazy — created on first access)
# ═══════════════════════════════════════════════════════════

_engine: CooldownEngine | None = None


def get_cooldown_engine() -> CooldownEngine:
    """Get or create the module-level CooldownEngine singleton."""
    global _engine
    if _engine is None:
        _engine = CooldownEngine()
    return _engine


def reset_cooldown_engine() -> None:
    """Reset the singleton (for testing)."""
    global _engine
    _engine = None
