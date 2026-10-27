"""E–J tests + the negative tests demanded by 555 verification (rev 2).

Isolated: imports the proposal module only.
Run: /root/arifOS/.venv/bin/python -m pytest -q test_seal_claim.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent))

from arifosmcp.runtime.seal_claim_v1 import (  # noqa: E402
    CONFIDENCE_SEMANTICS_VERSION,
    SealEventV3,
    VerificationStatus,
    apply_judge_actor_b,
    classify_legacy_event,
    derive_claim_id,
)

T0 = datetime(2026, 10, 28, 1, 0, tzinfo=UTC)


def _seal(**kw):
    base = dict(
        event_id="evt-1",
        event_type="vault_seal",
        session_id="sess-1",
        actor_id="333-AGI",
        stage="claim_test",
        verdict="SEAL",
        payload={"note": "x"},
        sealed_at=T0,
    )
    base.update(kw)
    return SealEventV3(**base)


def _confident(**kw):
    kw.setdefault("claim_text", "gate G approved 97 of 100 mutations")
    kw.setdefault("confidence", 0.8)
    kw.setdefault("confidence_actor", "555-asi")
    kw.setdefault("confidence_semantics", CONFIDENCE_SEMANTICS_VERSION)
    kw.setdefault("confidence_produced_at", T0 - timedelta(hours=1))
    return _seal(**kw)


# ── E: serialization / deserialization ─────────────────────────────────────────
def test_E1_roundtrip_preserves_claim_fields():
    ev = _confident()
    again = SealEventV3.model_validate_json(ev.model_dump_json())
    assert again == ev
    assert again.claim_id == ev.claim_id
    assert again.confidence == 0.8


def test_E2_legacy_v2_row_deserialises_without_loss():
    legacy = {
        "event_id": "old-1",
        "event_type": "vault_seal",
        "session_id": "s",
        "actor_id": "codex-cli",
        "stage": "constitutional_gap_closed",
        "verdict": "SEAL",
        "payload": {"summary": "All 12 bugs fixed."},
        "sealed_at": "2026-06-20T00:00:00+00:00",
    }
    ev = classify_legacy_event(legacy)
    assert ev.verification_status is VerificationStatus.EVENT_ONLY
    assert ev.claim_text is None and ev.claim_id is None and ev.confidence is None
    assert ev.to_legacy_vault_event()["verdict"] == "SEAL"


def test_E3_both_writer_rows_carry_the_claim_columns():
    ev = _confident()
    for row in (ev.to_supabase_row(), ev.to_vault_events_row()):
        for col in (
            "claim_id",
            "claim_text",
            "confidence",
            "confidence_actor",
            "confidence_semantics",
            "evidence_refs",
            "verification_status",
        ):
            assert col in row, col
    assert ev.to_supabase_row()["verification_status"] == "CLAIM_RECORDED"


# ── F: missing / empty / whitespace claim_text ─────────────────────────────────
@pytest.mark.parametrize("bad", [None, "", "   ", "\t\n  "])
def test_F_missing_or_blank_claim_is_event_only(bad):
    ev = _seal(claim_text=bad)
    assert ev.claim_text is None
    assert ev.claim_id is None
    assert ev.verification_status is VerificationStatus.EVENT_ONLY


@pytest.mark.parametrize("bad", ["", "  "])
def test_F2_blank_claim_cannot_be_declared_recorded(bad):
    with pytest.raises(ValidationError, match="requires claim_text"):
        _seal(claim_text=bad, verification_status=VerificationStatus.CLAIM_RECORDED)


def test_F3_claim_id_without_claim_text_is_rejected():
    with pytest.raises(ValidationError, match="claim_id set without claim_text"):
        _seal(claim_id="clm-deadbeef", claim_text=None)


# ── G: SEAL does not imply VERIFIED ────────────────────────────────────────────
def test_G1_seal_defaults_to_not_verified():
    assert _seal(verdict="SEAL").verification_status is VerificationStatus.EVENT_ONLY


def test_G2_verified_without_separate_verification_event_is_rejected():
    with pytest.raises(ValidationError, match="requires a separate verification event"):
        _seal(
            claim_text="service X is live",
            verification_status=VerificationStatus.VERIFIED,
            verification_witness_class="store_resolved",
            verified_by="888-apex",
        )


def test_G3_self_verification_is_rejected():
    with pytest.raises(ValidationError, match="self-verification"):
        _seal(
            claim_text="service X is live",
            verification_status=VerificationStatus.VERIFIED,
            verification_witness_class="store_resolved",
            verified_by="333-AGI",  # same as actor_id
            verification_event_id="ver-9",
        )


def test_G4_independent_store_resolved_verification_is_accepted():
    ev = _seal(
        claim_text="service X is live",
        verification_status=VerificationStatus.VERIFIED,
        verification_witness_class="store_resolved",
        verified_by="888-apex",
        verification_event_id="ver-9",
        outcome_observed_at=T0 + timedelta(hours=2),
    )
    assert ev.verification_status is VerificationStatus.VERIFIED


# ── G5–G8: 555 block conditions B1 (rule 5 was self-assertable) ────────────────
@pytest.mark.parametrize(
    "status", [VerificationStatus.VERIFIED, VerificationStatus.FALSIFIED]
)
def test_G5_asserted_witness_class_is_rejected(status):
    with pytest.raises(ValidationError, match="store_resolved"):
        _seal(
            claim_text="c",
            verification_status=status,
            verification_event_id="invented-id",
            verified_by="888-apex",
            # witness_class defaults to "asserted"
        )


def test_G6_self_verification_bypass_by_case_or_space_is_rejected():
    for sneaky in ("333-agi", "333-AGI ", " 333-AGI"):
        with pytest.raises(ValidationError, match="self-verification"):
            _seal(
                claim_text="c",
                verification_status=VerificationStatus.VERIFIED,
                verification_witness_class="store_resolved",
                verified_by=sneaky,
                verification_event_id="ver-1",
            )


def test_G7_witness_class_without_verified_status_is_rejected():
    with pytest.raises(ValidationError, match="only applies to VERIFIED/FALSIFIED"):
        _seal(claim_text="c", verification_witness_class="store_resolved")


# ── H: null preserved, never zero ──────────────────────────────────────────────
def test_H_null_confidence_survives_all_paths():
    ev = _seal(claim_text="claim recorded, no probability produced")
    assert ev.confidence is None
    assert json.loads(ev.model_dump_json())["confidence"] is None
    assert ev.to_supabase_row()["confidence"] is None
    assert ev.to_vault_events_row()["confidence"] is None
    assert ev.to_supabase_row()["confidence"] != 0.0


def test_H2_confidence_metadata_without_value_is_rejected():
    with pytest.raises(ValidationError, match="metadata declared with null confidence"):
        _seal(claim_text="c", confidence_actor="555-asi")


def test_H3_bool_is_not_a_probability():
    with pytest.raises(ValidationError):
        _confident(confidence=True)


# ── I: range enforcement ───────────────────────────────────────────────────────
@pytest.mark.parametrize("bad", [1.5, -0.1, 101.0])
def test_I_out_of_range_confidence_rejected(bad):
    with pytest.raises(ValidationError):
        _confident(confidence=bad)


def test_I2_boundary_values_accepted():
    assert _confident(confidence=0.0).confidence == 0.0
    assert _confident(confidence=1.0).confidence == 1.0


def test_I3_confidence_after_outcome_is_rejected():
    with pytest.raises(ValidationError, match="not a prediction"):
        _confident(
            outcome_observed_at=T0 - timedelta(hours=2),
            confidence_produced_at=T0 - timedelta(hours=1),
        )


# ── J: actor_B cannot masquerade as claim confidence ───────────────────────────
def test_J1_apply_judge_actor_b_refuses():
    ev = _seal(claim_text="c")
    with pytest.raises(ValueError, match="actor_B cannot populate claim confidence"):
        apply_judge_actor_b(ev, 0.93)
    assert ev.confidence is None


@pytest.mark.parametrize(
    "name",
    ["actor_B", "ACTOR_B", "actor_b", "actor-b", "arif_judge:actor_B", "Judge.Actor_B"],
)
def test_J2_actor_b_as_confidence_actor_is_rejected(name):
    with pytest.raises(ValidationError, match="actor_B input"):
        _confident(confidence_actor=name)


def test_J3_judge_confidence_stays_in_payload_not_claim():
    ev = _seal(claim_text="c", payload={"judge_actor_b": 0.93})
    assert ev.confidence is None
    assert ev.payload["judge_actor_b"] == 0.93


# ── new negative tests demanded by 555 (§B untested rules) ─────────────────────
def test_R1_claim_id_is_stable_across_sessions_and_actors():
    a = _seal(event_id="evt-A", claim_text="Service X is live", session_id="sess-A", actor_id="333-agi")
    b = _seal(
        event_id="evt-B",
        claim_text="  service x   is LIVE ",
        session_id="sess-B",
        actor_id="kimi-code",
    )
    assert a.claim_id == b.claim_id == derive_claim_id("Service X is live")
    assert a.event_id != b.event_id  # same proposition, different events


def test_R2_caller_supplied_claim_id_must_match_proposition():
    with pytest.raises(ValidationError, match="does not match the proposition hash"):
        _seal(claim_text="Service X is live", claim_id="clm-0000000000000000")


def test_R3_legacy_dirty_row_is_downgraded_not_crashed():
    dirty = {
        "event_id": "old-2",
        "verdict": "SEAL",
        "actor_id": "codex-cli",
        "sealed_at": "2026-06-20T00:00:00+00:00",
        "claim_text": "All 12 bugs fixed.",
        "confidence": 1.0,
        "verification_status": "VERIFIED",
        "verified_by": "codex-cli",
    }
    ev = classify_legacy_event(dirty)
    assert ev.claim_text is None and ev.confidence is None
    assert ev.verification_status is VerificationStatus.EVENT_ONLY
    assert ev.verification_witness_class == "asserted"


def test_R4_no_backfill_from_prose_payload():
    legacy = {
        "event_id": "old-3",
        "verdict": "SEAL",
        "payload": {"summary": "all fixed"},
    }
    ev = classify_legacy_event(legacy)
    assert ev.claim_text is None  # prose in payload is not a claim


def test_R5_semantics_token_is_enforced_not_narrated():
    with pytest.raises(ValidationError, match="contract token"):
        _confident(confidence_semantics="banana")


def test_R6_confidence_actor_must_be_ident_shaped():
    with pytest.raises(ValidationError, match="not an actor id"):
        _confident(confidence_actor="!!! nobody ???")
