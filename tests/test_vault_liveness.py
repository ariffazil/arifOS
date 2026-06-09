"""
tests/test_vault_liveness.py — Vault Liveness Contract tests
════════════════════════════════════════════════════════════

Verifies AAA-GOV-VAULT-LIVENESS-v1 contract behavior:
- Freshness thresholds
- Chain gap detection
- Merkle/signature verification
- Execution gating by liveness state
- ProductionContractManifest integrity

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest

from arifosmcp.schemas.vault_liveness import (
    ContractEntry,
    ContractStatus,
    LivenessCheckResult,
    ProductionContractManifest,
    VaultLivenessContract,
    VaultLivenessState,
)


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT LIVENESS CONTRACT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestVaultLivenessFresh:
    """FRESH state: all thresholds passed."""

    def test_fresh_when_all_checks_pass(self):
        contract = VaultLivenessContract()
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.FRESH
        assert result.chain_height == 5
        assert result.merkle_verified is True
        assert "all thresholds passed" in result.detail

    def test_fresh_allows_mutate(self):
        contract = VaultLivenessContract()
        contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is True
        assert reason == "SEAL"

    def test_fresh_allows_atomic(self):
        contract = VaultLivenessContract()
        contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("ATOMIC")
        assert allowed is True
        assert reason == "SEAL"


class TestVaultLivenessStale:
    """STALE state: last seal too old."""

    def test_stale_when_age_exceeds_threshold(self):
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        result = contract.check(
            last_seal_age_seconds=400,  # > 300
            chain_height=5,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.STALE
        assert "400s > threshold 300s" in result.detail

    def test_stale_blocks_mutate(self):
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        contract.check(
            last_seal_age_seconds=400,
            chain_height=5,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is False
        assert "HOLD" in reason
        assert "STALE" in reason

    def test_stale_blocks_atomic(self):
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        contract.check(
            last_seal_age_seconds=400,
            chain_height=5,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("ATOMIC")
        assert allowed is False
        assert "HOLD" in reason

    def test_stale_allows_observe(self):
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        contract.check(
            last_seal_age_seconds=400,
            chain_height=5,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("OBSERVE")
        assert allowed is True
        assert "WARN" in reason

    def test_stale_allows_prepare(self):
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        contract.check(
            last_seal_age_seconds=400,
            chain_height=5,
            merkle_verified=True,
            signature_verified=True,
        )
        allowed, reason = contract.allows_execution("PREPARE")
        assert allowed is True
        assert "WARN" in reason

    def test_disabled_freshness_always_fresh(self):
        """max_seal_age_seconds=0 disables freshness checks."""
        contract = VaultLivenessContract(max_seal_age_seconds=0)
        result = contract.check(
            last_seal_age_seconds=999999,  # ancient
            chain_height=5,
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.FRESH


class TestVaultLivenessCompromised:
    """COMPROMISED: chain broken beyond tolerance."""

    def test_compromised_when_gaps_exceed_tolerance(self):
        contract = VaultLivenessContract(max_chain_gap_tolerance=0)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            chain_gaps=1,  # > tolerance 0
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.COMPROMISED

    def test_compromised_blocks_observe(self):
        """COMPROMISED blocks everything, including OBSERVE."""
        contract = VaultLivenessContract(max_chain_gap_tolerance=0)
        contract.check(last_seal_age_seconds=60, chain_height=5, chain_gaps=1)
        allowed, reason = contract.allows_execution("OBSERVE")
        assert allowed is False
        assert "VOID" in reason
        assert "COMPROMISED" in reason

    def test_compromised_blocks_mutate(self):
        contract = VaultLivenessContract(max_chain_gap_tolerance=0)
        contract.check(last_seal_age_seconds=60, chain_height=5, chain_gaps=1)
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is False
        assert "VOID" in reason

    def test_tolerance_allows_some_gaps(self):
        """With tolerance=2, 1 gap is not compromised."""
        contract = VaultLivenessContract(max_chain_gap_tolerance=2)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            chain_gaps=1,  # < tolerance 2
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.FRESH


class TestVaultLivenessUnknown:
    """UNKNOWN: chain too short."""

    def test_unknown_when_chain_too_short(self):
        contract = VaultLivenessContract(min_chain_height=1)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=0,  # < min 1
        )
        assert result.state == VaultLivenessState.UNKNOWN

    def test_unknown_blocks_mutate(self):
        contract = VaultLivenessContract(min_chain_height=1)
        contract.check(last_seal_age_seconds=60, chain_height=0)
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is False
        assert "HOLD" in reason
        assert "UNKNOWN" in reason

    def test_unknown_allows_observe_with_warning(self):
        contract = VaultLivenessContract(min_chain_height=1)
        contract.check(last_seal_age_seconds=60, chain_height=0)
        allowed, reason = contract.allows_execution("OBSERVE")
        assert allowed is True
        assert "WARN" in reason


class TestVaultLivenessDegraded:
    """DEGRADED: verification failures."""

    def test_degraded_when_merkle_not_verified(self):
        contract = VaultLivenessContract(require_merkle_chain=True)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            merkle_verified=False,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.DEGRADED
        assert "merkle" in result.detail

    def test_degraded_when_signature_not_verified(self):
        contract = VaultLivenessContract(require_signature=True)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            merkle_verified=True,
            signature_verified=False,
        )
        assert result.state == VaultLivenessState.DEGRADED
        assert "signature" in result.detail

    def test_degraded_when_both_verifications_fail(self):
        contract = VaultLivenessContract(require_merkle_chain=True, require_signature=True)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            merkle_verified=False,
            signature_verified=False,
        )
        assert result.state == VaultLivenessState.DEGRADED
        assert "merkle" in result.detail
        assert "signature" in result.detail

    def test_degraded_blocks_mutate(self):
        contract = VaultLivenessContract(require_merkle_chain=True)
        contract.check(last_seal_age_seconds=60, chain_height=5, merkle_verified=False)
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is False
        assert "HOLD" in reason
        assert "DEGRADED" in reason

    def test_degraded_allows_observe(self):
        contract = VaultLivenessContract(require_merkle_chain=True)
        contract.check(last_seal_age_seconds=60, chain_height=5, merkle_verified=False)
        allowed, reason = contract.allows_execution("OBSERVE")
        assert allowed is True
        assert "WARN" in reason

    def test_verification_disabled_bypasses_degraded(self):
        """When verification not required, missing checks don't degrade."""
        contract = VaultLivenessContract(require_merkle_chain=False, require_signature=False)
        result = contract.check(
            last_seal_age_seconds=60,
            chain_height=5,
            merkle_verified=False,
            signature_verified=False,
        )
        assert result.state == VaultLivenessState.FRESH


