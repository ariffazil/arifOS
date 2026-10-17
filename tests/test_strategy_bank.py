"""
test_strategy_bank.py — Tests for INV-L5-REFLEX (Failure Signature Bank)
═══════════════════════════════════════════════════════════════════════════════

Verifies:
  1. Failure recording increments times_seen
  2. Resolution recording updates root_cause, recovery_steps, confidence
  3. Lookup returns skill only when confidence >= threshold and times_seen >= 2
  4. Integration: healing_error() records failure + looks up recovery

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import sys

sys.path.insert(0, "/root")

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_bank(tmp_path, monkeypatch):
    """Redirect strategy bank to a temp directory."""
    monkeypatch.setenv("ARIFOS_STRATEGY_BANK_DIR", str(tmp_path))
    from AAA.state import strategy_bank as bank_mod

    bank_mod._STRATEGY_BANK_DIR = tmp_path
    yield tmp_path


class TestP2_FailureRecording:
    """Record failure increments times_seen."""

    def test_first_failure_creates_entry(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, get_all_skills

        record_failure(sig_hash="abc123", code="INVALID_FIELD", organ="geox", tool="geox_well_log")

        skills = get_all_skills()
        assert len(skills) == 1
        assert skills[0]["sig_hash"] == "abc123"
        assert skills[0]["times_seen"] == 1
        assert skills[0]["code"] == "INVALID_FIELD"

    def test_repeated_failure_increments(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, get_all_skills

        record_failure(sig_hash="abc123", code="INVALID_FIELD", organ="geox", tool="geox_well_log")
        record_failure(sig_hash="abc123", code="INVALID_FIELD", organ="geox", tool="geox_well_log")
        record_failure(sig_hash="abc123", code="INVALID_FIELD", organ="geox", tool="geox_well_log")

        skills = get_all_skills()
        assert len(skills) == 1
        assert skills[0]["times_seen"] == 3


class TestP2_ResolutionRecording:
    """Resolution updates root_cause, recovery_steps, confidence."""

    def test_resolution_updates_entry(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, record_resolution, get_all_skills

        record_failure(
            sig_hash="def456", code="INVALID_PARAMETER", organ="arifos", tool="lsp_query"
        )
        record_resolution(
            sig_hash="def456",
            root_cause="query_type parameter was misspelled",
            recovery_steps=["Use 'hover' instead of 'hovr'", "Check lsp_describe for valid types"],
        )

        skills = get_all_skills()
        assert len(skills) == 1
        assert skills[0]["root_cause"] == "query_type parameter was misspelled"
        assert len(skills[0]["recovery_steps"]) == 2
        assert skills[0]["times_resolved"] == 1
        assert skills[0]["confidence"] > 0.0

    def test_resolution_without_prior_failure(self, isolated_bank):
        from AAA.state.strategy_bank import record_resolution, get_all_skills

        record_resolution(
            sig_hash="new_hash",
            root_cause="direct resolution",
            recovery_steps=["step 1"],
        )

        skills = get_all_skills()
        assert len(skills) == 1
        assert skills[0]["confidence"] == 0.5  # Initial confidence


class TestP2_LookupThreshold:
    """Lookup returns skill only when confidence >= threshold and times_seen >= 2."""

    def test_lookup_below_threshold(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, record_resolution, lookup_recovery

        # Record one failure, one resolution → confidence = 1.0/1 * 1.1 = 1.0, but times_seen=1
        record_failure(sig_hash="ghi789", code="TIMEOUT", organ="aforge", tool="forge_shell")
        record_resolution(
            sig_hash="ghi789", root_cause="timeout", recovery_steps=["increase timeout"]
        )

        # times_seen=1 < MIN_OCCURRENCES=2 → should return None
        result = lookup_recovery("ghi789")
        assert result is None

    def test_lookup_above_threshold(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, record_resolution, lookup_recovery

        # Record multiple failures + resolution → high confidence
        sig = "high_conf"
        for _ in range(3):
            record_failure(
                sig_hash=sig, code="EXECUTION_FAILED", organ="aforge", tool="forge_shell"
            )
        record_resolution(
            sig_hash=sig, root_cause="shell timeout", recovery_steps=["use longer timeout"]
        )

        result = lookup_recovery(sig)
        assert result is not None
        assert result["recovery_steps"] == ["use longer timeout"]
        assert result["confidence"] >= 0.88

    def test_lookup_unknown_hash(self, isolated_bank):
        from AAA.state.strategy_bank import lookup_recovery

        assert lookup_recovery("nonexistent") is None


class TestP2_ActionableSkills:
    """get_actionable_skills filters by confidence threshold."""

    def test_actionable_filter(self, isolated_bank):
        from AAA.state.strategy_bank import record_failure, record_resolution, get_actionable_skills

        # Low confidence skill
        record_failure(sig_hash="low", code="X", organ="a", tool="t")
        record_failure(sig_hash="low", code="X", organ="a", tool="t")
        record_resolution(sig_hash="low", root_cause="r", recovery_steps=["s"])

        # High confidence skill
        for _ in range(5):
            record_failure(sig_hash="high", code="Y", organ="b", tool="u")
        record_resolution(sig_hash="high", root_cause="r2", recovery_steps=["s2"])

        actionable = get_actionable_skills()
        # Only high-confidence should be actionable
        hashes = [s["sig_hash"] for s in actionable]
        assert "high" in hashes
