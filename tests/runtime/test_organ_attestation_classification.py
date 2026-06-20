"""
Test Suite: arif_organ_attest_all classification helper
═════════════════════════════════════════════════════════

Regression test for issue #509:
  arif_organ_attest_all returns DEGRADED_CLAIM for healthy services
  because the wrapper's narrow allow-list rejects "ALIVE" and other
  valid healthy status strings.

DITEMPA BUKAN DIBERI — Floors without tests are wishes.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.organ_attestation import is_healthy


# ═══════════════════════════════════════════════════════════════════════════════
# Healthy status strings (must be accepted)
# ═══════════════════════════════════════════════════════════════════════════════


class TestIsHealthyAccepts:
    """is_healthy() must recognise every valid healthy status string."""

    @pytest.mark.parametrize(
        "status",
        [
            "healthy",   # arifOS, A-FORGE, AAA
            "HEALTHY",   # case-insensitive
            "alive",     # WEALTH canonical
            "ALIVE",     # case-insensitive
            "ok",        # legacy / informal
            "OK",        # case-insensitive
            "pass",      # arifOS /ready
            "ready",     # generic
            "serving",   # gRPC-style
        ],
    )
    def test_accepts_healthy_status(self, status):
        assert is_healthy(status) is True, f"Expected is_healthy({status!r}) is True"

    def test_accepts_boolean_true(self):
        assert is_healthy(True) is True

    def test_accepts_with_whitespace(self):
        assert is_healthy("  healthy  ") is True
        assert is_healthy("\talive\n") is True


# ═══════════════════════════════════════════════════════════════════════════════
# Unhealthy / unknown status strings (must be rejected)
# ═══════════════════════════════════════════════════════════════════════════════


class TestIsHealthyRejects:
    """is_healthy() must reject unhealthy or unknown status strings."""

    @pytest.mark.parametrize(
        "status",
        [
            "unhealthy",     # the false-positive string from #509
            "degraded",
            "DEGRADED_CLAIM",
            "fail",
            "failed",
            "down",
            "timeout",
            "error",
            "404",
            "502",
            "unknown",       # F2: conservative-fail
        ],
    )
    def test_rejects_unhealthy_status(self, status):
        assert is_healthy(status) is False, f"Expected is_healthy({status!r}) is False"

    def test_rejects_boolean_false(self):
        assert is_healthy(False) is False

    def test_rejects_none(self):
        assert is_healthy(None) is False

    def test_rejects_empty_string(self):
        assert is_healthy("") is False

    def test_rejects_non_string_non_bool(self):
        assert is_healthy(123) is False
        assert is_healthy([]) is False
        assert is_healthy({}) is False


# ═══════════════════════════════════════════════════════════════════════════════
# Issue #509 regression — the original false-positive case
# ═══════════════════════════════════════════════════════════════════════════════


class TestIssue509Regression:
    """Reproduce the original bug to prove the fix.

    Before:  is_healthy("ALIVE") returned False → DEGRADED_CLAIM (wrong)
    After:   is_healthy("ALIVE") returns True → ALIVE (correct)
    """

    def test_wealth_alive_now_classified_healthy(self):
        """WEALTH's /health returns status='ALIVE'. This must be healthy."""
        # Before fix: False (the bug)
        # After fix:  True
        assert is_healthy("ALIVE") is True

    def test_healthy_status_with_unhealthy_string_is_rejected(self):
        """The original reason string 'Health probe returned: unhealthy' should NOT be classified healthy."""
        assert is_healthy("unhealthy") is False


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-organ consistency
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrossOrganConsistency:
    """Every federation organ's /health status must be classified correctly."""

    @pytest.mark.parametrize(
        "organ,status,expected",
        [
            ("arifOS", "healthy", True),
            ("A-FORGE", "healthy", True),
            ("AAA", "healthy", True),
            ("GEOX", "ok", True),
            ("WEALTH", "ALIVE", True),       # the bug case
            ("WELL", "healthy", True),
            ("arifOS", "pass", True),         # /ready result
            ("WEALTH", "unhealthy", False),
            ("GEOX", "down", False),
        ],
    )
    def test_organ_specific_statuses(self, organ, status, expected):
        assert is_healthy(status) is expected, (
            f"is_healthy({status!r}) for {organ} should be {expected}"
        )
