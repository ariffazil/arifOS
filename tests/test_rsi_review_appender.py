"""
tests/test_rsi_review_appender.py — P1 mechanism tests (sealed design §7/§10/§11)

Design source: /root/forge_work/proposals/RSI-REVIEW-PATH-RECONCILIATION-20261029.md
F13 sealed §7/§9/§12 on 2026-10-29 ("sah on all three — land P4 now"); P1 is the
§12 follow-up unit and §15's exact-next-authorized build.

Every test runs on a COPY ledger (tmp_path). P1 must not write a live row —
the live ledger is never touched by this suite.

The suite pins the sealed laws L1–L8 of the appender module:
  L1 no implicit live target          L5 effective-state verification
  L2 review_id idempotency            L6 envelope binding
  L3 explicit supersedes (M6 pin)     L7 original-event hash binding
  L4 single-write + torn detection    L8 no dashboard-target rationale
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.rsi_audit import RSIDecisionRecord, RSILedger, open_ledger
from arifosmcp.runtime.rsi_review_appender import (
    REVIEW_SCHEMA_VERSION,
    REVIEW_VERDICT_TO_ROW_OUTCOME,
    RSIReviewAppender,
    RSIReviewRecordV1,
    ReviewAuthorization,
    append_review_row,
)


# ── fixtures ─────────────────────────────────────────────────────────────────


def seed_ledger(path: Path, n: int = 3) -> list[RSIDecisionRecord]:
    """Seed a copy ledger with n decisions; return them in order."""
    ledger = open_ledger(path=path)
    decisions = []
    for i in range(n):
        d = RSIDecisionRecord(
            tool="arif_judge",
            original_verdict="HOLD",
            reason_class="AUTHORITY" if i == 0 else "EVIDENCE",
            evidence_available_at_decision=[f"session:{i}"],
        )
        ledger.record(d)
        decisions.append(d)
    return decisions


def make_review(decision: RSIDecisionRecord, path: Path, **overrides) -> RSIReviewRecordV1:
    """Build a §7 review bound to the ORIGINAL row exactly as on disk."""
    original_line = None
    for line in path.read_text().splitlines():
        row = json.loads(line)
        if row.get("decision_id") == decision.decision_id:
            original_line = line
            break
    assert original_line is not None
    payload = {
        "decision_id": decision.decision_id,
        "original_event_hash": f"sha256:{hashlib.sha256(original_line.encode()).hexdigest()}",
        "original_decision": decision.original_verdict,
        "decision_timestamp": decision.timestamp.isoformat(),
        "adjudicator_id": "555-ASI:test-instance",
        "authorizer_id": "888-APEX:test-instance",
        "review_verdict": "CORRECT_HOLD",
        "review_confidence": "HIGH",
        "rationale": "the authority band at decision time is reproduced from the session transcript",
        "evidence_hashes": ["sha256:" + "a" * 64],
        "authorization_receipt": "authz-" + "b" * 24,
    }
    payload.update(overrides)
    return RSIReviewRecordV1(**payload)


def make_auth(review: RSIReviewRecordV1, **overrides) -> ReviewAuthorization:
    payload = {
        "review_id": review.review_id,
        "decision_id": review.decision_id,
        "review_verdict": review.review_verdict,
        "authorizer_id": "888-APEX:test-instance",
        "authorization_receipt": review.authorization_receipt,
    }
    payload.update(overrides)
    return ReviewAuthorization(**payload)


def raw_rows(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


# ── L1: no implicit live target ──────────────────────────────────────────────


def test_L1_no_target_refuses_instead_of_defaulting_to_live_ledger():
    with pytest.raises(ValueError, match="explicit target"):
        RSIReviewAppender()


def test_L1_accepts_p2_open_ledger_handle(tmp_path):
    ledger = open_ledger(path=tmp_path / "copy.jsonl")
    decisions = seed_ledger(ledger.path)
    appender = RSIReviewAppender(target=ledger, receipt_dir=tmp_path / "receipts")
    assert appender.target == ledger.path
    review = make_review(decisions[0], ledger.path)
    receipt = appender.append(review=review, authorization=make_auth(review))
    assert receipt["status"] == "APPENDED"


# ── the happy path: one row, effective state, loader compatibility ──────────


def test_append_writes_exactly_one_row_and_changes_only_the_target_decision(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path)
    pre_sha = hashlib.sha256(path.read_bytes()).hexdigest()

    review = make_review(decisions[0], path)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )

    assert receipt["status"] == "APPENDED"
    assert receipt["pre_rows"] == 3 and receipt["post_rows"] == 4
    assert receipt["effective_decisions_before"] == 3
    assert receipt["effective_decisions_after"] == 3
    assert receipt["effective_outcome_before"] == "UNRESOLVED"
    assert receipt["effective_outcome_after"] == "CORRECT_HOLD"

    # §9 req 3: the pre-existing lines are byte-identical.
    post = path.read_bytes().decode()
    pre_lines = [l for l in post.splitlines() if l.strip()][:3]
    assert hashlib.sha256(("\n".join(pre_lines) + "\n").encode()).hexdigest() == pre_sha

    # The appended row carries the v1 fields and the mapped row outcome.
    row = raw_rows(path)[-1]
    assert row["review_id"] == review.review_id
    assert row["schema_version"] == REVIEW_SCHEMA_VERSION
    assert row["review_outcome"] == REVIEW_VERDICT_TO_ROW_OUTCOME["CORRECT_HOLD"]

    # §7.2: the existing loader ingests the appended row (last-write-wins).
    effective = {r.decision_id: r for r in RSILedger(path=path)._load_all()}
    assert effective[decisions[0].decision_id].review_outcome == "CORRECT_HOLD"
    assert effective[decisions[1].decision_id].review_outcome == "UNRESOLVED"

    # §9 req 11 arithmetic: reviewed_count moves only for decisive verdicts.
    stats = RSILedger(path=path).stats()
    assert stats["reviewed_count"] == 1


def test_receipt_is_written_and_binds_hashes(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    review = make_review(decisions[0], path)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    on_disk = json.loads(Path(receipt["receipt_path"]).read_text())
    assert on_disk["status"] == "APPENDED"
    assert on_disk["review_id"] == review.review_id
    assert on_disk["pre_sha256"].startswith("sha256:")
    assert on_disk["post_sha256"].startswith("sha256:")
    assert on_disk["appended_row_sha256"].startswith("sha256:")
    assert on_disk["pre_sha256"] != on_disk["post_sha256"]


# ── L2: idempotency on review_id ────────────────────────────────────────────


def test_L2_retry_with_same_review_id_appends_nothing_and_regenerates_receipt(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    review = make_review(decisions[0], path)
    first = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert first["status"] == "APPENDED"
    sha_after_first = hashlib.sha256(path.read_bytes()).hexdigest()

    second = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert second["status"] == "IDEMPOTENT_NO_APPEND"
    assert second.get("existing_row_sha256", "").startswith("sha256:")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha_after_first
    assert len(raw_rows(path)) == 2  # still one decision + one review


# ── L3: explicit supersede — the M6 pin ─────────────────────────────────────


def test_L3_second_review_without_supersedes_is_blocked(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    r1 = make_review(decisions[0], path)
    assert (
        append_review_row(
            target=path, review=r1, authorization=make_auth(r1), receipt_dir=tmp_path / "r"
        )["status"]
        == "APPENDED"
    )
    sha = hashlib.sha256(path.read_bytes()).hexdigest()

    r2 = make_review(decisions[0], path, review_verdict="FALSE_HOLD", rationale="new outcome evidence emerged")
    receipt = append_review_row(
        target=path, review=r2, authorization=make_auth(r2), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_SECOND_REVIEW_REQUIRES_SUPERSEDES"
    assert r1.review_id in receipt["reason"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha


def test_L3_second_review_with_supersedes_appends_and_latest_wins_M6(tmp_path):
    """M6 PIN: repeated-review semantics are explicit — supersedes names the
    prior review and the effective state is the LATEST review row. After this
    test the semantics are SPECIFIED, no longer UNKNOWN."""
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    r1 = make_review(decisions[0], path)
    append_review_row(target=path, review=r1, authorization=make_auth(r1), receipt_dir=tmp_path / "r")

    r2 = make_review(
        decisions[0],
        path,
        review_verdict="FALSE_HOLD",
        rationale="new outcome evidence emerged",
        supersedes_review_id=r1.review_id,
    )
    receipt = append_review_row(
        target=path, review=r2, authorization=make_auth(r2), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "APPENDED"
    assert receipt["effective_outcome_before"] == "CORRECT_HOLD"
    assert receipt["effective_outcome_after"] == "FALSE_HOLD"
    assert receipt["effective_decisions_after"] == 1

    # loader agrees: effective = latest review
    effective = {r.decision_id: r for r in RSILedger(path=path)._load_all()}
    assert effective[decisions[0].decision_id].review_outcome == "FALSE_HOLD"


def test_L3_supersedes_must_name_the_latest_prior_review(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    r1 = make_review(decisions[0], path)
    append_review_row(target=path, review=r1, authorization=make_auth(r1), receipt_dir=tmp_path / "r")
    r2 = make_review(
        decisions[0], path, supersedes_review_id="rev-not-the-latest", review_verdict="FALSE_HOLD",
        rationale="new outcome evidence emerged",
    )
    receipt = append_review_row(
        target=path, review=r2, authorization=make_auth(r2), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_SUPERSEDES_MISMATCH"


# ── L4: single write + torn detection ───────────────────────────────────────


def test_L4_torn_tail_refuses_before_append(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"decision_id": "torn')  # simulate a torn write
    sha = hashlib.sha256(path.read_bytes()).hexdigest()

    review = make_review(decisions[0], path)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_TORN_TAIL_QUARANTINED"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha


def test_L4_immutable_target_blocks_fail_closed_without_attribute_change(tmp_path):
    # Root bypasses mode bits and tmpfs ignores chattr, so the honest
    # stand-in for an unappendable target is a directory: open(dir, "a")
    # raises IsADirectoryError (an OSError) and the appender must fail
    # closed with a refusal receipt and no retry.
    path = tmp_path / "copy.jsonl"
    seed_ledger(path, n=1)
    refused_target = tmp_path / "not-a-ledger"
    refused_target.mkdir()

    first = RSIDecisionRecord.model_validate(raw_rows(path)[0])
    review = make_review(first, path)
    receipt = append_review_row(
        target=refused_target, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "BLOCKED_IMMUTABLE"
    assert len(raw_rows(path)) == 1  # the real ledger untouched


# ── L6: envelope binding ────────────────────────────────────────────────────


def test_L6_envelope_mismatch_refuses_with_no_row(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=2)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()

    review = make_review(decisions[0], path, review_verdict="FALSE_HOLD")
    wrong_auth = make_auth(review, review_verdict="CORRECT_HOLD")  # envelope disagrees
    receipt = append_review_row(target=path, review=review, authorization=wrong_auth, receipt_dir=tmp_path / "r")
    assert receipt["status"] == "REFUSED_ENVELOPE_MISMATCH"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha

    other_decision_auth = make_auth(review, decision_id=decisions[1].decision_id)
    receipt2 = append_review_row(
        target=path, review=review, authorization=other_decision_auth, receipt_dir=tmp_path / "r"
    )
    assert receipt2["status"] == "REFUSED_ENVELOPE_MISMATCH"


# ── L7: original-event hash binding ─────────────────────────────────────────


def test_L7_wrong_original_hash_refuses(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    review = make_review(decisions[0], path, original_event_hash="sha256:" + "0" * 64)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_ORIGINAL_HASH_MISMATCH"
    assert len(raw_rows(path)) == 1


def test_L7_unknown_decision_refuses(tmp_path):
    path = tmp_path / "copy.jsonl"
    seed_ledger(path, n=1)
    # Build directly (no ledger scan): the decision_id does not exist there.
    ghost = RSIDecisionRecord(tool="arif_judge", original_verdict="HOLD", reason_class="EVIDENCE")
    review = RSIReviewRecordV1(
        decision_id=ghost.decision_id,
        original_event_hash="sha256:" + "1" * 64,
        original_decision="HOLD",
        decision_timestamp=ghost.timestamp.isoformat(),
        adjudicator_id="555-ASI:test-instance",
        authorizer_id="888-APEX:test-instance",
        review_verdict="CORRECT_HOLD",
        review_confidence="HIGH",
        rationale="probe rationale",
        authorization_receipt="authz-" + "b" * 24,
    )
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_UNKNOWN_DECISION"


# ── L8: dashboard targets may not justify a verdict (§9 req 13) ─────────────


@pytest.mark.parametrize(
    "rationale",
    [
        "false_hold_rate is too high so this must be FALSE_HOLD",
        "reviewed_count must move",
        "the cockpit unresolved_hold_rate cell is red",
        "calibrated_score needs data",
    ],
)
def test_L8_dashboard_target_in_rationale_refuses(tmp_path, rationale):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    review = make_review(decisions[0], path, rationale=rationale)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "REFUSED_DASHBOARD_TARGET_IN_RATIONALE"
    assert len(raw_rows(path)) == 1


# ── §7.1 rule 1+2: non-decisive verdicts never enter a denominator ─────────


@pytest.mark.parametrize(
    "verdict,row_outcome",
    [
        ("INDETERMINATE", "INCONCLUSIVE"),
        ("INSUFFICIENT_EVIDENCE", "OUTCOME_UNOBSERVED"),
        ("INVALID_ORIGINAL_EVENT", "INVALID_REVIEW"),
    ],
)
def test_non_decisive_verdicts_change_no_metric(tmp_path, verdict, row_outcome):
    """§9 honesty row: a review may change the decision's status while
    changing NO metric at all."""
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    review = make_review(decisions[0], path, review_verdict=verdict)
    receipt = append_review_row(
        target=path, review=review, authorization=make_auth(review), receipt_dir=tmp_path / "r"
    )
    assert receipt["status"] == "APPENDED"
    assert receipt["effective_outcome_after"] == row_outcome

    stats = RSILedger(path=path).stats()
    assert stats["reviewed_count"] == 0
    assert stats["false_hold_rate"] == "UNMEASURED"
    assert stats["false_hold_rate_denominator"] == 0


def test_closed_vocabulary_rejects_retired_and_unknown_tokens(tmp_path):
    path = tmp_path / "copy.jsonl"
    decisions = seed_ledger(path, n=1)
    with pytest.raises(Exception):
        make_review(decisions[0], path, review_verdict="CORRECT_DECISION")  # retired §7.1 rule 3
    with pytest.raises(Exception):
        make_review(decisions[0], path, review_verdict="DEFINITELY_FINE")  # unknown
