"""
test_phoenix72_canonical13.py — PHOENIX-72 Canonical 13 Refactor Tests
═══════════════════════════════════════════════════════════════════════

Verifies:
1. Public MCP surface is exactly 13 tools in normal mode.
2. mcp_drift_check reports drift_detected=False, extra=[].
3. Absorbed diagnostic/wiki modes route through canonical handlers.
4. Dev-mode flag ARIFOS_MCP_EXPOSE_DEV_TOOLS exposes extra tools.

Ditempa Bukan Diberi — Forged, Not Given.
"""

from __future__ import annotations
import os

import pytest


# ── 1. Drift checker ──────────────────────────────────────────────────────────

def test_drift_check_passes_in_normal_mode():
    """mcp_drift_check must report SEAL when canonical13 is the target."""
    from arifosmcp.tools.drift_check import mcp_drift_check

    report = mcp_drift_check(mode="report", target_manifest="canonical13")
    assert report["drift_detected"] is False
    assert report["verdict"] == "SEAL"
    assert report["missing"] == []
    assert report["extra"] == []
    assert report["registered_count"] == 13


def test_drift_check_counts_diagnostic_tools_in_dev_mode(monkeypatch):
    """When dev tools are exposed, drift check must count 19 (13 + 6 diagnostic)."""
    from arifosmcp.tools.drift_check import mcp_drift_check

    monkeypatch.setenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "true")
    report = mcp_drift_check(mode="report", target_manifest="all")
    assert report["registered_count"] == 19  # 13 canonical + 6 diagnostic


# ── 2. Absorbed mode dispatch ─────────────────────────────────────────────────

def test_kernel_route_surface_drift_mode():
    """arif_kernel_route mode='surface_drift' must return a drift report."""
    from arifosmcp.runtime.tools import _arif_kernel_route

    result = _arif_kernel_route(mode="surface_drift")
    assert result["verdict"] == "SEAL"
    assert result["drift_detected"] is False


def test_ops_measure_stack_health_mode():
    """arif_ops_measure mode='stack_health' must probe federation health."""
    from arifosmcp.runtime.tools import _arif_ops_measure

    result = _arif_ops_measure(mode="stack_health")
    assert result["status"] in ("SELAMAT", "AMANAH", "VOID")
    assert "services" in result


def test_ops_measure_budget_mode():
    """arif_ops_measure mode='budget' must return budget ledger."""
    from arifosmcp.runtime.tools import _arif_ops_measure

    result = _arif_ops_measure(mode="budget")
    assert result["status"] in ("SEAL", "HOLD")
    assert "cumulative_cost" in result or "ledger" in result


def test_memory_recall_repo_search_mode():
    """arif_memory_recall mode='repo_search' must return scored chunks."""
    from arifosmcp.runtime.tools import _arif_memory_recall

    result = _arif_memory_recall(mode="repo_search", query="test", memory_id=".")
    assert isinstance(result, list)


def test_sense_observe_repo_map_mode_needs_index():
    """arif_sense_observe mode='repo_map' raises ValueError when repo is unindexed."""
    from arifosmcp.runtime.tools import _arif_sense_observe

    with pytest.raises(ValueError, match="Run 'arif-wiki ingest"):
        _arif_sense_observe(mode="repo_map", query=".")


@pytest.mark.asyncio
async def test_reply_compose_repo_answer_mode():
    """arif_reply_compose mode='repo_answer' must return evidence-grounded answer."""
    from arifosmcp.runtime.tools import _arif_reply_compose_tool

    result = await _arif_reply_compose_tool(
        mode="repo_answer", message="what is arifos", style="."
    )
    assert isinstance(result, dict)
    assert "answer" in result or "confidence" in result


@pytest.mark.asyncio
async def test_heart_critique_instruction_scan_mode():
    """arif_heart_critique mode='instruction_scan' must scan for local directives."""
    from arifosmcp.runtime.tools import _arif_heart_critique

    result = await _arif_heart_critique(mode="instruction_scan", target=os.environ.get("ARIFOS_HOME", "/root") + "/arifOS")
    assert result.get("status") == "CLEAR"
    assert "findings" in result


@pytest.mark.asyncio
async def test_judge_deliberate_floor_status_mode():
    """arif_judge_deliberate mode='floor_status' must report floor enforcement."""
    from arifosmcp.runtime.tools import _arif_judge_deliberate_tool

    result = await _arif_judge_deliberate_tool(mode="floor_status")
    assert "floors" in result
    assert "floor_count" in result


@pytest.mark.asyncio
async def test_judge_deliberate_witness_consensus_mode():
    """arif_judge_deliberate mode='witness_consensus' must aggregate organ signals."""
    from arifosmcp.runtime.tools import _arif_judge_deliberate_tool

    result = await _arif_judge_deliberate_tool(
        mode="witness_consensus", candidate="test action"
    )
    assert isinstance(result, dict)
    assert "status" in result
