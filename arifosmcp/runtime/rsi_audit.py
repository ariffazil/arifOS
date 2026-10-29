"""
arifosmcp/runtime/rsi_audit.py — RSI Stop-Correctness Audit Module
═══════════════════════════════════════════════════════════════════

Fable5 Audit — Confusion Matrix + Stratified Sampling + Derived Scoring
for the arifOS HOLD/PROCEED verdict pipeline.

DOCTRINE: "Time heals = HARAM" — RSI calibration is NOT passive aging.
Every HOLD is a cost. Every un-reviewed HOLD is an unresolved debt.
Review must be ACTIVE: scheduled, sampled, scored, and escalated.
The ledger is append-only. The sampler is stratified. The scorer
is multi-dimensional — NEVER reduced to a single number without
calibration guard (≥30 reviewed records required for calibrated_score).

Architecture:
  RSIDecisionRecord   — Pydantic v2 confusion-matrix row
  RSILedger           — Append-only JSONL at /root/VAULT999/rsi_ledger.jsonl
  StratifiedSampler   — Multi-strata audit batch selection
  RSIScorer           — Derived scoring (false_proceed_rate, false_hold_rate, …)
  record_rsi_decision — Integration hook for tools.py HOLD/PROCEED calls

Floors engaged: F1 (AMANAH — review is reversible-first), F2 (TRUTH —
every verdict gets an evidence trail), F11 (AUTH — ledger integrity).
F13 SOVEREIGN: calibrated_score is advisory only; Arif decides.

DITEMPA BUKAN DIBERI — Forged, Not Given 🔥🌎🧠🪙
"""

from __future__ import annotations

import json
import logging
import uuid
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

LEDGER_PATH: Path = Path("/root/VAULT999/rsi_ledger.jsonl")
CALIBRATION_MINIMUM: int = 30  # minimum reviewed records for calibrated_score

# ── Metric semantics (F2 TRUTH: an unmeasured rate is never 0.0) ─────────────
# House rule (333-AGI, 2026-10-28): arifosmcp/runtime/act_token.UNMEASURED +
# tests/test_memory_audit_zero_laundering.py. A rate whose denominator holds no
# REVIEWED example is UNMEASURED, never 0.0 — 0.0 is a reading, "nobody
# reviewed" is not.
#
# Why this exists (FI-003 audit, 2026-10-29): the live ledger held 14193 HOLD
# records with review_outcome UNRESOLVED on every row, so false_hold_rate
# computed 0.0 — reading as PERFECT governance purely because nobody reviewed.
# That number laundered an absence; it was not a measurement.
from arifosmcp.runtime.act_token import UNMEASURED

METRIC_STATUS_MEASURED = "MEASURED"
METRIC_STATUS_UNKNOWN = "UNKNOWN"
METRIC_STATUS_INSUFFICIENT = "INSUFFICIENT"
METRIC_STATUS_INVALID_INPUT = "INVALID_INPUT"

# A review that ADJUDICATES a decision. Reviews that happened but did not
# decide (INCONCLUSIVE / OUTCOME_UNOBSERVED / INVALID_REVIEW) are real
# reviews, but they must never enter a rate denominator - a rate is a
# statement about decisions, and an undecided decision is not a data point
# (FI-003, 2026-10-29, Phase 5).
DECISIVE_REVIEW_OUTCOMES = frozenset(
    {
        "CORRECT_HOLD",
        "FALSE_HOLD",
        "CORRECT_PROCEED",
        "FALSE_PROCEED",
        "CORRECT_SABAR",
        "FALSE_SABAR",
        "CORRECT_VOID",
        "FALSE_VOID",
        "CORRECT_DECISION",
    }
)


def _rate(
    numerator: int,
    denominator: int,
    *,
    no_reviewed_reason: str,
    invalid_records: int = 0,
) -> dict:
    """Build one rate with an explicit, non-laundered status.

    value is UNMEASURED when no reviewed example backs the denominator.
    status is MEASURED / UNKNOWN / INSUFFICIENT / INVALID_INPUT.
    numerator and denominator always travel with the value.
    """
    if denominator > 0:
        sufficient = denominator >= CALIBRATION_MINIMUM
        return {
            "value": round(numerator / denominator, 4),
            "status": METRIC_STATUS_MEASURED if sufficient else METRIC_STATUS_INSUFFICIENT,
            "reason": None if sufficient else "BELOW_CALIBRATION_MINIMUM",
            "numerator": numerator,
            "denominator": denominator,
        }
    if invalid_records > 0:
        return {
            "value": UNMEASURED,
            "status": METRIC_STATUS_INVALID_INPUT,
            "reason": "INVALID_REVIEW_RECORDS",
            "numerator": numerator,
            "denominator": 0,
        }
    return {
        "value": UNMEASURED,
        "status": METRIC_STATUS_UNKNOWN,
        "reason": no_reviewed_reason,
        "numerator": numerator,
        "denominator": 0,
    }

