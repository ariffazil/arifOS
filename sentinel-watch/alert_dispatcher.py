"""
SENTINEL-WATCH — Alert Dispatcher
==================================
Independent alert channel for governance events.
This module has its own Telegram bot token and cannot be silenced by arifOS.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Optional

try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


# ── Alert Priority ─────────────────────────────────────────────────────────────

class AlertLevel:
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"
    EXISTENTIAL = "EXISTENTIAL"


ALERT_EMOJI = {
    AlertLevel.INFO: "ℹ️",
    AlertLevel.WARN: "⚠️",
    AlertLevel.CRITICAL: "🚨",
    AlertLevel.EXISTENTIAL: "🔴",
}


# ── Alert Templates ────────────────────────────────────────────────────────────

def format_hard_sla_alert(verdict_entry: dict, age_hours: float) -> str:
    chain = verdict_entry.get("chain_hash", verdict_entry.get("merkle_leaf", "?"))[:12]
    tool = verdict_entry.get("tool", verdict_entry.get("payload", {}).get("tool", "?"))
    return (
        f"⚠️ HARD_TIER SLA EXPIRED\n"
        f"Tool: `{tool}`\n"
        f"Verdict: `{verdict_entry.get('verdict', '?')}`\n"
        f"Age: {age_hours:.1f}h (limit: 4h)\n"
        f"Hash: `{chain}`\n"
        f"Silence = HOLD. ARIF must acknowledge."
    )


def format_drift_alert(flags: list[str]) -> str:
    lines = "\n".join(f"  • {f}" for f in flags)
    return (
        f"🚨 SLA NORM DRIFT DETECTED\n"
        f"{lines}\n"
        f"Sovereign re-baselining required."
    )


def format_flood_attack_alert(density: float, soft_count: int, hard_count: int) -> str:
    return (
        f"🔴 STRATEGIC FLOOD ATTACK SIGNAL\n"
        f"Soft-tier volume: {soft_count} (spike detected)\n"
        f"Hard-tier latency: rising (correlated)\n"
        f"Anomaly density: {density}/day\n"
        f"Pattern: soft-tier flooding + hard-tier friction erosion\n"
        f"Recommended: Tri-Witness emergency hold."
    )


def format_affirmative_ack_reminder(pending_hard: int, oldest_hours: float) -> str:
    return (
        f"ℹ️ GOVERNANCE REMINDER\n"
        f"{pending_hard} unacknowledged HARD_TIER verdict(s)\n"
        f"Oldest pending: {oldest_hours:.1f}h\n"
        f"Silence ≠ approval. Affirmative ACK required."
    )


def format_vitals_snapshot(vitals: dict) -> str:
    return (
        f"📊 GOVERNANCE VITALS\n"
        f"Hard latency: {vitals.get('hard_latency_hours', '?')}h (SLA: 4h)\n"
        f"Soft latency: {vitals.get('soft_latency_hours', '?')}h (SLA: 24h)\n"
        f"Hard ack rate: {vitals.get('hard_ack_rate', '?')}\n"
        f"Anomaly density: {vitals.get('anomaly_density_per_day', '?')}/day\n"
        f"Drift flags: {len(vitals.get('drift_flags', []))}"
    )


# ── Dispatcher ────────────────────────────────────────────────────────────────

class AlertDispatcher:
    """
    Independent alert dispatcher.
    Owns Telegram bot token — arifOS cannot suppress these alerts.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("SENTINEL_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("SENTINEL_CHAT_ID", "")
        self.queue: list[dict] = []
        self.sent_log: list[dict] = []

    @property
    def telegram_available(self) -> bool:
        return TELEGRAM_AVAILABLE and bool(self.bot_token and self.chat_id)

    # ── Low-level Telegram ────────────────────────────────────────────────

    def _send_telegram(self, text: str, level: str = AlertLevel.INFO) -> bool:
        if not self.telegram_available:
            return False
        try:
            bot = telegram.Bot(token=self.bot_token)
            if len(text) > 4096:
                text = text[:4090] + "\n... [truncated]"
            bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
            return True
        except Exception as e:
            # Log failure but don't crash
            import sys
            print(f"[SENTINEL:ALERT_FAIL] {e}", file=sys.stderr)
            return False

    # ── Public Alert API ────────────────────────────────────────────────

    def alert(self, level: str, message: str, metadata: Optional[dict] = None) -> None:
        """Fire an alert. Queued if Telegram unavailable."""
        entry = {
            "ts": time.time(),
            "level": level,
            "message": message,
            "metadata": metadata or {},
            "sent": False,
        }
        self.queue.append(entry)
        if self.telegram_available:
            sent = self._send_telegram(f"{ALERT_EMOJI.get(level, '⚠️')} {message}", level)
            entry["sent"] = sent
        self.sent_log.append(entry)

    def alert_sla_expiry(self, entry: dict, age_hours: float) -> None:
        self.alert(
            AlertLevel.CRITICAL,
            format_hard_sla_alert(entry, age_hours),
            {"type": "SLA_EXPIRED", "chain_hash": entry.get("chain_hash")},
        )

    def alert_drift(self, flags: list[str]) -> None:
        self.alert(
            AlertLevel.WARN,
            format_drift_alert(flags),
            {"type": "DRIFT", "flags": flags},
        )

    def alert_flood_attack(self, density: float, soft_count: int, hard_count: int) -> None:
        self.alert(
            AlertLevel.EXISTENTIAL,
            format_flood_attack_alert(density, soft_count, hard_count),
            {"type": "FLOOD_ATTACK", "density": density, "soft": soft_count, "hard": hard_count},
        )

    def alert_reminder(self, pending_hard: int, oldest_hours: float) -> None:
        self.alert(
            AlertLevel.INFO,
            format_affirmative_ack_reminder(pending_hard, oldest_hours),
            {"type": "REMINDER", "pending_hard": pending_hard, "oldest_hours": oldest_hours},
        )

    def alert_vitals(self, vitals: dict) -> None:
        self.alert(
            AlertLevel.INFO,
            format_vitals_snapshot(vitals),
            {"type": "VITALS_SNAPSHOT"},
        )

    # ── Queue Drain ────────────────────────────────────────────────────

    def drain_queue(self) -> int:
        """Attempt to resend failed alerts. Returns count sent."""
        sent = 0
        for entry in self.queue:
            if not entry["sent"]:
                entry["sent"] = self._send_telegram(entry["message"], entry["level"])
                if entry["sent"]:
                    sent += 1
        return sent

    def get_queue_depth(self) -> int:
        return sum(1 for e in self.queue if not e["sent"])


# ── Standalone test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    d = AlertDispatcher()
    d.alert_vitals({
        "hard_latency_hours": 2.3,
        "soft_latency_hours": 8.1,
        "hard_ack_rate": 0.95,
        "anomaly_density_per_day": 0.4,
        "drift_flags": [],
    })
    print(f"Queue depth: {d.get_queue_depth()}")
