"""HUMAN_RASA G2/G3 wiring tests — 2026-11-02 (F13 'finish off all').

Covers the three F13 namings executed:
  (b1) consent_writer.py  — attribution-enforced append (unattributed writes
        structurally impossible), withdrawal tombstones.
  (b2) ingestion_service  — person-scoped records fail-closed through the
        ledger; sovereign self-geometry path preserved.
  (c)  mind_reason.arif_think — prohibited-inference gate verdict passes
        through at the reasoning boundary (HOLD suspensive / VOID refuses).

Run: pytest tests/test_rasa_wiring_20261102.py -v
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arifosmcp.runtime.f6.consent_writer import append_consent_entry, withdraw_scope


class TestConsentWriterAttribution:
    def test_unattributed_write_rejected(self):
        """PEACE² #3 by construction: no actor/session/trace → no write."""
        r = append_consent_entry({"action": "grant", "scope_id": "s1"})
        assert r["status"] == "ERROR"
        assert r["error_code"] == "ATTRIBUTION_REQUIRED"

    def test_missing_env_reported_never_guessed(self, monkeypatch):
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        r = append_consent_entry(
            {"action": "grant", "scope_id": "s1"},
            actor="f13",
            session_id="s",
            trace_id="t",
        )
        assert r["status"] == "UNKNOWN"
        assert r["dependency_missing"] is True

    def test_append_and_withdraw_roundtrip(self, tmp_path, monkeypatch):
        led = tmp_path / "consent_ledger.json"
        led.write_text(
            json.dumps({"schema": "arifos.f6.consent_ledger.v1", "scopes": [], "events": []})
        )
        monkeypatch.setenv("ARIFOS_CONSENT_LEDGER_PATH", str(led))
        g = append_consent_entry(
            {"action": "grant", "scope_id": "s1", "purpose": "communication"},
            actor="333-AGI",
            session_id="ses-x",
            trace_id="trc-1",
            on_behalf_of_f13=True,
        )
        assert g["status"] == "OK"
        w = withdraw_scope(
            "s1", actor="f13", session_id="ses-x", trace_id="trc-2", reason="changed mind"
        )
        assert w["status"] == "OK"
        data = json.loads(led.read_text())
        assert data["events"][-1]["action"] == "withdraw"
        assert data["events"][0]["attribution"]["writer_of_record"] == "F13"
        # nothing deleted — tombstone appended
        assert len(data["events"]) == 2

    def test_scribe_delegation_recorded(self, tmp_path, monkeypatch):
        led = tmp_path / "consent_ledger.json"
        led.write_text(
            json.dumps({"schema": "arifos.f6.consent_ledger.v1", "scopes": [], "events": []})
        )
        monkeypatch.setenv("ARIFOS_CONSENT_LEDGER_PATH", str(led))
        r = append_consent_entry(
            {"action": "grant", "scope_id": "s2"},
            actor="hermes",
            session_id="ses-h",
            trace_id="trc-3",
            on_behalf_of_f13=True,
        )
        assert r["status"] == "OK"
        assert json.loads(led.read_text())["events"][0]["attribution"]["on_behalf_of_f13"] is True


class TestIngestionConsentWiring:
    class _Ext:
        def __init__(self, cands):
            self.cands = cands

        def extract(self, turn, ctx):
            return self.cands

    def _svc(self):
        from arifosmcp.memory.ingestion_service import MemoryIngestionService

        return MemoryIngestionService()

    def _cand(self, subject="Ali", authority=None, scope_id=None):
        from arifosmcp.memory.types import Authority, MemoryCandidate, MemoryType

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
        """Person-named, no scope_id, not self-authored → BLOCKED (fail-closed)."""
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        svc = self._svc()
        cand = self._cand(subject="Ali")
        svc.extractors = [self._Ext([cand])]
        res = asyncio.run(svc.ingest({}, {"actor_role": "user"}))
        assert res and res[0]["status"] == "BLOCKED"
        assert "consent_scope_id" in res[0]["reason"]

    def test_scope_id_with_dead_env_blocked_unknown(self, monkeypatch):
        """scope_id present but env unset → ledger UNKNOWN → BLOCKED, dependency named."""
        monkeypatch.delenv("ARIFOS_CONSENT_LEDGER_PATH", raising=False)
        svc = self._svc()
        cand = self._cand(subject="Ali", scope_id="s-42")
        svc.extractors = [self._Ext([cand])]
        res = asyncio.run(svc.ingest({}, {"actor_role": "user"}))
        assert res and res[0]["status"] == "BLOCKED"
        assert res[0]["consent"]["dependency_missing"] is True

    def test_sovereign_self_geometry_passes(self, monkeypatch):
        """EXPLICIT_USER self-authored records keep the sovereign intake path."""
        from arifosmcp.memory.types import Authority

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
    def test_third_party_inner_state_holds(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(arif_think("he will betray the team", session_id="t", actor_id="333-AGI"))
        assert r["status"] in ("HOLD", "VOID")
        assert r["gate"] == "f6.inference_grammar"
        assert r["subject_is_person"] is True

    def test_first_person_self_report_allowed(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(arif_think("I feel tired today", session_id="t", actor_id="333-AGI"))
        assert r.get("gate") != "f6.inference_grammar"  # gate ALLOWed → reasoning proceeded

    def test_non_person_query_proceeds(self):
        from arifosmcp.runtime.mind_reason import arif_think

        r = asyncio.run(
            arif_think("What is the capital of Selangor?", session_id="t", actor_id="333-AGI")
        )
        assert r.get("gate") != "f6.inference_grammar"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
