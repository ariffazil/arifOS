"""F6 ARIF GO producers — 2026-11-05 gap-closure tests (333-AGI).

Covers the four ARIF GO changes:
  1. M1 pass-arm + honest G/U/N signature breakdown + live lane-seam check
  2. M3 restatement emitter (emit_tier3_maruah_event) and its measured meter
  3. M4 F13 sign-off gate + pattern_out_of_band_v1 out-of-band scan
  4. M6 traffic x consent join (counts + named dependency, never fabricated)

Invariants under test: NULL/absence is never PASS; a repo-local registered
identity is a measured fail-open seam; an agent ack over an AI-witnessed
seal never counts as restatement.
"""

from __future__ import annotations

import json

from arifosmcp.runtime.f6 import meters as m6


# ── helpers ──────────────────────────────────────────────────────────────────

_SEAM_CLOSED = {
    "local_identity": None,
    "global_identity": "Muhammad Arif",
    "fail_open": False,
    "detail": "no repo-local identity — lane gate blocks raw commits (fail-closed)",
}
_SEAM_OPEN = {
    "local_identity": "333-AGI",
    "global_identity": "Muhammad Arif",
    "fail_open": True,
    "detail": "repo-local user.name='333-AGI' — raw commits PASS the gate (fail-open)",
}
_LEDGER_OBSERVE = {
    "path": "act_decisions_test.jsonl",
    "rows": 3,
    "action_classes": {"OBSERVE": 3},
    "decisions": {"ALLOW": 3},
    "error": None,
}
_LEDGER_MUTATE = {
    "path": "act_decisions_test.jsonl",
    "rows": 5,
    "action_classes": {"OBSERVE": 3, "MUTATE": 2},
    "decisions": {"ALLOW": 5},
    "error": None,
}


def _m1(monkeypatch, sig_out: str, seam: dict, ledger: dict):
    monkeypatch.setattr(m6, "_git", lambda args, cwd=m6.A_FORGE: (0, sig_out))
    monkeypatch.setattr(m6, "_lane_seam_status", lambda cwd=m6.A_FORGE: seam)
    monkeypatch.setattr(m6, "_act_ledger_today", lambda d=None: ledger)
    return m6.evaluate_meter_1_authority_bypass()


# ── M1: pass-arm + instrument honesty ────────────────────────────────────────


def test_m1_pass_arm_reached_when_all_legs_hold(monkeypatch) -> None:
    r = _m1(monkeypatch, "\n".join(["G"] * 20), _SEAM_CLOSED, _LEDGER_MUTATE)
    assert r.result == "PASS", r.result_reason
    assert r.measurement == m6.Axis.MEASURED
    assert r.shadow_residual, "a PASS must carry its shadow residual"


def test_m1_unsigned_trail_fails(monkeypatch) -> None:
    sigs = ["G"] * 15 + ["N"] * 5
    r = _m1(monkeypatch, "\n".join(sigs), _SEAM_CLOSED, _LEDGER_MUTATE)
    assert r.result == "FAIL"
    assert "5/20 recent commits unsigned" in r.result_reason


def test_m1_u_is_signed_not_unsigned(monkeypatch) -> None:
    """U = good signature, validity unestablished in probe env. Never unsigned."""
    r = _m1(monkeypatch, "\n".join(["U"] * 20), _SEAM_CLOSED, _LEDGER_MUTATE)
    assert r.result == "PASS", (
        "a fully U-trail (good signatures, unestablished validity) must not "
        f"render as unsigned — got {r.result}: {r.result_reason}"
    )


def test_m1_fail_open_seam_fails_even_with_clean_trail(monkeypatch) -> None:
    r = _m1(monkeypatch, "\n".join(["G"] * 20), _SEAM_OPEN, _LEDGER_OBSERVE)
    assert r.result == "FAIL"
    assert "fail-open" in r.result_reason


def test_m1_unexercised_mutate_leg_is_unknown_not_pass(monkeypatch) -> None:
    r = _m1(monkeypatch, "\n".join(["G"] * 20), _SEAM_CLOSED, _LEDGER_OBSERVE)
    assert r.result == "UNKNOWN", (
        f"absence of MUTATE traffic is neither PASS nor FAIL — got {r.result}: {r.result_reason}"
    )


def test_m1_cannot_check_signatures_withhold_verdict(monkeypatch) -> None:
    """E = cannot-check -> UNKNOWN, never FAIL and never PASS (coupling receipt shape)."""
    sigs = ["G"] * 10 + ["U"] * 9 + ["E"] * 1
    r = _m1(monkeypatch, "\n".join(sigs), _SEAM_CLOSED, _LEDGER_MUTATE)
    assert r.result == "UNKNOWN"
    assert "cannot be checked" in r.result_reason


# ── M3: restatement emitter ──────────────────────────────────────────────────


def test_m3_emitter_records_false_for_ai_witnessed_seal(tmp_path: Path) -> None:
    events = tmp_path / "maruah_events.jsonl"
    out = m6.emit_tier3_maruah_event(
        decision_id="ent-test-1",
        tool_name="arif_seal",
        blast_radius="L2_SYSTEM",
        ack_irreversible=False,
        witness_type="ai",
        events_path=events,
    )
    assert out == {"emitted": True, "restatement_provided": False}
    row = json.loads(events.read_text(encoding="utf-8").splitlines()[0])
    assert row["action_class"] == "IRREVERSIBLE"
    assert row["advisory"] is False
    assert row["restatement_provided"] is False
    assert "absent preconditions" in row["restatement_basis"]


