"""The deterministic promotion gate (FI-003, 2026-10-29, Phase 4).

Contract: forge_work/2026-10-29-TTME-MEMORY-PROMOTION-GATE.md

Rules under test:
- one record + one set of inputs -> one decision, every time (pure);
- every gap is reported, not just the first;
- a REJECT-grade gap beats a REVIEW-grade gap;
- PROMOTE means ELIGIBLE, never ACTIVE — activation is an authority step;
- the decision grammar is memory-promotion, NOT constitutional: no SEAL, and
  HOLD here means "a human must arbitrate";
- low-information, test-only, self-validated, expired and authority-claiming
  records cannot be promoted;
- duplicates are linked (REVIEW), not multiplied;
- the gate mutates nothing.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from arifosmcp.runtime.experience_memory import ExperienceMemory
from arifosmcp.runtime.memory_promotion import (
    AUTHORITY_CLAIM,
    CONTRADICTORY_EVIDENCE,
    DECISION_GRAMMAR,
    DECISIONS,
    DUPLICATE,
    EXPIRED,
    HOLD,
    INDEPENDENCE_NOT_VERIFIED,
    INVALID_SCHEMA,
    LOW_INFORMATION,
    MISSING_OUTCOME,
    MISSING_PROVENANCE,
    NO_CHECKER_EVIDENCE,
    NO_CONSUMER,
    NO_FALSIFIER,
    NOT_REVERSIBLE,
    PROMOTE,
    REASON_CODES,
    REVIEW,
    REJECT,
    SCOPE_TOO_BROAD,
    SELF_VALIDATION_ONLY,
    TEST_ACTOR_ONLY,
    evaluate_promotion,
    evaluate_payload,
    fingerprint,
    main,
)

NOW = datetime(2026, 10, 29, 12, 0, tzinfo=timezone.utc)


def _good(**over) -> ExperienceMemory:
    base = dict(
        memory_id="mem-test-1",
        source_surface="chron_lesson",
        source_record_id="lesson-1",
        actor_id="333-AGI",
        memory_class="LESSON",
        epistemic_status="VERIFIED",
        outcome="SUCCESS",
        promotion_status="RAW",
        distilled_lesson="count underlying objects, not paths",
        applicability_scope="git-history vs live-surface comparisons",
        falsifier="if inode/bind-mount inspection shows one object, this lesson is wrong",
        checker_type="brier_score",
        outcome_evidence="pred-4b67c1dad6b0 verified CORRECT",
        proposed_by="333-AGI",
        verified_by="555-verifier",
        reversible=True,
        eligible_consumers=["chron_prediction"],
        evidence_refs=["/root/chron/data/lessons.jsonl"],
    )
    base.update(over)
    return ExperienceMemory(**base)


# ── the happy path ─────────────────────────────────────────────────────────
def test_a_complete_record_is_eligible_and_never_activated():
    d = evaluate_promotion(_good(), now=NOW)
    assert d.decision == PROMOTE
    assert d.reason_codes == []
    # ELIGIBLE, not ACTIVE: activation is an authority step (F13).
    assert d.next_promotion_status == "REVIEWED"
    assert d.to_dict()["decision_grammar"] == DECISION_GRAMMAR


# ── every criterion produces its reason code ───────────────────────────────
@pytest.mark.parametrize(
    "over,expected",
    [
        ({"actor_id": None, "evidence_refs": [], "source_record_id": ""}, MISSING_PROVENANCE),
        ({"outcome": "UNKNOWN"}, MISSING_OUTCOME),
        ({"outcome": "UNOBSERVED"}, MISSING_OUTCOME),
        ({"checker_type": None, "outcome_evidence": None}, NO_CHECKER_EVIDENCE),
        ({"applicability_scope": None}, SCOPE_TOO_BROAD),
        ({"falsifier": None}, NO_FALSIFIER),
        ({"eligible_consumers": []}, NO_CONSUMER),
        ({"reversible": False}, NOT_REVERSIBLE),
        ({"authorized_by": "F13"}, AUTHORITY_CLAIM),
    ],
)
def test_each_missing_requirement_is_named(over, expected):
    d = evaluate_promotion(_good(**over), now=NOW)
    assert expected in d.reason_codes
    assert d.decision in (REVIEW, REJECT)


def test_all_gaps_are_reported_not_just_the_first():
    d = evaluate_promotion(
        _good(
            actor_id=None,
            source_record_id="",
            evidence_refs=[],
            outcome="UNKNOWN",
            checker_type=None,
            outcome_evidence=None,
            falsifier=None,
        ),
        now=NOW,
    )
    assert {MISSING_PROVENANCE, MISSING_OUTCOME, NO_CHECKER_EVIDENCE, NO_FALSIFIER} <= set(d.reason_codes)


def test_self_validation_cannot_promote():
    d = evaluate_promotion(_good(verified_by="333-AGI"), now=NOW)
    assert SELF_VALIDATION_ONLY in d.reason_codes
    assert d.decision == REJECT


def test_independence_flagged_false_is_a_reject():
    d = evaluate_promotion(_good(), independent_verified=False, now=NOW)
    assert SELF_VALIDATION_ONLY in d.reason_codes
    assert d.decision == REJECT


def test_independence_claim_overrides_a_self_match():
    d = evaluate_promotion(_good(verified_by="333-AGI"), independent_verified=True, now=NOW)
    assert SELF_VALIDATION_ONLY not in d.reason_codes
    assert d.decision == PROMOTE


def test_a_candidate_that_claims_review_must_have_independent_verification():
    d = evaluate_promotion(_good(promotion_status="REVIEWED"), now=NOW)
    assert INDEPENDENCE_NOT_VERIFIED in d.reason_codes
    assert d.decision == REVIEW


def test_contradictions_need_a_human():
    d = evaluate_promotion(_good(), contradictions=["CHRON says the opposite"], now=NOW)
    assert CONTRADICTORY_EVIDENCE in d.reason_codes
    assert d.decision == HOLD
    assert d.next_promotion_status == "CANDIDATE"


def test_duplicate_is_linked_not_multiplied():
    d = evaluate_promotion(_good(), duplicate_of="abc123", now=NOW)
    assert DUPLICATE in d.reason_codes
    assert d.decision == REVIEW


def test_low_information_is_noise_and_never_promotable():
    d = evaluate_promotion(_good(memory_class="NOISE", distilled_lesson="x"), now=NOW)
    assert LOW_INFORMATION in d.reason_codes
    assert d.decision == REJECT


def test_test_actor_provenance_is_never_promotable():
    mem = ExperienceMemory(
        memory_id="mem-test-actor",
        source_surface="seal_c_proposal",
        source_record_id="prop-1",
        actor_id="test-actor",
        memory_class="EPISODE",
        outcome="UNKNOWN",
        distilled_lesson="a plausible sounding line",
        source_payload={"actor_id": "test-actor", "session_id": "observe-only-session"},
    )
    d = evaluate_promotion(mem, now=NOW)
    assert TEST_ACTOR_ONLY in d.reason_codes
    assert d.decision == REJECT


def test_expired_records_are_rejected():
    d = evaluate_promotion(_good(expires_at=(NOW - timedelta(days=1)).isoformat()), now=NOW)
    assert EXPIRED in d.reason_codes
    assert d.decision == REJECT


def test_a_future_expiry_does_not_reject():
    d = evaluate_promotion(_good(expires_at=(NOW + timedelta(days=30)).isoformat()), now=NOW)
    assert EXPIRED not in d.reason_codes


def test_invalid_schema_is_rejected():
    d = evaluate_promotion(_good(schema_version="experience-memory/0.1"), now=NOW)
    assert INVALID_SCHEMA in d.reason_codes
    assert d.decision == REJECT


# ── precedence and purity ──────────────────────────────────────────────────
def test_a_reject_grade_gap_beats_a_review_grade_gap():
    d = evaluate_promotion(_good(falsifier=None, memory_class="NOISE"), now=NOW)
    assert d.decision == REJECT
    assert LOW_INFORMATION in d.reason_codes
    assert NO_FALSIFIER in d.reason_codes


def test_the_gate_is_deterministic():
    mem = _good(outcome="UNKNOWN")
    first = evaluate_promotion(mem, now=NOW).to_dict()
    second = evaluate_promotion(mem, now=NOW).to_dict()
    assert first == second


def test_the_gate_mutates_nothing():
    mem = _good()
    before = mem.to_dict()
    evaluate_promotion(mem, now=NOW)
    assert mem.to_dict() == before


# ── grammar separation ─────────────────────────────────────────────────────
def test_decision_grammar_is_not_constitutional():
    assert "SEAL" not in DECISIONS
    assert "VOID" not in DECISIONS
    assert set(DECISIONS) == {PROMOTE, REVIEW, REJECT, HOLD, "UNKNOWN"}
    d = evaluate_promotion(_good(), now=NOW)
    assert d.to_dict()["decision_grammar"] == "memory_promotion/1.0"


def test_every_reason_code_emitted_is_a_known_code():
    d = evaluate_promotion(_good(falsifier=None, outcome="UNKNOWN", eligible_consumers=[]), now=NOW)
    assert set(d.reason_codes) <= REASON_CODES


# ── duplicates ─────────────────────────────────────────────────────────────
def test_fingerprint_is_stable_for_the_same_lesson():
    a = _good(distilled_lesson="Count  underlying objects, not paths")
    b = _good(distilled_lesson="count underlying objects, not paths")
    c = _good(distilled_lesson="something entirely different")
    assert fingerprint(a) == fingerprint(b)
    assert fingerprint(a) != fingerprint(c)


# ── payload routing (the route other organs use) ───────────────────────────
def test_evaluate_payload_routes_a_chron_lesson():
    d = evaluate_payload(
        {
            "lesson_id": "lesson-x",
            "status": "CANDIDATE",
            "lesson": "the promotion gate needs external validation",
            "principal": "arif",
            "brier_score": 0.06,
            "basis": "pred-4b67c1dad6b0",
        },
        now=NOW,
    )
    assert d.decision in (REVIEW, HOLD, REJECT, PROMOTE)
    assert d.decision != "UNKNOWN"


def test_evaluate_payload_reports_unknown_for_an_unknown_surface():
    d = evaluate_payload({"something": "else"}, now=NOW)
    assert d.decision == "UNKNOWN"
    assert INVALID_SCHEMA in d.reason_codes


# ── CLI (the subprocess route for organs that must not import arifOS) ───────
def test_cli_prints_a_json_decision(tmp_path, capsys):
    path = tmp_path / "mem.json"
    path.write_text(json.dumps(_good().to_dict()), encoding="utf-8")
    rc = main([str(path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["decision"] in DECISIONS
    assert out["decision_grammar"] == DECISION_GRAMMAR
