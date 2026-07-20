"""arifosmcp/runtime/audit_fatigue.py — Vector #10 Audit Fatigue Mitigations
(1) T3DailyCounter: caps T3 approvals/24h (default 12), /root/VAULT999/t3_daily.json.
(2) ReceiptRandomizer: deep_read_probability (0.15), /root/VAULT999/deep_read_log.jsonl.
(3) ReviewConsistencyScorer: time-of-day review drift detection.
(4) Integration: check_t3_fatigue_gate() before T3 gate routes to Arif.
F1 (AMANAH) · F2 (TRUTH) · F13 (SOVEREIGN). DITEMPA BUKAN DIBERI 🔥🌎🧠🪙
"""

from __future__ import annotations

import json
import logging
import math
import random
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────
T3_DAILY_PATH: Path = Path("/root/VAULT999/t3_daily.json")
DEEP_READ_LOG_PATH: Path = Path("/root/VAULT999/deep_read_log.jsonl")
DEFAULT_T3_CAP = 12
DEFAULT_DEEP_READ_PROB = 0.15
SIGNIFICANCE_THRESHOLD = 0.05

DAYTIME_BUCKETS = {"morning", "afternoon", "evening"}
TIME_BUCKETS = [("night", 0, 6), ("morning", 6, 12), ("afternoon", 12, 18), ("evening", 18, 24)]
ReviewOutcome = Literal["approved", "rejected", "amended"]


# ── Helpers ────────────────────────────────────────────────────────────
def _utc_today() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _time_bucket(hour: int) -> str:
    for name, s, e in TIME_BUCKETS:
        if s <= hour < e:
            return name
    return "evening"


def _normal_cdf(x: float) -> float:
    """Abramowitz & Stegun 7.1.26 standard normal CDF approximation."""
    if x < 0:
        return 1 - _normal_cdf(-x)
    b = [0.31938153, -0.356563782, 1.781477937, -1.821255978, 1.330274429]
    t = 1 / (1 + 0.2316419 * x)
    poly = t * (b[0] + t * (b[1] + t * (b[2] + t * (b[3] + t * b[4]))))
    return 1 - 0.3989422804014327 * math.exp(-0.5 * x * x) * poly  # 0.3989... = 1/√(2π)


def _two_proportion_z(n1: int, p1: float, n2: int, p2: float) -> float | None:
    """Two-proportion z-test two-tailed p-value. None if insufficient data."""
    if n1 < 5 or n2 < 5:
        return None
    pp = (n1 * p1 + n2 * p2) / (n1 + n2)
    if not (0 < pp < 1):
        return None
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0
    return 2 * (1 - _normal_cdf(abs(p1 - p2) / se))


# ═══════════════════════════════════════════════════════════════════════════
# 1. T3DailyCounter
# ═══════════════════════════════════════════════════════════════════════════
class T3DailyCounter:
    """Caps sovereign T3 approvals per 24h UTC, persisted to JSON."""

    def __init__(self, cap: int = DEFAULT_T3_CAP, path: Path = T3_DAILY_PATH):
        self.cap = cap
        self.path = path

    def _read(self) -> dict:
        if not self.path.exists():
            return {"date": _utc_today(), "count": 0}
        try:
            return json.loads(self.path.read_text())
        except (json.JSONDecodeError, OSError):
            logger.warning("T3DailyCounter: corrupt state, resetting")
            return {"date": _utc_today(), "count": 0}

    def _write(self, state: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(state))

    def check_and_increment(self) -> dict[str, Any]:
        """Returns {'proceed': True/False, ...}. Cap hit → DEFER_TO_TOMORROW."""
        today = _utc_today()
        state = self._read()
        if state.get("date") != today:
            state = {"date": today, "count": 0}
        if state["count"] >= self.cap:
            logger.warning("T3DailyCounter: cap %d hit for %s", self.cap, today)
            return {
                "proceed": False,
                "count": state["count"],
                "cap": self.cap,
                "verdict": "DEFER_TO_TOMORROW",
                "date": today,
            }
        state["count"] += 1
        self._write(state)
        logger.info("T3DailyCounter: %d/%d for %s", state["count"], self.cap, today)
        return {
            "proceed": True,
            "count": state["count"],
            "remaining": self.cap - state["count"],
            "date": today,
        }

    def remaining(self) -> int:
        state = self._read()
        if state.get("date") != _utc_today():
            return self.cap
        return max(0, self.cap - state["count"])


# ═══════════════════════════════════════════════════════════════════════════
# 2. ReceiptRandomizer
# ═══════════════════════════════════════════════════════════════════════════
class ReceiptRecord(BaseModel):
    receipt_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deep_read_probability: float = DEFAULT_DEEP_READ_PROB
    selected_for_deep_read: bool = False
    deep_read_completed: bool = False
    deep_read_timestamp: datetime | None = None
    receipt_type: str = "T3"