# Review outcome literals that count as "reviewed" (definitively adjudicated)
REVIEWED_OUTCOMES: set[str] = {
    "CORRECT_HOLD",
    "FALSE_HOLD",
    "CORRECT_PROCEED",
    "FALSE_PROCEED",
}


# ═══════════════════════════════════════════════════════════════════════════
# 1. Confusion Matrix Schema — RSIDecisionRecord
# ═══════════════════════════════════════════════════════════════════════════


class RSIDecisionRecord(BaseModel):
    """A single HOLD/PROCEED decision tracked for RSI stop-correctness audit.

    Each record is one row in the confusion matrix. The review_outcome
    field starts as UNRESOLVED and is updated post-hoc after human (F13)
    or automated review.
    """

    decision_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for this decision record (UUID v4)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the original HOLD/PROCEED verdict was issued",
    )
    tool: str = Field(
        ...,
        description="Which tool issued the verdict (e.g. 'arif_judge', 'arif_seal')",
    )
    original_verdict: Literal["HOLD", "PROCEED", "SABAR", "VOID"] = Field(
        ...,
        description="The original verdict issued by the tool",
    )
    reason_class: Literal["AUTHORITY", "EVIDENCE", "SAFETY", "TOOL_FAILURE", "UNCERTAINTY"] = Field(
        ...,
        description="Classification of why HOLD/PROCEED was issued",
    )
    review_outcome: Literal[
        "CORRECT_HOLD",
        "FALSE_HOLD",
        "CORRECT_PROCEED",
        "FALSE_PROCEED",
        "CORRECT_SABAR",
        "FALSE_SABAR",
        "CORRECT_VOID",
        "FALSE_VOID",
        "CORRECT_DECISION",
        "INCONCLUSIVE",
        "OUTCOME_UNOBSERVED",
        "INVALID_REVIEW",
        "UNRESOLVED",
    ] = Field(
        default="UNRESOLVED",
        description="Post-hoc review outcome — starts UNRESOLVED",
    )
    review_latency_hours: float | None = Field(
        default=None,
        description="Hours between original decision and review completion",
    )
    reviewed_by: str | None = Field(
        default=None,
        description="Who performed the review (identity, not a role label)",
    )
    review_evidence: list[str] = Field(
        default_factory=list,
        description="Evidence refs the review relied on (post-hoc or independent)",
    )
    review_independent: bool | None = Field(
        default=None,
        description=(
            "Whether the reviewer claims independence from the original decider. "
            "None = not claimed; False = same actor/failure domain. Counted and "
            "exposed, never silently assumed."
        ),
    )
    review_note: str | None = Field(
        default=None,
        description="Reviewer's own reasoning, including why INCONCLUSIVE",
    )
    evidence_available_at_decision: list[str] = Field(
        default_factory=list,
        description="Evidence sources available when the decision was made",
    )
    evidence_available_post_hoc: list[str] = Field(
        default_factory=list,
        description="Evidence sources discovered/available after the decision",
    )
    severity_weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Cost weight — 1.0 default, higher for high-cost blocked actions",
    )

    @field_validator("review_latency_hours")
    @classmethod
    def _latency_must_be_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            raise ValueError(f"review_latency_hours must be >= 0, got {v}")
        return v

    @property
    def is_reviewed(self) -> bool:
        """True only when the review ADJUDICATED the decision.

        INCONCLUSIVE / OUTCOME_UNOBSERVED / INVALID_REVIEW are reviews that
        happened but decided nothing, so they stay out of the rate
        denominators (2026-10-29, Phase 5).
        """
        return self.review_outcome in DECISIVE_REVIEW_OUTCOMES

    @property
    def is_hold(self) -> bool:
        """True if the original verdict was HOLD."""
        return self.original_verdict == "HOLD"

    @property
    def is_unresolved_hold(self) -> bool:
        """True if HOLD verdict that has not yet been reviewed."""
        return self.is_hold and self.review_outcome == "UNRESOLVED"

    def to_jsonl(self) -> str:
        """Serialize to a single JSONL line (with model_dump by='json' for datetime)."""
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False) + "\n"


