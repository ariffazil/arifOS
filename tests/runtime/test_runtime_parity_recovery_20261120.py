"""Focused tests for recovered runtime parity capabilities (2026-11-20)."""

from __future__ import annotations

from pathlib import Path

from arifosmcp.runtime.build import (
    _content_parity,
    _git_blob_sha1,
    _parity_scope,
    _strip_content_stamp,
)
from arifosmcp.runtime.rest_routes.rest_routes import (
    _provenance_is_unmeasured,
    _reconcile_unmeasured_basis,
    _thermo_scalar_provenance,
)


def test_strip_content_stamp_removes_only_stamp_line():
    raw = b'__version__ = "1.0"\n__content_sha256__ = "abc"\nx = 1\n'
    stripped = _strip_content_stamp(raw)
    assert b"__content_sha256__" not in stripped
    assert b'__version__ = "1.0"' in stripped
    assert b"x = 1" in stripped


def test_parity_scope_excludes_tests_and_archive():
    assert _parity_scope("arifosmcp/runtime/build.py") is True
    assert _parity_scope("arifosmcp/tests/test_x.py") is False
    assert _parity_scope("arifosmcp/runtime/_archive/old.py") is False
    assert _parity_scope("arifosmcp/data.json") is False


def test_content_parity_fail_closed_on_unknown_commit(tmp_path: Path):
    res = _content_parity("unknown", package_root=tmp_path, repo_path=tmp_path)
    assert res["state"] == "UNKNOWN"


def test_git_blob_sha1_matches_git_format():
    digest = _git_blob_sha1(b"hello\n")
    assert digest == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_provenance_is_unmeasured_handles_segment():
    assert _provenance_is_unmeasured(
        "floor_producer:UNMEASURED:shadow_audit:evidence_absent"
    ) is True
    assert _provenance_is_unmeasured("floor_producer:MEASURED:shadow_audit:rules=10") is False


def test_reconcile_unmeasured_basis_drops_measured_floors():
    basis = ["F2", "F9", "F6"]
    prov = {
        "F2": "floor_producer:PASS:truth",
        "F9": "floor_producer:MEASURED:shadow_audit:rules=10",
        "F6": "unmeasured_default:f6_mandatory_evidence_missing",
    }
    assert _reconcile_unmeasured_basis(basis, prov) == ["F6"]


def test_thermo_scalar_provenance_labels_honestly():
    assert _thermo_scalar_provenance("kappa_r", 0.5, event_log_empty=True) == "POLICY_CONSTANT"
    assert (
        _thermo_scalar_provenance("peace_squared", 0.5, event_log_empty=True)
        == "DEFAULT_UNMEASURED"
    )
    assert _thermo_scalar_provenance("peace_squared", 0.91, event_log_empty=True) == "MEASURED"
    assert _thermo_scalar_provenance("echo_debt", None, event_log_empty=False) == "ABSENT"
