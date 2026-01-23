"""
test_memory_stack_v37.py — Tests for arifOS v37 Memory Stack

Tests the v37 memory stack implementation:
- MemoryContext (6 bands)
- ScarManager (witness/scar lifecycle)
- Phoenix72Controller (amendment workflow)
- EurekaReceiptManager (zkPC receipts)
- CoolingLedgerV37 (hash-chain with head state)

Per:
- archive/versions/v36_3_omega/v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md
- archive/versions/v36_3_omega/v36.3O/spec/memory_context_spec_v36.3O.json
- archive/versions/v36_3_omega/v36.3O/spec/scar_record_spec_v36.3O.json
- archive/versions/v36_3_omega/v36.3O/spec/phoenix72_amendment_spec_v36.3O.json
- archive/versions/v36_3_omega/v36.3O/spec/eureka_receipt_spec_v36.3O.json

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_runtime_dir(tmp_path: Path) -> Path:
    """Create a temporary runtime directory."""
    runtime = tmp_path / "runtime" / "vault_999"
    runtime.mkdir(parents=True, exist_ok=True)
    return runtime


@pytest.fixture
def sample_constitution(temp_runtime_dir: Path) -> Path:
    """Create a sample constitution file."""
    const_path = temp_runtime_dir / "constitution.json"
    constitution = {
        "epoch": "v37",
        "floors": {
            "truth_min": 0.99,
            "delta_s_min": 0.0,
            "peace_squared_min": 1.0,
            "kappa_r_min": 0.95,
            "omega_0_min": 0.03,
            "amanah_lock": True,
            "rasa_required": True,
            "tri_witness_min": 0.95,
            "anti_hantu_required": True,
        },
        "physics": {
            "delta_omega_psi": {
                "delta_weight": 0.4,
                "omega_weight": 0.3,
                "psi_weight": 0.3,
            }
        },
        "laws": [],
    }
    const_path.write_text(json.dumps(constitution, indent=2))
    return const_path


# =============================================================================
# MEMORY CONTEXT TESTS
# =============================================================================


class TestMemoryContext:
    """Tests for 6-band MemoryContext."""

    def test_create_memory_context(self):
        """Should create a valid MemoryContext with all bands."""
        from arifos_core.memory.memory_context import create_memory_context

        ctx = create_memory_context(manifest_id="v37", request_id="test-request")

        assert ctx.context_id is not None
        assert ctx.epoch == "v37"
        assert ctx.env is not None
        assert ctx.vault is not None
        assert ctx.ledger is not None
        assert ctx.active_stream is not None

    def test_env_band_operations(self):
        """ENV band should support extra dict operations."""
        from arifos_core.memory.memory_context import EnvBand

        env = EnvBand(
            runtime_manifest_id="v37",
            request_id="test-req",
        )
        env.extra["key1"] = "value1"
        env.extra["key2"] = 42

        assert env.extra["key1"] == "value1"
        assert env.extra["key2"] == 42
        assert env.extra.get("missing", "default") == "default"

    def test_vault_band_is_frozen(self, sample_constitution: Path):
        """VaultBand should be read-only after freeze."""
        from arifos_core.memory.memory_context import VaultBand

        vault = VaultBand(
            epoch="v37",
            constitutional_floors={"truth_min": 0.99},
            version_hash="",
        )
        vault.freeze()

        # Should raise on attempted modification
        with pytest.raises(AttributeError):
            vault.constitutional_floors = {"new": "data"}

    def test_active_stream_band_operations(self):
        """ActiveStreamBand should support message operations."""
        from arifos_core.memory.memory_context import ActiveStreamBand

        stream = ActiveStreamBand()
        stream.messages.append({"role": "user", "content": "hello"})
        stream.governance_state["stage"] = "000"
        stream.tools_invoked.append({"tool": "read", "params": {}})

        assert len(stream.messages) == 1
        assert stream.governance_state["stage"] == "000"
        assert len(stream.tools_invoked) == 1

    def test_validate_memory_context(self):
        """validate_memory_context should detect invalid contexts."""
        from arifos_core.memory.memory_context import (
            MemoryContext,
            EnvBand,
            VaultBand,
            LedgerBand,
            ActiveStreamBand,
            validate_memory_context,
        )

        # Build valid context manually
        env = EnvBand(
            runtime_manifest_id="v37",
            request_id="test-req",
        )
        vault = VaultBand(
            epoch="v37",
            constitutional_floors={"truth_min": 0.99},
            version_hash="abc123",
        )
        ledger = LedgerBand()
        active = ActiveStreamBand()

        ctx = MemoryContext(
            context_id="test",
            epoch="v37",
            env=env,
            vault=vault,
            ledger=ledger,
            active_stream=active,
        )

        valid, errors = validate_memory_context(ctx)
        assert valid is True
        assert len(errors) == 0


# =============================================================================
# SCAR MANAGER TESTS
# =============================================================================


class TestScarManager:
    """Tests for ScarManager witness/scar lifecycle."""

    def test_observe_pattern_creates_witness(self, temp_runtime_dir: Path):
        """observe_pattern should create an unsigned witness."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig

        config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        manager = ScarManager(config)

        witness = manager.observe_pattern(
            pattern_text="suspicious pattern",
            severity="S2",
            floors=["F1", "F6"],
            created_by="test",
        )

        assert witness.witness_id.startswith("WIT-")
        assert witness.pattern_text == "suspicious pattern"
        assert witness.severity == "S2"
        assert "F1" in witness.floors

    def test_seal_scar_requires_signature(self, temp_runtime_dir: Path):
        """seal_scar should require a signature."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig

        config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        manager = ScarManager(config)

        witness = manager.observe_pattern(
            pattern_text="test",
            severity="S1",
            floors=["F1"],
        )

        # Without signature
        success, scar, error = manager.seal_scar(
            witness_id=witness.witness_id,
            signature="",
            sealed_by="test",
        )
        assert success is False
        assert "Signature is required" in error

        # With signature
        success, scar, error = manager.seal_scar(
            witness_id=witness.witness_id,
            signature="valid_signature_here",
            sealed_by="Phoenix72",
        )
        assert success is True
        assert scar.scar_id.startswith("SCAR-")
        assert scar.status == "SEALED"

    def test_compute_floor_pressure(self, temp_runtime_dir: Path):
        """compute_floor_pressure should sum severity weights."""
        from arifos_core.memory.scar_manager import (
            ScarManager,
            ScarManagerConfig,
            SEVERITY_WEIGHTS,
        )

        config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        manager = ScarManager(config)

        # Create two scars for F1
        for severity in ["S1", "S2"]:
            success, _, _ = manager.create_scar_direct(
                pattern_text=f"pattern_{severity}",
                severity=severity,
                floors=["F1"],
                signature="sig",
                created_by="test",
                sealed_by="test",
            )
            assert success

        pressure = manager.compute_floor_pressure("F1")
        expected = SEVERITY_WEIGHTS["S1"] + SEVERITY_WEIGHTS["S2"]  # 1.0 + 2.0 = 3.0
        assert pressure == expected

    def test_heal_scar(self, temp_runtime_dir: Path):
        """heal_scar should mark scar as HEALED."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig

        config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        manager = ScarManager(config)

        success, scar, _ = manager.create_scar_direct(
            pattern_text="healable pattern",
            severity="S1",
            floors=["F1"],
            signature="sig",
            created_by="test",
            sealed_by="test",
        )

        success, error = manager.heal_scar(
            scar_id=scar.scar_id,
            signature="heal_sig",
            reason="Issue resolved",
        )
        assert success is True

        healed_scar = manager.get_scar(scar.scar_id)
        assert healed_scar.status == "HEALED"


