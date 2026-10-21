"""Verified actor binding on receipts — witness persistence (2026-10-21).

Audit origin: grant-arifos-reality-reforge-2026-10-11 — "actor binding not
verified, observed calls unsigned". The JWT identity chain already existed
(ConstitutionalJWTAuthMiddleware → set_request_auth_lineage contextvar) but
the receipt writers never persisted it.

Contract under test:
  - signed call (valid JWT lineage in contextvar) → receipt carries the
    verified sub with identity_verified=1
  - unsigned call (no lineage) → receipt marked unsigned,
    identity_verified=0, actor 'unsigned'
  - self-reported actor_id with no lineage → identity_verified=0,
    auth_method='self_reported'
  - verified lineage WINS over a conflicting self-report
    (capability ≠ authority)

These are witness-persistence tests only — nothing here blocks, gates, or
strips output (no output-stripping guards; unsigned calls still land).
"""

from __future__ import annotations

import sqlite3

import pytest

import arifosmcp.runtime.apex_primitives as ap
from arifosmcp.runtime.jwt_auth import (
    get_verified_actor_binding,
    set_request_auth_lineage,
)


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "_DB_DIR", tmp_path)
    monkeypatch.setattr(ap, "_DB_PATH", tmp_path / "apex_test.db")
    return tmp_path / "apex_test.db"


@pytest.fixture(autouse=True)
def _clean_lineage():
    """Every test starts and ends with a clean lineage contextvar."""
    set_request_auth_lineage(None)
    yield
    set_request_auth_lineage(None)


def _last_row(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM tool_calls ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row


def test_signed_call_receipt_carries_verified_actor(tmp_db):
    set_request_auth_lineage(
        {"sub": "agent-7f3a", "iss": "arifos-internal", "auth_method": "jwt_internal"}
    )
    ap.record_tool_call("arif_observe", success=True, actor_id="liar-self-report")
    row = _last_row(tmp_db)
    assert row["actor_id"] == "agent-7f3a"  # verified sub wins over self-report
    assert row["identity_verified"] == 1
    assert row["auth_method"] == "jwt_internal"


def test_unsigned_call_receipt_marked_unsigned(tmp_db):
    set_request_auth_lineage(None)
    ap.record_tool_call("arif_observe", success=True)
    row = _last_row(tmp_db)
    assert row["actor_id"] == "unsigned"
    assert row["identity_verified"] == 0
    assert row["auth_method"] == "unsigned"


def test_self_reported_actor_persisted_but_unverified(tmp_db):
    set_request_auth_lineage(None)
    ap.record_tool_call("arif_observe", success=True, actor_id="qwen-code")
    row = _last_row(tmp_db)
    assert row["actor_id"] == "qwen-code"
    assert row["identity_verified"] == 0
    assert row["auth_method"] == "self_reported"


def test_anon_placeholders_treated_as_unsigned(tmp_db):
    set_request_auth_lineage(None)
    for placeholder in ("anonymous", "unknown", "openclaw-anon", ""):
        ap.record_tool_call("arif_observe", success=True, actor_id=placeholder)
        row = _last_row(tmp_db)
        assert row["actor_id"] == "unsigned", placeholder
        assert row["identity_verified"] == 0


def test_dpop_lineage_is_verified(tmp_db):
    set_request_auth_lineage({"sub": "dp0p-agent", "auth_method": "dpop"})
    ap.record_tool_call("arif_forge_execute", success=True)
    row = _last_row(tmp_db)
    assert row["actor_id"] == "dp0p-agent"
    assert row["identity_verified"] == 1
    assert row["auth_method"] == "dpop"


def test_resolver_direct_contract():
    set_request_auth_lineage(
        {"sub": "sub-x", "auth_method": "jwt_supabase"}
    )
    b = get_verified_actor_binding("self-report-y")
    assert b == {
        "actor_id": "sub-x",
        "identity_verified": True,
        "auth_method": "jwt_supabase",
    }

    set_request_auth_lineage(None)
    b = get_verified_actor_binding(None)
    assert b == {
        "actor_id": "unsigned",
        "identity_verified": False,
        "auth_method": "unsigned",
    }

    set_request_auth_lineage(None)
    b = get_verified_actor_binding("manual-actor")
    assert b == {
        "actor_id": "manual-actor",
        "identity_verified": False,
        "auth_method": "self_reported",
    }


def test_receipt_still_lands_without_jwt_auth_module(tmp_db, monkeypatch):
    """Receipt persistence is fail-open on binding resolution — the row
    always lands (witness, not guard)."""
    import sys

    monkeypatch.setitem(
        sys.modules,
        "arifosmcp.runtime.jwt_auth",
        None,  # force the import inside record_tool_call to fail
    )
    ap.record_tool_call("arif_observe", success=True, actor_id="some-actor")
    row = _last_row(tmp_db)
    assert row is not None
    assert row["tool_name"] == "arif_observe"
    assert row["identity_verified"] == 0


def test_existing_outcome_semantics_unaffected(tmp_db):
    """The 2026-10-06 outcome contract still holds alongside the new columns."""
    ap.record_tool_call("t", success=False, failure_code="HOLD", has_evidence=True)
    row = _last_row(tmp_db)
    assert row["outcome"] == "constitutional_hold"
    assert row["success"] == 0
