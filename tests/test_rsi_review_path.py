"""RSI review path — Phase 5 (FI-003, 2026-10-29).

What this locks:
- a review is an APPEND that supersedes the earlier row by decision_id; the
  earlier row stays on disk (history is never rewritten);
- a review that did not adjudicate (INCONCLUSIVE / OUTCOME_UNOBSERVED /
  INVALID_REVIEW) does NOT enter a rate denominator, and does not silently
  count as unresolved either;
- the reviewer must state identity, evidence refs and an explicit independence
  claim - none of them is inferred;
- the live verdict vocabulary is HOLD / PROCEED / SABAR / VOID (the kernel
  emits all four);
- a canary batch can be SELECTED; nothing auto-reviews.

SAFETY: these tests use temp ledgers only. The module-level
record_rsi_review() writes to the LIVE /root/VAULT999/rsi_ledger.jsonl and is
therefore NOT invoked here - only its signature is asserted.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from arifosmcp.runtime.rsi_audit import (
    DECISIVE_REVIEW_OUTCOMES,
    RSIDecisionRecord,
    RSILedger,
    record_rsi_review,
    select_review_batch,
)


def _rec(verdict: str = "HOLD", review: str = "UNRESOLVED", tool: str = "arif_judge") -> RSIDecisionRecord:
    return RSIDecisionRecord(
        tool=tool,
        original_verdict=verdict,
        reason_class="AUTHORITY",
        review_outcome=review,
    )


def _ledger(tmp_path: Path) -> RSILedger:
    return RSILedger(tmp_path / "rsi_ledger.jsonl")


# ── append-only supersede ──────────────────────────────────────────────────
def test_review_appends_and_supersedes_without_rewriting_history(tmp_path):
    led = _ledger(tmp_path)
    original = _rec()
    led.record(original)
    before = (tmp_path / "rsi_ledger.jsonl").read_text(encoding="utf-8")
    assert len([l for l in before.splitlines() if l.strip()]) == 1

    reviewed = led.record_review(
        original.decision_id,
        "CORRECT_HOLD",
        reviewed_by="555-verifier",
        evidence_refs=["/root/VAULT999/rsi_ledger.jsonl#decision"],
        independent=True,
        note="the blocked mutation was later performed under seal",
    )
    after = (tmp_path / "rsi_ledger.jsonl").read_text(encoding="utf-8")
    lines = [l for l in after.splitlines() if l.strip()]
    assert len(lines) == 2  # appended, not rewritten
    assert json.loads(lines[0])["review_outcome"] == "UNRESOLVED"  # original row intact
    assert json.loads(lines[1])["review_outcome"] == "CORRECT_HOLD"

    # the loader takes last-write-wins per decision_id
    effective = led._load_all()
    assert len(effective) == 1
    assert effective[0].review_outcome == "CORRECT_HOLD"
    assert reviewed.reviewed_by == "555-verifier"
    assert reviewed.review_evidence == ["/root/VAULT999/rsi_ledger.jsonl#decision"]
    assert reviewed.review_independent is True
    assert reviewed.review_latency_hours is not None


def test_review_of_unknown_decision_is_refused(tmp_path):
    led = _ledger(tmp_path)
    with pytest.raises(KeyError):
        led.record_review("does-not-exist", "CORRECT_HOLD", reviewed_by="x")


# ── decisive vs non-decisive ───────────────────────────────────────────────
def test_inconclusive_review_is_not_in_the_denominator(tmp_path):
    led = _ledger(tmp_path)
    original = _rec()
    led.record(original)
    led.record_review(original.decision_id, "INCONCLUSIVE", reviewed_by="555-verifier", note="no post-hoc evidence")
    stats = led.stats()
    assert stats["reviewed_count"] == 0  # decided nothing
    assert stats["unresolved_count"] == 0  # and it is no longer "unreviewed" either
    assert stats["confusion_matrix"]["INCONCLUSIVE"] == 1
    assert stats["false_hold_rate"] == "UNMEASURED"
    assert stats["false_hold_rate_status"] == "UNKNOWN"
    assert stats["total_records"] == 1


def test_outcome_unobserved_and_invalid_review_are_counted_separately(tmp_path):
    led = _ledger(tmp_path)
    a = _rec()
    b = _rec(tool="other_tool")
    led.record(a)
    led.record(b)
    led.record_review(a.decision_id, "OUTCOME_UNOBSERVED", reviewed_by="r1")
    led.record_review(b.decision_id, "INVALID_REVIEW", reviewed_by="r1")
    stats = led.stats()
    assert stats["confusion_matrix"]["OUTCOME_UNOBSERVED"] == 1
    assert stats["confusion_matrix"]["INVALID_REVIEW"] == 1
    assert stats["reviewed_count"] == 0
    assert stats["unresolved_count"] == 0


def test_correct_decision_counts_against_the_verdict_it_judged(tmp_path):
    led = _ledger(tmp_path)
    h = _rec(verdict="HOLD")
    p = _rec(verdict="PROCEED")
    led.record(h)
    led.record(p)
    led.record_review(h.decision_id, "CORRECT_DECISION", reviewed_by="r")
    led.record_review(p.decision_id, "CORRECT_DECISION", reviewed_by="r")
    stats = led.stats()
    assert stats["confusion_matrix"]["CORRECT_HOLD"] == 1
    assert stats["confusion_matrix"]["CORRECT_PROCEED"] == 1
    assert stats["confusion_matrix"]["CORRECT_DECISION"] == 2
    assert stats["reviewed_count"] == 2


def test_decisive_outcomes_exclude_non_decisive_ones(tmp_path):
    assert "CORRECT_HOLD" in DECISIVE_REVIEW_OUTCOMES
    assert "INCONCLUSIVE" not in DECISIVE_REVIEW_OUTCOMES
    assert "OUTCOME_UNOBSERVED" not in DECISIVE_REVIEW_OUTCOMES
    assert "INVALID_REVIEW" not in DECISIVE_REVIEW_OUTCOMES
    assert "UNRESOLVED" not in DECISIVE_REVIEW_OUTCOMES


# ── live verdict vocabulary ────────────────────────────────────────────────
@pytest.mark.parametrize("verdict", ["HOLD", "PROCEED", "SABAR", "VOID"])
def test_record_supports_the_live_verdict_vocabulary(tmp_path, verdict):
    led = _ledger(tmp_path)
    rec = _rec(verdict=verdict)
    led.record(rec)
    assert rec.original_verdict == verdict
    assert led.stats()["total_records"] == 1


# ── independence is claimed, never inferred ────────────────────────────────
def test_independence_claim_is_explicit(tmp_path):
    led = _ledger(tmp_path)
    rec = _rec()
    led.record(rec)
    reviewed = led.record_review(rec.decision_id, "CORRECT_HOLD", reviewed_by="same-actor")
    assert reviewed.review_independent is None  # not claimed
    reviewed2 = led.record_review(rec.decision_id, "FALSE_HOLD", reviewed_by="x", independent=False)
    assert reviewed2.review_independent is False


# ── canary selection ───────────────────────────────────────────────────────
def test_select_review_batch_returns_a_small_stratified_batch(tmp_path):
    led = _ledger(tmp_path)
    for i in range(12):
        led.record(_rec(tool=f"tool-{i % 3}"))
    batch = led.select_review_batch(3)
    assert len(batch) == 3
    assert all(r.review_outcome == "UNRESOLVED" for r in batch)


def test_module_level_entry_points_exist_but_are_not_run_here():
    # These write to the LIVE ledger - signature only, never executed in tests.
    assert "decision_id" in inspect.signature(record_rsi_review).parameters
    assert "review_outcome" in inspect.signature(record_rsi_review).parameters
    assert "reviewed_by" in inspect.signature(record_rsi_review).parameters
    assert "n" in inspect.signature(select_review_batch).parameters


# ── D2 / D3: published counts (555-verifier findings) ──────────────────────
def test_stats_publishes_disk_rows_and_effective_decisions_separately(tmp_path):
    led = _ledger(tmp_path)
    rec = _rec()
    led.record(rec)
    led.record_review(rec.decision_id, "CORRECT_HOLD", reviewed_by="r", independent=True)
    stats = led.stats()
    assert stats["total_records"] == 1        # effective decisions
    assert stats["ledger_rows"] == 2         # rows on disk (append-only)
    assert stats["reviewed_count"] == 1


def test_stats_exposes_reviewer_independence(tmp_path):
    led = _ledger(tmp_path)
    a = _rec()
    b = _rec(tool="t2")
    c = _rec(tool="t3")
    led.record(a)
    led.record(b)
    led.record(c)
    led.record_review(a.decision_id, "CORRECT_HOLD", reviewed_by="r", independent=True)
    led.record_review(b.decision_id, "CORRECT_HOLD", reviewed_by="r", independent=False)
    led.record_review(c.decision_id, "INCONCLUSIVE", reviewed_by="r")
    stats = led.stats()
    assert stats["independent_reviews"] == 1
    assert stats["non_independent_reviews"] == 1
    assert stats["reviews_without_independence_claim"] == 1
