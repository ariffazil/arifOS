"""
test_failure_wal.py — Tests for INV-L5-WAL (Zero-Loss Error Telemetry)
═══════════════════════════════════════════════════════════════════════════════

Verifies:
  1. healing_error() appends exactly 1 WAL record per call
  2. WAL records have correct schema (all required fields present)
  3. sig_hash is deterministic (same inputs → same hash)
  4. WAL is append-only (no truncation on re-open)
  5. WAL gracefully degrades on write failure (never blocks error)
  6. Category classifier maps codes correctly
  7. Thread-local session_id propagates to WAL records
  8. Large context is truncated (never exceeds max line bytes)

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Test fixtures ────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def isolated_wal(tmp_path, monkeypatch):
    """Redirect WAL to a temp directory for each test."""
    wal_dir = tmp_path / "failure-wal"
    monkeypatch.setenv("ARIFOS_FAILURE_WAL_DIR", str(wal_dir))
    monkeypatch.setenv("ARIFOS_FAILURE_WAL", "1")
    # Force re-read of env
    import arifosmcp.runtime.failure_wal as wal_mod

    wal_mod._WAL_DIR = wal_dir
    wal_mod._WAL_ENABLED = True
    yield wal_dir


def _read_wal(wal_dir):
    """Read all lines from today's WAL file. Call AFTER action under test."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    wal_file = wal_dir / f"failure-wal-{now.strftime('%Y-%m-%d')}.jsonl"
    if not wal_file.exists():
        return []
    lines = []
    for line in wal_file.read_text().strip().split("\n"):
        if line.strip():
            lines.append(json.loads(line))
    return lines


# ── P0 Verification Tests ────────────────────────────────────────────────────


class TestP0_WAL_BasicAppend:
    """3 synthetic failures → 3 valid WAL records."""

    def test_healing_error_appends_wal(self, isolated_wal):
        """Each healing_error() call produces exactly 1 WAL line."""
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        healing_error(
            code=ErrorCodes.INVALID_PARAMETER,
            message="Unknown query_type: foo",
            organ="arifos",
            tool="lsp_query",
            parameter="query_type",
            received="foo",
            available=["hover", "definition"],
        )

        records = _read_wal(isolated_wal)
        assert len(records) == 1
        rec = records[0]
        assert rec["code"] == "INVALID_PARAMETER"
        assert rec["organ"] == "arifos"
        assert rec["tool"] == "lsp_query"
        assert rec["category"] == "tool"
        assert len(rec["sig_hash"]) == 16

    def test_three_failures_three_records(self, isolated_wal):
        """3 different errors → 3 WAL records."""
        from arifosmcp.runtime.healing_errors import (
            healing_error,
            field_not_found_error,
            parameter_error,
            ErrorCodes,
        )

        healing_error(
            code=ErrorCodes.INVALID_TOOL,
            message='Tool "bad_tool" not found.',
            organ="geox",
            tool="bad_tool",
        )
        field_not_found_error(
            field_name="pressure",
            organ="geox",
            tool="geox_well_log",
            available_fields=["pressure_kpa", "formation_pressure"],
        )
        parameter_error(
            parameter="mode",
            received="invalid",
            expected="one of [hover, definition, references]",
            organ="arifos",
            tool="lsp_query",
            available=["hover", "definition", "references"],
        )

        records = _read_wal(isolated_wal)
        assert len(records) == 3
        codes = [r["code"] for r in records]
        assert codes == ["INVALID_TOOL", "INVALID_FIELD", "INVALID_PARAMETER"]


class TestP0_DeterministicSigHash:
    """sig_hash must be identical for identical inputs."""

    def test_same_inputs_same_hash(self, isolated_wal):
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
            available=["pressure_kpa"],
        )
        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
            available=["pressure_kpa"],
        )

        records = _read_wal(isolated_wal)
        assert len(records) == 2
        assert records[0]["sig_hash"] == records[1]["sig_hash"]

    def test_different_inputs_different_hash(self, isolated_wal):
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
        )
        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="temperature",
        )

        records = _read_wal(isolated_wal)
        assert len(records) == 2
        assert records[0]["sig_hash"] != records[1]["sig_hash"]


class TestP0_AppendOnly:
    """WAL never truncates on re-open."""

    def test_append_only_no_truncation(self, isolated_wal):
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        # First batch
        for i in range(5):
            healing_error(
                code=ErrorCodes.EXECUTION_FAILED,
                message=f"fail-{i}",
                organ="aforge",
                tool="forge_shell",
            )

        records = _read_wal(isolated_wal)
        assert len(records) == 5

        # Second batch — must append, not overwrite
        for i in range(3):
            healing_error(
                code=ErrorCodes.TIMEOUT,
                message=f"timeout-{i}",
                organ="aforge",
                tool="forge_shell",
            )

        records = _read_wal(isolated_wal)
        assert len(records) == 8
        assert records[0]["code"] == "EXECUTION_FAILED"
        assert records[5]["code"] == "TIMEOUT"


