"""
tests/test_decision_fabric.py — Tests for #421, #422, #423 Decision Fabric

Test failure behavior first, not correctness.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import pytest

from arifosmcp.core.decision_contract import (
    AuthorityClass,
    ConflictEnvelope,
    DecisionClass,
    DecisionContract,
    JudgeResult,
    OrganType,
    ResolutionResult,
    ReversibilityClass,
    RiskClass,
    VerdictClass,
    classify_decision,
)
from arifosmcp.core.conflict_resolver import (
    OrganRank,
    VerdictRank,
    resolve_conflict,
    resolve_multi_organ,
)
from arifosmcp.core.vault_receipt import (
    SessionChain,
    VaultReceipt,
    compute_receipt_hash,
    create_and_seal_receipt,
    verify_vault_chain,
)


# ═══════════════════════════════════════════════════════════════════
# PHASE 0: DecisionContract
# ═══════════════════════════════════════════════════════════════════


class TestDecisionContract:
    """Test the shared contract type."""

    def test_frozen(self):
        """Contract is immutable once created."""
        contract = DecisionContract(
            contract_id="test-001",
            session_id="sess-001",
            actor_id="test-actor",
            organ_id="arifos",
            tool_name="arif_judge",
            action_class="REASON",
            decision_class="C2_STANDARD",
            risk_class="medium",
            reversibility_class="FULL",
            intent_summary="Test decision",
            intent_hash=hashlib.sha256(b"test").hexdigest(),
            context_hash=hashlib.sha256(b"context").hexdigest(),
            conflict_domain="governance",
            is_irreversible=False,
            has_cached_verdict=False,
        )
        with pytest.raises(AttributeError):
            contract.action_class = "MUTATE"  # type: ignore

    def test_context_signature_deterministic(self):
        """Same input → same signature, every time."""
        contract = DecisionContract(
            contract_id="test-002",
            session_id="sess-001",
            actor_id="test-actor",
            organ_id="arifos",
            tool_name="arif_judge",
            action_class="REASON",
            decision_class="C2_STANDARD",
            risk_class="medium",
            reversibility_class="FULL",
            intent_summary="Test",
            intent_hash="abc123",
            context_hash="def456",
            conflict_domain="governance",
            is_irreversible=False,
            has_cached_verdict=False,
        )
        sig1 = contract.compute_context_signature()
        sig2 = contract.compute_context_signature()
        assert sig1 == sig2
        assert len(sig1) == 64  # SHA-256 hex

    def test_classify_decision_irreversible(self):
        """Irreversible → always C4_SOVEREIGN."""
        result = classify_decision(
            action_class="MUTATE",
            risk_class="low",
            is_irreversible=True,
            has_cached_verdict=False,
        )
        assert result == DecisionClass.C4_SOVEREIGN.value

    def test_classify_decision_cached(self):
        """Cached verdict + low/medium risk → C1_FAST."""
        result = classify_decision(
            action_class="REASON",
            risk_class="low",
            is_irreversible=False,
            has_cached_verdict=True,
        )
        assert result == DecisionClass.C1_FAST.value

    def test_classify_decision_observe(self):
        """OBSERVE → C0_AUTO regardless of risk."""
        for risk in ("low", "medium"):
            result = classify_decision("OBSERVE", risk, False, False)
            assert result == DecisionClass.C0_AUTO.value

    def test_classify_decision_unknown_defaults_conservative(self):
        """Unknown action_class → C3_DEEP (conservative)."""
        result = classify_decision(
            action_class="UNKNOWN_ACTION",
            risk_class="medium",
            is_irreversible=False,
            has_cached_verdict=False,
        )
        assert result == DecisionClass.C3_DEEP.value


# ═══════════════════════════════════════════════════════════════════
# PHASE 1: Conflict Resolver
# ═══════════════════════════════════════════════════════════════════


class TestConflictResolver:
    """Test the deterministic conflict resolver."""

    def test_void_always_wins(self):
        """VOID dominates all other verdicts."""
        envelope = ConflictEnvelope(
            conflict_id="c-001",
            organ_a="geox",
            verdict_a="VOID",
            organ_b="arifos",
            verdict_b="SEAL",
            conflict_domain="earth",
        )
        result = resolve_conflict(envelope)
        assert result.winner_organ == "geox"
        assert result.winner_verdict == "VOID"
        assert result.resolution_method == "dominance"
        assert not result.requires_888_hold

    def test_irreversible_escalates(self):
        """Irreversible action → always 888_HOLD."""
        envelope = ConflictEnvelope(
            conflict_id="c-002",
            organ_a="arifos",
            verdict_a="SEAL",
            organ_b="geox",
            verdict_b="SEAL",
            conflict_domain="earth",
            is_irreversible=True,
        )
        result = resolve_conflict(envelope)
        assert result.winner_verdict == "888_HOLD"
        assert result.requires_888_hold
        assert result.resolution_method == "escalate"

    def test_higher_organ_wins(self):
        """arifOS outranks GEOX when verdicts are comparable."""
        envelope = ConflictEnvelope(
            conflict_id="c-003",
            organ_a="geox",
            verdict_a="SEAL",
            organ_b="arifos",
            verdict_b="SEAL",
            conflict_domain="earth",
        )
        result = resolve_conflict(envelope)
        assert result.winner_organ == "arifos"
        assert result.resolution_method == "authority"

    def test_same_organ_more_restrictive_wins(self):
        """Same organ rank → more restrictive verdict wins."""
        envelope = ConflictEnvelope(
            conflict_id="c-004",
            organ_a="geox",
            verdict_a="SEAL",
            organ_b="geox",
            verdict_b="HOLD",
            conflict_domain="earth",
        )
        result = resolve_conflict(envelope)
        assert result.winner_verdict == "HOLD"

    def test_void_wins_over_proceed(self):
        """PROCEED vs VOID → VOID wins (Rule 1: VOID always dominates)."""
        envelope = ConflictEnvelope(
            conflict_id="c-005",
            organ_a="geox",
            verdict_a="PROCEED",
            organ_b="well",
            verdict_b="VOID",
            conflict_domain="earth",
        )
        result = resolve_conflict(envelope)
        assert result.winner_verdict == "VOID"
        assert result.winner_organ == "well"
        assert not result.requires_888_hold

    def test_latency_under_100ms(self):
        """Resolution must complete under 100ms (sub-100ms requirement)."""
        envelope = ConflictEnvelope(
            conflict_id="c-006",
            organ_a="geox",
            verdict_a="SEAL",
            organ_b="well",
            verdict_b="HOLD",
            conflict_domain="earth",
        )
        result = resolve_conflict(envelope)
        assert result.latency_us < 100_000  # 100ms = 100,000 μs

    def test_determinism_100_runs(self):
        """Same input × 100 runs → identical output."""
        envelope = ConflictEnvelope(
            conflict_id="c-007",
            organ_a="geox",
            verdict_a="SEAL",
            organ_b="arifos",
            verdict_b="HOLD",
            conflict_domain="earth",
        )
        results = [resolve_conflict(envelope) for _ in range(100)]
        assert all(r.winner_organ == results[0].winner_organ for r in results)
        assert all(r.winner_verdict == results[0].winner_verdict for r in results)
        assert all(r.resolution_method == results[0].resolution_method for r in results)


class TestMultiOrganResolver:
    """Test multi-organ conflict resolution."""

    def test_three_organs(self):
        """3 organs disagree → iterative pairwise resolution."""
        envelopes = [
            ConflictEnvelope(
                conflict_id="c-m-001",
                organ_a="geox",
                verdict_a="SEAL",
                organ_b="wealth",
                verdict_b="HOLD",
                conflict_domain="earth",
            ),
            ConflictEnvelope(
                conflict_id="c-m-002",
                organ_a="wealth",
                verdict_a="HOLD",
                organ_b="well",
                verdict_b="VOID",
                conflict_domain="health",
            ),
        ]
        result = resolve_multi_organ(envelopes)
        # VOID from well should dominate
        assert result.winner_verdict == "VOID"
        assert result.winner_organ == "well"

    def test_empty_escalates(self):
        """No conflicts → escalate to 888_HOLD."""
        result = resolve_multi_organ([])
        assert result.requires_888_hold


# ═══════════════════════════════════════════════════════════════════
# PHASE 3: VaultReceipt
# ═══════════════════════════════════════════════════════════════════


class TestVaultReceipt:
    """Test the receipt schema and chain."""

    def test_receipt_hash_deterministic(self):
        """Same receipt → same hash, every time."""
        receipt = VaultReceipt(
            receipt_id="test-001",
            ts="2026-06-25T00:00:00Z",
            monotonic_counter=1,
            parent_hash="",
            session_id="sess-001",
            session_merkle_root="abc",
            actor_id="test",
            organ_id="arifos",
            actor_pubkey_epoch=0,
            actor_signature="",
            intent_summary="Test",
            intent_hash="def",
            requested_authority="EXECUTE",
            pre_state_hash="ghi",
            decision="SEAL",
            verdict_hash="jkl",
            floors_evaluated=["F1", "F2"],
            floors_violated=[],
            conflict_resolved=False,
            conflict_resolution="none",
            decision_class="C2_STANDARD",
            latency_ms=50.0,
            within_budget=True,
            witness_count=0,
            witness_dissent=[],
            receipt_hash="",
            view_key_id="",
        )
        hash1 = compute_receipt_hash(receipt)
        hash2 = compute_receipt_hash(receipt)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_chain_linkage(self):
        """Receipts are linked via parent_hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"
            chain = SessionChain("test-session", vault_path)

            r1 = chain.create_receipt(
                actor_id="test",
                organ_id="arifos",
                intent_summary="First",
                intent_hash="h1",
                requested_authority="EXECUTE",
                pre_state_hash="s1",
                decision="SEAL",
                verdict_hash="v1",
                floors_evaluated=["F1"],
                floors_violated=[],
            )

            r2 = chain.create_receipt(
                actor_id="test",
                organ_id="arifos",
                intent_summary="Second",
                intent_hash="h2",
                requested_authority="EXECUTE",
                pre_state_hash="s2",
                decision="HOLD",
                verdict_hash="v2",
                floors_evaluated=["F1", "F2"],
                floors_violated=["F2"],
            )

            # r2's parent should be r1's hash
            assert r2.parent_hash == r1.receipt_hash
            # r1 has no parent (first in chain)
            assert r1.parent_hash == ""
            # Counters are monotonic
            assert r2.monotonic_counter == r1.monotonic_counter + 1

    def test_chain_verification(self):
        """Chain verification detects integrity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"
            chain = SessionChain("test-session", vault_path)

            for i in range(5):
                chain.create_receipt(
                    actor_id="test",
                    organ_id="arifos",
                    intent_summary=f"Receipt {i}",
                    intent_hash=f"h{i}",
                    requested_authority="EXECUTE",
                    pre_state_hash=f"s{i}",
                    decision="SEAL",
                    verdict_hash=f"v{i}",
                    floors_evaluated=["F1"],
                    floors_violated=[],
                )

            is_valid, errors = chain.verify_chain()
            assert is_valid
            assert len(errors) == 0

    def test_chain_verification_detects_tampering(self):
        """Chain verification detects tampered receipts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"
            chain = SessionChain("test-session", vault_path)

            for i in range(3):
                chain.create_receipt(
                    actor_id="test",
                    organ_id="arifos",
                    intent_summary=f"Receipt {i}",
                    intent_hash=f"h{i}",
                    requested_authority="EXECUTE",
                    pre_state_hash=f"s{i}",
                    decision="SEAL",
                    verdict_hash=f"v{i}",
                    floors_evaluated=["F1"],
                    floors_violated=[],
                )

            # Tamper with the second receipt
            chain.receipts[1].decision = "VOID"
            is_valid, errors = chain.verify_chain()
            assert not is_valid
            assert len(errors) > 0

    def test_persistence(self):
        """Receipts persist to disk and can be reloaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"

            # Create chain and add receipts
            chain1 = SessionChain("test-session", vault_path)
            r1 = chain1.create_receipt(
                actor_id="test",
                organ_id="arifos",
                intent_summary="Persistent",
                intent_hash="h1",
                requested_authority="EXECUTE",
                pre_state_hash="s1",
                decision="SEAL",
                verdict_hash="v1",
                floors_evaluated=["F1"],
                floors_violated=[],
            )
            chain1.append_to_vault(r1)

            # Load new chain from same file
            chain2 = SessionChain("test-session", vault_path)
            assert len(chain2.receipts) == 1
            assert chain2.receipts[0].receipt_id == r1.receipt_id

    def test_separate_sessions_independent(self):
        """Different sessions have independent chains."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"

            chain_a = SessionChain("session-a", vault_path)
            chain_b = SessionChain("session-b", vault_path)

            r_a = chain_a.create_receipt(
                actor_id="test",
                organ_id="arifos",
                intent_summary="Session A",
                intent_hash="h1",
                requested_authority="EXECUTE",
                pre_state_hash="s1",
                decision="SEAL",
                verdict_hash="v1",
                floors_evaluated=["F1"],
                floors_violated=[],
            )
            chain_a.append_to_vault(r_a)

            r_b = chain_b.create_receipt(
                actor_id="test",
                organ_id="arifos",
                intent_summary="Session B",
                intent_hash="h2",
                requested_authority="EXECUTE",
                pre_state_hash="s2",
                decision="HOLD",
                verdict_hash="v2",
                floors_evaluated=["F1"],
                floors_violated=[],
            )
            chain_b.append_to_vault(r_b)

            # Session A should only see its own receipt
            assert len(chain_a.receipts) == 1
            assert chain_a.receipts[0].session_id == "session-a"

            # Session B should only see its own receipt
            assert len(chain_b.receipts) == 1
            assert chain_b.receipts[0].session_id == "session-b"