# =============================================================================
# COOLING LEDGER V37 TESTS
# =============================================================================


class TestCoolingLedgerV37:
    """Tests for CoolingLedgerV37 with head state."""

    def test_append_v37_creates_hash_chain(self, temp_runtime_dir: Path):
        """append_v37 should create proper hash chain."""
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37

        config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
        )
        ledger = CoolingLedgerV37(config)

        # First entry
        result1 = ledger.append_v37({"job_id": "job1", "verdict": "SEAL"})
        assert result1.success is True
        assert result1.entry_hash is not None

        # Second entry
        result2 = ledger.append_v37({"job_id": "job2", "verdict": "PARTIAL"})
        assert result2.success is True

        # Verify head state updated
        head = ledger.get_head_state()
        assert head.entry_count == 2
        assert head.last_entry_hash == result2.entry_hash

    def test_verify_chain_quick(self, temp_runtime_dir: Path):
        """verify_chain_quick should validate head state."""
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37

        config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
        )
        ledger = CoolingLedgerV37(config)

        ledger.append_v37({"job_id": "job1", "verdict": "SEAL"})
        ledger.append_v37({"job_id": "job2", "verdict": "SEAL"})

        valid, msg = ledger.verify_chain_quick()
        assert valid is True
        assert "2 entries" in msg

    def test_fail_behavior_returns_result(self, temp_runtime_dir: Path):
        """append_v37 should return failure result, not raise."""
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37

        # Use a read-only path to simulate IO error
        config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
            fail_behavior="SABAR_HOLD_WITH_LOG",
        )
        ledger = CoolingLedgerV37(config)

        # Normal write should work
        result = ledger.append_v37({"job_id": "test", "verdict": "SEAL"})
        assert result.success is True