class TestVaultLivenessNoCheck:
    """Behavior when no check has been performed."""

    def test_blocks_execution_before_first_check(self):
        contract = VaultLivenessContract()
        # No check() called yet
        allowed, reason = contract.allows_execution("MUTATE")
        assert allowed is False
        assert "not been performed" in reason

    def test_last_check_summary_unchecked(self):
        contract = VaultLivenessContract()
        summary = contract.last_check_summary()
        assert summary["state"] == "UNCHECKED"


class TestVaultLivenessValidation:
    """Schema validation tests."""

    def test_negative_min_chain_height_raises(self):
        with pytest.raises(ValueError, match="min_chain_height"):
            VaultLivenessContract(min_chain_height=-1)

    def test_negative_gap_tolerance_raises(self):
        with pytest.raises(ValueError, match="max_chain_gap_tolerance"):
            VaultLivenessContract(max_chain_gap_tolerance=-1)

    def test_negative_seal_age_raises(self):
        with pytest.raises(ValueError, match="max_seal_age_seconds"):
            VaultLivenessContract(max_seal_age_seconds=-1)

    def test_too_frequent_check_interval_raises(self):
        with pytest.raises(ValueError, match="liveness_check_interval_seconds"):
            VaultLivenessContract(liveness_check_interval_seconds=5)

    def test_default_contract_values(self):
        contract = VaultLivenessContract()
        assert contract.contract_id == "AAA-GOV-VAULT-LIVENESS-v1"
        assert contract.version == "1.0.0"
        assert contract.max_seal_age_seconds == 300
        assert contract.max_chain_gap_tolerance == 0
        assert contract.min_chain_height == 1
        assert contract.require_merkle_chain is True
        assert contract.require_signature is True
        assert contract.liveness_check_interval_seconds == 60


