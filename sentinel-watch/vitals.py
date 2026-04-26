"""
SENTINEL-WATCH — Attentional Integrity Sidecar
==============================================
Read-only vault999 observer. Computes SLA vitals. Fires independent alerts.
DITEMPA BUKAN DIBERI — Forged, Not Given.

This process has NO WRITE ACCESS to vault999.
It observes. It alerts. It cannot be silenced without evidence.
"""

from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── SLA Tier Definitions ─────────────────────────────────────────────────────

HARD_TIERS = {"F13", "F1", "F2", "F6", "F9", "F10"}  # Irreversible
SOFT_TIERS = {"F3", "F4", "F5", "F7", "F8", "F11", "F12"}  # Reversible/soft

SLA_HARD_HOURS = 4   # Hard-tier: ACK required within 4 hours
SLA_SOFT_HOURS = 24  # Soft-tier: ACK required within 24 hours
DRIFT_THRESHOLD = 0.20  # 20% deviation from rolling baseline → alert
ROLLING_WINDOW_DAYS = 30  # Baseline window


# ── Vault999 Reader ────────────────────────────────────────────────────────────

def vault999_path() -> Path:
    return Path(os.getenv("SENTINEL_VAULT999", "/root/.agent-workbench/vault999.jsonl"))


def read_vault999(limit: Optional[int] = None) -> list[dict]:
    """Read vault999 entries. Most recent last."""
    path = vault999_path()
    if not path.exists():
        return []
    try:
        lines = open(path, "r", encoding="utf-8").read().splitlines()
        if limit:
            lines = lines[-limit:]
        return [json.loads(l) for l in lines if l.strip()]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


# ── ACK State Machine ───────────────────────────────────────────────────────────

@dataclass
class VerdictEntry:
    ts: float
    event_type: str
    tool: str
    verdict: str
    consequence_tier: str  # "HARD_TIER" | "SOFT_TIER" | "UNKNOWN"
    payload: dict
    ack_ts: Optional[float] = None
    chain_hash: Optional[str] = None


class ACKMachine:
    """
    Affirmative ACK state machine.
    HARD_TIER verdicts require explicit human ACK before irreversible progression.
    Silence = HOLD. Never approval.
    """

    def __init__(self):
        self.pending_hard: list[VerdictEntry] = []
        self.acked: list[VerdictEntry] = []
        self.hard_sla_expired: list[VerdictEntry] = []

    def ingest(self, entry: dict) -> Optional[str]:
        """
        Ingest a vault999 entry.
        Returns: verdict state if action needed, else None.
        """
        event_type = entry.get("event_type", "")
        verdict = entry.get("verdict", entry.get("payload", {}).get("verdict", ""))
        payload = entry.get("payload", {})
        floor_tags = payload.get("floors_triggered", [])

        # Determine consequence tier
        hard = bool(set(floor_tags) & HARD_TIERS)
        tier = "HARD_TIER" if hard else "SOFT_TIER"

        ts = entry.get("ts", time.time())
        v = VerdictEntry(
            ts=ts,
            event_type=event_type,
            tool=entry.get("tool", payload.get("tool", "unknown")),
            verdict=verdict,
            consequence_tier=tier,
            payload=payload,
            chain_hash=entry.get("chain_hash") or entry.get("merkle_leaf"),
        )

        if tier == "HARD_TIER" and verdict in ("SEAL", "HOLD_888", "VOID"):
            self.pending_hard.append(v)
            return f"HARD_PENDING:{v.chain_hash}"

        return None

    def acknowledge(self, chain_hash: str) -> bool:
        """
        Record human ACK for a verdict.
        Returns True if found and acked, False if not found.
        """
        for v in self.pending_hard:
            if v.chain_hash == chain_hash:
                v.ack_ts = time.time()
                self.acked.append(v)
                self.pending_hard.remove(v)
                return True
        return False

    def acknowledge_all(self) -> int:
        """Acknowledge all pending. Returns count acked."""
        count = 0
        for v in self.pending_hard:
            v.ack_ts = time.time()
            self.acked.append(v)
        count = len(self.pending_hard)
        self.pending_hard.clear()
        return count

    def check_sla_expiry(self) -> list[VerdictEntry]:
        """Return hard-tier verdicts whose SLA has expired without ACK."""
        now = time.time()
        expired = []
        for v in self.pending_hard:
            age_hours = (now - v.ts) / 3600
            limit = SLA_HARD_HOURS if v.consequence_tier == "HARD_TIER" else SLA_SOFT_HOURS
            if age_hours > limit:
                v.ack_ts = -1  # marker for expired without ACK
                expired.append(v)
        self.hard_sla_expired.extend(expired)
        return expired

    def get_pending(self) -> list[VerdictEntry]:
        return list(self.pending_hard)

    def get_stats(self) -> dict:
        now = time.time()
        pending_hard_count = len([v for v in self.pending_hard if v.consequence_tier == "HARD_TIER"])
        pending_soft_count = len([v for v in self.pending_hard if v.consequence_tier == "SOFT_TIER"])
        expired_count = len(self.hard_sla_expired)
        acked_count = len(self.acked)

        # Oldest pending
        oldest_ts = min((v.ts for v in self.pending_hard), default=None)
        oldest_age_hours = (now - oldest_ts) / 3600 if oldest_ts else 0

        return {
            "pending_hard": pending_hard_count,
            "pending_soft": pending_soft_count,
            "hard_sla_expired": expired_count,
            "acked": acked_count,
            "oldest_pending_hours": round(oldest_age_hours, 1),
        }