class ReceiptRandomizer:
    """Assigns T3 receipts a deep_read_probability, tracks in append-only JSONL."""

    def __init__(
        self, probability: float = DEFAULT_DEEP_READ_PROB, path: Path = DEEP_READ_LOG_PATH
    ):
        self.probability = probability
        self.path = path

    def assign(self, receipt_type: str = "T3") -> ReceiptRecord:
        selected = random.random() < self.probability
        record = ReceiptRecord(
            deep_read_probability=self.probability,
            selected_for_deep_read=selected,
            receipt_type=receipt_type,
        )
        self._append(record)
        return record

    def mark_deep_read(self, receipt_id: str) -> bool:
        records = self._load_all()
        for i, r in enumerate(records):
            if r.receipt_id == receipt_id and not r.deep_read_completed:
                records[i] = r.model_copy(
                    update={"deep_read_completed": True, "deep_read_timestamp": datetime.now(UTC)}
                )
                self._write_all(records)
                return True
        return False

    def stats(self) -> dict[str, Any]:
        records = self._load_all()
        total = len(records)
        selected = sum(1 for r in records if r.selected_for_deep_read)
        completed = sum(1 for r in records if r.deep_read_completed)
        return {
            "total_receipts": total,
            "selected_for_deep_read": selected,
            "deep_read_completed": completed,
            "actual_deep_read_rate": round(completed / total, 4) if total else 0.0,
            "target_deep_read_rate": self.probability,
        }

    def _load_all(self) -> list[ReceiptRecord]:
        if not self.path.exists():
            return []
        results = []
        for line in self.path.read_text().strip().splitlines():
            if not line.strip():
                continue
            try:
                results.append(ReceiptRecord.model_validate_json(line))
            except Exception:
                logger.debug("ReceiptRandomizer: skipping corrupt line")
        return results

    def _append(self, record: ReceiptRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as f:
            f.write(record.model_dump_json() + "\n")

    def _write_all(self, records: list[ReceiptRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            for r in records:
                f.write(r.model_dump_json() + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# 3. ReviewConsistencyScorer
# ═══════════════════════════════════════════════════════════════════════════
class ReviewConsistencyScorer:
    """Tracks review outcomes per time-of-day bucket. Flags late-night drift."""

    def __init__(self):
        self._counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record(self, timestamp: datetime, outcome: ReviewOutcome) -> None:
        bucket = _time_bucket(timestamp.hour)
        self._counts[bucket][outcome] += 1

    def check(self) -> dict[str, Any]:
        daytime = defaultdict(int)
        for b in DAYTIME_BUCKETS:
            for o, c in self._counts[b].items():
                daytime[o] += c
        night = dict(self._counts.get("night", {}))

        dt_total, nt_total = sum(daytime.values()), sum(night.values())
        if dt_total < 10 or nt_total < 5:
            return {
                "flagged": False,
                "reason": "insufficient_data",
                "daytime_total": dt_total,
                "night_total": nt_total,
            }

        flags = []
        for outcome in ("approved", "rejected", "amended"):
            dt_rate = daytime.get(outcome, 0) / dt_total
            nt_rate = night.get(outcome, 0) / nt_total if nt_total else 0.0
            p_val = _two_proportion_z(dt_total, dt_rate, nt_total, nt_rate)
            if p_val is not None and p_val < SIGNIFICANCE_THRESHOLD:
                flags.append(
                    {
                        "outcome": outcome,
                        "daytime_rate": round(dt_rate, 4),
                        "night_rate": round(nt_rate, 4),
                        "p_value": round(p_val, 4),
                    }
                )
        return {
            "flagged": len(flags) > 0,
            "flags": flags,
            "daytime_total": dt_total,
            "night_total": nt_total,
            "significance_threshold": SIGNIFICANCE_THRESHOLD,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 4. Integration hook
# ═══════════════════════════════════════════════════════════════════════════
t3_counter = T3DailyCounter()
receipt_randomizer = ReceiptRandomizer()
review_scorer = ReviewConsistencyScorer()


def check_t3_fatigue_gate() -> dict[str, Any]:
    """Integration hook: call BEFORE any T3/888_HOLD gate routes to Arif."""
    return t3_counter.check_and_increment()


def reset_fatigue_state() -> None:
    """Reset all fatigue state (testing only)."""
    for p in (T3_DAILY_PATH, DEEP_READ_LOG_PATH):
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass
    global review_scorer
    review_scorer = ReviewConsistencyScorer()