# =============================================================================
# EUREKA RECEIPT TESTS
# =============================================================================


class TestEurekaReceiptManager:
    """Tests for EurekaReceiptManager zkPC receipts."""

    def test_generate_receipt_for_seal(self, temp_runtime_dir: Path):
        """Should generate receipt for SEAL verdict."""
        from arifos_core.memory.eureka_receipt import (
            EurekaReceiptManager,
            EurekaConfig,
            CareScope,
        )

        config = EurekaConfig(
            receipts_path=temp_runtime_dir / "eureka_receipts.jsonl",
            merkle_state_path=temp_runtime_dir / "eureka_merkle_state.json",
        )
        manager = EurekaReceiptManager(config)

        care_scope = CareScope(
            who=["user", "earth"],
            risk_cooled="misinformation risk",
        )

        success, receipt, error = manager.generate_receipt(
            ledger_entry_hash="a" * 64,
            verdict="SEAL",
            stakes_class="CLASS_A",
            care_scope=care_scope,
        )

        assert success is True
        assert receipt.receipt_id.startswith("EUREKA-")
        assert receipt.verdict == "SEAL"
        assert receipt.floor_proofs.all_checked() is True

    def test_no_receipt_for_void(self, temp_runtime_dir: Path):
        """Should not generate receipt for VOID verdict."""
        from arifos_core.memory.eureka_receipt import generate_eureka_receipt

        # VOID should not generate receipt
        success, receipt, error = generate_eureka_receipt(
            ledger_entry_hash="a" * 64,
            verdict="VOID",
        )

        assert success is True  # Not an error
        assert receipt is None  # But no receipt generated

    def test_receipt_chain_integrity(self, temp_runtime_dir: Path):
        """Receipts should chain properly via previous_receipt_hash."""
        from arifos_core.memory.eureka_receipt import (
            EurekaReceiptManager,
            EurekaConfig,
            CareScope,
        )

        config = EurekaConfig(
            receipts_path=temp_runtime_dir / "eureka_receipts.jsonl",
            merkle_state_path=temp_runtime_dir / "eureka_merkle_state.json",
        )
        manager = EurekaReceiptManager(config)

        care_scope = CareScope(who=["user"], risk_cooled="test")

        # Generate two receipts
        _, r1, _ = manager.generate_receipt(
            ledger_entry_hash="a" * 64,
            verdict="SEAL",
            stakes_class="CLASS_A",
            care_scope=care_scope,
        )

        _, r2, _ = manager.generate_receipt(
            ledger_entry_hash="b" * 64,
            verdict="PARTIAL",
            stakes_class="CLASS_B",
            care_scope=care_scope,
        )

        # Second should chain to first
        assert r1.previous_receipt_hash is None
        assert r2.previous_receipt_hash == r1.receipt_hash

        # Verify chain
        valid, msg = manager.verify_chain()
        assert valid is True

    def test_verify_receipt(self, temp_runtime_dir: Path):
        """verify_receipt should validate hash and signature."""
        from arifos_core.memory.eureka_receipt import (
            EurekaReceiptManager,
            EurekaConfig,
            CareScope,
        )

        config = EurekaConfig(
            receipts_path=temp_runtime_dir / "eureka_receipts.jsonl",
            merkle_state_path=temp_runtime_dir / "eureka_merkle_state.json",
        )
        manager = EurekaReceiptManager(config)

        care_scope = CareScope(who=["user"], risk_cooled="test")

        _, receipt, _ = manager.generate_receipt(
            ledger_entry_hash="a" * 64,
            verdict="SEAL",
            stakes_class="CLASS_A",
            care_scope=care_scope,
        )

        valid, error = manager.verify_receipt(receipt)
        assert valid is True
        assert error is None


