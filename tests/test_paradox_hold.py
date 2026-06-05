"""
Tests for the Paradox Hold — productive tension between two verified truths
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import pytest

from arifosmcp.core.paradox.recursive_governance_locks import (
    LockViolationError,
    RecursiveGovernanceEngine,
)
from arifosmcp.schemas.governance_locks import (
    LockType,
    LockVerdict,
    ParadoxHoldReceipt,
    UnifiedGovernanceReceipt,
)
from arifosmcp.schemas.verdict import VerdictCode


@pytest.fixture
def engine() -> RecursiveGovernanceEngine:
    return RecursiveGovernanceEngine()


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX HOLD
# ═══════════════════════════════════════════════════════════════════════════════


class TestParadoxHold:
    """Tests for the PARADOX_HOLD verdict state and ParadoxHoldReceipt."""

    def test_paradox_hold_enum_exists(self) -> None:
        """PARADOX_HOLD is a member of VerdictCode."""
        assert "PARADOX_HOLD" in VerdictCode.__members__
        assert VerdictCode.PARADOX_HOLD == "PARADOX_HOLD"

    def test_paradox_hold_lock_type_exists(self) -> None:
        """PARADOX_HOLD is a member of LockType."""
        assert "PARADOX_HOLD" in LockType.__members__
        assert LockType.PARADOX_HOLD == "paradox_hold"

    def test_two_verified_claims_conflict_issues_paradox_hold(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        """When two contradictory claims are both verified, issue PARADOX_HOLD."""
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "test-session"},
            actor_id="test-agent",
            context={
                "paradox_claims": {
                    "claim_a": "The reservoir is water-wet at 4500m depth.",
                    "claim_b": "The reservoir is oil-wet at 4500m depth.",
                    "conflict_description": (
                        "Both wetting states cannot be true simultaneously "
                        "for the same reservoir at the same depth."
                    ),
                    "both_verified": True,
                    "resolution_attempted": False,
                }
            },
        )

        assert receipt.paradox_hold is not None
        assert receipt.paradox_hold.lock_type == LockType.PARADOX_HOLD
        assert receipt.paradox_hold.verdict == LockVerdict.HOLD
        assert receipt.paradox_hold.both_verified is True
        assert receipt.paradox_hold.resolution_attempted is False
        assert "water-wet" in receipt.paradox_hold.claim_a
        assert "oil-wet" in receipt.paradox_hold.claim_b
        assert "cannot be true" in receipt.paradox_hold.conflict_description

        # Composite verdict must be HOLD (paradox preserved, not resolved)
        assert receipt.composite_verdict == LockVerdict.HOLD

        # PARADOX_HOLD should appear in locks_applied
        assert LockType.PARADOX_HOLD in receipt.locks_applied

        # A paradox lock receipt should exist
        paradox_locks = [r for r in receipt.lock_receipts if r.lock_type == LockType.PARADOX_HOLD]
        assert len(paradox_locks) == 1
        assert paradox_locks[0].verdict == LockVerdict.HOLD

    def test_one_verified_one_unverified_no_paradox_hold(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        """When only one claim is verified, no paradox hold — single claim wins."""
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "test-session"},
            actor_id="test-agent",
            context={
                "paradox_claims": {
                    "claim_a": "The reservoir is water-wet.",
                    "claim_b": "The reservoir is oil-wet.",
                    "conflict_description": "Contradictory wetting states.",
                    "both_verified": False,
                    "resolution_attempted": False,
                }
            },
        )

        # Both claims not verified → paradox hold NOT applied
        assert receipt.paradox_hold is None

        # PARADOX_HOLD should NOT be in locks_applied
        assert LockType.PARADOX_HOLD not in receipt.locks_applied

        # No paradox lock receipt
        paradox_locks = [r for r in receipt.lock_receipts if r.lock_type == LockType.PARADOX_HOLD]
        assert len(paradox_locks) == 0

    def test_no_paradox_claims_context_normal_operation(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        """When no paradox_claims in context, all three locks operate normally."""
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "test-session"},
            actor_id="test-agent",
            context={},
        )

        assert receipt.paradox_hold is None
        assert LockType.PARADOX_HOLD not in receipt.locks_applied
        # Normal operation: 3 locks applied
        assert LockType.GODEL in receipt.locks_applied
        assert LockType.STRANGE_LOOP in receipt.locks_applied
        assert LockType.ANTI_BEAUTIFUL_ONE in receipt.locks_applied
        assert receipt.composite_verdict == LockVerdict.SEAL

    def test_paradox_hold_preserves_both_claims(self) -> None:
        """ParadoxHoldReceipt stores both claims — neither is discarded."""
        receipt = ParadoxHoldReceipt(
            claim_a="Claim A: Shale is sealing.",
            claim_b="Claim B: Shale is leaking.",
            conflict_description="Sealing integrity in contradiction.",
            both_verified=True,
            resolution_attempted=False,
        )

        assert receipt.claim_a == "Claim A: Shale is sealing."
        assert receipt.claim_b == "Claim B: Shale is leaking."
        assert receipt.both_verified is True
        assert receipt.resolution_attempted is False
        assert receipt.lock_type == LockType.PARADOX_HOLD
        assert receipt.verdict == LockVerdict.HOLD

    def test_paradox_hold_with_optional_expiry(self) -> None:
        """ParadoxHoldReceipt accepts an optional expiry datetime."""
        from datetime import UTC, datetime, timedelta

        next_week = datetime.now(UTC) + timedelta(days=7)

        receipt = ParadoxHoldReceipt(
            claim_a="Seismic shows closure.",
            claim_b="Well test shows no closure.",
            conflict_description="Structural vs dynamic data conflict.",
            both_verified=True,
            preserved_until=next_week,
        )

        assert receipt.preserved_until is not None
        assert receipt.preserved_until > datetime.now(UTC)

    def test_unified_receipt_serializes_paradox_hold(self) -> None:
        """UnifiedGovernanceReceipt.to_dict() includes paradox_hold."""
        receipt = UnifiedGovernanceReceipt(
            session_id="sess-1",
            actor_id="agent-1",
            paradox_hold=ParadoxHoldReceipt(
                claim_a="True statement A.",
                claim_b="True statement B.",
                conflict_description="A and B cannot both be true.",
                both_verified=True,
            ),
        )

        d = receipt.to_dict()
        assert d["paradox_hold"] is not None
        assert d["paradox_hold"]["lock_type"] == "paradox_hold"
        assert d["paradox_hold"]["verdict"] == "HOLD"
        assert d["paradox_hold"]["claim_a"] == "True statement A."
        assert d["paradox_hold"]["claim_b"] == "True statement B."
        assert d["composite_verdict"] == "HOLD"

    def test_paradox_hold_combined_with_other_locks(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        """Paradox HOLD coexists with other lock results."""
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "test-session"},
            actor_id="test-agent",
            context={
                "paradox_claims": {
                    "claim_a": "The anticline traps hydrocarbons.",
                    "claim_b": "The anticline has breached seal.",
                    "conflict_description": (
                        "Trap integrity paradox — both structural "
                        "interpretations have supporting evidence."
                    ),
                    "both_verified": True,
                }
            },
        )

        # All 4 locks applied
        assert len(receipt.locks_applied) == 4
        assert receipt.composite_verdict == LockVerdict.HOLD
        assert receipt.paradox_hold is not None

        # The three deep locks still ran
        lock_types = [r.lock_type for r in receipt.lock_receipts]
        assert LockType.GODEL in lock_types
        assert LockType.STRANGE_LOOP in lock_types
        assert LockType.ANTI_BEAUTIFUL_ONE in lock_types
        assert LockType.PARADOX_HOLD in lock_types

    def test_paradox_hold_with_missing_claim_keys_no_hold(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        """Incomplete paradox spec (missing claim_b) → paradox lock not applied."""
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "test-session"},
            actor_id="test-agent",
            context={
                "paradox_claims": {
                    "claim_a": "Only one claim.",
                    # claim_b missing
                }
            },
        )

        assert receipt.paradox_hold is None
        assert LockType.PARADOX_HOLD not in receipt.locks_applied