# ═══════════════════════════════════════════════════════════════════════════
# 2. RSILedger — Append-Only Ledger
# ═══════════════════════════════════════════════════════════════════════════


class RSILedger:
    """Append-only JSONL ledger for RSI decision records.

    Stored at /root/VAULT999/rsi_ledger.jsonl.
    Every write is an append. No deletes. No in-place edits.
    Audit trails are reconstructed from the immutable append log.

    Usage:
        ledger = RSILedger()
        ledger.record(decision)           # append one
        unresolved = ledger.pending_review()   # get UNRESOLVED records
        stats = ledger.stats()            # compute rates and confusion matrix
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self._path = Path(path) if path else LEDGER_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, decision: RSIDecisionRecord) -> None:
        """Append a single RSIDecisionRecord to the ledger (append-only)."""
        line = decision.to_jsonl()
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(line)
        logger.debug(
            "rsi_ledger: recorded %s verdict=%s reason=%s weight=%.2f",
            decision.decision_id,
            decision.original_verdict,
            decision.reason_class,
            decision.severity_weight,
        )

    def _load_all(self) -> list[RSIDecisionRecord]:
        """Load all records from the JSONL ledger."""
        records, _ = self._load_all_with_invalid()
        return records

    def _load_all_with_invalid(self) -> tuple[list[RSIDecisionRecord], int]:
        """Load records and count the rows that could not be parsed.

        A malformed row is evidence, not noise to be dropped in silence: the
        count feeds the INVALID_INPUT metric status (2026-10-29 audit).
        """
        records: list[RSIDecisionRecord] = []
        invalid = 0
        if not self._path.exists():
            return records, invalid
        with open(self._path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(RSIDecisionRecord.model_validate_json(line))
                except Exception:
                    invalid += 1
                    logger.warning("rsi_ledger: skipping corrupt line in %s", self._path)

        # Append-only supersede: a review row appended for an earlier
        # decision has the same decision_id and is the later truth for that
        # decision. The earlier row stays on disk — history is never
        # rewritten, only superseded (2026-10-29, Phase 5).
        effective: dict[str, RSIDecisionRecord] = {}
        for rec in records:
            effective[rec.decision_id] = rec
        return list(effective.values()), invalid

    def record_review(
        self,
        decision_id: str,
        review_outcome: str,
        *,
        reviewed_by: str,
        evidence_refs: list[str] | None = None,
        independent: bool | None = None,
        note: str = "",
    ) -> RSIDecisionRecord:
        """Append a REVIEW row that supersedes an earlier decision row.

        Append-only: the original row is never rewritten on disk. The review
        row carries the same decision_id and the loader takes last-write-wins,
        so the decision's effective review outcome changes without history
        being edited (2026-10-29, Phase 5).

        The reviewer must state WHO they are and WHAT evidence they used.
        `independent` is an explicit claim, not an inference: None means the
        reviewer did not claim independence, False means same actor or
        failure domain. Both are counted and exposed by stats().
        """
        effective = {r.decision_id: r for r in self._load_all()}
        original = effective.get(decision_id)
        if original is None:
            raise KeyError(f"no RSI decision with id {decision_id!r}")

        latency: float | None = None
        try:
            elapsed = datetime.now(UTC) - original.timestamp
            latency = round(elapsed.total_seconds() / 3600.0, 2)
        except Exception:  # noqa: BLE001 — latency is metadata, never a blocker
            latency = None

        reviewed = original.model_copy(
            update={
                "review_outcome": review_outcome,
                "reviewed_by": reviewed_by,
                "review_evidence": list(evidence_refs or []),
                "review_independent": independent,
                "review_note": note or None,
                "review_latency_hours": latency,
            }
        )
        self.record(reviewed)
        logger.info(
            "rsi_ledger: review %s -> %s by %s (independent=%s)",
            decision_id[:8],
            review_outcome,
            reviewed_by,
            independent,
        )
        return reviewed

    def select_review_batch(self, n: int = 10) -> list[RSIDecisionRecord]:
        """Select a stratified canary batch for REVIEW. Never auto-reviews.

        The 14193 historical HOLD rows are NOT to be bulk-reviewed. A small
        stratified batch is selected so the first reviews test the review
        contract itself, not the population (2026-10-29, Phase 5).
        """
        return StratifiedSampler(self).select_batch(n=n)

    def raw_row_count(self) -> int:
        """Number of ROWS on disk (not effective decisions).

        The ledger is append-only: a review appends a row, so the file holds
        one row per review on top of one row per decision. stats() publishes
        both numbers so `wc -l` and total_records can never be confused
        (2026-10-29, 555-verifier finding D2).
        """
        if not self._path.exists():
            return 0
        with open(self._path, encoding="utf-8") as fh:
            return sum(1 for line in fh if line.strip())

    def pending_review(self) -> list[RSIDecisionRecord]:
        """Return all records whose review_outcome is UNRESOLVED.

        Active review is the only path — "time heals = HARAM".
        """
        return [r for r in self._load_all() if r.review_outcome == "UNRESOLVED"]

    def stats(self) -> dict:
        """Compute stop-correctness statistics from the ledger.

        Returns:
            dict with keys:
                false_proceed_rate: float
                false_hold_rate: float
                unresolved_hold_rate: float
                hold_reversal_latency_avg: Optional[float] (None if no reversals)
                confusion_matrix: dict[str, int]
                total_records: int
                reviewed_count: int
                unresolved_count: int
        """
        all_records, invalid_records = self._load_all_with_invalid()
        total = len(all_records)

        # A ledger whose rows are ALL malformed is an input defect, not an
        # absence of decisions. "NO_RECORDS" would be a false statement —
        # there WERE records, they could not be parsed. Report
        # INVALID_INPUT (2026-10-29: caught by tests/test_rsi_metric_semantics.py).
        _empty_status = (
            METRIC_STATUS_INVALID_INPUT if invalid_records > 0 else METRIC_STATUS_UNKNOWN
        )
        _empty_reason = "INVALID_REVIEW_RECORDS" if invalid_records > 0 else "NO_RECORDS"

        if total == 0:
            return {
                "false_proceed_rate": UNMEASURED,
                "false_hold_rate": UNMEASURED,
                "unresolved_hold_rate": UNMEASURED,
                "false_proceed_rate_status": _empty_status,
                "false_hold_rate_status": _empty_status,
                "unresolved_hold_rate_status": _empty_status,
                "false_proceed_rate_reason": _empty_reason,
                "false_hold_rate_reason": _empty_reason,
                "unresolved_hold_rate_reason": _empty_reason,
                "false_proceed_rate_numerator": 0,
                "false_proceed_rate_denominator": 0,
                "false_hold_rate_numerator": 0,
                "false_hold_rate_denominator": 0,
                "unresolved_hold_rate_numerator": 0,
                "unresolved_hold_rate_denominator": 0,
                "hold_reversal_latency_avg": None,
                "confusion_matrix": {
                    "CORRECT_HOLD": 0,
                    "FALSE_HOLD": 0,
                    "CORRECT_PROCEED": 0,
                    "FALSE_PROCEED": 0,
                    "CORRECT_SABAR": 0,
                    "FALSE_SABAR": 0,
                    "CORRECT_VOID": 0,
                    "FALSE_VOID": 0,
                    "CORRECT_DECISION": 0,
                    "INCONCLUSIVE": 0,
                    "OUTCOME_UNOBSERVED": 0,
                    "INVALID_REVIEW": 0,
                    "UNRESOLVED": 0,
                },
                "total_records": 0,
                "reviewed_count": 0,
                "unresolved_count": 0,
                "invalid_records": invalid_records,
                "metric_status": _empty_status,
            }

        # Confusion matrix counts. Built from (original_verdict,
        # review_outcome) pairs so a generic CORRECT_DECISION is counted
        # against the verdict it actually judged (2026-10-29, Phase 5).
        confusion: dict[str, int] = {
            "CORRECT_HOLD": 0,
            "FALSE_HOLD": 0,
            "CORRECT_PROCEED": 0,
            "FALSE_PROCEED": 0,
            "CORRECT_SABAR": 0,
            "FALSE_SABAR": 0,
            "CORRECT_VOID": 0,
            "FALSE_VOID": 0,
            "CORRECT_DECISION": 0,
            "INCONCLUSIVE": 0,
            "OUTCOME_UNOBSERVED": 0,
            "INVALID_REVIEW": 0,
            "UNRESOLVED": 0,
        }
        for _rec in all_records:
            _ro = _rec.review_outcome
            if _ro == "CORRECT_DECISION":
                confusion["CORRECT_DECISION"] += 1
                if _rec.original_verdict in ("HOLD", "PROCEED", "SABAR", "VOID"):
                    confusion[f"CORRECT_{_rec.original_verdict}"] += 1
            elif _ro in confusion:
                confusion[_ro] += 1
        matrix = confusion

        # Reviewed-only pool for rate calculations (excludes UNRESOLVED)
        reviewed = [r for r in all_records if r.is_reviewed]
        reviewed_count = len(reviewed)
        # UNRESOLVED is its own state: a review that happened but did not
        # adjudicate (INCONCLUSIVE / OUTCOME_UNOBSERVED / INVALID_REVIEW) is
        # neither a decisive data point nor still-unreviewed
        # (2026-10-29, Phase 5).
        unresolved_count = sum(1 for r in all_records if r.review_outcome == "UNRESOLVED")

        # False proceed rate: FALSE_PROCEED / (CORRECT_PROCEED + FALSE_PROCEED)
        # False hold rate:   FALSE_HOLD   / (CORRECT_HOLD   + FALSE_HOLD)
        # Unresolved hold rate: UNRESOLVED holds / total holds
        #
        # Every rate below carries an explicit status and its numerator and
        # denominator. A denominator with no REVIEWED example yields UNMEASURED,
        # never 0.0 (2026-10-29 audit: 14193 HOLD rows, 0 reviewed ->
        # false_hold_rate reported 0.0, i.e. perfect governance by omission).
        proceed_total = matrix.get("CORRECT_PROCEED", 0) + matrix.get("FALSE_PROCEED", 0)
        hold_total = matrix.get("CORRECT_HOLD", 0) + matrix.get("FALSE_HOLD", 0)
        unresolved_holds = sum(1 for r in all_records if r.is_unresolved_hold)
        total_holds = sum(1 for r in all_records if r.is_hold)

        proceed_rate = _rate(
            matrix.get("FALSE_PROCEED", 0),
            proceed_total,
            no_reviewed_reason="NO_REVIEWED_PROCEEDS",
            invalid_records=invalid_records,
        )
        hold_rate = _rate(
            matrix.get("FALSE_HOLD", 0),
            hold_total,
            no_reviewed_reason="NO_REVIEWED_HOLDS",
            invalid_records=invalid_records,
        )
        unresolved_rate = _rate(
            unresolved_holds,
            total_holds,
            no_reviewed_reason="NO_HOLD_RECORDS",
            invalid_records=invalid_records,
        )

        # Hold reversal latency average (FALSE_HOLD records with latency data)
        reversal_latencies = [
            r.review_latency_hours
            for r in reviewed
            if r.review_outcome == "FALSE_HOLD" and r.review_latency_hours is not None
        ]
        hold_reversal_latency_avg = (
            sum(reversal_latencies) / len(reversal_latencies) if reversal_latencies else None
        )

        # Reviewer independence is a CLAIM, and a claim that is not surfaced
        # cannot be audited (2026-10-29, 555-verifier finding D3).
        independent_reviews = sum(1 for r in all_records if r.review_independent is True)
        non_independent_reviews = sum(1 for r in all_records if r.review_independent is False)
        reviews_without_claim = sum(
            1
            for r in all_records
            if r.review_independent is None and r.review_outcome != "UNRESOLVED"
        )

        statuses = [
            proceed_rate["status"],
            hold_rate["status"],
            unresolved_rate["status"],
        ]
        if METRIC_STATUS_INVALID_INPUT in statuses:
            overall_status = METRIC_STATUS_INVALID_INPUT
        elif METRIC_STATUS_UNKNOWN in statuses:
            overall_status = METRIC_STATUS_UNKNOWN
        elif METRIC_STATUS_INSUFFICIENT in statuses:
            overall_status = METRIC_STATUS_INSUFFICIENT
        else:
            overall_status = METRIC_STATUS_MEASURED

        return {
            "false_proceed_rate": proceed_rate["value"],
            "false_hold_rate": hold_rate["value"],
            "unresolved_hold_rate": unresolved_rate["value"],
            "false_proceed_rate_status": proceed_rate["status"],
            "false_hold_rate_status": hold_rate["status"],
            "unresolved_hold_rate_status": unresolved_rate["status"],
            "false_proceed_rate_reason": proceed_rate["reason"],
            "false_hold_rate_reason": hold_rate["reason"],
            "unresolved_hold_rate_reason": unresolved_rate["reason"],
            "false_proceed_rate_numerator": proceed_rate["numerator"],
            "false_proceed_rate_denominator": proceed_rate["denominator"],
            "false_hold_rate_numerator": hold_rate["numerator"],
            "false_hold_rate_denominator": hold_rate["denominator"],
            "unresolved_hold_rate_numerator": unresolved_rate["numerator"],
            "unresolved_hold_rate_denominator": unresolved_rate["denominator"],
            "hold_reversal_latency_avg": (
                round(hold_reversal_latency_avg, 2)
                if hold_reversal_latency_avg is not None
                else None
            ),
            "confusion_matrix": dict(matrix),
            "total_records": total,
            "ledger_rows": self.raw_row_count(),
            "reviewed_count": reviewed_count,
            "unresolved_count": unresolved_count,
            "invalid_records": invalid_records,
            "independent_reviews": independent_reviews,
            "non_independent_reviews": non_independent_reviews,
            "reviews_without_independence_claim": reviews_without_claim,
            "metric_status": overall_status,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 3. StratifiedSampler — Audit Batch Selection
# ═══════════════════════════════════════════════════════════════════════════


class StratifiedSampler:
    """Sampling design for audit selection — NOT random, stratified.

    Strata (in priority order):
      1. HIGH_FREQUENCY_REASON    — Most common reason classes (bias toward review)
      2. HIGH_COST_BLOCKED       — HOLDs with severity_weight > 1.0
      3. REPEATED_HOLD_SAME_TOOL — Multiple HOLDs from the same tool
      4. UNUSUALLY_FAST_HOLD     — HOLDs issued with no evidence at decision time
      5. NO_EVIDENCE_HOLD        — HOLDs without any evidence_available_at_decision
      6. BYPASSED_HOLD           — HOLDs later bypassed (evidence grew post-hoc)
      7. UNREVIEWED_TAIL         — Remaining UNRESOLVED records (fill)
    """

    def __init__(self, ledger: RSILedger | None = None) -> None:
        self._ledger = ledger or RSILedger()

    def select_batch(self, n: int = 10) -> list[RSIDecisionRecord]:
        """Select a stratified batch of up to `n` records for audit review.

        Returns records in priority order across strata. If fewer than n
        unresolved records exist, returns all available.

        Stratified design ensures no single failure mode dominates the sample
        while guaranteeing high-cost and high-frequency patterns are covered.
        """
        pending = self._ledger.pending_review()
        if not pending:
            return []

        selected: list[RSIDecisionRecord] = []
        remaining = list(pending)
        taken_ids: set[str] = set()

        def _take(records: list[RSIDecisionRecord], label: str) -> None:
            """Pull records into selected set, tracking by decision_id."""
            for rec in records:
                if len(selected) >= n:
                    return
                if rec.decision_id not in taken_ids:
                    selected.append(rec)
                    taken_ids.add(rec.decision_id)
                    remaining[:] = [r for r in remaining if r.decision_id != rec.decision_id]

        # Stratum 1: High-frequency reason classes (pick top reason class first)
        reason_freq: Counter[str] = Counter(r.reason_class for r in remaining)
        for reason, _ in reason_freq.most_common():
            stratum = [r for r in remaining if r.reason_class == reason]
            _take(stratum, f"high_freq:{reason}")

        # Stratum 2: High-cost blocked actions (severity_weight > 1.0, HOLDs)
        high_cost = [r for r in remaining if r.is_hold and r.severity_weight > 1.0]
        _take(high_cost, "high_cost_blocked")

        # Stratum 3: Repeated HOLDs from the same tool
        tool_counts: Counter[str] = Counter(r.tool for r in remaining if r.is_hold)
        repeated_tools = {tool for tool, cnt in tool_counts.items() if cnt >= 2}
        if repeated_tools:
            repeated_holds = [r for r in remaining if r.is_hold and r.tool in repeated_tools]
            _take(repeated_holds, "repeated_hold_same_tool")

        # Stratum 4: Unusually fast HOLDs (no evidence gathered at decision time)
        fast_holds = [r for r in remaining if r.is_hold and not r.evidence_available_at_decision]
        _take(fast_holds, "no_evidence_hold")

        # Stratum 5: HOLDs later bypassed (evidence grew post-hoc but not reviewed)
        bypassed_holds = [
            r
            for r in remaining
            if r.is_hold and r.evidence_available_post_hoc and not r.evidence_available_at_decision
        ]
        _take(bypassed_holds, "bypassed_hold")

        # Stratum 6: Remaining unreviewed tail
        _take(remaining, "unreviewed_tail")

        return selected


# ═══════════════════════════════════════════════════════════════════════════
# 4. RSIScorer — Derived Scoring (NOT reduced to single number)
# ═══════════════════════════════════════════════════════════════════════════


class RSIScorer:
    """Derived scoring from the RSI ledger.

    Produces a multi-dimensional score profile. The calibrated_score
    is ONLY computed when >= 30 reviewed records exist in the ledger.
    Below that threshold, calibrated_score is None — the system
    refuses to collapse uncertainty into a premature single number.

    All rates are derived, not asserted.
    """

    def __init__(self, ledger: RSILedger | None = None) -> None:
        self._ledger = ledger or RSILedger()

    @property
    def false_proceed_rate(self) -> float | str:
        """Rate at which PROCEED verdicts were later found incorrect.

        Returns UNMEASURED (not 0.0) when no reviewed PROCEED exists.
        """
        return self._ledger.stats()["false_proceed_rate"]

    @property
    def false_hold_rate(self) -> float | str:
        """Rate at which HOLD verdicts were later found incorrect.

        Returns UNMEASURED (not 0.0) when no reviewed HOLD exists.
        """
        return self._ledger.stats()["false_hold_rate"]

    @property
    def unresolved_hold_rate(self) -> float | str:
        """Fraction of HOLD verdicts that remain unreviewed.

        Returns UNMEASURED (not 0.0) when no HOLD record exists at all.
        """
        return self._ledger.stats()["unresolved_hold_rate"]

    @property
    def hold_reversal_latency_avg(self) -> float | None:
        """Average hours to reverse a FALSE_HOLD (None if no reversals)."""
        return self._ledger.stats()["hold_reversal_latency_avg"]

    @property
    def calibrated_score(self) -> dict | None:
        """Composite calibrated score — ONLY when >= 30 reviewed records exist.

        Returns None if insufficient data (the scorer refuses to collapse
        uncertainty into a single number before calibration threshold).

        When available, returns:
            {
                "calibrated_score": float,        # 0.0 (perfect) to 1.0 (worst)
                "false_proceed_rate": float,
                "false_hold_rate": float,
                "unresolved_hold_rate": float,
                "hold_reversal_latency_avg": float or None,
                "reviewed_count": int,
                "calibration_met": bool,
            }
        """
        s = self._ledger.stats()
        reviewed = s["reviewed_count"]

        if reviewed < CALIBRATION_MINIMUM:
            return None

        # Calibrated score: weighted average of error rates
        # false_proceed_rate (0.4) + false_hold_rate (0.4) + unresolved_hold_rate (0.2)
        #
        # If any term is UNMEASURED there is no composite: a weighted average
        # containing an unmeasured term is a fabricated number, so the score
        # stays absent (2026-10-29 audit).
        components = (
            s["false_proceed_rate"],
            s["false_hold_rate"],
            s["unresolved_hold_rate"],
        )
        if any(not isinstance(c, (int, float)) or isinstance(c, bool) for c in components):
            return None
        calibrated = (
            0.4 * s["false_proceed_rate"]
            + 0.4 * s["false_hold_rate"]
            + 0.2 * s["unresolved_hold_rate"]
        )

        return {
            "calibrated_score": round(calibrated, 4),
            "false_proceed_rate": s["false_proceed_rate"],
            "false_hold_rate": s["false_hold_rate"],
            "unresolved_hold_rate": s["unresolved_hold_rate"],
            "hold_reversal_latency_avg": s["hold_reversal_latency_avg"],
            "reviewed_count": reviewed,
            "calibration_met": True,
        }

    def profile(self) -> dict:
        """Full score profile including calibration guard.

        Always returns all available rates. calibrated_score is None
        until >= 30 reviewed records exist.
        """
        calibrated = self.calibrated_score
        s = self._ledger.stats()
        return {
            "false_proceed_rate": self.false_proceed_rate,
            "false_hold_rate": self.false_hold_rate,
            "unresolved_hold_rate": self.unresolved_hold_rate,
            "false_proceed_rate_status": s["false_proceed_rate_status"],
            "false_hold_rate_status": s["false_hold_rate_status"],
            "unresolved_hold_rate_status": s["unresolved_hold_rate_status"],
            "false_proceed_rate_denominator": s["false_proceed_rate_denominator"],
            "false_hold_rate_denominator": s["false_hold_rate_denominator"],
            "unresolved_hold_rate_denominator": s["unresolved_hold_rate_denominator"],
            "metric_status": s["metric_status"],
            "hold_reversal_latency_avg": self.hold_reversal_latency_avg,
            "calibrated_score": (calibrated["calibrated_score"] if calibrated else None),
            "calibration_met": calibrated is not None,
            "calibration_minimum": CALIBRATION_MINIMUM,
            "reviewed_count": s["reviewed_count"],
            "total_records": s["total_records"],
            "unresolved_count": s["unresolved_count"],
            "invalid_records": s["invalid_records"],
        }


# ═══════════════════════════════════════════════════════════════════════════
# 5. Integration Hook — record_rsi_decision()
# ═══════════════════════════════════════════════════════════════════════════

# Module-level singleton ledger (one per process)
_default_ledger: RSILedger | None = None


def _get_ledger() -> RSILedger:
    """Lazy-initialize the default ledger singleton."""
    global _default_ledger
    if _default_ledger is None:
        _default_ledger = RSILedger()
    return _default_ledger


def record_rsi_decision(
    *,
    tool: str,
    verdict: Literal["HOLD", "PROCEED", "SABAR", "VOID"],
    reason_class: Literal["AUTHORITY", "EVIDENCE", "SAFETY", "TOOL_FAILURE", "UNCERTAINTY"],
    severity_weight: float = 1.0,
    evidence_available: list[str] | None = None,
) -> RSIDecisionRecord:
    """Convenience function for tools.py to record HOLD/PROCEED decisions.

    Import and call wherever a tool issues a HOLD or PROCEED verdict:

        from arifosmcp.runtime.rsi_audit import record_rsi_decision

        record_rsi_decision(
            tool="arif_judge",
            verdict="HOLD",
            reason_class="AUTHORITY",
            severity_weight=1.0,
            evidence_available=["session: OBSERVE_ONLY"],
        )

    Returns the created RSIDecisionRecord for caller inspection.
    """
    decision = RSIDecisionRecord(
        tool=tool,
        original_verdict=verdict,
        reason_class=reason_class,
        severity_weight=severity_weight,
        evidence_available_at_decision=list(evidence_available or []),
    )
    _get_ledger().record(decision)
    logger.info(
        "rsi_audit: recorded %s %s reason=%s weight=%.2f",
        verdict,
        decision.decision_id[:8],
        reason_class,
        severity_weight,
    )
    return decision


def record_rsi_review(
    *,
    decision_id: str,
    review_outcome: str,
    reviewed_by: str,
    evidence_refs: list[str] | None = None,
    independent: bool | None = None,
    note: str = "",
) -> RSIDecisionRecord:
    """Record a post-hoc review of an existing RSI decision.

    The review contract (forge_work/2026-10-29-TTME-RSI-REVIEW-CONTRACT.md):

    - a valid reviewer uses evidence occurring AFTER or independently of the
      original decision;
    - a valid reviewer does not merely restate the original judge's narrative;
    - a valid reviewer states whether it is independent;
    - a valid reviewer produces evidence references;
    - INCONCLUSIVE is a legitimate outcome;
    - absence of an incident is NEVER evidence of a correct decision.

    Returns the superseding RSIDecisionRecord.
    """
    return _get_ledger().record_review(
        decision_id,
        review_outcome,
        reviewed_by=reviewed_by,
        evidence_refs=evidence_refs,
        independent=independent,
        note=note,
    )


def select_review_batch(n: int = 10) -> list[RSIDecisionRecord]:
    """Select a stratified canary batch of decisions awaiting review."""
    return _get_ledger().select_review_batch(n=n)


# ═══════════════════════════════════════════════════════════════════════════
# Module exports
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "RSIDecisionRecord",
    "RSILedger",
    "RSIScorer",
    "StratifiedSampler",
    "record_rsi_decision",
    "record_rsi_review",
    "select_review_batch",
    "DECISIVE_REVIEW_OUTCOMES",
    "LEDGER_PATH",
    "CALIBRATION_MINIMUM",
]