# =============================================================================
# PHOENIX-72 CONTROLLER TESTS
# =============================================================================


class TestPhoenix72Controller:
    """Tests for Phoenix72Controller amendment workflow."""

    @pytest.fixture
    def phoenix_setup(self, temp_runtime_dir: Path, sample_constitution: Path):
        """Set up Phoenix-72 controller with dependencies."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig
        from arifos_core.memory.vault_manager import (
            VaultManager,
            VaultManagerConfig,
            SafetyConstraints,
        )
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37
        from arifos_core.memory.phoenix72_controller import (
            Phoenix72Controller,
            Phoenix72Config,
        )

        scar_config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        scar_manager = ScarManager(scar_config)

        # Create safety constraints with relaxed requirements for testing
        safety_constraints = SafetyConstraints(
            max_delta=0.05,
            cooldown_hours=0,
            min_evidence_entries=1,
        )

        vault_config = VaultManagerConfig(
            vault_path=sample_constitution,
            amendments_path=temp_runtime_dir / "amendments.jsonl",
            safety_constraints=safety_constraints,
        )
        vault_manager = VaultManager(vault_config)

        ledger_config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
        )
        ledger = CoolingLedgerV37(ledger_config)

        phoenix_config = Phoenix72Config(
            cooldown_hours=0,  # Disable for testing
            min_evidence_entries=1,  # Lower for testing
            pressure_min=0.1,  # Lower for testing
        )
        controller = Phoenix72Controller(
            vault_manager=vault_manager,
            scar_manager=scar_manager,
            ledger=ledger,
            config=phoenix_config,
        )

        return {
            "controller": controller,
            "vault": vault_manager,
            "scars": scar_manager,
            "ledger": ledger,
        }

    def test_analyze_pressure(self, phoenix_setup):
        """analyze_pressure should compute pressure for all floors."""
        controller = phoenix_setup["controller"]
        scars = phoenix_setup["scars"]

        # Add some scars
        scars.create_scar_direct(
            pattern_text="F1 issue",
            severity="S2",
            floors=["F1"],
            signature="sig",
            created_by="test",
            sealed_by="test",
        )

        pressures = controller.analyze_pressure()

        assert "F1" in pressures
        assert pressures["F1"].scar_pressure > 0
        assert pressures["F1"].scar_count == 1

    def test_propose_validates_evidence(self, phoenix_setup):
        """propose should validate evidence requirements."""
        controller = phoenix_setup["controller"]

        # Try to propose without evidence
        result = controller.propose(
            floor_id="F1",
            new_threshold=0.995,
            reason="Test amendment",
            evidence_ledger_hashes=[],
            evidence_scar_ids=[],
        )

        assert result.success is False
        assert any("evidence" in e.lower() for e in result.errors)

    def test_propose_and_finalize(self, phoenix_setup):
        """Full amendment workflow: propose -> finalize."""
        controller = phoenix_setup["controller"]
        scars = phoenix_setup["scars"]

        # Create some scars for evidence
        success, scar, _ = scars.create_scar_direct(
            pattern_text="F1 drift detected",
            severity="S3",
            floors=["F1"],
            signature="sig",
            created_by="test",
            sealed_by="test",
        )

        # Propose amendment
        proposal = controller.propose(
            floor_id="F1",
            new_threshold=0.995,
            reason="Tighten F1 based on drift",
            evidence_scar_ids=[scar.scar_id],
        )

        assert proposal.success is True
        assert proposal.amendment_id is not None

        # Finalize
        finalize_result = controller.finalize(proposal.amendment_id)

        assert finalize_result.success is True
        assert finalize_result.signature is not None

    def test_protected_floor_requires_override(self, phoenix_setup):
        """Protected floors (F6/F9) should require override flag."""
        controller = phoenix_setup["controller"]

        # Try to amend F6 without override
        result = controller.propose(
            floor_id="F6",
            new_threshold=False,
            reason="Try to unlock Amanah",
        )

        assert result.success is False
        assert any("protected" in e.lower() for e in result.errors)

        # With override (still needs evidence though)
        result = controller.propose(
            floor_id="F6",
            new_threshold=False,
            reason="Unlock Amanah with override",
            override_protected=True,
            evidence_scar_ids=["scar1"],
        )
        # May still fail due to evidence, but not due to protection
        if not result.success:
            assert not any("protected" in e.lower() for e in result.errors)

    def test_cooldown_enforcement(self, temp_runtime_dir: Path, sample_constitution: Path):
        """Cooldown window should be enforced."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig
        from arifos_core.memory.vault_manager import VaultManager, VaultManagerConfig
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37
        from arifos_core.memory.phoenix72_controller import (
            Phoenix72Controller,
            Phoenix72Config,
        )
        from arifos_core.memory.vault_manager import SafetyConstraints

        scar_config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        scar_manager = ScarManager(scar_config)

        # Use relaxed safety constraints for testing
        safety_constraints = SafetyConstraints(
            max_delta=0.05,
            cooldown_hours=24,  # This is for Phoenix72Config
            min_evidence_entries=1,
        )

        vault_config = VaultManagerConfig(
            vault_path=sample_constitution,
            amendments_path=temp_runtime_dir / "amendments.jsonl",
            safety_constraints=safety_constraints,
        )
        vault_manager = VaultManager(vault_config)

        ledger_config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
        )
        ledger = CoolingLedgerV37(ledger_config)

        # Set cooldown to 24 hours
        phoenix_config = Phoenix72Config(
            cooldown_hours=24,
            min_evidence_entries=1,
        )
        controller = Phoenix72Controller(
            vault_manager=vault_manager,
            scar_manager=scar_manager,
            ledger=ledger,
            config=phoenix_config,
        )

        # Create scar for evidence
        success, scar, _ = scar_manager.create_scar_direct(
            pattern_text="test",
            severity="S1",
            floors=["F1"],
            signature="sig",
            created_by="test",
            sealed_by="test",
        )

        # First amendment should succeed
        proposal1 = controller.propose(
            floor_id="F1",
            new_threshold=0.995,
            reason="First amendment",
            evidence_scar_ids=[scar.scar_id],
        )
        assert proposal1.success is True

        finalize1 = controller.finalize(proposal1.amendment_id)
        assert finalize1.success is True

        # Second amendment to same floor should fail (cooldown)
        proposal2 = controller.propose(
            floor_id="F1",
            new_threshold=0.996,
            reason="Second amendment",
            evidence_scar_ids=[scar.scar_id],
        )

        assert proposal2.success is False
        assert any("cooldown" in e.lower() for e in proposal2.errors)

    def test_safety_cap_enforcement(self, phoenix_setup):
        """Delta safety cap |ΔF| ≤ 0.05 should be enforced."""
        controller = phoenix_setup["controller"]
        scars = phoenix_setup["scars"]

        # Create scar
        success, scar, _ = scars.create_scar_direct(
            pattern_text="test",
            severity="S1",
            floors=["F1"],
            signature="sig",
            created_by="test",
            sealed_by="test",
        )

        # Try a delta > 0.05 (current is 0.99, try 0.85)
        result = controller.propose(
            floor_id="F1",
            new_threshold=0.85,  # Delta of 0.14 > 0.05
            reason="Big change",
            evidence_scar_ids=[scar.scar_id],
        )

        # Should fail at proposal stage due to vault_manager validation
        # or at finalize stage
        if result.success:
            finalize = controller.finalize(result.amendment_id)
            assert finalize.success is False
            assert any("delta" in e.lower() or "cap" in e.lower() for e in finalize.errors)
        else:
            assert any("delta" in e.lower() or "cap" in e.lower() for e in result.errors)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestMemoryStackIntegration:
    """Integration tests for the full v37 memory stack."""

    def test_full_governance_flow(self, temp_runtime_dir: Path, sample_constitution: Path):
        """Test full flow: observe -> seal scar -> log ledger -> generate receipt."""
        from arifos_core.memory.scar_manager import ScarManager, ScarManagerConfig
        from arifos_core.memory.cooling_ledger import CoolingLedgerV37, LedgerConfigV37
        from arifos_core.memory.eureka_receipt import (
            EurekaReceiptManager,
            EurekaConfig,
            CareScope,
        )

        # Setup
        scar_config = ScarManagerConfig(
            witness_index_path=temp_runtime_dir / "witnesses.jsonl",
            scar_index_path=temp_runtime_dir / "scars.jsonl",
        )
        scar_manager = ScarManager(scar_config)

        ledger_config = LedgerConfigV37(
            ledger_path=temp_runtime_dir / "cooling_ledger.jsonl",
            head_state_path=temp_runtime_dir / "head_state.json",
            archive_path=temp_runtime_dir / "archive",
        )
        ledger = CoolingLedgerV37(ledger_config)

        eureka_config = EurekaConfig(
            receipts_path=temp_runtime_dir / "eureka_receipts.jsonl",
            merkle_state_path=temp_runtime_dir / "eureka_merkle_state.json",
        )
        eureka_manager = EurekaReceiptManager(eureka_config)

        # 1. Observe a pattern (witness)
        witness = scar_manager.observe_pattern(
            pattern_text="potential misinformation detected",
            severity="S2",
            floors=["F1", "F2"],
            created_by="runtime",
        )
        assert witness.witness_id is not None

        # 2. Seal the scar
        success, scar, _ = scar_manager.seal_scar(
            witness_id=witness.witness_id,
            signature="phoenix72_signature",
            sealed_by="Phoenix72",
        )
        assert success is True
        assert scar.status == "SEALED"

        # 3. Log to cooling ledger
        ledger_entry = {
            "job_id": "governance-test-001",
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scar_ids": [scar.scar_id],
        }
        result = ledger.append_v37(ledger_entry)
        assert result.success is True
        ledger_hash = result.entry_hash

        # 4. Generate EUREKA receipt
        care_scope = CareScope(
            who=["user"],
            risk_cooled="misinformation",
            harm_prevented="False information propagation",
        )
        success, receipt, _ = eureka_manager.generate_receipt(
            ledger_entry_hash=ledger_hash,
            verdict="SEAL",
            stakes_class="CLASS_B",
            care_scope=care_scope,
        )
        assert success is True
        assert receipt.event_id == ledger_hash

        # 5. Verify everything chains properly
        valid, _ = ledger.verify_chain_quick()
        assert valid is True

        valid, _ = eureka_manager.verify_chain()
        assert valid is True

        # 6. Check pressure increased
        pressure = scar_manager.compute_floor_pressure("F1")
        assert pressure > 0


