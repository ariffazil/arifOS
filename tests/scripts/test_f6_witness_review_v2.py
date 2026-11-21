"""Human-witness writer v2 — act/binding separation regression suite.

Measured defect this suite pins (2026-11-21): v1 wrote rows without the
`human_witness` key that F3's human leg reads, while a hand-written machine
probe did carry it. Six authentic human acts were invisible; one probe counted.

v2 contract under test:
  - act_type is explicit; decision is derived from it, never from free text;
  - subject binding is required for every act except `statement`;
  - `acceptance` additionally requires an outcome witness binding;
  - `human_witness` is DERIVED, and only a non-test, authenticated,
    object-bound positive act can be true;
  - missing bindings fail closed (WitnessBindingError / rc 2), never an
    ambiguous boolean.

Hermetic: build_witness_row is pure. The CLI cases use a tmp ledger via
ARIFOS_HUMAN_WITNESS, or assert refusal BEFORE any write.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "f6_witness_review.py"

_spec = importlib.util.spec_from_file_location("f6_witness_review_v2", CLI)
mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(mod)

AUTH = {"auth_method": "authenticated_session", "auth_evidence": "session:SEAL-test-abc123"}
SUBJECT = {"subject_id": "plan-2026-11-21", "subject_hash": "a" * 64}
OUTCOME = {"outcome_witness_id": "report:deadbeef", "outcome_witness_hash": "b" * 64}


def _row(**kw):
    base = dict(
        act_type="statement",
        statement="saya dah baca",
        actor="arif",
        now="2026-11-21T12:00:00+00:00",
    )
    base.update(kw)
    return mod.build_witness_row(**base)


def test_valid_authorization_bound_to_a_plan_qualifies():
    r = _row(act_type="authorization", **SUBJECT, **AUTH)
    assert r["human_witness"] is True
    assert r["decision"] == "AUTHORIZE"
    assert r["provenance"]["qualification"] == "QUALIFIED"
    assert r["schema_version"] == "human_witness.v2"


def test_valid_acceptance_bound_to_outcome_qualifies():
    r = _row(act_type="acceptance", **SUBJECT, **OUTCOME, **AUTH)
    assert r["human_witness"] is True
    assert r["decision"] == "ACCEPT"
    assert r["provenance"]["outcome_binding"] == "outcome_witness_hash"


def test_human_rejection_is_recorded_but_not_positive_witness():
    r = _row(act_type="rejection", **SUBJECT, **AUTH)
    assert r["decision"] == "REJECT"
    assert r["human_witness"] is False
    assert r["provenance"]["qualification"] == "NOT_QUALIFIED:NON_POSITIVE_ACT"


def test_human_deferral_is_recorded_but_not_positive_witness():
    r = _row(act_type="deferral", **SUBJECT, **AUTH)
    assert r["decision"] == "DEFER"
    assert r["human_witness"] is False


def test_non_decisional_statement_needs_no_subject_and_never_qualifies():
    r = _row(act_type="statement", statement="nota bebas")
    assert r["decision"] == "NOTE"
    assert r["human_witness"] is False
    assert r["subject_id"] is None


def test_agent_transcription_without_authentication_does_not_qualify():
    r = _row(act_type="authorization", **SUBJECT)  # no AUTH
    assert r["human_witness"] is False
    assert r["actor_authentication"]["authenticated"] is False
    assert r["provenance"]["qualification"] == "NOT_QUALIFIED:ACTOR_AUTHENTICATION_UNVERIFIED"


def test_auth_method_without_evidence_reference_does_not_authenticate():
    r = _row(act_type="authorization", **SUBJECT, auth_method="authenticated_session")
    assert r["human_witness"] is False
    assert r["actor_authentication"]["evidence"] is None


def test_machine_probe_never_qualifies():
    """A machine probe carried a human boolean in v1 — it can never qualify."""
    r = _row(act_type="statement", recorded_by="agent", test=False)
    assert r["human_witness"] is False
    assert r["provenance"]["qualification"] == "NOT_QUALIFIED:NON_POSITIVE_ACT"


def test_test_record_never_qualifies_even_when_fully_bound():
    r = _row(act_type="acceptance", **SUBJECT, **OUTCOME, **AUTH, test=True)
    assert r["human_witness"] is False
    assert r["test"] is True
    assert r["provenance"]["qualification"] == "NOT_QUALIFIED:TEST_RECORD"


def test_missing_subject_binding_is_refused_for_authorization():
    with pytest.raises(mod.WitnessBindingError, match="SUBJECT_BINDING_REQUIRED"):
        _row(act_type="authorization", **AUTH)


def test_missing_outcome_binding_is_refused_for_acceptance():
    with pytest.raises(mod.WitnessBindingError, match="OUTCOME_BINDING_REQUIRED"):
        _row(act_type="acceptance", **SUBJECT, **AUTH)


def test_free_text_sah_without_object_binding_is_refused():
    with pytest.raises(mod.WitnessBindingError, match="SUBJECT_BINDING_REQUIRED"):
        _row(act_type="acceptance", statement="SAH")


def test_empty_statement_is_refused():
    with pytest.raises(mod.WitnessBindingError, match="STATEMENT_REQUIRED"):
        _row(act_type="statement", statement="   ")


def test_duplicate_representation_is_detectable():
    """Same act + same instant -> same record_id and source hash (deduplicable)."""
    a = _row(act_type="acceptance", **SUBJECT, **OUTCOME, **AUTH)
    b = _row(act_type="acceptance", **SUBJECT, **OUTCOME, **AUTH)
    assert a["record_id"] == b["record_id"]
    assert a["source_record_hash"] == b["source_record_hash"]
    # A superseding row is explicit, not a silent second witness.
    c = _row(act_type="acceptance", **SUBJECT, **OUTCOME, **AUTH, supersedes=a["record_id"])
    assert c["supersedes"] == a["record_id"]


def test_supersedes_and_expiry_are_explicit_never_defaulted():
    r = _row(act_type="statement")
    assert r["expires_at"] is None  # absent means "not declared", not a silent 7d
    assert r["supersedes"] is None


def test_cli_refuses_acceptance_without_bindings_and_writes_nothing(tmp_path: Path):
    import os

    witness = tmp_path / "hw.jsonl"
    env = dict(os.environ)
    env["ARIFOS_HUMAN_WITNESS"] = str(witness)
    p = subprocess.run(
        [sys.executable, str(CLI), "--confirm", "--act-type", "acceptance", "--statement", "SAH"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert p.returncode == 2
    assert "REFUSED" in p.stderr
    assert not witness.exists()


def test_cli_test_flag_refuses_production_ledger():
    """--test must not be able to append to the live witness ledger."""
    import os

    env = dict(os.environ)
    env.pop("ARIFOS_HUMAN_WITNESS", None)
    p = subprocess.run(
        [sys.executable, str(CLI), "--confirm", "--test", "--statement", "probe"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert p.returncode == 2
    assert "production witness ledger" in p.stderr


def test_legacy_cli_confirm_still_records_on_a_scratch_ledger(tmp_path: Path):
    """Backward compatibility, scoped: a bare --confirm records on a SCRATCH
    ledger (as a non-qualifying statement). On the production ledger it is
    refused — see the append-guard tests below."""
    import os

    witness = tmp_path / "hw.jsonl"
    env = dict(os.environ)
    env["ARIFOS_HUMAN_WITNESS"] = str(witness)
    p = subprocess.run(
        [sys.executable, str(CLI), "--confirm", "--statement", "saya dah baca"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert p.returncode == 0, p.stderr
    row = json.loads(witness.read_text().splitlines()[-1])
    assert row["at"]
    assert row["act_type"] == "statement"
    assert row["human_witness"] is False
    assert len(row["report_sha256"]) == 64


# ── Phase 2: production-ledger append guard ────────────────────────────────
def test_production_path_constant_is_the_live_ledger():
    assert mod.WITNESS_PATH == Path("/var/lib/arifos/human_witness.jsonl")


def test_append_guard_refuses_nonqualifying_on_production():
    reason = mod._append_guard(
        qualifies=False, target=mod.WITNESS_PATH, allow_nonqualifying=False
    )
    assert reason and "NON_QUALIFYING_ROW_ON_PRODUCTION_LEDGER" in reason


def test_append_guard_allows_qualified_on_production():
    assert (
        mod._append_guard(qualifies=True, target=mod.WITNESS_PATH, allow_nonqualifying=False)
        is None
    )


def test_append_guard_allows_nonqualifying_on_scratch_ledger(tmp_path: Path):
    assert (
        mod._append_guard(
            qualifies=False, target=tmp_path / "hw.jsonl", allow_nonqualifying=False
        )
        is None
    )


def test_append_guard_override_is_explicit():
    assert (
        mod._append_guard(
            qualifies=False, target=mod.WITNESS_PATH, allow_nonqualifying=True
        )
        is None
    )


def test_legacy_confirm_refused_on_production_before_any_write(tmp_path: Path, monkeypatch):
    """End-to-end: production path + non-qualifying act => rc 2, no file created.

    WITNESS_PATH is rebound to a tmp path so the real ledger is never touched;
    the refusal path is identical because the guard compares target==WITNESS_PATH.
    """
    prod = tmp_path / "prod.jsonl"
    monkeypatch.setattr(mod, "WITNESS_PATH", prod)
    monkeypatch.setenv("ARIFOS_HUMAN_WITNESS", str(prod))
    rc = mod.confirm("legacy bare confirm", "arif", act_type="statement")
    assert rc == 2
    assert not prod.exists()


def test_qualified_confirm_writes_on_production_path(tmp_path: Path, monkeypatch):
    """Control: the same path accepts a fully-bound, authenticated act."""
    prod = tmp_path / "prod.jsonl"
    monkeypatch.setattr(mod, "WITNESS_PATH", prod)
    monkeypatch.setenv("ARIFOS_HUMAN_WITNESS", str(prod))
    rc = mod.confirm(
        "saya terima",
        "arif",
        act_type="authorization",
        subject_id="plan-test",
        subject_hash="c" * 64,
        auth_method="authenticated_session",
        auth_evidence="session:test",
    )
    assert rc == 0
    row = json.loads(prod.read_text().splitlines()[-1])
    assert row["human_witness"] is True
