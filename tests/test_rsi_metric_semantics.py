"""RSI metric semantics — an unmeasured rate is never 0.0 (FI-003, 2026-10-29).

Contract locked here (mirrors tests/test_memory_audit_zero_laundering.py,
333-AGI 2026-10-28 — F2 TRUTH: unknown is never 0.0, never a bare null):

- A rate whose denominator holds no REVIEWED example is UNMEASURED, with an
  explicit status (UNKNOWN / INSUFFICIENT / INVALID_INPUT) and a reason code.
- 0.0 is a reading; "nobody reviewed" is not a reading.
- numerator and denominator always travel with the value.
- No composite score may contain an unmeasured term.
- Historical rows are never rewritten — these tests use their own temp ledgers.

Why (measured 2026-10-29): the live ledger held 14193 HOLD records with
review_outcome UNRESOLVED on every row, so false_hold_rate computed 0.0 —
reading as PERFECT governance purely by omission.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.runtime.act_token import UNMEASURED
from arifosmcp.runtime.rsi_audit import (
    METRIC_STATUS_INSUFFICIENT,
    METRIC_STATUS_INVALID_INPUT,
    METRIC_STATUS_MEASURED,
    METRIC_STATUS_UNKNOWN,
    RSIDecisionRecord,
    RSILedger,
    RSIScorer,
)


def _rec(
    verdict: str = "HOLD",
    review: str = "UNRESOLVED",
    tool: str = "arif_judge",
    reason: str = "AUTHORITY",
) -> RSIDecisionRecord:
    return RSIDecisionRecord(
        tool=tool,
        original_verdict=verdict,
        reason_class=reason,
        review_outcome=review,
    )


def _ledger(tmp_path: Path, rows: list[dict]) -> RSILedger:
    p = tmp_path / "rsi_ledger.jsonl"
    with open(p, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return RSILedger(p)


def _raw(**over) -> dict:
    base = {
        "decision_id": "d1",
        "timestamp": "2026-10-29T00:00:00Z",
        "tool": "arif_judge",
        "original_verdict": "HOLD",
        "reason_class": "AUTHORITY",
        "review_outcome": "UNRESOLVED",
        "review_latency_hours": None,
        "evidence_available_at_decision": [],
        "evidence_available_post_hoc": [],
        "severity_weight": 1.0,
    }
    base.update(over)
    return base


# ── 1. no records ───────────────────────────────────────────────────────────
def test_empty_ledger_is_unknown_not_zero(tmp_path):
    stats = RSILedger(tmp_path / "empty.jsonl").stats()
    assert stats["false_hold_rate"] == UNMEASURED
    assert stats["false_proceed_rate"] == UNMEASURED
    assert stats["false_hold_rate_status"] == METRIC_STATUS_UNKNOWN
    assert stats["false_hold_rate_reason"] == "NO_RECORDS"
    assert stats["metric_status"] == METRIC_STATUS_UNKNOWN
    assert stats["total_records"] == 0


# ── 2. HOLD-only, no reviews ────────────────────────────────────────────────
def test_hold_only_without_reviews_is_unmeasured(tmp_path):
    led = _ledger(tmp_path, [_raw(), _raw(decision_id="d2")])
    stats = led.stats()
    assert stats["false_hold_rate"] == UNMEASURED
    assert stats["false_hold_rate"] != 0.0  # the laundering this test exists to prevent
    assert stats["false_hold_rate_status"] == METRIC_STATUS_UNKNOWN
    assert stats["false_hold_rate_reason"] == "NO_REVIEWED_HOLDS"
    assert stats["false_hold_rate_denominator"] == 0
    assert stats["reviewed_count"] == 0
    assert stats["unresolved_count"] == 2
    # the unresolved ratio IS measurable — 1.0 is a true reading
    assert stats["unresolved_hold_rate"] == 1.0
    assert stats["unresolved_hold_rate_numerator"] == 2
    assert stats["unresolved_hold_rate_denominator"] == 2


# ── 3. PROCEED-only, no reviews ─────────────────────────────────────────────
def test_proceed_only_without_reviews_is_unmeasured(tmp_path):
    led = _ledger(tmp_path, [_raw(original_verdict="PROCEED")])
    stats = led.stats()
    assert stats["false_proceed_rate"] == UNMEASURED
    assert stats["false_proceed_rate_status"] == METRIC_STATUS_UNKNOWN
    assert stats["false_proceed_rate_reason"] == "NO_REVIEWED_PROCEEDS"
    assert stats["false_hold_rate"] == UNMEASURED


# ── 4. mixed reviewed records ───────────────────────────────────────────────
def test_reviewed_records_produce_a_real_rate_with_denominator(tmp_path):
    rows = [_raw(decision_id=f"h{i}", review_outcome="CORRECT_HOLD") for i in range(30)]
    rows += [_raw(decision_id=f"f{i}", review_outcome="FALSE_HOLD") for i in range(10)]
    stats = _ledger(tmp_path, rows).stats()
    assert stats["false_hold_rate"] == 0.25
    assert stats["false_hold_rate_status"] == METRIC_STATUS_MEASURED
    assert stats["false_hold_rate_numerator"] == 10
    assert stats["false_hold_rate_denominator"] == 40
    assert stats["reviewed_count"] == 40


def test_small_reviewed_sample_is_insufficient_not_measured(tmp_path):
    rows = [_raw(decision_id=f"h{i}", review_outcome="CORRECT_HOLD") for i in range(3)]
    stats = _ledger(tmp_path, rows).stats()
    assert stats["false_hold_rate_status"] == METRIC_STATUS_INSUFFICIENT
    assert stats["false_hold_rate_reason"] == "BELOW_CALIBRATION_MINIMUM"
    assert stats["false_hold_rate_numerator"] == 0
    assert stats["false_hold_rate_denominator"] == 3


# ── 5. unresolved records ───────────────────────────────────────────────────
def test_unresolved_records_are_counted_not_folded(tmp_path):
    rows = [_raw(decision_id="u1"), _raw(decision_id="h1", review_outcome="CORRECT_HOLD")]
    stats = _ledger(tmp_path, rows).stats()
    assert stats["unresolved_count"] == 1
    assert stats["reviewed_count"] == 1
    assert stats["total_records"] == 2
    assert stats["unresolved_hold_rate"] == 0.5
    assert stats["unresolved_hold_rate_numerator"] == 1
    assert stats["unresolved_hold_rate_denominator"] == 2


# ── 6. malformed records ────────────────────────────────────────────────────
def test_malformed_row_is_counted_as_invalid_not_silently_dropped(tmp_path):
    p = tmp_path / "rsi_ledger.jsonl"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(_raw()) + "\n")
        fh.write("{not json at all\n")
    stats = RSILedger(p).stats()
    assert stats["invalid_records"] == 1
    assert stats["total_records"] == 1
    assert stats["false_hold_rate_status"] == METRIC_STATUS_INVALID_INPUT
    assert stats["false_hold_rate_reason"] == "INVALID_REVIEW_RECORDS"
    assert stats["false_hold_rate"] == UNMEASURED


# ── 7. unknown verdict class ────────────────────────────────────────────────
def test_unknown_review_verdict_class_is_invalid_input(tmp_path):
    led = _ledger(tmp_path, [_raw(review_outcome="MAYBE_PESSIMISTIC")])
    stats = led.stats()
    assert stats["invalid_records"] == 1
    assert stats["total_records"] == 0
    assert stats["false_hold_rate"] == UNMEASURED
    assert stats["false_hold_rate_status"] == METRIC_STATUS_INVALID_INPUT


# ── 8. no composite may contain an unmeasured term ──────────────────────────
def test_calibrated_score_absent_when_a_rate_is_unmeasured(tmp_path):
    rows = [
        _raw(decision_id=f"p{i}", original_verdict="PROCEED", review_outcome="CORRECT_PROCEED")
        for i in range(30)
    ]
    led = _ledger(tmp_path, rows)
    scorer = RSIScorer(led)
    assert scorer.false_proceed_rate == 0.0  # measured: 0 of 30 were wrong
    assert scorer.false_hold_rate == UNMEASURED  # no reviewed HOLD exists
    assert scorer.calibrated_score is None  # no composite over an unmeasured term


def test_profile_exposes_denominators_and_status(tmp_path):
    led = _ledger(tmp_path, [_raw()])
    profile = RSIScorer(led).profile()
    assert profile["false_hold_rate_status"] == METRIC_STATUS_UNKNOWN
    assert profile["false_hold_rate_denominator"] == 0
    assert profile["unresolved_hold_rate_denominator"] == 1
    assert profile["metric_status"] in {
        METRIC_STATUS_MEASURED,
        METRIC_STATUS_UNKNOWN,
        METRIC_STATUS_INSUFFICIENT,
        METRIC_STATUS_INVALID_INPUT,
    }
    assert profile["invalid_records"] == 0


@pytest.mark.parametrize("verdict", ["HOLD", "PROCEED"])
def test_ledger_append_never_rewrites_history(tmp_path, verdict):
    led = RSILedger(tmp_path / "append.jsonl")
    led.record(_rec(verdict=verdict))
    led.record(_rec(verdict=verdict, review="CORRECT_HOLD" if verdict == "HOLD" else "CORRECT_PROCEED"))
    lines = [
        l for l in (tmp_path / "append.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()
    ]
    assert len(lines) == 2  # append-only, both rows survive
