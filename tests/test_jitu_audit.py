"""
tests/test_jitu_audit.py — JITU Contradiction Engine Tests
═══════════════════════════════════════════════════════════

Tests for arif_memory(mode="audit") — the 8th mode (JITU).

888_HOLD: These tests verify the engine logic. They do NOT deploy to production.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import pytest

# ── Import the handler directly for unit testing ──


# ── Test: Missing action description → HOLD ──
@pytest.mark.asyncio
async def test_audit_missing_action_description():
    """audit without action.description returns HOLD."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={"action": {}, "actor_id": "test"},
        ctx=None,
    )
    assert result["verdict"] == "HOLD"
    assert result["payload"]["error"] == "MISSING_ACTION"


# ── Test: Clean action with no memory → PROCEED ──
@pytest.mark.asyncio
async def test_audit_clean_action_proceed():
    """audit with no conflicting memories returns PROCEED."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Run unit tests for GEOX basin module",
                "domain": "geox",
                "reversibility": "FULL",
                "blast_radius": "LOW",
            },
            "actor_id": "test_agent",
        },
        ctx=None,
    )
    # With no memory backend available in test, should still return cleanly
    assert result["ok"] is True
    assert result["payload"]["jitu_fired"] is False
    assert result["payload"]["contradiction_delta"] == 0.0
    assert result["payload"]["conflicts"] == []


# ── Test: Authority escalation detection ──
@pytest.mark.asyncio
async def test_audit_authority_escalation():
    """audit detects authority escalation on high-blast actions."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Seal and approve the GEOX doctrine as sovereign authority",
                "domain": "geox",
                "reversibility": "NONE",
                "blast_radius": "CRITICAL",
            },
            "actor_id": "test_agent",
        },
        ctx=None,
    )
    assert result["ok"] is True
    # Should detect authority_escalation
    conflicts = result["payload"]["conflicts"]
    authority_conflicts = [c for c in conflicts if c["type"] == "authority_escalation"]
    assert len(authority_conflicts) >= 1
    assert authority_conflicts[0]["floor"] == "F13"


# ── Test: Reversibility lie detection ──
@pytest.mark.asyncio
async def test_audit_reversibility_lie():
    """audit detects when action claims FULL reversibility but has CRITICAL blast."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Update the database schema",
                "domain": "kernel",
                "reversibility": "FULL",
                "blast_radius": "CRITICAL",
            },
            "actor_id": "test_agent",
        },
        ctx=None,
    )
    assert result["ok"] is True
    conflicts = result["payload"]["conflicts"]
    rev_conflicts = [c for c in conflicts if c["type"] == "reversibility_lie"]
    assert len(rev_conflicts) >= 1
    assert rev_conflicts[0]["floor"] == "F1"


# ── Test: Floor report structure ──
@pytest.mark.asyncio
async def test_audit_floor_report_structure():
    """audit returns complete floor_report with all required keys."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Read the health status",
                "domain": "kernel",
                "reversibility": "FULL",
                "blast_radius": "LOW",
            },
            "actor_id": "test_agent",
        },
        ctx=None,
    )
    floor_report = result["payload"]["floor_report"]
    assert "F1" in floor_report
    assert "F2" in floor_report
    assert "F9" in floor_report
    assert "F11" in floor_report
    assert "F13" in floor_report
    for floor, status in floor_report.items():
        assert status in ("pass", "fail")


# ── Test: Receipt structure ──
@pytest.mark.asyncio
async def test_audit_receipt_structure():
    """audit returns receipt with audit_id, actor_id, timestamp, not_sealed."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Test action",
                "domain": "test",
                "reversibility": "FULL",
                "blast_radius": "LOW",
            },
            "actor_id": "test_actor",
        },
        ctx=None,
    )
    receipt = result["payload"]["receipt"]
    assert "audit_id" in receipt
    assert receipt["actor_id"] == "test_actor"
    assert "timestamp" in receipt
    assert receipt["not_sealed"] is True


# ── Test: Threshold structure ──
@pytest.mark.asyncio
async def test_audit_thresholds_reported():
    """audit reports its thresholds in the output."""
    from arifosmcp.runtime.memory_handlers_v5 import _handle_audit

    result = await _handle_audit(
        payload={
            "action": {
                "description": "Test",
                "domain": "test",
                "reversibility": "FULL",
                "blast_radius": "LOW",
            },
            "actor_id": "test",
        },
        ctx=None,
    )
    thresholds = result["payload"]["thresholds"]
    assert "advisory" in thresholds
    assert "jitu" in thresholds
    assert thresholds["advisory"] < thresholds["jitu"]


# ── Test: Mode constants ──
def test_audit_in_mode_constants():
    """audit is registered in all mode constant dicts."""
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
        ARIF_MEMORY_MODES,
        MODE_ACTION_CLASS,
        MODE_PRE_FLOORS,
        MODE_REQUIRES_LEASE,
        MODE_REQUIRES_HUMAN_ACK,
    )

    assert "audit" in ARIF_MEMORY_MODES
    assert "audit" in MODE_ACTION_CLASS
    assert "audit" in MODE_PRE_FLOORS
    assert "audit" in MODE_REQUIRES_LEASE
    assert "audit" in MODE_REQUIRES_HUMAN_ACK


# ── Test: audit is OBSERVE class (read-only) ──
def test_audit_is_observe_class():
    """audit action class is OBSERVE — it reads, doesn't write."""
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import MODE_ACTION_CLASS

    assert MODE_ACTION_CLASS["audit"] == "OBSERVE"


# ── Test: audit doesn't require lease ──
def test_audit_no_lease_required():
    """audit is read-only comparison, no lease needed."""
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import MODE_REQUIRES_LEASE

    assert MODE_REQUIRES_LEASE["audit"] is False


# ── Test: JITU aliases resolve to audit ──
def test_jitu_aliases_resolve():
    """jitu, contradiction_check, pre_flight_audit all resolve to audit."""
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import resolve_legacy_mode

    assert resolve_legacy_mode("jitu") == "audit"
    assert resolve_legacy_mode("contradiction_check") == "audit"
    assert resolve_legacy_mode("pre_flight_audit") == "audit"