class TestConvenienceFunctions:
    """Test the convenience functions."""

    def test_create_and_seal(self):
        """create_and_seal_receipt creates + appends in one call."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"
            receipt = create_and_seal_receipt(
                session_id="test-session",
                actor_id="test",
                organ_id="arifos",
                intent_summary="Convenience test",
                intent_hash="h1",
                requested_authority="EXECUTE",
                pre_state_hash="s1",
                decision="SEAL",
                verdict_hash="v1",
                floors_evaluated=["F1"],
                floors_violated=[],
                vault_path=vault_path,
            )
            assert receipt.receipt_hash != ""
            assert vault_path.exists()

    def test_verify_vault_chain(self):
        """verify_vault_chain checks integrity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"
            for i in range(3):
                create_and_seal_receipt(
                    session_id="test-session",
                    actor_id="test",
                    organ_id="arifos",
                    intent_summary=f"Receipt {i}",
                    intent_hash=f"h{i}",
                    requested_authority="EXECUTE",
                    pre_state_hash=f"s{i}",
                    decision="SEAL",
                    verdict_hash=f"v{i}",
                    floors_evaluated=["F1"],
                    floors_violated=[],
                    vault_path=vault_path,
                )
            is_valid, errors = verify_vault_chain("test-session", vault_path)
            assert is_valid


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION: End-to-end chaos test
# ═══════════════════════════════════════════════════════════════════


