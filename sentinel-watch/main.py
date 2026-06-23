#!/usr/bin/env python3
"""
SENTINEL-WATCH — Main Polling Loop
==================================
Read-only vault999 observer + SLA vitals + independent alerting.
Run as a standalone process: python3 main.py

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations
import os
import sys
import time
import signal
from datetime import datetime, timezone
from pathlib import Path

# Add sentinel-watch to path
sys.path.insert(0, str(Path(__file__).parent))

from vitals import ACKMachine
from drift_detector import DriftDetector
from alert_dispatcher import AlertDispatcher

# ── Config ────────────────────────────────────────────────────────────────────

VAULT999_PATH = os.getenv(
    "SENTINEL_VAULT999", os.environ.get("ARIFOS_HOME", "/root") + "/.agent-workbench/vault999.jsonl"
)
POLL_INTERVAL_SECONDS = int(os.getenv("SENTINEL_POLL_INTERVAL", "60"))  # poll every 60s
REMINDER_INTERVAL_SECONDS = int(
    os.getenv("SENTINEL_REMINDER_INTERVAL", "14400")
)  # reminder every 4h
DRIFT_CHECK_INTERVAL_SECONDS = int(
    os.getenv("SENTINEL_DRIFT_CHECK", "3600")
)  # drift check every hour


# ── State ────────────────────────────────────────────────────────────────────


class SentinelState:
    def __init__(self):
        self.ack_machine = ACKMachine()
        self.drift_detector = DriftDetector()
        self.dispatcher = AlertDispatcher()
        self.last_vault_size = 0
        self.last_reminder_ts = 0.0
        self.last_drift_check_ts = 0.0
        self.last_vitals_ts = 0.0
        self.running = True

    def stop(self):
        self.running = False


# ── Vault999 Polling ─────────────────────────────────────────────────────────


def poll_vault999(state: SentinelState) -> int:
    """
    Poll vault999 for new entries since last check.
    Returns count of new entries processed.
    """
    path = Path(VAULT999_PATH)
    if not path.exists():
        return 0

    try:
        size = path.stat().st_size
        if size == state.last_vault_size:
            return 0
        state.last_vault_size = size

        lines = open(path, "r", encoding="utf-8").read().splitlines()
        new_entries = lines  # simplified: process all on each poll
        processed = 0

        for line in new_entries:
            if not line.strip():
                continue
            try:
                import json

                entry = json.loads(line)
            except Exception:
                continue

            # Ingest into drift detector
            state.drift_detector.ingest(entry)

            # Ingest into ACK machine
            action = state.ack_machine.ingest(entry)
            if action:
                processed += 1
                # New pending HARD_TIER verdict
                if action.startswith("HARD_PENDING:"):
                    stats = state.ack_machine.get_stats()
                    state.dispatcher.alert_reminder(
                        pending_hard=stats["pending_hard"],
                        oldest_hours=stats["oldest_pending_hours"],
                    )

        return processed

    except Exception as e:
        print(f"[SENTINEL:POLL_ERROR] {e}", file=sys.stderr)
        return 0


# ── SLA Expiry Check ──────────────────────────────────────────────────────────


def check_sla_expiry(state: SentinelState) -> None:
    """Check for expired HARD_TIER SLA verdicts and fire alerts."""
    expired = state.ack_machine.check_sla_expiry()
    now = time.time()
    for entry in expired:
        age_hours = (now - entry.ts) / 3600
        state.dispatcher.alert_sla_expiry(
            {
                "chain_hash": entry.chain_hash,
                "verdict": entry.verdict,
                "tool": entry.tool,
            },
            age_hours,
        )


# ── Drift Check ────────────────────────────────────────────────────────────────


def check_drift(state: SentinelState) -> None:
    """Run drift detection and fire alerts if threshold exceeded."""
    if time.time() - state.last_drift_check_ts < DRIFT_CHECK_INTERVAL_SECONDS:
        return
    state.last_drift_check_ts = time.time()

    vitals = state.drift_detector.compute_vitals()
    drift_flags = vitals.get("drift_flags", [])
    if drift_flags:
        state.dispatcher.alert_drift(drift_flags)

    if vitals.get("flood_attack_signal"):
        state.dispatcher.alert_flood_attack(
            vitals["anomaly_density_per_day"],
            soft_count=0,  # TODO: populate from drift_detector
            hard_count=0,
        )


# ── Periodic Reminder ─────────────────────────────────────────────────────────


def periodic_reminder(state: SentinelState) -> None:
    """Fire governance reminder if pending HARD_TIER verdicts exist."""
    now = time.time()
    if now - state.last_reminder_ts < REMINDER_INTERVAL_SECONDS:
        return
    state.last_reminder_ts = now

    stats = state.ack_machine.get_stats()
    if stats["pending_hard"] > 0:
        state.dispatcher.alert_reminder(
            stats["pending_hard"],
            stats["oldest_pending_hours"],
        )


# ── Vitals Snapshot ────────────────────────────────────────────────────────────


def vitals_snapshot(state: SentinelState) -> dict:
    """Compute and return governance vitals snapshot."""
    vitals = state.drift_detector.compute_vitals()
    stats = state.ack_machine.get_stats()
    return {
        "sentinel_version": "v2026.04.26-KANON",
        "epoch": datetime.now(timezone.utc).isoformat(),
        "ack_stats": stats,
        "drift_vitals": vitals,
        "queue_depth": state.dispatcher.get_queue_depth(),
    }


# ── Signal Handler ────────────────────────────────────────────────────────────


def setup_signal_handler(state: SentinelState):
    def handler(signum, frame):
        print(f"\n[SENTINEL:SHUTDOWN] Received signal {signum}. Stopping...")
        state.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


# ── Main Loop ─────────────────────────────────────────────────────────────────


def main():
    print(
        f"[SENTINEL:WATCH] Starting v2026.04.26-KANON at {datetime.now(timezone.utc).isoformat()}"
    )
    print(f"[SENTINEL:WATCH] Vault999: {VAULT999_PATH}")
    print(f"[SENTINEL:WATCH] Poll interval: {POLL_INTERVAL_SECONDS}s")

    state = SentinelState()
    setup_signal_handler(state)

    while state.running:
        try:
            # Poll vault999
            poll_vault999(state)

            # Check SLA expiry
            check_sla_expiry(state)

            # Check drift
            check_drift(state)

            # Periodic reminder
            periodic_reminder(state)

            # Drain alert queue
            sent = state.dispatcher.drain_queue()
            if sent > 0:
                print(f"[SENTINEL:QUEUE_DRAIN] {sent} alerts sent")

        except Exception as e:
            print(f"[SENTINEL:LOOP_ERROR] {e}", file=sys.stderr)

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
