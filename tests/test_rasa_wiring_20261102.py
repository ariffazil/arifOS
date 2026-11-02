"""HUMAN_RASA consent v2 — writer/reader unified contract + revocation flow.

2026-11-02 (F13 reconciliation requirements 4/5). v2 settles:
  - ledger = JSON **array of ConsentScope rows** (reader contract canonical;
    v1's dict/events wrapper was a writer/reader mismatch — dead)
  - writer = attribution-enforced, confirm-gated, flock-serialised state upsert
  - withdrawal = scope row `revoked: true` → check_consent_from_ledger
    DENY_REVOKED (revocation flows downstream through the EXISTING reader)
  - corrupt/unavailable ledger → UNKNOWN, never implicit consent
  - concurrent writers serialise via flock — no lost rows

Run: pytest tests/test_rasa_wiring_20261102.py -v
"""

from __future__ import annotations

import asyncio
import json
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arifosmcp.memory.ingestion_service import MemoryIngestionService
from arifosmcp.memory.types import Authority, MemoryCandidate, MemoryType
from arifosmcp.runtime.f6.consent_ledger import check_consent_from_ledger
from arifosmcp.runtime.f6.consent_scope import ConsentSource
from arifosmcp.runtime.f6.consent_writer import (
    grant_scope,
    withdraw_scope,
)


def _iso(dt):
    return dt.isoformat()


NOW = datetime.now(timezone.utc)


def _person_a_file_scope(**kw) -> dict:
    """Valid scope ROW (dict form — what the ledger stores / reader parses)."""
    base = dict(
        scope_id="g2-person-a-file",
        subject="file:PERSON_A_upload",
        source=ConsentSource.OPERATOR_DECLARATION,
        can_access=True,
        can_use=True,
        can_disclose=True,
        not_after=_iso(NOW + timedelta(days=1)),
        data_subject="PERSON_A",
        purpose="communication",
        modality="text",
    )
    base.update(kw)
    return base


@pytest.fixture()
def ledger(tmp_path, monkeypatch):
    led = tmp_path / "consent_ledger.json"
    led.write_text("[]")
    monkeypatch.setenv("ARIFOS_CONSENT_LEDGER_PATH", str(led))
    return led


