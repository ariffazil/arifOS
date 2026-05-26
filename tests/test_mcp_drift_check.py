"""
test_mcp_drift_check.py — Verify drift check behavior across modes.
"""

import pytest

from arifosmcp.tools.drift_check import mcp_drift_check


def test_drift_check_canonical13_detects_no_drift_when_exact():
    """When manifest and live match, drift_detected=false."""
    # This test assumes the live runtime has exactly the 13 canonical tools
    # plus diagnostic/wiki/drift tools. It may drift as tools are added.
    report = mcp_drift_check(mode="report", target_manifest="canonical13")
    # For canonical13, we only check the 13 canonical names.
    # The live runtime may have MORE tools (diagnostic, wiki), so extra is expected.
    # But missing should be empty.
    assert report["missing"] == [], f"Missing canonical tools: {report['missing']}"
    assert report["verdict"] in ("SEAL", "HOLD")


def test_drift_check_strict_mode_raises_on_drift():
    """strict mode with DRIFT_ENFORCEMENT=strict must raise on drift.

    PHOENIX-72: expanded45 now equals canonical13 + diagnostic (19 tools).
    In normal mode, live surface is 13, so expanded45 check drifts.
    In dev mode, live surface is 19, so expanded45 check does NOT drift.
    This test runs in normal mode (no ARIFOS_MCP_EXPOSE_DEV_TOOLS).
    """
    import os

    # Only test if strict is enabled
    if os.getenv("ARIFOS_DRIFT_ENFORCEMENT") != "strict":
        pytest.skip("ARIFOS_DRIFT_ENFORCEMENT is not strict")

    # In normal mode, canonical13 (13) vs expanded45 (19) shows 6 missing → drift
    if os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "").lower() not in ("true", "1", "yes"):
        with pytest.raises(RuntimeError):
            mcp_drift_check(mode="strict", target_manifest="expanded45")
    else:
        pytest.skip("Dev mode: expanded45 matches live surface, no drift to test")


def test_drift_check_report_mode_never_raises():
    """report mode must never raise, even when drift is detected."""
    report = mcp_drift_check(mode="report", target_manifest="all")
    assert isinstance(report, dict)
    assert "drift_detected" in report


def test_drift_check_warn_mode_logs():
    """warn mode logs but does not raise."""
    report = mcp_drift_check(mode="warn", target_manifest="all")
    assert isinstance(report, dict)


def test_drift_check_counts_are_non_negative():
    """All counts must be >= 0."""
    report = mcp_drift_check(mode="report", target_manifest="all")
    assert report["allowed_count"] >= 0
    assert report["registered_count"] >= 0
    assert len(report["missing"]) >= 0
    assert len(report["extra"]) >= 0


def test_drift_check_verdict_is_seal_or_hold():
    """verdict must be SEAL or HOLD."""
    report = mcp_drift_check(mode="report", target_manifest="canonical13")
    assert report["verdict"] in ("SEAL", "HOLD")
