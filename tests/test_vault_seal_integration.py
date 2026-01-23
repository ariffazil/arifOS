"""
Test: Vault Seal Integration

Verifies that vault_999 seals work as cryptographic keys for vault access.

DITEMPA BUKAN DIBERI - Forged v50.1
"""

import pytest
from pathlib import Path

from arifos.core.memory.vault.vault_seal_accessor import (
    VaultSealAccessor,
    VaultAccessError,
    verify_vault_integrity
)
from arifos.core.memory.vault.ccc_constitutional_memory import (
    get_constitutional_memory,
    reset_constitutional_memory
)


class TestVaultSealIntegration:
    """Test vault seal validation and CCC memory integration"""

    def test_vault_seal_loads_successfully(self):
        """Vault should load seal and validate it"""
        vault = VaultSealAccessor("vault_999")

        assert vault.is_sealed(), "Vault should be sealed"
        assert vault.get_seal_version() == "50.0.0", "Should load v50 seal"

    def test_vault_seal_contains_floor_validation(self):
        """Seal should contain constitutional floor validation results"""
        vault = VaultSealAccessor("vault_999")

        # Check that seal contains floor validations
        f2_status = vault.get_floor_status("F2_truth")
        assert f2_status is not None, "Seal should contain F2 truth status"
        assert f2_status["pass"] == True, "F2 should have passed in seal"

    def test_ccc_memory_references_vault_seal(self):
        """CCC memory should get thresholds from vault seal"""
        reset_constitutional_memory()  # Fresh instance
        ccc = get_constitutional_memory()

        # CCC should reference seal version
        assert ccc.get_seal_version() == "50.0.0"

        # CCC should provide floor status from seal
        f2_status = ccc.get_floor_status("F2_truth")
        assert f2_status["pass"] == True
        assert "seal_version" in f2_status

    def test_ccc_memory_provides_sealed_constants(self):
        """CCC should provide all sealed constitutional constants"""
        reset_constitutional_memory()
        ccc = get_constitutional_memory()

        constants = ccc.get_sealed_constants()

        assert constants["version"] == "50.0.0"
        assert constants["status"] == "SEALED"
        assert "floors" in constants
        assert "zkpc" in constants

    def test_ccc_validates_actions(self):
        """CCC should validate actions against sealed constitution"""
        reset_constitutional_memory()
        ccc = get_constitutional_memory()

        # Action should pass if seal valid
        context = {"test": "action"}
        is_valid = ccc.validate_action("test_action", context)

        assert is_valid == True, "Action should pass with valid seal"

    def test_ccc_logs_constitutional_decisions(self):
        """CCC should log decisions to vault ledger"""
        reset_constitutional_memory()
        ccc = get_constitutional_memory()

        # Perform action that gets logged
        ccc.validate_action("test_log_action", {"test": "logging"})

        # Check decision history
        history = ccc.get_decision_history(limit=10)
        assert len(history) > 0, "Should have logged decision"

        last_decision = history[0]
        assert last_decision["action"] == "test_log_action"
        assert last_decision["seal_version"] == "50.0.0"

    def test_verify_vault_integrity_convenience_function(self):
        """Convenience function should verify vault integrity"""
        is_valid = verify_vault_integrity()
        assert is_valid == True, "Vault should have valid integrity"

    def test_vault_seal_accessor_creates_access_log(self):
        """Vault should log all access attempts"""
        vault = VaultSealAccessor("vault_999")

        # Read memory (should create access log)
        memory = vault.read_memory("AAA_MEMORY")

        # Check access log exists
        access_log = Path("vault_999/CCC_CONSTITUTIONAL/access_log.jsonl")
        assert access_log.exists(), "Access log should be created"

    def test_seal_validation_fails_gracefully_with_missing_seal(self, tmp_path):
        """Should raise VaultAccessError if seal missing"""
        fake_vault = tmp_path / "fake_vault"
        fake_vault.mkdir()

        with pytest.raises(VaultAccessError) as exc_info:
            VaultSealAccessor(str(fake_vault))

        assert "No seal found" in str(exc_info.value)
