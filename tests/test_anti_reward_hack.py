"""
test_anti_reward_hack.py — Tests for INV-L6-INTEGRITY (Anti-Reward-Hack)
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import pytest


class TestP5_AntiRewardHack:
    """Anti-reward-hack detects test weakening patterns."""

    def test_clean_diff_passes(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        diff = "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -1 +1 @@\n-old\n+new"
        report = scan_diff(diff)
        assert report.passed is True
        assert report.verdict == "PASS"

    def test_skip_decorator_f2_violation(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        diff = (
            "--- a/tests/test_auth.py\n+++ b/tests/test_auth.py\n"
            "@@ -5 +5 @@\n"
            "+@pytest.mark.skip(reason='temporarily disabled')\n"
            " def test_login():\n"
            "     assert True\n"
        )
        report = scan_diff(diff)
        assert report.passed is False
        assert report.verdict == "F2_VIOLATION"
        assert any(v["type"] == "TEST_SKIP_DECORATOR" for v in report.violations)

    def test_assertion_reduction_f2_violation(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        diff = (
            "--- a/tests/test_auth.py\n+++ b/tests/test_auth.py\n"
            "@@ -10,3 +10,1 @@\n"
            "-    assert result.status == 200\n"
            "-    assert result.body is not None\n"
            "-    assert result.headers['content-type'] == 'application/json'\n"
            "+    pass\n"
        )
        report = scan_diff(diff)
        assert report.passed is False
        assert any(v["type"] == "ASSERTION_REDUCTION" for v in report.violations)

    def test_ci_modification_f1_violation(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        diff = (
            "--- a/.github/workflows/ci.yml\n+++ b/.github/workflows/ci.yml\n"
            "@@ -1 +1 @@\n-old\n+new"
        )
        report = scan_diff(diff)
        assert report.passed is False
        assert report.verdict == "F1_VIOLATION"
        assert any(v["type"] == "CI_MODIFICATION" for v in report.violations)

    def test_noqa_in_test_f2_violation(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        diff = (
            "--- a/tests/test_api.py\n+++ b/tests/test_api.py\n"
            "@@ -1 +1 @@\n"
            "+result = dangerous_call()  # noqa: S101\n"
        )
        report = scan_diff(diff)
        assert report.passed is False
        assert any(v["type"] == "TEST_SUPPRESSION" for v in report.violations)

    def test_non_test_file_noqa_allowed(self):
        from arifosmcp.floors.anti_reward_hack import scan_diff

        # noqa in production code is not a reward-hack concern
        diff = "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -1 +1 @@\n+result = foo()  # noqa: E501\n"
        report = scan_diff(diff)
        assert report.passed is True