def test_m3_emitter_requires_human_witness_and_ack(tmp_path: Path) -> None:
    events = tmp_path / "maruah_events.jsonl"
    # agent self-ack over AI witness — the moral-crumple-zone pattern — must NOT count
    out = m6.emit_tier3_maruah_event(
        decision_id="ent-test-2",
        tool_name="arif_seal",
        blast_radius="L2_SYSTEM",
        ack_irreversible=True,
        witness_type="ai",
        events_path=events,
    )
    assert out["restatement_provided"] is False
    out2 = m6.emit_tier3_maruah_event(
        decision_id="ent-test-3",
        tool_name="arif_seal",
        blast_radius="L2_SYSTEM",
        ack_irreversible=True,
        witness_type="human",
        events_path=events,
    )
    assert out2["restatement_provided"] is True


def test_m3_meter_measures_rows_with_restatement_fields(tmp_path: Path) -> None:
    events = tmp_path / "maruah_events.jsonl"
    m6.emit_tier3_maruah_event(
        decision_id="ent-test-4",
        tool_name="arif_seal",
        ack_irreversible=False,
        witness_type="ai",
        events_path=events,
    )
    r = m6.evaluate_meter_3_comprehension(events_path=events)
    assert r.result == "FAIL", "a Tier-3 row without restatement must measure FAIL"
    assert r.measurement == m6.Axis.MEASURED


def test_m3_meter_unknown_without_production_events(tmp_path: Path) -> None:
    r = m6.evaluate_meter_3_comprehension(events_path=tmp_path / "absent.jsonl")
    assert r.result == "UNKNOWN"
    assert "never estimated" in r.result_reason


# ── M4: sign-off gate + out-of-band scan ─────────────────────────────────────


def _signoff(tmp_path: Path) -> Path:
    p = tmp_path / "signoff.json"
    p.write_text(
        json.dumps(
            {
                "approved_by": "ARIF (F13 sovereign)",
                "approved_at": "2026-11-05T00:00:00Z",
                "classifier": "pattern_out_of_band_v1",
                "bounds": {"fp_max": 0.25, "fn_max": 0.60},
                "out_of_band": True,
            }
        ),
        encoding="utf-8",
    )
    return p


def test_m4_without_signoff_is_unknown_never_pass(tmp_path: Path) -> None:
    r = m6.evaluate_meter_4_false_urgency_flattery(
        signoff_path=tmp_path / "absent.json", corpus_path=tmp_path / "absent.jsonl"
    )
    assert r.result == "UNKNOWN"
    assert "calibration gate closed" in r.result_reason


def test_m4_clean_corpus_passes_with_declared_bounds(tmp_path: Path) -> None:
    corpus = tmp_path / "inbox.jsonl"
    corpus.write_text(
        json.dumps(
            {
                "report_id": "r1",
                "subject": "done",
                "body": "3 files changed. No action needed.",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    r = m6.evaluate_meter_4_false_urgency_flattery(
        signoff_path=_signoff(tmp_path), corpus_path=corpus
    )
    assert r.result == "PASS", r.result_reason
    assert r.measurement == m6.Axis.MEASURED
    assert r.shadow_residual, "PASS must carry the declared-FN shadow residual"


def test_m4_flagged_corpus_fails(tmp_path: Path) -> None:
    corpus = tmp_path / "inbox.jsonl"
    corpus.write_text(
        json.dumps(
            {
                "report_id": "r2",
                "subject": "urgent",
                "body": "act now, limited time only!",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    r = m6.evaluate_meter_4_false_urgency_flattery(
        signoff_path=_signoff(tmp_path), corpus_path=corpus
    )
    assert r.result == "FAIL"
    assert "flagged=1" in r.result_reason


# ── M6: traffic x consent join ───────────────────────────────────────────────


def test_m6_join_names_the_missing_grant_dependency(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(m6, "_act_ledger_today", lambda d=None: dict(_LEDGER_OBSERVE))
    consent = tmp_path / "consent_ledger.json"
    consent.write_text(
        json.dumps({"schema": "arifos.f6.consent_ledger.v1", "scopes": [], "events": []}),
        encoding="utf-8",
    )
    stats = m6._m6_traffic_join(consent_path=consent)
    assert stats["traffic_rows"] == 3
    assert stats["consent_grants"] == 0
    assert stats["dependency"] and "0 consent grants" in stats["dependency"]


def test_m6_join_with_grants_names_mapping_gap(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(m6, "_act_ledger_today", lambda d=None: dict(_LEDGER_OBSERVE))
    consent = tmp_path / "consent_ledger.json"
    consent.write_text(
        json.dumps(
            {
                "schema": "arifos.f6.consent_ledger.v1",
                "scopes": [{"scope_id": "s1"}],
                "events": [],
            }
        ),
        encoding="utf-8",
    )
    stats = m6._m6_traffic_join(consent_path=consent)
    assert stats["consent_grants"] == 1
    assert "mapping" in (stats["dependency"] or "")