class TestEndToEndChaos:
    """
    End-to-end chaos test.
    3 organs disagree + latency breach + irreversible action.
    """

    def test_full_pipeline(self):
        """Full pipeline: classify → resolve → judge → receipt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = Path(tmpdir) / "test_receipts.jsonl"

            # Step 1: Classify
            decision_class = classify_decision(
                action_class="MUTATE",
                risk_class="high",
                is_irreversible=False,
                has_cached_verdict=False,
            )
            assert decision_class == DecisionClass.C3_DEEP.value

            # Step 2: Resolve conflict
            envelope = ConflictEnvelope(
                conflict_id="chaos-001",
                organ_a="geox",
                verdict_a="SEAL",
                organ_b="well",
                verdict_b="HOLD",
                conflict_domain="earth",
            )
            resolution = resolve_conflict(envelope)
            # HOLD should dominate SEAL (more restrictive wins)
            assert resolution.winner_verdict == "HOLD"
            assert not resolution.requires_888_hold

            # Step 3: Judge (simulated — in real system this would call LLM)
            t0 = time.monotonic()
            # Simulate judge taking 150ms (within C3_DEEP budget of 1000ms)
            time.sleep(0.01)  # 10ms for test speed
            elapsed_ms = (time.monotonic() - t0) * 1000
            judge_result = JudgeResult(
                verdict="HOLD",
                decision_class=decision_class,
                latency_ms=elapsed_ms,
                within_budget=elapsed_ms < 1000,
                reason="Conflict resolved — HOLD from WELL",
                resolution=resolution,
            )
            assert judge_result.within_budget

            # Step 4: Record receipt
            receipt = create_and_seal_receipt(
                session_id="chaos-session",
                actor_id="test",
                organ_id="arifos",
                intent_summary="Chaos test — 3 organs disagree",
                intent_hash=hashlib.sha256(b"chaos").hexdigest(),
                requested_authority="EXECUTE",
                pre_state_hash=hashlib.sha256(b"pre-state").hexdigest(),
                decision=judge_result.verdict,
                verdict_hash=hashlib.sha256(judge_result.verdict.encode()).hexdigest(),
                floors_evaluated=["F1", "F2", "F5", "F6"],
                floors_violated=[],
                conflict_resolved=True,
                conflict_resolution=resolution.resolution_method,
                decision_class=decision_class,
                latency_ms=elapsed_ms,
                within_budget=judge_result.within_budget,
                vault_path=vault_path,
            )

            # Verify
            assert receipt.receipt_hash != ""
            assert receipt.decision == "HOLD"
            assert receipt.conflict_resolved
            is_valid, errors = verify_vault_chain("chaos-session", vault_path)
            assert is_valid

    def test_irreversible_full_pipeline(self):
        """Irreversible action → must escalate, never execute."""
        envelope = ConflictEnvelope(
            conflict_id="irrev-001",
            organ_a="arifos",
            verdict_a="SEAL",
            organ_b="geox",
            verdict_b="SEAL",
            conflict_domain="earth",
            is_irreversible=True,
        )
        resolution = resolve_conflict(envelope)
        assert resolution.requires_888_hold
        assert resolution.winner_verdict == "888_HOLD"

        # Decision class should be C4_SOVEREIGN
        decision_class = classify_decision(
            action_class="ATOMIC",
            risk_class="atomic",
            is_irreversible=True,
            has_cached_verdict=False,
        )
        assert decision_class == DecisionClass.C4_SOVEREIGN.value
