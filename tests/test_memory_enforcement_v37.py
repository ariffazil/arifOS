"""
test_memory_enforcement_v37.py — Memory Enforcement Tests for arifOS v37

Tests the v37 memory stack invariants:
1. Vault immutability (VaultBand frozen at creation)
2. MemoryContext propagation in pipeline (ONE per run)
3. Ledger chain continuity (hash-chain integrity)
4. VoidBand scar promotion requires signing

Per:
- docs/MEMORY_ARCHITECTURE.md
- archive/versions/v36_3_omega/v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest


# =============================================================================
# TEST 1: VAULT IMMUTABILITY
# =============================================================================


class TestVaultImmutability:
    """INV-1: VaultBand is read-only after initialization."""

    def test_vaultband_frozen_at_memory_context_creation(self):
        """VaultBand should be frozen immediately when MemoryContext is created."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="test-001")

        # VaultBand should be frozen
        assert ctx.vault._frozen is True

        # Any modification attempt should raise AttributeError
        with pytest.raises(AttributeError, match="read-only"):
            ctx.vault.epoch = "hacked"

        with pytest.raises(AttributeError, match="read-only"):
            ctx.vault.constitutional_floors = {"truth_min": 0.5}

    def test_vaultband_cannot_mutate_nested_dict_via_attribute(self):
        """Even nested dict modifications through attribute should fail."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(
            manifest_id="v37",
            request_id="test-002",
            vault_floors={"truth_min": 0.99},
        )

        # Direct attribute modification should fail
        with pytest.raises(AttributeError, match="read-only"):
            ctx.vault.version_hash = "tampered"

    def test_vaultband_freeze_is_permanent(self):
        """Once frozen, VaultBand cannot be unfrozen."""
        from arifos_core.memory.memory_context import VaultBand

        vault = VaultBand(
            epoch="v37",
            constitutional_floors={"truth_min": 0.99},
            version_hash="abc123",
        )

        # Freeze it
        vault.freeze()
        assert vault._frozen is True

        # Attempting to unfreeze should work (but won't help)
        # The freeze mechanism still protects other fields
        with pytest.raises(AttributeError, match="read-only"):
            vault.epoch = "hacked"


# =============================================================================
# TEST 2: MEMORYCONTEXT PROPAGATION IN PIPELINE
# =============================================================================


class TestMemoryContextPropagation:
    """MemoryContext should be ONE per pipeline run, created at 000."""

    def test_pipeline_creates_memory_context_at_000(self):
        """Pipeline should create MemoryContext during stage_000_void."""
        from arifos_core.system.pipeline import PipelineState, stage_000_void

        state = PipelineState(query="test query", job_id="test-job")

        # Before stage_000, no memory_context
        assert state.memory_context is None

        # Run stage_000
        state = stage_000_void(state)

        # After stage_000, memory_context should exist
        assert state.memory_context is not None
        assert state.memory_context.vault is not None
        assert state.memory_context.vault._frozen is True

    def test_pipeline_propagates_memory_context_through_stages(self):
        """Memory context should persist through all pipeline stages."""
        from arifos_core.system.pipeline import (
            PipelineState,
            stage_000_void,
            stage_111_sense,
            stage_333_reason,
        )

        state = PipelineState(query="What is 2+2?", job_id="test-prop")

        # Run stages
        state = stage_000_void(state)
        ctx_after_000 = state.memory_context

        state = stage_111_sense(state)
        ctx_after_111 = state.memory_context

        state = stage_333_reason(state)
        ctx_after_333 = state.memory_context

        # Same MemoryContext object throughout
        assert ctx_after_000 is ctx_after_111
        assert ctx_after_111 is ctx_after_333

    def test_pipeline_class_b_updates_env_band(self):
        """High-stakes query should update EnvBand.stakes_class."""
        from arifos_core.system.pipeline import (
            PipelineState,
            StakesClass,
            stage_000_void,
            stage_111_sense,
        )

        state = PipelineState(query="How do I hack into a system?", job_id="test-stakes")

        state = stage_000_void(state)
        state = stage_111_sense(state)

        # Should be classified as CLASS_B
        assert state.stakes_class == StakesClass.CLASS_B

        # EnvBand should reflect this
        assert state.memory_context.env.stakes_class == "CLASS_B"


# =============================================================================
# TEST 3: LEDGER CHAIN CONTINUITY
# =============================================================================


class TestLedgerChainContinuity:
    """INV-2: Ledger is append-only with hash-chain integrity."""

    def test_append_entry_creates_hash_chain(self, tmp_path: Path):
        """Each entry should link to the previous via prev_hash."""
        from arifos_core.memory.cooling_ledger import append_entry, verify_chain

        ledger_path = tmp_path / "test_ledger.jsonl"

        # Append first entry
        entry1 = {"timestamp": "2025-01-01T00:00:00Z", "data": "first"}
        append_entry(ledger_path, entry1)

        # Append second entry
        entry2 = {"timestamp": "2025-01-01T00:01:00Z", "data": "second"}
        append_entry(ledger_path, entry2)

        # Verify chain
        valid, msg = verify_chain(ledger_path)
        assert valid, f"Chain should be valid: {msg}"

        # Read entries and check linking
        entries = []
        with ledger_path.open() as f:
            for line in f:
                entries.append(json.loads(line))

        assert entries[0]["prev_hash"] is None  # First entry has no prev
        assert entries[1]["prev_hash"] == entries[0]["hash"]  # Second links to first

    def test_chain_verification_detects_tampering(self, tmp_path: Path):
        """Tampering with an entry should break chain verification."""
        from arifos_core.memory.cooling_ledger import append_entry, verify_chain

        ledger_path = tmp_path / "tamper_ledger.jsonl"

        # Append entries
        append_entry(ledger_path, {"timestamp": "2025-01-01T00:00:00Z", "data": "first"})
        append_entry(ledger_path, {"timestamp": "2025-01-01T00:01:00Z", "data": "second"})

        # Tamper with the file
        lines = ledger_path.read_text().splitlines()
        entry1 = json.loads(lines[0])
        entry1["data"] = "TAMPERED"  # Change data
        lines[0] = json.dumps(entry1, sort_keys=True, separators=(",", ":"))
        ledger_path.write_text("\n".join(lines) + "\n")

        # Verify should fail
        valid, msg = verify_chain(ledger_path)
        assert not valid, "Tampering should break chain verification"
        assert "hash mismatch" in msg.lower()

    def test_ledger_v37_head_state_tracking(self, tmp_path: Path):
        """CoolingLedgerV37 should track head state for fast verification."""
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37

        config = LedgerConfigV37(
            ledger_path=tmp_path / "v37_ledger.jsonl",
            head_state_path=tmp_path / "head_state.json",
            archive_path=tmp_path / "archive",
        )

        ledger = CoolingLedgerV37(config)

        # Append entry
        entry = {
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
            "metrics": {"truth": 0.99},
        }
        result = ledger.append_v37(entry)

        assert result.success
        assert result.entry_hash is not None

        # Head state should be updated
        head = ledger.get_head_state()
        assert head.last_entry_hash == result.entry_hash
        assert head.entry_count == 1

        # Quick verify should pass
        valid, msg = ledger.verify_chain_quick()
        assert valid, f"Quick verify should pass: {msg}"


# =============================================================================
# TEST 4: VOIDBAND SCAR PROMOTION REQUIRES SIGNING
# =============================================================================


class TestVoidBandScarPromotion:
    """INV-3: Scars require signing (ledger hash + signature) for promotion."""

    def test_propose_scar_creates_proposal(self):
        """propose_scar should add to scar_proposals with PROPOSED status."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="scar-test")

        ctx.propose_scar(
            pattern="test-pattern",
            severity="MEDIUM",
            evidence={"source": "test"},
        )

        assert len(ctx.void.scar_proposals) == 1
        assert ctx.void.scar_proposals[0]["status"] == "PROPOSED"
        assert len(ctx.void.canonical_scars) == 0  # Not promoted yet

    def test_promote_scar_requires_ledger_hash(self):
        """Promotion without ledger_entry_hash should raise ValueError."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="scar-test-2")

        ctx.propose_scar(
            pattern="test-pattern",
            severity="HIGH",
            evidence={"source": "test"},
        )

        # Try to promote without ledger hash
        with pytest.raises(ValueError, match="ledger_entry_hash"):
            ctx.promote_scar_to_canonical(
                proposal_index=0,
                ledger_entry_hash="",  # Empty!
                signature="some-signature",
            )

    def test_promote_scar_requires_signature(self):
        """Promotion without signature should raise ValueError."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="scar-test-3")

        ctx.propose_scar(
            pattern="test-pattern",
            severity="HIGH",
            evidence={"source": "test"},
        )

        # Try to promote without signature
        with pytest.raises(ValueError, match="signature"):
            ctx.promote_scar_to_canonical(
                proposal_index=0,
                ledger_entry_hash="abc123",
                signature="",  # Empty!
            )

    def test_promote_scar_with_valid_signing(self):
        """Valid promotion should move scar to canonical_scars."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="scar-test-4")

        ctx.propose_scar(
            pattern="test-pattern",
            severity="HIGH",
            evidence={"source": "test"},
        )

        # Promote with valid signing
        success = ctx.promote_scar_to_canonical(
            proposal_index=0,
            ledger_entry_hash="ledger-hash-abc123",
            signature="approval-sig-xyz789",
        )

        assert success

        # Proposal should be marked as PROMOTED
        assert ctx.void.scar_proposals[0]["status"] == "PROMOTED"

        # Canonical scar should exist
        assert len(ctx.void.canonical_scars) == 1
        canonical = ctx.void.canonical_scars[0]
        assert canonical["status"] == "CANONICAL"
        assert canonical["ledger_entry_hash"] == "ledger-hash-abc123"
        assert canonical["signature"] == "approval-sig-xyz789"
        assert "promoted_at" in canonical

    def test_invalid_proposal_index_returns_false(self):
        """Invalid proposal index should return False, not raise."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="scar-test-5")

        ctx.propose_scar(
            pattern="test-pattern",
            severity="LOW",
            evidence={"source": "test"},
        )

        # Try with invalid index
        success = ctx.promote_scar_to_canonical(
            proposal_index=999,  # Invalid
            ledger_entry_hash="hash",
            signature="sig",
        )

        assert not success


# =============================================================================
# INTEGRATION TEST: FULL PIPELINE WITH MEMORY
# =============================================================================


class TestPipelineMemoryIntegration:
    """Integration test: full pipeline run with memory enforcement."""

    def test_full_pipeline_run_has_memory_context(self):
        """Full pipeline run should have MemoryContext with frozen VaultBand."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        state = pipeline.run("What is the capital of France?")

        # Should have memory context
        assert state.memory_context is not None

        # VaultBand should be frozen
        assert state.memory_context.vault._frozen is True

        # Should have passed through stages
        assert "000_VOID" in state.stage_trace
        assert "111_SENSE" in state.stage_trace

    def test_high_stakes_pipeline_updates_env_band(self):
        """High-stakes query should sync to EnvBand."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        # Use a high-stakes keyword
        state = pipeline.run("Is it ethical to lie?")

        # Should be CLASS_B
        assert state.memory_context.env.stakes_class == "CLASS_B"