class TestWriterContract:
    def test_unattributed_write_rejected(self, ledger):
        """PEACE² #3 by construction: no actor/session/trace → no write."""
        r = grant_scope(_person_a_file_scope(), confirm_write=True)
        assert r["status"] == "ERROR"
        assert r["error_code"] == "ATTRIBUTION_REQUIRED"

    def test_unconfirmed_write_rejected(self, ledger):
        """confirm_write is the write-side mirror of source_verified."""
        r = grant_scope(
            _person_a_file_scope(),
            actor="333-AGI",
            session_id="s",
            trace_id="t",
        )
        assert r["status"] == "ERROR"
        assert r["error_code"] == "CONFIRMATION_REQUIRED"

    def test_missing_env_reported_never_guessed(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        r = grant_scope(
            _person_a_file_scope(),
            actor="333-AGI",
            session_id="s",
            trace_id="t",
            confirm_write=True,
        )
        assert r["status"] == "UNKNOWN"
        assert r["dependency_missing"] is True

    def test_grant_upsert_last_wins(self, ledger):
        g1 = grant_scope(
            _person_a_file_scope(purpose="communication"),
            actor="333-AGI",
            session_id="s",
            trace_id="t1",
            confirm_write=True,
        )
        g2 = grant_scope(
            _person_a_file_scope(purpose="communication", can_disclose=False),
            actor="333-AGI",
            session_id="s",
            trace_id="t2",
            confirm_write=True,
        )
        assert g1["status"] == g2["status"] == "OK"
        assert g1["replaced"] is False and g2["replaced"] is True
        rows = json.loads(ledger.read_text())
        assert len(rows) == 1 and rows[0]["can_disclose"] is False


class TestRevocationDownstream:
    def test_grant_allows_then_withdraw_denies_revoked(self, ledger):
        """THE revocation flow: ALLOW → withdraw → DENY_REVOKED, end-to-end."""
        g = grant_scope(
            _person_a_file_scope(),
            actor="333-AGI",
            session_id="s",
            trace_id="t",
            confirm_write=True,
        )
        assert g["status"] == "OK"
        allow = check_consent_from_ledger(
            "g2-person-a-file",
            want_use=True,
            requested_purpose="communication",
            requested_modality="text",
            source_verified=True,
        )
        assert allow["decision"] == "ALLOW"

        w = withdraw_scope(
            "g2-person-a-file",
            reason="subject changed mind",
            actor="f13",
            session_id="s",
            trace_id="t2",
            confirm_write=True,
        )
        assert w["status"] == "OK"

        deny = check_consent_from_ledger(
            "g2-person-a-file",
            want_use=True,
            requested_purpose="communication",
            requested_modality="text",
            source_verified=True,
        )
        assert deny["decision"] == "DENY_REVOKED"

    def test_row_kept_for_audit_after_withdrawal(self, ledger):
        """Withdrawal flips the flag in place — the fact of former consent stays."""
        grant_scope(
            _person_a_file_scope(), actor="a", session_id="s", trace_id="t", confirm_write=True
        )
        withdraw_scope(
            "g2-person-a-file",
            reason="audit: flag flip check",
            actor="f13",
            session_id="s",
            trace_id="t2",
            confirm_write=True,
        )
        rows = json.loads(ledger.read_text())
        assert len(rows) == 1
        assert rows[0]["revoked"] is True
        assert rows[0]["revoked_reason"] == "audit: flag flip check"


class TestConcurrencyAndCorruption:
    def test_concurrent_writers_no_lost_rows(self, ledger):
        """10 concurrent grants, 10 distinct scope_ids → 10 rows survive."""

        def worker(i):
            grant_scope(
                _person_a_file_scope(scope_id=f"conc-{i}"),
                actor="a",
                session_id="s",
                trace_id=f"t{i}",
                confirm_write=True,
            )

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        rows = json.loads(ledger.read_text())
        assert len(rows) == 10
        assert len({r["scope_id"] for r in rows}) == 10

    def test_corrupt_ledger_is_unknown_never_consent(self, ledger):
        """Corrupt file cannot become implicit consent — reader fails closed."""
        ledger.write_text("{ this is not valid json")
        out = check_consent_from_ledger(
            "g2-person-a-file",
            want_use=True,
            source_verified=True,
        )
        assert out["decision"] == "UNKNOWN"
        assert out.get("dependency_missing") is True


class TestIngestionConsentWiring:
    class _Ext:
        def __init__(self, cands):
            self.cands = cands

        def extract(self, turn, ctx):
            return self.cands

    def _svc(self):
        return MemoryIngestionService()

    def _cand(self, subject="Ali", authority=None, scope_id=None):
        return MemoryCandidate(
            type=MemoryType.WORKING,
            subject=subject,
            content="meeting note about Ali",
            summary=None,
            source_type="test",
            source_ref={"consent_scope_id": scope_id} if scope_id else {},
            authority=authority if authority is not None else Authority.SYSTEM_INFERRED,
        )

    def test_person_scoped_without_scope_blocked(self, monkeypatch):
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        svc = self._svc()
        cand = self._cand(subject="Ali")
        svc.extractors = [self._Ext([cand])]
        res = asyncio.run(svc.ingest({}, {"actor_role": "user"}))
        assert res and res[0]["status"] == "BLOCKED"
        assert "consent_scope_id" in res[0]["reason"]

    def test_revoked_scope_blocks_ingestion(self, ledger):
        """End-to-end: withdrawn consent blocks a later ingestion attempt."""
        grant_scope(
            _person_a_file_scope(), actor="a", session_id="s", trace_id="t", confirm_write=True
        )
        withdraw_scope(
            "g2-person-a-file", actor="f13", session_id="s", trace_id="t2", confirm_write=True
        )
        svc = self._svc()
        cand = self._cand(subject="PERSON_A", scope_id="g2-person-a-file")
        svc.extractors = [self._Ext([cand])]
        res = asyncio.run(svc.ingest({}, {"actor_role": "user"}))
        assert res and res[0]["status"] == "BLOCKED"
        assert res[0]["consent"]["decision"] == "DENY_REVOKED"

    def test_sovereign_self_geometry_passes(self, monkeypatch):
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        svc = self._svc()
        cand = self._cand(subject="Arif", authority=Authority.EXPLICIT_USER)
        svc.extractors = [self._Ext([cand])]
        res = asyncio.run(svc.ingest({}, {"actor_role": "sovereign"}))
        assert not any(
            r.get("status") == "BLOCKED" and "consent_scope_id" in str(r.get("reason", ""))
            for r in res
        )


class TestMindReasonGate:
    def test_third_party_prediction_refused(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(arif_think("he will betray the team", session_id="t", actor_id="333-AGI"))
        assert r["status"] in ("HOLD", "VOID")
        assert r["gate"] == "f6.inference_grammar"
        assert r["subject_is_person"] is True

    def test_first_person_self_report_allowed(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(arif_think("I feel tired today", session_id="t", actor_id="333-AGI"))
        assert r.get("gate") != "f6.inference_grammar"  # gate ALLOWed → proceeded

    def test_non_person_query_proceeds(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(
            arif_think("What is the capital of Selangor?", session_id="t", actor_id="333-AGI")
        )
        assert r.get("gate") != "f6.inference_grammar"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
