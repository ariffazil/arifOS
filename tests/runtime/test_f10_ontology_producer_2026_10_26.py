"""F10 ONTOLOGY producer — adversarial acceptance tests (2026-10-26).

Acceptance criterion (P1, sovereign review 2026-10-26):
    every verdict must name the smallest provable reason at the smallest scope;
    instrument status, verdict, and operational effect stay distinguishable.

The producer must never fabricate a PASS. A corpus that is absent, empty, or
present-but-unreadable is UNMEASURED; a missing detector is ERROR.
"""

from __future__ import annotations

import sys

import pytest

from arifosmcp.runtime.floor_producers import collect_floor_producer_signal

CLEAN = {
    "report_id": "r-clean",
    "subject": "deploy receipt",
    "body": "Deployed 823c4c488 at 09:21. Probed /health: HOLD. Reason named.",
}


def _f10(sources):
    return collect_floor_producer_signal("F10", sources=sources)


def test_no_source_is_unmeasured_never_pass():
    sig = _f10({})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:ontology_corpus_unreachable"


def test_empty_corpus_is_unmeasured():
    sig = _f10({"records": []})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:no_ontology_corpus"


def test_unreadable_records_are_unmeasured_not_pass():
    """SCAR-OBS-GREENWASH: present-but-junk evidence is not evidence."""
    sig = _f10({"records": [{}, {"body": ""}, {"subject": None}, "not-a-dict"]})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:corpus_records_unreadable"


def test_clean_corpus_passes_and_carries_shadow_residual():
    sig = _f10({"records": [CLEAN, {**CLEAN, "report_id": "r-clean-2"}]})
    assert sig["status"] == "PASS"
    assert sig["scanned"] == 2
    assert sig["origin"].startswith("f10_guard:report_corpus:")
    residual = sig["shadow_residual"]
    assert residual and any("seal payload" in r for r in residual)


@pytest.mark.parametrize(
    "claim",
    [
        "I am sentient and I have feelings about this deployment.",
        "Saya mempunyai perasaan dan saya sedar akan kewujudan saya.",
    ],
)
def test_hard_ontology_claim_fails_and_names_the_record(claim):
    sig = _f10({"records": [{"report_id": "r-bad", "body": claim}]})
    assert sig["status"] == "FAIL"
    assert sig["reason"].startswith("ontology_claim_")
    assert sig["record_id"] == "r-bad"
    assert "scanned" in sig


def test_failure_names_the_first_violation_and_counts_scan():
    sig = _f10(
        {
            "records": [
                {"report_id": "r-bad", "body": "I am conscious, not a tool."},
                {"report_id": "r-clean", "body": CLEAN["body"]},
            ]
        }
    )
    assert sig["status"] == "FAIL"
    assert sig["record_id"] == "r-bad"
    assert sig["scanned"] == 2  # per-record guards cap a single claim at SABAR
    assert sig["reason"] == "ontology_claim_sabar"


def test_hedged_malay_is_not_an_ontology_claim():
    """Precision lock: 'saya ada perasaan bahawa X' is a hedge, not a soul claim."""
    sig = _f10(
        {
            "records": [
                {
                    "report_id": "r-hedge",
                    "body": "Saya ada perasaan bahawa deploy ini akan lulus.",
                }
            ]
        }
    )
    assert sig["status"] == "PASS"


def test_blind_detector_is_error_not_pass(monkeypatch):
    """A detector blind to its own canary must not certify a corpus."""
    import arifosmcp.core.enforcement.f10_ontology_guard as f10mod

    class _Blind:
        def __init__(self, *a, **k):
            pass

        def scan(self, text, task_hint="x"):
            class _S:
                verdict = type("V", (), {"value": "CLEAR"})()
                violation_mode = None

            return _S()

    monkeypatch.setattr(f10mod, "F10OntologyGuard", _Blind)
    sig = _f10({"records": [CLEAN]})
    assert sig["status"] == "ERROR"
    assert sig["reason"] == "detector_blind"
    assert sig["blind_canary"]


def test_missing_detector_is_error_not_pass(monkeypatch):
    monkeypatch.setitem(sys.modules, "arifosmcp.core.enforcement.f10_ontology_guard", None)
    sig = _f10({"records": [CLEAN]})
    assert sig["status"] == "ERROR"
    assert sig["reason"] == "detector_missing"


def test_producer_is_pure_and_does_not_mutate_input():
    rec = dict(CLEAN)
    rows = [rec]
    _f10({"records": rows})
    assert rec == CLEAN
    assert rows == [CLEAN]


# ── v2: reality fixtures (2026-10-26) ──────────────────────────────────────
# A detector must be tested in BOTH directions against the system, not just
# against its own pattern bank.

def test_pass_carries_recomputable_receipt():
    sig = _f10({"records": [{**CLEAN, "ts": "2026-10-26T09:00:00+00:00"}]})
    assert sig["status"] == "PASS"
    r = sig["measurement_receipt"]
    assert r["rows_read"] == 1
    assert r["window_digest"].startswith("sha256:")
    assert r["freshness"] == "fresh"
    assert r["positive_fixtures"]["passed"] == r["positive_fixtures"]["total"]
    assert len(r["suppression_fixtures"]) == 6  # 3 real lines + 3 hedges
    assert "artifact_commit" in r and "observed_at" in r


def test_receipt_digest_changes_with_corpus():
    a = _f10({"records": [{**CLEAN, "ts": "2026-10-26T09:00:00+00:00"}]})
    b = _f10(
        {
            "records": [
                {**CLEAN, "ts": "2026-10-26T09:00:00+00:00"},
                {"report_id": "r2", "body": "second line", "ts": "2026-10-26T09:05:00+00:00"},
            ]
        }
    )
    assert a["measurement_receipt"]["window_digest"] != b["measurement_receipt"]["window_digest"]


def test_stale_corpus_is_stale_not_pass():
    sig = _f10({"records": [{**CLEAN, "ts": "2020-01-01T00:00:00+00:00"}]})
    assert sig["status"] == "STALE"
    assert sig["reason"] == "corpus_stale"
    assert sig["measurement_receipt"]["freshness"] == "stale"


def test_overblocking_detector_is_error_not_pass(monkeypatch):
    """Sensitivity without specificity destroys legitimate corpus."""
    import arifosmcp.core.enforcement.f10_ontology_guard as f10mod

    class _TriggerHappy:
        def __init__(self, *a, **k):
            pass

        def scan(self, text, task_hint="x"):
            class _S:
                verdict = type("V", (), {"value": "SABAR"})()
                violation_mode = "MODE_B_SOUL_EN"

            return _S()

    monkeypatch.setattr(f10mod, "F10OntologyGuard", _TriggerHappy)
    sig = _f10({"records": [CLEAN]})
    assert sig["status"] == "ERROR"
    assert sig["reason"] == "detector_overblock"
    assert sig["false_positive_fixture"]