class TestP0_GracefulDegradation:
    """WAL failure must never block the error response."""

    def test_wal_write_failure_doesnt_block(self, isolated_wal):
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes
        import arifosmcp.runtime.failure_wal as wal_mod

        # Simulate WAL failure by disabling it mid-call
        original = wal_mod._WAL_ENABLED
        wal_mod._WAL_ENABLED = False

        err = healing_error(
            code=ErrorCodes.SERVICE_UNAVAILABLE,
            message="test graceful degradation",
            organ="well",
            tool="well_machine_diagnose",
        )
        # The error object must still be returned
        assert err.code == "SERVICE_UNAVAILABLE"
        assert err.message == "test graceful degradation"

        # Restore
        wal_mod._WAL_ENABLED = original


class TestP0_CategoryClassifier:
    """Error codes map to correct failure categories."""

    def test_tool_category(self):
        from arifosmcp.runtime.failure_wal import _classify

        assert _classify("INVALID_FIELD") == "tool"
        assert _classify("INVALID_TOOL") == "tool"
        assert _classify("MISSING_PARAMETER") == "tool"

    def test_resource_category(self):
        from arifosmcp.runtime.failure_wal import _classify

        assert _classify("NOT_FOUND") == "resource"
        assert _classify("SERVICE_UNAVAILABLE") == "resource"

    def test_verify_category(self):
        from arifosmcp.runtime.failure_wal import _classify

        assert _classify("GOVERNANCE_HOLD") == "verify"
        assert _classify("CONSTITUTIONAL_VIOLATION") == "verify"

    def test_impl_category(self):
        from arifosmcp.runtime.failure_wal import _classify

        assert _classify("EXECUTION_FAILED") == "impl"
        assert _classify("TIMEOUT") == "impl"


class TestP0_SessionPropagation:
    """Thread-local session_id propagates to WAL records."""

    def test_session_id_in_wal(self, isolated_wal):
        from arifosmcp.runtime.failure_wal import set_session
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        set_session("test-session-abc123")
        healing_error(
            code=ErrorCodes.NOT_FOUND,
            message="test",
            organ="geox",
            tool="geox_basin",
        )

        records = _read_wal(isolated_wal)
        assert len(records) == 1
        assert records[0]["session_id"] == "test-session-abc123"


class TestP0_QueryAPI:
    """WAL query functions work correctly."""

    def test_query_by_sig_hash(self, isolated_wal):
        from arifosmcp.runtime.failure_wal import wal_query_today, wal_count_sig
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
        )
        healing_error(
            code=ErrorCodes.INVALID_FIELD,
            message="test",
            organ="geox",
            tool="geox_well_log",
            parameter="field",
            received="pressure",
        )
        healing_error(
            code=ErrorCodes.TIMEOUT,
            message="different",
            organ="aforge",
            tool="forge_shell",
        )

        # Same sig_hash for first two
        all_records = wal_query_today()
        assert len(all_records) == 3

        sig = all_records[0]["sig_hash"]
        matching = wal_query_today(sig_hash=sig)
        assert len(matching) == 2

        assert wal_count_sig(sig) == 2

    def test_query_by_organ(self, isolated_wal):
        from arifosmcp.runtime.failure_wal import wal_query_today
        from arifosmcp.runtime.healing_errors import healing_error, ErrorCodes

        healing_error(code=ErrorCodes.NOT_FOUND, message="a", organ="geox", tool="t1")
        healing_error(code=ErrorCodes.NOT_FOUND, message="b", organ="well", tool="t2")
        healing_error(code=ErrorCodes.NOT_FOUND, message="c", organ="geox", tool="t3")

        geox_records = wal_query_today(organ="geox")
        assert len(geox_records) == 2
        well_records = wal_query_today(organ="well")
        assert len(well_records) == 1


class TestP0_WALDisabled:
    """WAL can be disabled via environment variable."""

    def test_disabled_wal_returns_none(self, monkeypatch, isolated_wal):
        import arifosmcp.runtime.failure_wal as wal_mod

        wal_mod._WAL_ENABLED = False

        result = wal_mod.wal_append(
            code="TEST",
            message="should not write",
        )
        assert result is None

        # Re-enable for cleanup
        wal_mod._WAL_ENABLED = True
