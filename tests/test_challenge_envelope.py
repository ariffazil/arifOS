"""555 challenge envelope — one verification protocol (shape approved 2026-10-18).

Fields: claim · evidence · provenance · freshness · contradiction · falsifier ·
confidence · independent_witness. Verdicts: ACCEPT · REJECT · UNKNOWN_OUTCOME.

NAMED CONSUMERS: arif_judge evidence gate (kernel) · HERMES claim_validate ·
CHRON prediction mint · FRAME observation handoff · A-FORGE claim gates —
each through its adapter below.
NAMED FAILURE CLASSES: CLAIM_WITHOUT_FALSIFIER (a claim no one can falsify is
not a challenge), WITNESS_SELF (the claimant is not its own witness),
EVIDENCE_ABSENT (cannot judge -> UNKNOWN_OUTCOME, never ACCEPT).

Spec home: /root/AAA/schemas/challenge-envelope.schema.json
"""

from __future__ import annotations

from arifosmcp.runtime.challenge_envelope import (
    CLAIM_WITHOUT_FALSIFIER,
    VERDICT_ACCEPT,
    VERDICT_REJECT,
    VERDICT_UNKNOWN_OUTCOME,
    WITNESS_SELF,
    from_aforge_receipt,
    from_chron_prediction,
    from_frame_observation,
    from_hermes_claim,
    validate_envelope,
)

FULL = {
    "claim": "F5 floor is measured by a live producer",
    "evidence": [{"ref": "probe:2026-10-18T10:11Z", "kind": "live_probe"}],
    "provenance": "333-AGI session SEAL-47c40a7516854c11",
    "freshness": "2026-10-18T10:11:12Z",
    "contradiction": "arif_observe once reported the same floor unmeasured",
    "falsifier": "a probe pair disagreeing on floor_passed reopens the claim",
    "confidence": 0.85,
    "independent_witness": [{"id": "frame", "kind": "witness"}],
    "claimant": "333-AGI",
}


def test_full_envelope_accepts() -> None:
    r = validate_envelope(FULL)
    assert r["verdict"] == VERDICT_ACCEPT
    assert r["reason"] is None


def test_claim_without_falsifier_is_rejected() -> None:
    env = dict(FULL, falsifier="")
    r = validate_envelope(env)
    assert r["verdict"] == VERDICT_REJECT
    assert r["reason"] == CLAIM_WITHOUT_FALSIFIER


def test_whitespace_falsifier_is_rejected() -> None:
    env = dict(FULL, falsifier="   \n ")
    r = validate_envelope(env)
    assert r["verdict"] == VERDICT_REJECT
    assert r["reason"] == CLAIM_WITHOUT_FALSIFIER


def test_missing_falsifier_field_is_rejected() -> None:
    env = dict(FULL)
    env.pop("falsifier")
    r = validate_envelope(env)
    assert r["verdict"] == VERDICT_REJECT
    assert r["reason"] == CLAIM_WITHOUT_FALSIFIER


def test_absent_evidence_is_unknown_outcome_never_accept() -> None:
    env = dict(FULL)
    env.pop("evidence")
    r = validate_envelope(env)
    assert r["verdict"] == VERDICT_UNKNOWN_OUTCOME
    assert "evidence" in r["missing"]


def test_claimant_cannot_be_its_own_only_witness() -> None:
    env = dict(FULL, independent_witness=[{"id": "333-AGI", "kind": "self"}])
    r = validate_envelope(env)
    assert r["verdict"] == VERDICT_UNKNOWN_OUTCOME
    assert r["reason"] == WITNESS_SELF


def test_confidence_out_of_band_is_unknown_outcome() -> None:
    r = validate_envelope(dict(FULL, confidence=1.4))
    assert r["verdict"] == VERDICT_UNKNOWN_OUTCOME


def test_adapters_map_native_shapes_including_falsifiers() -> None:
    h = from_hermes_claim(
        {
            "claim": "X holds",
            "sources": ["s1"],
            "counterstory": "Y undermines X",
            "ts": "2026-10-18T00:00:00Z",
        }
    )
    assert h["claim"] == "X holds"
    assert h["contradiction"] == "Y undermines X"
    assert h["falsifier"]  # adapter derives a challenge path from counterstory

    c = from_chron_prediction(
        {
            "prediction": "gold > 4300 by Nov",
            "resolution": "close above 4300 on 2026-11-30",
            "minted_at": "2026-10-01",
        }
    )
    assert c["falsifier"] == "close above 4300 on 2026-11-30"

    f = from_frame_observation(
        {
            "observation": "drift detected on GEOX",
            "signals": ["degraded"],
            "observed_at": "2026-10-18T10:00:00Z",
        }
    )
    assert f["contradiction"] == "signals: degraded"

    a = from_aforge_receipt(
        {"justification": "fix deploy gate", "receipt_id": "r1", "revert": "git revert <sha>"}
    )
    assert a["falsifier"] == "git revert <sha>"
    for env in (h, c, f, a):
        assert validate_envelope(env)["verdict"] != VERDICT_REJECT


def test_schema_declares_consumers_and_failure_class() -> None:
    import json
    from pathlib import Path

    p = Path("/root/AAA/schemas/challenge-envelope.schema.json")
    assert p.exists(), "spec home must exist"
    s = json.loads(p.read_text())
    assert s.get("x-consumers"), "schema header must name consumers (Law 2)"
    assert "CLAIM_WITHOUT_FALSIFIER" in s.get("x-failure-classes", [])
