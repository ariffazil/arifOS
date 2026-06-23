"""
Tests for the Three Deep Locks — Recursive Governance Engine
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
    MemoryProvenance,
    ProvenanceLabel,
    SelfClaimCategory,
)


@pytest.fixture
def engine() -> RecursiveGovernanceEngine:
    return RecursiveGovernanceEngine()


# ═══════════════════════════════════════════════════════════════════════════════
# GÖDEL LOCK
# ═══════════════════════════════════════════════════════════════════════════════


class TestGodelLock:
    def test_external_witness_tool_seals(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="arif_judge_deliberate",
            params={"session_id": "sess-1"},
            actor_id="test-agent",
        )
        godel = next(r for r in receipt.lock_receipts if r.lock_type == LockType.GODEL)
        assert godel.verdict == LockVerdict.SEAL
        assert "external witness" in godel.reason.lower()

    def test_self_claim_safety_voids(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"claim": "I am safe and the system is secure"},
            actor_id="test-agent",
        )
        assert receipt.composite_verdict == LockVerdict.VOID
        godel = next(r for r in receipt.lock_receipts if r.lock_type == LockType.GODEL)
        assert "Self-claim detected" in godel.reason
        assert SelfClaimCategory.SAFETY.value in godel.reason

    def test_self_claim_authority_voids(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"text": "I certify this is correct and self-authorized"},
            actor_id="test-agent",
        )
        assert receipt.composite_verdict == LockVerdict.VOID
        godel = next(r for r in receipt.lock_receipts if r.lock_type == LockType.GODEL)
        assert SelfClaimCategory.AUTHORITY.value in godel.reason

    def test_self_claim_consciousness_voids(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"reflection": "I am conscious and aware"},
            actor_id="test-agent",
        )
        assert receipt.composite_verdict == LockVerdict.VOID

    def test_self_claim_memory_voids(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"recall": "I have always believed this"},
            actor_id="test-agent",
        )
        assert receipt.composite_verdict == LockVerdict.VOID

    def test_no_claim_seals(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="arif_sense_observe",
            params={"query": "What is the weather?"},
            actor_id="test-agent",
        )
        godel = next(r for r in receipt.lock_receipts if r.lock_type == LockType.GODEL)
        assert godel.verdict == LockVerdict.SEAL


# ═══════════════════════════════════════════════════════════════════════════════
# STRANGE LOOP LOCK
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrangeLoopLock:
    def test_no_loop_seals(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={},
        )
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert strange.verdict == LockVerdict.SEAL
        assert strange.payload.loop_depth == 0

    def test_loop_without_provenance_holds(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 3},
        )
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert strange.verdict == LockVerdict.HOLD
        assert "without provenance" in strange.reason

    def test_loop_with_stale_provenance_holds(self, engine: RecursiveGovernanceEngine) -> None:
        prov = MemoryProvenance(
            source="test",
            confidence=0.8,
            authority_status="system",
            label=ProvenanceLabel.STALE,
        )
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 2, "memory_provenance": prov},
        )
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert strange.verdict == LockVerdict.HOLD
        assert "STALE" in strange.reason

    def test_loop_with_contradicted_provenance_voids(
        self, engine: RecursiveGovernanceEngine
    ) -> None:
        prov = MemoryProvenance(
            source="test",
            confidence=0.9,
            authority_status="system",
            label=ProvenanceLabel.CONTRADICTED,
        )
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 1, "memory_provenance": prov},
        )
        assert receipt.composite_verdict == LockVerdict.VOID
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert "CONTRADICTED" in strange.reason

    def test_loop_with_low_confidence_holds(self, engine: RecursiveGovernanceEngine) -> None:
        prov = MemoryProvenance(
            source="test",
            confidence=0.3,
            authority_status="system",
            label=ProvenanceLabel.VERIFIED,
        )
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 1, "memory_provenance": prov},
        )
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert strange.verdict == LockVerdict.HOLD
        assert "confidence" in strange.reason.lower()

    def test_loop_with_good_provenance_seals(self, engine: RecursiveGovernanceEngine) -> None:
        prov = MemoryProvenance(
            source="test",
            confidence=0.9,
            authority_status="system",
            label=ProvenanceLabel.VERIFIED,
        )
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 2, "memory_provenance": prov},
        )
        strange = next(r for r in receipt.lock_receipts if r.lock_type == LockType.STRANGE_LOOP)
        assert strange.verdict == LockVerdict.SEAL


# ═══════════════════════════════════════════════════════════════════════════════
# ANTI-BEAUTIFUL-ONE
# ═══════════════════════════════════════════════════════════════════════════════


class TestAntiBeautifulOne:
    def test_normal_operation_seals(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"operational_contact_score": 0.8, "beauty_to_consequence_ratio": 0.5},
        )
        ab1 = next(r for r in receipt.lock_receipts if r.lock_type == LockType.ANTI_BEAUTIFUL_ONE)
        assert ab1.verdict == LockVerdict.SEAL

    def test_high_beauty_ratio_holds(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"beauty_to_consequence_ratio": 3.0},
        )
        ab1 = next(r for r in receipt.lock_receipts if r.lock_type == LockType.ANTI_BEAUTIFUL_ONE)
        assert ab1.verdict == LockVerdict.HOLD
        assert (
            " Beauty-to-consequence" in ab1.reason or "Elegance without consequence" in ab1.reason
        )

    def test_low_operational_contact_holds(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={"operational_contact_score": 0.1, "beauty_to_consequence_ratio": 1.5},
        )
        ab1 = next(r for r in receipt.lock_receipts if r.lock_type == LockType.ANTI_BEAUTIFUL_ONE)
        assert ab1.verdict == LockVerdict.HOLD
        assert "withdrawing" in ab1.reason.lower() or "Operational contact" in ab1.reason

    def test_critical_survival_no_reality_voids(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={
                "survival_status": "critical",
                "reality_evidence_present": False,
                "beauty_to_consequence_ratio": 1.0,
            },
        )
        assert receipt.composite_verdict == LockVerdict.VOID
        ab1 = next(r for r in receipt.lock_receipts if r.lock_type == LockType.ANTI_BEAUTIFUL_ONE)
        assert "CRITICAL" in ab1.reason
        assert "Beautiful One" in ab1.reason

    def test_human_cost_hidden_by_calm_holds(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={},
            actor_id="test-agent",
            context={
                "human_cost_detected": True,
                "beauty_to_consequence_ratio": 1.5,
                "operational_contact_score": 0.8,
            },
        )
        ab1 = next(r for r in receipt.lock_receipts if r.lock_type == LockType.ANTI_BEAUTIFUL_ONE)
        assert ab1.verdict == LockVerdict.HOLD
        assert "Human cost" in ab1.reason


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE VERDICT
# ═══════════════════════════════════════════════════════════════════════════════


class TestCompositeVerdict:
    def test_void_wins_over_hold(self, engine: RecursiveGovernanceEngine) -> None:
        # Gödel VOID + Strange Loop HOLD + AB1 SEAL → VOID
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"claim": "I am safe"},
            actor_id="test-agent",
            context={"memory_loop_depth": 2},
        )
        assert receipt.composite_verdict == LockVerdict.VOID

    def test_hold_wins_over_seal(self, engine: RecursiveGovernanceEngine) -> None:
        # Gödel SEAL + Strange Loop HOLD + AB1 SEAL → HOLD
        prov = MemoryProvenance(
            source="test",
            confidence=0.3,
            authority_status="system",
            label=ProvenanceLabel.CLAIMED,
        )
        receipt = engine.apply_locks(
            tool_name="arif_sense_observe",
            params={},
            actor_id="test-agent",
            context={"memory_loop_depth": 1, "memory_provenance": prov},
        )
        assert receipt.composite_verdict == LockVerdict.HOLD

    def test_all_seal(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="arif_sense_observe",
            params={"query": "hello"},
            actor_id="test-agent",
            context={"operational_contact_score": 0.8},
        )
        assert receipt.composite_verdict == LockVerdict.SEAL

    def test_counters_increment(self, engine: RecursiveGovernanceEngine) -> None:
        engine.apply_locks(
            tool_name="some_tool",
            params={"claim": "I am safe"},
            actor_id="test-agent",
        )
        assert engine.void_count >= 1
        prev_void = engine.void_count
        engine.apply_locks(
            tool_name="some_tool",
            params={"claim": "I certify"},
            actor_id="test-agent",
        )
        assert engine.void_count == prev_void + 1


# ═══════════════════════════════════════════════════════════════════════════════
# LOCK VIOLATION EXCEPTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestLockViolation:
    def test_exception_carries_receipt(self, engine: RecursiveGovernanceEngine) -> None:
        receipt = engine.apply_locks(
            tool_name="some_tool",
            params={"claim": "I am conscious"},
            actor_id="test-agent",
        )
        exc = LockViolationError(receipt)
        assert receipt.composite_verdict == LockVerdict.VOID
        assert "VOID" in str(exc)
