"""F6 G2 — ConsentScope purpose/modality axes + read-only ConsentLedger (HUMAN_RASA P0).

Gap G2: the consent object had no notion of WHO the data is about (data_subject),
WHY it may be used (purpose), or in WHAT form (modality); and no production
consent ledger feeds live evaluations (meters.py M6 reports "live consent
store MISSING"). This suite freezes the tightened contract:

  - ConsentScope carries data_subject / purpose / modality / processor /
    derived_features / withdrawal_effect (all optional, audit-only fields).
  - The purpose (and modality) axis is FAIL-CLOSED the moment it is in play:
      mismatch                 -> DENY_OUT_OF_SCOPE
      missing on either side   -> UNKNOWN (never ALLOW)
  - A file-backed, READ-ONLY ConsentLedger reader keyed by env var NAME
    (ARIFOS_CONSENT_LEDGER_PATH). Absent env or absent file -> UNKNOWN, never ALLOW.

Fixtures are synthetic only (subject "PERSON_A" — never a real person).
No egress. No VAULT999. No live /root writes. Env var NAMES only.

Run:
    python3 -m pytest tests/constitutional/test_f6_consent_scope_purpose_g2.py -q
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

KERNEL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KERNEL_ROOT))

from arifosmcp.runtime.f6.consent_ledger import (  # noqa: E402
    ENV_CONSENT_LEDGER_PATH,
    check_consent_from_ledger,
    read_consent_ledger,
)
from arifosmcp.runtime.f6.consent_scope import (  # noqa: E402
    ConsentDecision,
    ConsentScope,
    ConsentSource,
    check_consent,
)

NOW = datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _person_a_file_scope(**kw):
    """Synthetic grant: PERSON_A sent a file. Operator declared it; no purpose by default."""
    base = dict(
        scope_id="g2-person-a-file",
        subject="file:PERSON_A_upload",
        source=ConsentSource.OPERATOR_DECLARATION,
        can_access=True,
        can_use=True,
        can_disclose=True,
        not_after=_iso(NOW + timedelta(days=1)),
        data_subject="PERSON_A",
    )
    base.update(kw)
    return ConsentScope(**base)


class TestConsentPurposeAxis(unittest.TestCase):
    """A person's data without a matching declared purpose never resolves to ALLOW."""

    def test_person_a_sent_file_no_purpose_unknown(self) -> None:
        scope = _person_a_file_scope()  # purpose intentionally absent
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="communication",
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.UNKNOWN)

        # Even with no requested purpose, person data with no declared purpose
        # on the scope stays UNKNOWN — purpose is load-bearing for a person.
        out2 = check_consent(scope, want_use=True, source_verified=True, now=NOW)
        self.assertEqual(out2["decision"], ConsentDecision.UNKNOWN)

    def test_communication_purpose_is_not_profiling(self) -> None:
        scope = _person_a_file_scope(purpose="communication", modality="text")
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="profiling",
            requested_modality="text",
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.DENY_OUT_OF_SCOPE)

    def test_matching_purpose_and_modality_allow(self) -> None:
        scope = _person_a_file_scope(purpose="communication", modality="text")
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="communication",
            requested_modality="text",
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.ALLOW)

    def test_modality_missing_on_scope_side_unknown(self) -> None:
        scope = _person_a_file_scope(purpose="communication")  # no modality
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="communication",
            requested_modality="voice",
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.UNKNOWN)

    def test_requested_modality_missing_on_request_side_unknown(self) -> None:
        scope = _person_a_file_scope(purpose="communication", modality="text")
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="communication",
            # requested_modality intentionally omitted -> UNKNOWN, never ALLOW
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.UNKNOWN)

    def test_revoked_still_denied_revoked(self) -> None:
        scope = _person_a_file_scope(purpose="communication", modality="text", revoked=True)
        out = check_consent(
            scope,
            want_use=True,
            source_verified=True,
            requested_purpose="communication",
            requested_modality="text",
            now=NOW,
        )
        self.assertEqual(out["decision"], ConsentDecision.DENY_REVOKED)

    def test_legacy_scope_without_person_context_unchanged(self) -> None:
        """Pre-existing callers (no data_subject/purpose/modality) keep ALLOW."""
        scope = ConsentScope(
            scope_id="g2-legacy-system",
            subject="system-A",
            source=ConsentSource.OPERATOR_DECLARATION,
            can_access=True,
            can_use=True,
            can_disclose=False,
            not_after=_iso(NOW + timedelta(days=1)),
        )
        out = check_consent(scope, want_access=True, source_verified=True, now=NOW)
        self.assertEqual(out["decision"], ConsentDecision.ALLOW)


