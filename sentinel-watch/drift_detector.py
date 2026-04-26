"""
SENTINEL-WATCH — Drift Detector
==============================
Tracks SLA baseline over 30-day rolling window.
Flags >20% deviation from baseline.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import json
import os
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DRIFT_THRESHOLD = 0.20  # 20% upward deviation → alert
ROLLING_WINDOW_DAYS = 30
BASELINE_CHECKPOINT_FILE = "/root/arifOS/sentinel-watch/baseline_checkpoint.jsonl"


@dataclass
class BaselineSnapshot:
    ts: float
    hard_median_latency_hours: float
    soft_median_latency_hours: float
    hard_ack_rate: float      # fraction acked within SLA
    soft_ack_rate: float
    anomaly_density_per_day: float
    snapshot_id: str


class DriftDetector:
    """
    Monitors SLA norm drift over rolling 30-day window.
    Detects:
    - ACK latency drift (SLA norm erosion)
    - Variance collapse (ritualized acknowledgment pattern)
    - Anomaly density spikes (strategic flooding)
    - Cross-tier coupling (soft spike + hard latency rise = flooding attack)
    """

    def __init__(self):
        self.entries: deque[dict] = deque(maxlen=5000)  # rolling vault999 entries
        self.ack_records: deque[dict] = deque(maxlen=1000)  # ACK events
        self.snapshots: list[BaselineSnapshot] = []
        self._load_checkpoint()

    # ── Ingest vault999 entries ───────────────────────────────────────────

    def ingest(self, entry: dict) -> None:
        """Ingest a vault999 entry for drift tracking."""
        self.entries.append(entry)

    def ingest_ack(self, chain_hash: str, ack_ts: float) -> None:
        """Record an ACK event."""
        self.ack_records.append({
            "chain_hash": chain_hash,
            "ack_ts": ack_ts,
            "ingested_at": time.time(),
        })

    # ── Compute current vitals ────────────────────────────────────────────

    def _get_latency_hours(self, entry: dict) -> Optional[float]:
        """Compute hours from verdict to ACK for an entry. None if not acked."""
        verdict_ts = entry.get("ts")
        ack_rec = next(
            (r for r in self.ack_records if r["chain_hash"] == entry.get("chain_hash")),
            None
        )
        if not ack_rec:
            return None
        return (ack_rec["ack_ts"] - verdict_ts) / 3600 if verdict_ts else None

    def _get_recent_entries(self, days: int = ROLLING_WINDOW_DAYS) -> list[dict]:
        cutoff = time.time() - (days * 86400)
        return [e for e in self.entries if e.get("ts", 0) >= cutoff]

    def compute_vitals(self) -> dict:
        """
        Compute governance vitals from rolling window.
        Returns: latency, variance, density signals.
        """
        recent = self._get_recent_entries()
        if not recent:
            return {
                "hard_latency_hours": None,
                "soft_latency_hours": None,
                "hard_ack_variance": None,
                "soft_ack_variance": None,
                "anomaly_density_per_day": 0.0,
                "hard_ack_rate": None,
                "soft_ack_rate": None,
                "drift_flags": [],
                "flood_attack_signal": False,
            }

        HARD_FLOORS = {"F13", "F1", "F2", "F6", "F9", "F10"}
        SOFT_FLOORS = {"F3", "F4", "F5", "F7", "F8", "F11", "F12"}

        hard_entries = []
        soft_entries = []
        for e in recent:
            floors = e.get("payload", {}).get("floors_triggered", [])
            if set(floors) & HARD_FLOORS:
                hard_entries.append(e)
            elif set(floors) & SOFT_FLOORS:
                soft_entries.append(e)

        def median(values: list[float]) -> Optional[float]:
            if not values:
                return None
            s = sorted(values)
            n = len(s)
            return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

        def variance(values: list[float]) -> Optional[float]:
            if len(values) < 2:
                return None
            mean = sum(values) / len(values)
            return sum((v - mean) ** 2 for v in values) / len(values)

        hard_latencies = []
        soft_latencies = []
        for e in hard_entries:
            lat = self._get_latency_hours(e)
            if lat is not None:
                hard_latencies.append(lat)
        for e in soft_entries:
            lat = self._get_latency_hours(e)
            if lat is not None:
                soft_latencies.append(lat)

        # Anomaly density: count HOLD_888 / VOID per day
        anomaly_count = sum(
            1 for e in recent
            if e.get("verdict") in ("HOLD_888", "VOID") or e.get("event_type") == "888_JUDGE_EXECUTION"
        )
        days_span = (time.time() - min((e["ts"] for e in recent), default=time.time())) / 86400 or 1
        density_per_day = anomaly_count / days_span

        hard_ack_rate = len([l for l in hard_latencies if l is not None and l <= 4]) / max(len(hard_entries), 1)
        soft_ack_rate = len([l for l in soft_latencies if l is not None and l <= 24]) / max(len(soft_entries), 1)

        return {
            "hard_latency_hours": round(median(hard_latencies) or 0, 2),
            "soft_latency_hours": round(median(soft_latencies) or 0, 2),
            "hard_ack_variance": round(variance(hard_latencies) or 0, 3),
            "soft_ack_variance": round(variance(soft_latencies) or 0, 3),
            "anomaly_density_per_day": round(density_per_day, 2),
            "hard_ack_rate": round(hard_ack_rate, 2),
            "soft_ack_rate": round(soft_ack_rate, 2),
            "drift_flags": self._detect_drift(),
            "flood_attack_signal": self._flood_attack_signal(hard_entries, soft_entries, density_per_day),
        }

    # ── Drift Detection ───────────────────────────────────────────────────

    def _detect_drift(self) -> list[str]:
        """Compare current vitals against last baseline snapshot."""
        if not self.snapshots:
            return []
        baseline = self.snapshots[-1]
        current = self.compute_vitals()
        flags = []

        # Latency drift
        if current["hard_latency_hours"] and baseline.hard_median_latency_hours:
            delta = (current["hard_latency_hours"] - baseline.hard_median_latency_hours) / max(baseline.hard_median_latency_hours, 0.01)
            if delta > DRIFT_THRESHOLD:
                flags.append(f"HARD_LATENCY_DRIFT:+{round(delta*100,1)}% (baseline={baseline.hard_median_latency_hours}h, current={current['hard_latency_hours']}h)")

        if current["soft_latency_hours"] and baseline.soft_median_latency_hours:
            delta = (current["soft_latency_hours"] - baseline.soft_median_latency_hours) / max(baseline.soft_median_latency_hours, 0.01)
            if delta > DRIFT_THRESHOLD:
                flags.append(f"SOFT_LATENCY_DRIFT:+{round(delta*100,1)}%")

        # Ack rate collapse
        if current["hard_ack_rate"] and baseline.hard_ack_rate:
            erosion = baseline.hard_ack_rate - current["hard_ack_rate"]
            if erosion > DRIFT_THRESHOLD:
                flags.append(f"HARD_ACK_RATE_EROSION:-{round(erosion*100,1)}%")

        # Variance collapse (too little variance = ritualized)
        if current["hard_ack_variance"] is not None and current["hard_ack_variance"] < 0.01 and baseline.hard_ack_rate > 0.8:
            flags.append("VARIANCE_COLLAPSE:Suspiciously uniform hard-tier ACK latency — possible ritualization")

        return flags

    def _flood_attack_signal(self, hard_entries: list, soft_entries: list, density: float) -> bool:
        """Soft-tier spike + hard-tier latency rise = flooding attack pattern."""
        recent = self._get_recent_entries(days=1)
        if not recent:
            return False
        soft_today = sum(1 for e in recent if e.get("payload", {}).get("floors_triggered") and not (set(e["payload"]["floors_triggered"]) & {"F13", "F1", "F2", "F6", "F9", "F10"}))
        hard_today = sum(1 for e in recent if set(e.get("payload", {}).get("floors_triggered", [])) & {"F13", "F1", "F2", "F6", "F9", "F10"})
        if soft_today > hard_today * 3 and density > 2.0:
            return True
        return False

    # ── Baseline Snapshot ───────────────────────────────────────────────────

    def take_snapshot(self) -> BaselineSnapshot:
        """Take a governance baseline snapshot. Requires sovereign re-affirmation."""
        v = self.compute_vitals()
        snap = BaselineSnapshot(
            ts=time.time(),
            hard_median_latency_hours=v["hard_latency_hours"] or 0,
            soft_median_latency_hours=v["soft_latency_hours"] or 0,
            hard_ack_rate=v["hard_ack_rate"] or 0,
            soft_ack_rate=v["soft_ack_rate"] or 0,
            anomaly_density_per_day=v["anomaly_density_per_day"] or 0,
            snapshot_id=f"snap_{int(time.time())}",
        )
        self.snapshots.append(snap)
        self._save_checkpoint()
        return snap

    # ── Checkpoint Persistence ───────────────────────────────────────────

    def _checkpoint_path(self) -> Path:
        return Path(BASELINE_CHECKPOINT_FILE)

    def _load_checkpoint(self) -> None:
        p = self._checkpoint_path()
        if not p.exists():
            return
        try:
            lines = open(p).read().splitlines()
            for line in lines:
                if line.strip():
                    s = json.loads(line)
                    self.snapshots.append(BaselineSnapshot(**s))
        except Exception:
            pass

    def _save_checkpoint(self) -> None:
        p = self._checkpoint_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(asdict(s)) for s in self.snapshots]
        open(p, "w").write("\n".join(lines) + "\n")


from dataclasses import dataclass, asdict
