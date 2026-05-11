"""
tests/runtime/test_forge_ninesignal.py — Regression test for Lane 2 (010_FORGE)
Verifies nine_signal block is present and F11 is not falsely tripped on read-only modes.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
import pytest

os.environ["ARIFOS_DEV_MODE"] = "1"

from arifosmcp.runtime.tools import _arif_forge_execute


class TestForgeNineSignalContract:
    """Regression: all forge modes must emit nine_signal, and read-only modes must not F11-fail."""

    @pytest.mark.parametrize(
        "mode",
        ["query", "recall", "dry_run"],
    )
    def test_read_only_modes_return_ok_without_f11_breach(self, mode):
        """
        query / recall / dry_run are read-only modes.
        They must NOT trip F11 when session_id and actor_id are None.
        """
        result = _arif_forge_execute(
            mode=mode, query="status check", session_id=None, actor_id=None
        )

        assert (
            result.get("status") == "OK"
        ), f"Expected OK for {mode}, got {result.get('status')}"

        failed = result.get("meta", {}).get("failed_floors", [])
        assert (
            "F11" not in failed
        ), f"F11 breach on {mode} despite being read-only: {failed}"

        nine = result.get("nine_signal", {})
        assert (
            nine.get("overall") == "SELAMAT"
        ), f"Expected SELAMAT nine_signal on {mode}, got {nine.get('overall')}"

    def test_nine_signal_present_on_query_ok(self):
        """Query mode must emit nine_signal on success path."""
        result = _arif_forge_execute(
            mode="query", query="status", session_id=None, actor_id=None
        )
        assert "nine_signal" in result, "nine_signal missing from query OK response"
        assert result["nine_signal"].get("overall") == "SELAMAT"

    def test_nine_signal_present_on_recall_ok(self):
        """Recall mode must emit nine_signal on success path."""
        result = _arif_forge_execute(
            mode="recall", artifact_id="test-artifact", session_id=None, actor_id=None
        )
        assert "nine_signal" in result, "nine_signal missing from recall OK response"
        assert result["nine_signal"].get("overall") == "SELAMAT"

    def test_nine_signal_present_on_dry_run_ok(self):
        """Dry-run mode must emit nine_signal on success path."""
        result = _arif_forge_execute(mode="dry_run", session_id=None, actor_id=None)
        assert "nine_signal" in result, "nine_signal missing from dry_run OK response"
        assert result["nine_signal"].get("overall") == "SELAMAT"

    def test_nine_signal_present_on_engineer_hold(self):
        """
        Engineer mode without plan_id must return HOLD with nine_signal block.
        nine_signal is required even on non-success paths (F2 addendum).
        """
        result = _arif_forge_execute(
            mode="engineer", manifest="some code", session_id=None, actor_id=None
        )
        assert (
            result.get("status") == "HOLD"
        ), f"Expected HOLD for engineer without plan_id, got {result.get('status')}"
        assert (
            "nine_signal" in result
        ), "nine_signal missing from engineer HOLD response"
        assert result["nine_signal"].get("overall") in (
            "RETAK",
            "SABAR",
            "GANTUNG",
        ), f"Expected RETAK/SABAR/GANTUNG on HOLD, got {result['nine_signal'].get('overall')}"

    def test_commit_mode_also_has_nine_signal(self):
        """
        commit mode was previously missing _inject_nine_signal — a direct bug.
        This is now covered by ensuring every mode returns nine_signal.
        """
        result = _arif_forge_execute(
            mode="commit",
            artifact_id="test-artifact",
            session_id=None,
            actor_id=None,
            ack_irreversible=False,
        )
        assert "nine_signal" in result, "nine_signal missing from commit response"
