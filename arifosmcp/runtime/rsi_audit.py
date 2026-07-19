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
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════

LEDGER_PATH: Path = Path("/root/VAULT999/rsi_ledger.jsonl")
CALIBRATION_MINIMUM: int = 30  # minimum reviewed records for calibrated_score

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
    original_verdict: Literal["HOLD", "PROCEED"] = Field(
        ...,
        description="The original verdict issued by the tool",
    )
    reason_class: Literal[
        "AUTHORITY", "EVIDENCE", "SAFETY", "TOOL_FAILURE", "UNCERTAINTY"
    ] = Field(
        ...,
        description="Classification of why HOLD/PROCEED was issued",
    )
    review_outcome: Literal[
        "CORRECT_HOLD", "FALSE_HOLD", "CORRECT_PROCEED", "FALSE_PROCEED", "UNRESOLVED"
    ] = Field(
        default="UNRESOLVED",
        description="Post-hoc review outcome — starts UNRESOLVED",
    )
    review_latency_hours: Optional[float] = Field(
        default=None,
        description="Hours between original decision and review completion",
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
    def _latency_must_be_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError(f"review_latency_hours must be >= 0, got {v}")
        return v

    @property
    def is_reviewed(self) -> bool:
        """True if this record has a definitive review outcome."""
        return self.review_outcome in REVIEWED_OUTCOMES

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

    def __init__(self, path: Optional[Path | str] = None) -> None:
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
        records: list[RSIDecisionRecord] = []
        if not self._path.exists():
            return records
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(RSIDecisionRecord.model_validate_json(line))
                except Exception:
                    logger.warning("rsi_ledger: skipping corrupt line in %s", self._path)
        return records

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
        all_records = self._load_all()
        total = len(all_records)

        if total == 0:
            return {
                "false_proceed_rate": 0.0,
                "false_hold_rate": 0.0,
                "unresolved_hold_rate": 0.0,
                "hold_reversal_latency_avg": None,
                "confusion_matrix": {
                    "CORRECT_HOLD": 0,
                    "FALSE_HOLD": 0,
                    "CORRECT_PROCEED": 0,
                    "FALSE_PROCEED": 0,
                    "UNRESOLVED": 0,
                },
                "total_records": 0,
                "reviewed_count": 0,
                "unresolved_count": 0,
            }

        # Confusion matrix counts
        matrix = Counter(r.review_outcome for r in all_records)

        # Reviewed-only pool for rate calculations (excludes UNRESOLVED)
        reviewed = [r for r in all_records if r.is_reviewed]
        reviewed_count = len(reviewed)
        unresolved_count = total - reviewed_count

        # False proceed rate: FALSE_PROCEED / (CORRECT_PROCEED + FALSE_PROCEED)
        proceed_total = matrix.get("CORRECT_PROCEED", 0) + matrix.get("FALSE_PROCEED", 0)
        false_proceed_rate = (
            matrix.get("FALSE_PROCEED", 0) / proceed_total if proceed_total > 0 else 0.0
        )

        # False hold rate: FALSE_HOLD / (CORRECT_HOLD + FALSE_HOLD)
        hold_total = matrix.get("CORRECT_HOLD", 0) + matrix.get("FALSE_HOLD", 0)
        false_hold_rate = (
            matrix.get("FALSE_HOLD", 0) / hold_total if hold_total > 0 else 0.0
        )

        # Unresolved hold rate: UNRESOLVED holds / total holds
        unresolved_holds = sum(
            1 for r in all_records if r.is_unresolved_hold
        )
        total_holds = sum(1 for r in all_records if r.is_hold)
        unresolved_hold_rate = (
            unresolved_holds / total_holds if total_holds > 0 else 0.0
        )

        # Hold reversal latency average (FALSE_HOLD records with latency data)
        reversal_latencies = [
            r.review_latency_hours
            for r in reviewed
            if r.review_outcome == "FALSE_HOLD" and r.review_latency_hours is not None
        ]
        hold_reversal_latency_avg = (
            sum(reversal_latencies) / len(reversal_latencies)
            if reversal_latencies
            else None
        )

        return {
            "false_proceed_rate": round(false_proceed_rate, 4),
            "false_hold_rate": round(false_hold_rate, 4),
            "unresolved_hold_rate": round(unresolved_hold_rate, 4),
            "hold_reversal_latency_avg": (
                round(hold_reversal_latency_avg, 2)
                if hold_reversal_latency_avg is not None
                else None
            ),
            "confusion_matrix": {
                "CORRECT_HOLD": matrix.get("CORRECT_HOLD", 0),
                "FALSE_HOLD": matrix.get("FALSE_HOLD", 0),
                "CORRECT_PROCEED": matrix.get("CORRECT_PROCEED", 0),
                "FALSE_PROCEED": matrix.get("FALSE_PROCEED", 0),
                "UNRESOLVED": matrix.get("UNRESOLVED", 0),
            },
            "total_records": total,
            "reviewed_count": reviewed_count,
            "unresolved_count": unresolved_count,
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

    def __init__(self, ledger: Optional[RSILedger] = None) -> None:
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
                    remaining[:] = [
                        r for r in remaining if r.decision_id != rec.decision_id
                    ]

        # Stratum 1: High-frequency reason classes (pick top reason class first)
        reason_freq: Counter[str] = Counter(r.reason_class for r in remaining)
        for reason, _ in reason_freq.most_common():
            stratum = [r for r in remaining if r.reason_class == reason]
            _take(stratum, f"high_freq:{reason}")

        # Stratum 2: High-cost blocked actions (severity_weight > 1.0, HOLDs)
        high_cost = [
            r for r in remaining
            if r.is_hold and r.severity_weight > 1.0
        ]
        _take(high_cost, "high_cost_blocked")

        # Stratum 3: Repeated HOLDs from the same tool
        tool_counts: Counter[str] = Counter(
            r.tool for r in remaining if r.is_hold
        )
        repeated_tools = {tool for tool, cnt in tool_counts.items() if cnt >= 2}
        if repeated_tools:
            repeated_holds = [
                r for r in remaining
                if r.is_hold and r.tool in repeated_tools
            ]
            _take(repeated_holds, "repeated_hold_same_tool")

        # Stratum 4: Unusually fast HOLDs (no evidence gathered at decision time)
        fast_holds = [
            r for r in remaining
            if r.is_hold and not r.evidence_available_at_decision
        ]
        _take(fast_holds, "no_evidence_hold")

        # Stratum 5: HOLDs later bypassed (evidence grew post-hoc but not reviewed)
        bypassed_holds = [
            r for r in remaining
            if r.is_hold
            and r.evidence_available_post_hoc
            and not r.evidence_available_at_decision
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

    def __init__(self, ledger: Optional[RSILedger] = None) -> None:
        self._ledger = ledger or RSILedger()

    @property
    def false_proceed_rate(self) -> float:
        """Rate at which PROCEED verdicts were later found incorrect."""
        return self._ledger.stats()["false_proceed_rate"]

    @property
    def false_hold_rate(self) -> float:
        """Rate at which HOLD verdicts were later found incorrect."""
        return self._ledger.stats()["false_hold_rate"]

    @property
    def unresolved_hold_rate(self) -> float:
        """Fraction of HOLD verdicts that remain unreviewed."""
        return self._ledger.stats()["unresolved_hold_rate"]

    @property
    def hold_reversal_latency_avg(self) -> Optional[float]:
        """Average hours to reverse a FALSE_HOLD (None if no reversals)."""
        return self._ledger.stats()["hold_reversal_latency_avg"]

    @property
    def calibrated_score(self) -> Optional[dict]:
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
        return {
            "false_proceed_rate": self.false_proceed_rate,
            "false_hold_rate": self.false_hold_rate,
            "unresolved_hold_rate": self.unresolved_hold_rate,
            "hold_reversal_latency_avg": self.hold_reversal_latency_avg,
            "calibrated_score": (
                calibrated["calibrated_score"] if calibrated else None
            ),
            "calibration_met": calibrated is not None,
            "calibration_minimum": CALIBRATION_MINIMUM,
            "reviewed_count": self._ledger.stats()["reviewed_count"],
        }


# ═══════════════════════════════════════════════════════════════════════════
# 5. Integration Hook — record_rsi_decision()
# ═══════════════════════════════════════════════════════════════════════════

# Module-level singleton ledger (one per process)
_default_ledger: Optional[RSILedger] = None


def _get_ledger() -> RSILedger:
    """Lazy-initialize the default ledger singleton."""
    global _default_ledger
    if _default_ledger is None:
        _default_ledger = RSILedger()
    return _default_ledger


def record_rsi_decision(
    *,
    tool: str,
    verdict: Literal["HOLD", "PROCEED"],
    reason_class: Literal[
        "AUTHORITY", "EVIDENCE", "SAFETY", "TOOL_FAILURE", "UNCERTAINTY"
    ],
    severity_weight: float = 1.0,
    evidence_available: Optional[list[str]] = None,
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


# ═══════════════════════════════════════════════════════════════════════════
# Module exports
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "RSIDecisionRecord",
    "RSILedger",
    "RSIScorer",
    "StratifiedSampler",
    "record_rsi_decision",
    "LEDGER_PATH",
    "CALIBRATION_MINIMUM",
]
