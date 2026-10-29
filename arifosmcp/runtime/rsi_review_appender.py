"""
arifosmcp/runtime/rsi_review_appender.py — P1: canonical single-row review append
═════════════════════════════════════════════════════════════════════════════════

The one sanctioned writer of RSI review rows on a target ledger.

Design source (sealed by F13 2026-10-29 ~21:55 MYT, "sah on all three"):
  /root/forge_work/proposals/RSI-REVIEW-PATH-RECONCILIATION-20261029.md
  §7   review schema v1 (rsi.review.v1) + closed verdict vocabulary
  §8   authority split — adjudication is never append capability
  §10  immutability transition — no attribute relaxation in steady state
  §11  failure & idempotency model
  §15  P1 builds the MECHANISM ONLY. It must not write a review row.

Laws encoded here (each maps to a sealed requirement):

  L1  ONE writer. The appender is the only sanctioned review-row writer.
      It never mutates an existing row, never chattrs anything, and never
      falls back to the live LEDGER_PATH — an explicit target is required
      (P2's open_ledger supplies handles; the live file stays immutable and
      a live append is F13's one-time bridge, §10).
  L2  review_id is the idempotency key (§11). A retry that finds the id
      already on disk appends NOTHING and regenerates the receipt from the
      existing row.
  L3  A second review of the same decision_id is BLOCKED unless it names
      supersedes_review_id == the latest prior review_id (§11 + §7.2).
      This pins M6: repeated-review semantics are explicit at the writer,
      never an accident of loader order.
  L4  The append is one single write() of one complete line, verified by
      re-reading the last line. A torn line is FAILED, never blind-retried.
  L5  Effective-state verification: after the append, exactly ONE
      decision's effective review_outcome changed and the effective
      decision count is unchanged (§9 req 11).
  L6  The authorization envelope names ONE review_id + ONE decision_id +
      ONE verdict. Envelope/row disagreement refuses the append (§8).
  L7  The original event is hash-bound: original_event_hash must equal the
      sha256 of the original row exactly as on disk (§9 req 3, M5 method).
  L8  A rationale that cites a dashboard metric (false_hold_rate,
      reviewed_count, unresolved_hold_rate) is refused — a review whose
      only effect is to move a number is a failed review (§9 req 13).

The appended row is an RSIDecisionRecord-compatible line (the existing
loader's last-write-wins semantics keep working) carrying the rsi.review.v1
fields alongside. Non-decisive verdicts map onto the existing non-decisive
row outcomes so they can never enter a rate denominator.

Floors: F1 (reversible — append-only, no rewrite), F2 (hash-bound evidence),
F11 (ledger integrity), F13 (SOVEREIGN — the first live row still needs a
555 adjudication and an 888 authorization; this module gates, never grants).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from arifosmcp.runtime.rsi_audit import RSILedger

logger = logging.getLogger(__name__)

REVIEW_SCHEMA_VERSION = "rsi.review.v1"

RECEIPT_DIR_DEFAULT = Path("/var/lib/arifos/rsi_review_receipts")

# §7.1 closed verdict vocabulary (sealed). The four decisive pairs map 1:1;
# the three non-decisive tokens map onto existing non-decisive row outcomes
# so they can never enter a rate denominator (rule 1 + rule 2 of §7.1).
REVIEW_VERDICT_LITERALS = frozenset(
    {
        "CORRECT_HOLD",
        "FALSE_HOLD",
        "CORRECT_PROCEED",
        "FALSE_PROCEED",
        "INDETERMINATE",
        "INSUFFICIENT_EVIDENCE",
        "INVALID_ORIGINAL_EVENT",
    }
)

REVIEW_VERDICT_TO_ROW_OUTCOME: dict[str, str] = {
    "CORRECT_HOLD": "CORRECT_HOLD",
    "FALSE_HOLD": "FALSE_HOLD",
    "CORRECT_PROCEED": "CORRECT_PROCEED",
    "FALSE_PROCEED": "FALSE_PROCEED",
    "INDETERMINATE": "INCONCLUSIVE",
    "INSUFFICIENT_EVIDENCE": "OUTCOME_UNOBSERVED",
    "INVALID_ORIGINAL_EVENT": "INVALID_REVIEW",
}

REVIEW_CONFIDENCE_LITERALS = frozenset({"HIGH", "MEDIUM", "LOW", "INSUFFICIENT"})

# §9 req 13: these strings must not appear in a review rationale.
_DASHBOARD_TARGET_PATTERN = re.compile(
    r"false_hold_rate|false_proceed_rate|reviewed_count|unresolved_hold_rate|calibrated_score"
)

# Statuses the append can end in. Only APPENDED and IDEMPOTENT_NO_APPEND
# leave a (pre-existing or new) row on disk; every REFUSED_* / BLOCKED_* /
# *FAILED* status leaves the ledger byte-identical.
STATUS_APPENDED = "APPENDED"
STATUS_IDEMPOTENT = "IDEMPOTENT_NO_APPEND"
STATUS_REFUSED_ENVELOPE = "REFUSED_ENVELOPE_MISMATCH"
STATUS_REFUSED_UNKNOWN_DECISION = "REFUSED_UNKNOWN_DECISION"
STATUS_REFUSED_HASH = "REFUSED_ORIGINAL_HASH_MISMATCH"
STATUS_REFUSED_SUPERSEDES = "REFUSED_SECOND_REVIEW_REQUIRES_SUPERSEDES"
STATUS_REFUSED_SUPERSEDES_MISMATCH = "REFUSED_SUPERSEDES_MISMATCH"
STATUS_REFUSED_TORN_TAIL = "REFUSED_TORN_TAIL_QUARANTINED"
STATUS_REFUSED_DASHBOARD = "REFUSED_DASHBOARD_TARGET_IN_RATIONALE"
STATUS_BLOCKED_TARGET = "BLOCKED_TARGET_REQUIRED"
STATUS_BLOCKED_IMMUTABLE = "BLOCKED_IMMUTABLE"
STATUS_TORN = "APPEND_FAILED_TORN_QUARANTINED"
STATUS_VERIFY_FAILED = "APPEND_VERIFY_FAILED"


class ReviewAuthorization(BaseModel):
    """The 888-APEX append authorization (§8). Narrowly scoped by construction.

    The appender does not mint, verify, or interpret the authorization
    receipt itself — it only binds the row to the envelope and refuses any
    disagreement. Who may issue one is F13's pending role decision.
    """

    review_id: str = Field(..., min_length=8, description="The ONE review this covers")
    decision_id: str = Field(..., min_length=8, description="The ONE decision this covers")
    review_verdict: str = Field(..., description="The ONE verdict authorized")
    authorizer_id: str = Field(..., min_length=3, description="Who authorized (888 side)")
    authorization_receipt: str = Field(..., min_length=8, description="Receipt / envelope hash")


class RSIReviewRecordV1(BaseModel):
    """§7 review schema v1 — a new EVENT appended to the ledger."""

    schema_version: str = Field(default=REVIEW_SCHEMA_VERSION)
    review_id: str = Field(default_factory=lambda: f"rev-{uuid.uuid4()}")
    decision_id: str = Field(..., min_length=8)
    original_event_hash: str = Field(..., description="sha256:<hex> of the ORIGINAL decision row as on disk")
    original_decision: str = Field(..., description="HOLD|PROCEED|SABAR|VOID as recorded")
    decision_timestamp: str = Field(..., description="RFC3339 timestamp of the original decision")
    adjudicator_id: str = Field(..., min_length=3, description="555-ASI:<instance> — who adjudicated")
    authorizer_id: str = Field(..., min_length=3, description="888-APEX:<instance> — who authorized")
    review_verdict: str = Field(...)
    review_confidence: str = Field(...)
    rationale: str = Field(..., min_length=1)
    evidence_hashes: list[str] = Field(default_factory=list)
    outcome_evidence: list[dict] = Field(default_factory=list)
    authorization_receipt: str = Field(..., min_length=8)
    review_timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    supersedes_review_id: str | None = None
    review_independent: bool | None = Field(
        default=None,
        description="Explicit independence claim, never inferred (None = not claimed)",
    )

    @field_validator("review_verdict")
    @classmethod
    def _verdict_closed(cls, v: str) -> str:
        if v not in REVIEW_VERDICT_LITERALS:
            raise ValueError(f"review_verdict {v!r} not in the §7.1 closed vocabulary")
        return v

    @field_validator("review_confidence")
    @classmethod
    def _confidence_closed(cls, v: str) -> str:
        if v not in REVIEW_CONFIDENCE_LITERALS:
            raise ValueError(f"review_confidence {v!r} not in {{HIGH,MEDIUM,LOW,INSUFFICIENT}}")
        return v


def _sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


class RSIReviewAppender:
    """The canonical single-row review append mechanism (P1).

    Usage (on a target-bound handle, never a default live path)::

        appender = RSIReviewAppender(target="/tmp/copy_of_ledger.jsonl")
        receipt = appender.append(review=review, authorization=auth)

    The appender refuses to guess a target. The live ledger is chattr +i;
    an append attempt against it returns BLOCKED_IMMUTABLE with a refusal
    receipt and changes no attribute — the one-time bridge for the first
    live row is an explicitly authorized chattr cycle (§10), not this code.
    """

    def __init__(
        self,
        target: Path | str | RSILedger | None = None,
        *,
        receipt_dir: Path | str | None = None,
    ) -> None:
        if target is None or (isinstance(target, (str, Path)) and str(target).strip() == ""):
            # L1: no implicit live target. Ever.
            raise ValueError(
                "RSIReviewAppender requires an explicit target (P1 §10/L1); "
                "refusing to default to the live ledger"
            )
        # P2 seam: a target-bound RSILedger handle (open_ledger(path=...))
        # carries its own bound file — use it.
        self._target = target.path if isinstance(target, RSILedger) else Path(target)
        self._receipt_dir = Path(receipt_dir) if receipt_dir else RECEIPT_DIR_DEFAULT

    @property
    def target(self) -> Path:
        return self._target

    # ── row-level scans (raw lines, not the loader: extra fields matter) ─────

    def _raw_lines(self) -> list[str]:
        if not self._target.exists():
            return []
        with open(self._target, encoding="utf-8") as fh:
            return [line for line in fh.read().splitlines() if line.strip()]

    def _scan(self) -> dict:
        """One pass: prior review rows (any row carrying a review_id) and torn lines.

        A review row is any row with a review_id — original decision rows
        never carry one, so this stays robust even if schema_version drifts.
        Any unparseable non-empty line marks the ledger torn (§11 quarantine).
        """
        reviews: list[dict] = []
        torn_tail = False
        for line in self._raw_lines():
            try:
                row = json.loads(line)
            except Exception:
                torn_tail = True
                continue
            if row.get("review_id"):
                reviews.append(row)
        return {"reviews": reviews, "torn_tail": torn_tail}

    def _original_row(self, decision_id: str) -> tuple[dict | None, str | None]:
        """Return (first raw row for decision_id, its raw line) or (None, None)."""
        for line in self._raw_lines():
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("decision_id") != decision_id:
                continue
            if row.get("schema_version") == REVIEW_SCHEMA_VERSION:
                continue  # a review row, not the original event
            return row, line
        return None, None

    def _effective_outcomes(self) -> dict[str, str]:
        """decision_id -> effective review_outcome under last-write-wins."""
        effective: dict[str, str] = {}
        for line in self._raw_lines():
            try:
                row = json.loads(line)
            except Exception:
                continue
            did = row.get("decision_id")
            if did is None:
                continue
            effective[did] = row.get("review_outcome", "UNRESOLVED")
        return effective

    # ── the append ────────────────────────────────────────────────────────────

    def append(
        self,
        *,
        review: RSIReviewRecordV1,
        authorization: ReviewAuthorization,
    ) -> dict:
        """Append exactly one authorized review row. Returns the receipt.

        Only STATUS_APPENDED and STATUS_IDEMPOTENT_NO_APPEND mean a row for
        this review_id exists on disk. Every other status leaves the target
        byte-identical.
        """
        receipt: dict = {
            "review_id": review.review_id,
            "decision_id": review.decision_id,
            "requested_verdict": review.review_verdict,
            "target": str(self._target),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "status": None,
        }

        # L6 — envelope binding (§8): one review, one decision, one verdict.
        if (
            authorization.review_id != review.review_id
            or authorization.decision_id != review.decision_id
            or authorization.review_verdict != review.review_verdict
        ):
            receipt["status"] = STATUS_REFUSED_ENVELOPE
            receipt["reason"] = "authorization envelope does not bind this exact review"
            return self._finish(receipt)

        # L8 — dashboard targets may not justify a verdict (§9 req 13).
        if _DASHBOARD_TARGET_PATTERN.search(review.rationale or ""):
            receipt["status"] = STATUS_REFUSED_DASHBOARD
            receipt["reason"] = "rationale cites a dashboard metric — a review that moves a number is a failed review"
            return self._finish(receipt)

        # From here on the target is opened repeatedly (scan, original-row
        # lookup, pre-state freeze). Any OSError on an unusable target is a
        # refusal with a receipt — never an uncaught exception, never a retry.
        try:
            return self._append_after_preflight(review=review, authorization=authorization, receipt=receipt)
        except OSError as exc:
            receipt["status"] = STATUS_BLOCKED_IMMUTABLE
            receipt["reason"] = f"target unusable before append ({exc}) — fail closed, no retry"
            return self._finish(receipt)

    def _append_after_preflight(
        self,
        *,
        review: RSIReviewRecordV1,
        authorization: ReviewAuthorization,
        receipt: dict,
    ) -> dict:

        # L4 pre-check — a torn tail quarantines the ledger (§11).
        scan = self._scan()
        if scan["torn_tail"]:
            receipt["status"] = STATUS_REFUSED_TORN_TAIL
            receipt["reason"] = "target has an unparseable line — ledger quarantined, no append"
            return self._finish(receipt)

        # L2 — idempotency: an existing review_id appends nothing (§11).
        for prior in scan["reviews"]:
            if prior.get("review_id") == review.review_id:
                receipt["status"] = STATUS_IDEMPOTENT
                receipt["existing_row_sha256"] = _sha256_bytes(
                    json.dumps(prior, ensure_ascii=False).encode()
                )
                receipt["reason"] = "review_id already on disk — receipt regenerated, no second row"
                return self._finish(receipt)

        # Original event must exist and be hash-bound (L7, §9 req 3).
        original_row, original_line = self._original_row(review.decision_id)
        if original_row is None:
            receipt["status"] = STATUS_REFUSED_UNKNOWN_DECISION
            receipt["reason"] = "no original decision row with this decision_id on the target"
            return self._finish(receipt)
        original_hash = _sha256_bytes(original_line.encode("utf-8"))
        if review.original_event_hash != original_hash:
            receipt["status"] = STATUS_REFUSED_HASH
            receipt["reason"] = "original_event_hash does not match the on-disk original row"
            return self._finish(receipt)

        # L3 — a second review must supersede explicitly (§11 + §7.2, M6).
        prior_for_decision = [r for r in scan["reviews"] if r.get("decision_id") == review.decision_id]
        if prior_for_decision:
            latest_prior = prior_for_decision[-1]
            if review.supersedes_review_id is None:
                receipt["status"] = STATUS_REFUSED_SUPERSEDES
                receipt["reason"] = (
                    "decision already reviewed — re-review must name supersedes_review_id "
                    f"(latest prior review_id={latest_prior.get('review_id')})"
                )
                return self._finish(receipt)
            if review.supersedes_review_id != latest_prior.get("review_id"):
                receipt["status"] = STATUS_REFUSED_SUPERSEDES_MISMATCH
                receipt["reason"] = "supersedes_review_id does not name the latest prior review"
                return self._finish(receipt)

        # Pre-state freeze (§9 req 3/9: failure before append leaves ledger unchanged).
        pre_bytes = self._target.read_bytes() if self._target.exists() else b""
        pre_sha = _sha256_bytes(pre_bytes)
        pre_rows = len([l for l in pre_bytes.decode("utf-8", "replace").splitlines() if l.strip()])
        pre_effective = self._effective_outcomes()

        # Build the appended row: original fields + review updates + v1 fields.
        # Stays RSIDecisionRecord-compatible so the existing loader's
        # last-write-wins semantics are untouched (§7.2).
        latency: float | None = None
        try:
            decision_dt = datetime.fromisoformat(review.decision_timestamp.replace("Z", "+00:00"))
            latency = round((datetime.now(UTC) - decision_dt).total_seconds() / 3600.0, 2)
        except Exception:  # noqa: BLE001 — latency is metadata, never a blocker
            latency = None

        appended = dict(original_row)
        appended.update(
            {
                "schema_version": REVIEW_SCHEMA_VERSION,
                "review_id": review.review_id,
                "supersedes_review_id": review.supersedes_review_id,
                "review_outcome": REVIEW_VERDICT_TO_ROW_OUTCOME[review.review_verdict],
                "review_verdict": review.review_verdict,
                "review_confidence": review.review_confidence,
                "reviewed_by": review.adjudicator_id,
                "authorizer_id": review.authorizer_id,
                "adjudicator_id": review.adjudicator_id,
                "review_evidence": list(review.evidence_hashes),
                "outcome_evidence": list(review.outcome_evidence),
                "review_independent": review.review_independent,
                "review_note": review.rationale,
                "review_latency_hours": latency,
                "original_event_hash": original_hash,
                "authorization_receipt": review.authorization_receipt,
                "review_timestamp": review.review_timestamp,
            }
        )
        line = json.dumps(appended, ensure_ascii=False) + "\n"

        # L4 — one single write() of one complete line (§11: temp+rename is
        # impossible on an append-only file; verify by re-reading).
        try:
            with open(self._target, "a", encoding="utf-8") as fh:
                fh.write(line)
        except PermissionError as exc:
            receipt["status"] = STATUS_BLOCKED_IMMUTABLE
            receipt["reason"] = (
                f"target refused the append ({exc}) — no attribute changed; "
                "a live append is the F13 one-time bridge (§10)"
            )
            return self._finish(receipt)
        except OSError as exc:
            receipt["status"] = STATUS_BLOCKED_IMMUTABLE
            receipt["reason"] = f"target refused the append ({exc})"
            return self._finish(receipt)

        # Verify the write: last line must parse and carry this review_id.
        raw = self._raw_lines()
        if not raw:
            receipt["status"] = STATUS_TORN
            receipt["reason"] = "post-append read found no rows — quarantine"
            return self._finish(receipt)
        try:
            last = json.loads(raw[-1])
        except Exception:
            receipt["status"] = STATUS_TORN
            receipt["reason"] = "last line unparseable after append — torn write, FAILED, do not blind-retry"
            return self._finish(receipt)
        if last.get("review_id") != review.review_id:
            receipt["status"] = STATUS_TORN
            receipt["reason"] = "last line is not this review — concurrent writer suspected, quarantine"
            return self._finish(receipt)

        # L5 — effective-state verification (§9 req 11).
        post_effective = self._effective_outcomes()
        post_rows = len(raw)
        changed = {
            did for did, outcome in post_effective.items() if pre_effective.get(did) != outcome
        }
        if (
            post_rows != pre_rows + 1
            or changed != {review.decision_id}
            or len(post_effective) != len(pre_effective)
        ):
            receipt["status"] = STATUS_VERIFY_FAILED
            receipt["reason"] = (
                "effective-state verification failed — no compensating row will be written "
                "(§11); 888 decides"
            )
            receipt["changed_decision_ids"] = sorted(changed)
            return self._finish(receipt)

        post_bytes = self._target.read_bytes()
        receipt.update(
            {
                "status": STATUS_APPENDED,
                "pre_sha256": pre_sha,
                "post_sha256": _sha256_bytes(post_bytes),
                "appended_row_sha256": _sha256_bytes(raw[-1].encode("utf-8")),
                "pre_rows": pre_rows,
                "post_rows": post_rows,
                "effective_outcome_before": pre_effective.get(review.decision_id),
                "effective_outcome_after": post_effective.get(review.decision_id),
                "effective_decisions_before": len(pre_effective),
                "effective_decisions_after": len(post_effective),
            }
        )
        return self._finish(receipt)

    # ── receipt persistence ──────────────────────────────────────────────────

    def _finish(self, receipt: dict) -> dict:
        """Persist the receipt. A receipt-write failure never triggers a retry."""
        receipt["receipt_timestamp_utc"] = datetime.now(UTC).isoformat()
        try:
            self._receipt_dir.mkdir(parents=True, exist_ok=True)
            path = self._receipt_dir / f"{receipt.get('review_id', 'unknown')}.json"
            path.write_text(json.dumps(receipt, indent=1, ensure_ascii=False) + "\n")
            receipt["receipt_path"] = str(path)
        except Exception as exc:  # noqa: BLE001 — receipt failure ≠ append failure
            receipt["receipt_write_error"] = str(exc)
        return receipt


def append_review_row(
    *,
    target: Path | str,
    review: RSIReviewRecordV1,
    authorization: ReviewAuthorization,
    receipt_dir: Path | str | None = None,
) -> dict:
    """Functional front door (mirrors open_ledger's explicit-target style)."""
    return RSIReviewAppender(target=target, receipt_dir=receipt_dir).append(
        review=review, authorization=authorization
    )


__all__ = [
    "REVIEW_SCHEMA_VERSION",
    "REVIEW_VERDICT_LITERALS",
    "REVIEW_VERDICT_TO_ROW_OUTCOME",
    "REVIEW_CONFIDENCE_LITERALS",
    "RSIReviewAppender",
    "RSIReviewRecordV1",
    "ReviewAuthorization",
    "append_review_row",
    "RECEIPT_DIR_DEFAULT",
]
