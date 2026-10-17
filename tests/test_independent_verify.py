"""
test_independent_verify.py — Tests for INV-L6-ORTHO (Orthogonal Verification)
═══════════════════════════════════════════════════════════════════════════════

Verifies:
  1. Locus check detects out-of-scope file modifications
  2. Integrity check detects test-weakening patterns
  3. VerificationResult structure is correct
  4. Pass/FAIL verdict logic

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, "/root")

import pytest


class TestP3_LocusCheck:
    """Locus check detects out-of-scope modifications."""

    def test_in_locus_no_violations(self):
        from arifosmcp.gates.independent_verify import _check_locus_violations

        diff = "--- a/src/auth/jwt.py\n+++ b/src/auth/jwt.py\n@@ -1 +1 @@\n-old\n+new"
        violations = _check_locus_violations(diff, ["src/auth/*.py"])
        assert violations == []

    def test_out_of_locus_detected(self):
        from arifosmcp.gates.independent_verify import _check_locus_violations

        diff = "--- a/src/database/models.py\n+++ b/src/database/models.py\n@@ -1 +1 @@\n-old\n+new"
        violations = _check_locus_violations(diff, ["src/auth/*.py"])
        assert len(violations) == 1
        assert "OUT_OF_LOCUS" in violations[0]

    def test_directory_pattern_matches(self):
        from arifosmcp.gates.independent_verify import _check_locus_violations

        diff = "--- a/src/api/routes.py\n+++ b/src/api/routes.py\n@@ -1 +1 @@\n-old\n+new"
        violations = _check_locus_violations(diff, ["src/api/"])
        assert violations == []

    def test_empty_locus_allows_all(self):
        from arifosmcp.gates.independent_verify import _check_locus_violations

        diff = "--- a/any/file.py\n+++ b/any/file.py\n@@ -1 +1 @@\n-old\n+new"
        violations = _check_locus_violations(diff, [])
        assert violations == []

    def test_multiple_files_mixed(self):
        from arifosmcp.gates.independent_verify import _check_locus_violations

        diff = (
            "--- a/src/auth/jwt.py\n+++ b/src/auth/jwt.py\n@@ -1 +1 @@\n-old\n+new\n"
            "--- a/src/database/models.py\n+++ b/src/database/models.py\n@@ -1 +1 @@\n-old\n+new"
        )
        violations = _check_locus_violations(diff, ["src/auth/*.py"])
        assert len(violations) == 1
        assert "src/database/models.py" in violations[0]


class TestP3_IntegrityCheck:
    """Integrity check detects test-weakening patterns."""

    def test_clean_diff_no_violations(self):
        from arifosmcp.gates.independent_verify import _check_integrity_violations

        diff = "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -1 +1 @@\n-old\n+new"
        violations = _check_integrity_violations(diff)
        assert violations == []

    def test_skip_decorator_in_test_detected(self):
        from arifosmcp.gates.independent_verify import _check_integrity_violations

        diff = (
            "--- a/tests/test_auth.py\n+++ b/tests/test_auth.py\n"
            "@@ -1 +1 @@\n+@pytest.mark.skip\ndef test_login(): pass"
        )
        violations = _check_integrity_violations(diff)
        assert any("SKIP_DECORATOR" in v for v in violations)

    def test_noqa_in_test_detected(self):
        from arifosmcp.gates.independent_verify import _check_integrity_violations

        diff = (
            "--- a/tests/test_auth.py\n+++ b/tests/test_auth.py\n"
            "@@ -1 +1 @@\n+result = foo()  # noqa: E501"
        )
        violations = _check_integrity_violations(diff)
        assert any("NOQA_SUPPRESSION" in v for v in violations)


class TestP3_VerificationResult:
    """VerificationResult structure is correct."""

    def test_pass_verdict(self):
        from arifosmcp.gates.independent_verify import VerificationResult

        result = VerificationResult(verdict="PASS")
        assert result.passed is True
        assert result.to_dict()["verdict"] == "PASS"
        assert "timestamp" in result.to_dict()

    def test_fail_verdict(self):
        from arifosmcp.gates.independent_verify import VerificationResult

        result = VerificationResult(
            verdict="FAIL",
            violations=["OUT_OF_LOCUS: src/db.py"],
        )
        assert result.passed is False
        assert len(result.to_dict()["violations"]) == 1