class TestVaultLivenessPriority:
    """Strictest check wins — order of judgment matters."""

    def test_chain_height_beats_freshness(self):
        """Chain too short = UNKNOWN, even if age is fresh."""
        contract = VaultLivenessContract(min_chain_height=10)
        result = contract.check(
            last_seal_age_seconds=1,  # very fresh
            chain_height=3,  # but too short
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.UNKNOWN

    def test_gaps_beat_freshness(self):
        """Chain gaps > tolerance = COMPROMISED, even if age is fresh."""
        contract = VaultLivenessContract(max_chain_gap_tolerance=0)
        result = contract.check(
            last_seal_age_seconds=1,  # very fresh
            chain_height=100,
            chain_gaps=5,  # compromised
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.COMPROMISED

    def test_verification_beats_freshness(self):
        """Failed verification = DEGRADED, even if age is fresh."""
        contract = VaultLivenessContract(require_merkle_chain=True)
        result = contract.check(
            last_seal_age_seconds=1,
            chain_height=100,
            chain_gaps=0,
            merkle_verified=False,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.DEGRADED

    def test_freshness_only_matters_after_other_checks(self):
        """Staleness is the last check — only matters if everything else passes."""
        contract = VaultLivenessContract(max_seal_age_seconds=300)
        result = contract.check(
            last_seal_age_seconds=600,  # stale
            chain_height=5,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
        )
        assert result.state == VaultLivenessState.STALE


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION CONTRACT MANIFEST TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestProductionContractManifest:
    """Verify the production contract manifest."""

    def test_manifest_has_ten_contracts(self):
        manifest = ProductionContractManifest()
        assert len(manifest.contracts) == 10

    def test_no_contracts_are_sealed_yet(self):
        """Honest: zero contracts are SEALED as of forge date."""
        manifest = ProductionContractManifest()
        assert manifest.sealed_count() == 0, "Zero SEALED is honest — hardening in progress"

    def test_some_contracts_partial(self):
        manifest = ProductionContractManifest()
        assert manifest.partial_count() >= 5

    def test_readiness_is_hardening(self):
        """With 1 ABSENT (attestation), readiness is PARTIAL.
        HARDENING requires zero absent contracts (all at least DRAFT).
        """
        manifest = ProductionContractManifest()
        summary = manifest.summary()
        # 1 absent (attestation) → PARTIAL, not HARDENING yet
        assert summary["readiness"] == "PARTIAL"
        assert summary["absent"] >= 1

    def test_all_contracts_have_ids(self):
        manifest = ProductionContractManifest()
        for contract in manifest.contracts:
            assert contract.contract_id, f"Contract missing ID: {contract}"

    def test_contract_statuses_are_known(self):
        manifest = ProductionContractManifest()
        for contract in manifest.contracts:
            assert contract.status in ContractStatus

    def test_vault_liveness_is_draft(self):
        manifest = ProductionContractManifest()
        vault_contract = next(
            c for c in manifest.contracts if c.contract_id == "AAA-GOV-VAULT-LIVENESS-v1"
        )
        assert vault_contract.status == ContractStatus.DRAFT
        assert len(vault_contract.gaps) > 0

    def test_summary_counts_are_consistent(self):
        manifest = ProductionContractManifest()
        summary = manifest.summary()
        total = summary["sealed"] + summary["partial"] + summary["draft"] + summary["absent"]
        assert total == summary["total_contracts"]
        assert total == len(manifest.contracts)


# ═══════════════════════════════════════════════════════════════════════════════
# LIVENESS CHECK RESULT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestLivenessCheckResult:
    """Test the check result model."""

    def test_default_result_is_unchecked(self):
        result = LivenessCheckResult(state=VaultLivenessState.UNKNOWN)
        assert result.chain_height == 0
        assert result.merkle_verified is False

    def test_fresh_result_has_all_fields(self):
        result = LivenessCheckResult(
            state=VaultLivenessState.FRESH,
            last_seal_age_seconds=30.0,
            chain_height=42,
            chain_gaps=0,
            merkle_verified=True,
            signature_verified=True,
            detail="all good",
        )
        assert result.state == VaultLivenessState.FRESH
        assert result.chain_height == 42
        assert result.merkle_verified is True
        assert result.signature_verified is True


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT ENTRY TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestContractEntry:
    """Test the contract entry model."""

    def test_sealed_entry_has_no_gaps(self):
        entry = ContractEntry(
            contract_id="TEST-SEALED-v1",
            status=ContractStatus.SEALED,
            description="A sealed contract",
            schema_file="some/path.py",
            test_file="tests/test_it.py",
        )
        assert entry.gaps == []

    def test_partial_entry_has_gaps(self):
        entry = ContractEntry(
            contract_id="TEST-PARTIAL-v1",
            status=ContractStatus.PARTIAL,
            description="A partial contract",
            gaps=["missing tests", "not wired to runtime"],
        )
        assert len(entry.gaps) == 2

    def test_absent_entry_has_no_files(self):
        entry = ContractEntry(
            contract_id="TEST-ABSENT-v1",
            status=ContractStatus.ABSENT,
            description="Does not exist yet",
        )
        assert entry.schema_file is None
        assert entry.test_file is None
        assert entry.enforcement_path is None
