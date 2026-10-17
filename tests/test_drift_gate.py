"""
test_drift_gate.py — Tests for INV-L4-DRIFT (Spec-Code Drift Gate)
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, "/root")

import pytest


@pytest.fixture(autouse=True)
def isolated_spec(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_SPEC_LOCK_DIR", str(tmp_path))
    from pathlib import Path as P
    from AAA.state import spec_lock as spec_mod

    spec_mod._SPEC_LOCK_DIR = P(tmp_path)
    import arifosmcp.governance.drift_gate as drift_mod

    drift_mod._SPEC_LOCK_DIR = P(tmp_path)
    yield tmp_path


class TestP4_DriftGate:
    """Drift gate blocks out-of-scope and negative constraint violations."""

    def test_clean_diff_passes(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock
        from arifosmcp.governance.drift_gate import check_drift

        create_spec_lock(
            task_id="drift-test-1",
            locus=["src/auth/"],
            negative=["src/db/"],
        )

        diff = "--- a/src/auth/jwt.py\n+++ b/src/auth/jwt.py\n@@ -1 +1 @@\n-old\n+new"
        report = check_drift(diff=diff)
        assert report.passed is True
        assert report.checked_files == 1

    def test_out_of_locus_blocks(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock
        from arifosmcp.governance.drift_gate import check_drift

        create_spec_lock(
            task_id="drift-test-2",
            locus=["src/auth/"],
        )

        diff = "--- a/src/api/routes.py\n+++ b/src/api/routes.py\n@@ -1 +1 @@\n-old\n+new"
        report = check_drift(diff=diff)
        assert report.passed is False
        assert report.verdict == "BLOCK"
        assert any(v["type"] == "OUT_OF_LOCUS" for v in report.violations)

    def test_negative_constraint_blocks(self, isolated_spec):
        from AAA.state.spec_lock import create_spec_lock
        from arifosmcp.governance.drift_gate import check_drift

        create_spec_lock(
            task_id="drift-test-3",
            negative=["src/database/migrations/"],
        )

        diff = "--- a/src/database/migrations/001_init.py\n+++ b/src/database/migrations/001_init.py\n@@ -1 +1 @@\n-old\n+new"
        report = check_drift(diff=diff)
        assert report.passed is False
        assert any(v["type"] == "NEGATIVE_CONSTRAINT" for v in report.violations)

    def test_no_spec_passes(self, isolated_spec):
        from arifosmcp.governance.drift_gate import check_drift

        diff = "--- a/anything.py\n+++ b/anything.py\n@@ -1 +1 @@\n-old\n+new"
        report = check_drift(diff=diff)
        assert report.passed is True