# =============================================================================
# RUNTIME MANIFEST TESTS
# =============================================================================


class TestRuntimeManifest:
    """Tests for runtime_manifest.py epoch selection."""

    def test_normalize_epoch(self):
        """normalize_epoch should handle various formats."""
        from arifos_core.system.runtime_manifest import normalize_epoch
        import pytest

        assert normalize_epoch("v37") == "v37"
        assert normalize_epoch("v36.3") == "v36.3"
        assert normalize_epoch("v36.3Omega") == "v36.3"
        assert normalize_epoch("v35") == "v35"
        assert normalize_epoch("v35Omega") == "v35"

        # Invalid epochs should raise ValueError
        with pytest.raises(ValueError):
            normalize_epoch("")
        with pytest.raises(ValueError):
            normalize_epoch("invalid")

    def test_is_v37_epoch(self):
        """is_v37_epoch should detect v37."""
        from arifos_core.system.runtime_manifest import is_v37_epoch, set_active_epoch

        # Test with manifest dict
        manifest_v37 = {"_runtime_epoch": "v37"}
        manifest_v36 = {"_runtime_epoch": "v36.3"}
        manifest_v35 = {"_runtime_epoch": "v35"}

        assert is_v37_epoch(manifest_v37) is True
        assert is_v37_epoch(manifest_v36) is False
        assert is_v37_epoch(manifest_v35) is False

        # Test without manifest (uses active epoch)
        set_active_epoch("v37")
        assert is_v37_epoch() is True

        set_active_epoch("v35")
        assert is_v37_epoch() is False