class TestConsentLedgerReader:
    """File-backed ledger lookup is READ-ONLY and fail-closed (UNKNOWN, never ALLOW)."""

    def test_absent_env_var_never_allows(self) -> None:
        import os

        saved = os.environ.pop(ENV_CONSENT_LEDGER_PATH, None)
        try:
            out = check_consent_from_ledger("g2-person-a-file", want_use=True, source_verified=True)
            assert out["decision"] == ConsentDecision.UNKNOWN
            assert ENV_CONSENT_LEDGER_PATH in out["reason"]
        finally:
            if saved is not None:
                os.environ[ENV_CONSENT_LEDGER_PATH] = saved

    def test_absent_ledger_file_never_allows(self, tmp_path: Path) -> None:
        import os

        os.environ[ENV_CONSENT_LEDGER_PATH] = str(tmp_path / "does_not_exist.json")
        try:
            out = check_consent_from_ledger("g2-person-a-file", want_use=True, source_verified=True)
            assert out["decision"] == ConsentDecision.UNKNOWN
        finally:
            os.environ.pop(ENV_CONSENT_LEDGER_PATH, None)

    def test_present_ledger_roundtrip_and_scope_check(self, tmp_path: Path) -> None:
        import json
        import os

        ledger_path = tmp_path / "consent_ledger.json"
        ledger_path.write_text(
            json.dumps(
                [
                    {
                        "scope_id": "g2-person-a-file",
                        "subject": "file:PERSON_A_upload",
                        "source": ConsentSource.OPERATOR_DECLARATION,
                        "can_access": True,
                        "can_use": True,
                        "can_disclose": False,
                        "not_after": _iso(NOW + timedelta(days=1)),
                        "data_subject": "PERSON_A",
                        "purpose": "communication",
                        "modality": "text",
                    }
                ]
            ),
            encoding="utf-8",
        )
        os.environ[ENV_CONSENT_LEDGER_PATH] = str(ledger_path)
        try:
            # Matching purpose -> ALLOW (verified source asserted by caller).
            out = check_consent_from_ledger(
                "g2-person-a-file",
                want_use=True,
                source_verified=True,
                requested_purpose="communication",
                requested_modality="text",
                now=NOW,
            )
            assert out["decision"] == ConsentDecision.ALLOW

            # Profiling is not communication -> DENY_OUT_OF_SCOPE.
            out2 = check_consent_from_ledger(
                "g2-person-a-file",
                want_use=True,
                source_verified=True,
                requested_purpose="profiling",
                requested_modality="text",
                now=NOW,
            )
            assert out2["decision"] == ConsentDecision.DENY_OUT_OF_SCOPE

            # Reader never writes: file content unchanged after reads.
            stored = json.loads(ledger_path.read_text(encoding="utf-8"))
            assert len(stored) == 1

            # Unknown scope id -> UNKNOWN, never ALLOW.
            out3 = check_consent_from_ledger(
                "g2-not-in-ledger", want_use=True, source_verified=True, now=NOW
            )
            assert out3["decision"] == ConsentDecision.UNKNOWN

            # read_consent_ledger reports the resolved path + scope ids, no secrets.
            info = read_consent_ledger()
            assert info["status"] == "OK"
            assert "g2-person-a-file" in info["scope_ids"]
        finally:
            os.environ.pop(ENV_CONSENT_LEDGER_PATH, None)

    def test_unparseable_ledger_never_allows(self, tmp_path: Path) -> None:
        import os

        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        os.environ[ENV_CONSENT_LEDGER_PATH] = str(bad)
        try:
            out = check_consent_from_ledger("g2-person-a-file", want_use=True, source_verified=True)
            assert out["decision"] == ConsentDecision.UNKNOWN
        finally:
            os.environ.pop(ENV_CONSENT_LEDGER_PATH, None)


if __name__ == "__main__":
    unittest.main()
