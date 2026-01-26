"""
Tests for canonical SEAL-999 implementation.
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vault import SEAL999, VaultEntry
from state import VaultConfig
from datetime import datetime


def test_vault_initialization():
    """Test SEAL-999 initializes correctly."""
    test_dir = tempfile.mkdtemp(prefix="vault999_test_")
    config = VaultConfig(base_path=test_dir)
    vault = SEAL999(config=config)
    
    assert vault.config.base_path == test_dir
    assert os.path.exists(test_dir)
    print("✓ SEAL-999 initialization test passed")


def test_seal_single_entry():
    """Test sealing a single vault entry."""
    test_dir = tempfile.mkdtemp(prefix="vault_test_")
    config = VaultConfig(base_path=test_dir)
    vault = SEAL999(config=config)
    
    entry = VaultEntry(
        entry_id="test_001",
        session_id="sess_123",
        stage=888,
        timestamp=datetime.utcnow(),
        verdict="SEAL",
        merkle_root="a1b2c3d4e5f6",
        floor_scores={"F12_Injection": 0.15, "F2_Truth": 0.99},
    )
    
    merkle_root = vault.seal_entry(entry)
    assert merkle_root is not None
    assert len(merkle_root) == 16
    print("✓ Single entry sealing test passed")


def test_assign_cooling_tier():
    """Test cooling tier assignment."""
    test_dir = tempfile.mkdtemp(prefix="vault_test_")
    config = VaultConfig(base_path=test_dir)
    vault = SEAL999(config=config)
    
    # Test SEAL with high genius → L5 eternal
    entry = VaultEntry(
        entry_id="test_002",
        session_id="sess_124",
        stage=888,
        timestamp=datetime.utcnow(),
        verdict="SEAL",
        merkle_root="b2c3d4e5f6g7",
        floor_scores={"F8_Genius": 0.90},
    )
    vault.seal_entry(entry)
    assert entry.cooling_tier == 5
    print("✓ Cooling tier assignment test passed")


def test_void_never_stored():
    """Test VOID verdicts are never stored."""
    test_dir = tempfile.mkdtemp(prefix="vault_test_")
    config = VaultConfig(base_path=test_dir)
    vault = SEAL999(config=config)
    
    entry = VaultEntry(
        entry_id="test_003",
        session_id="sess_125",
        stage=888,
        timestamp=datetime.utcnow(),
        verdict="VOID",
        merkle_root="c3d4e5f6g7h8",
        floor_scores={"F12_Injection": 0.90},
    )
    vault.seal_entry(entry)
    assert entry.cooling_tier == -1
    print("✓ VOID never stored test passed")


if __name__ == "__main__":
    print("Running SEAL-999 canonical tests...")
    
    test_vault_initialization()
    test_seal_single_entry()
    test_assign_cooling_tier()
    test_void_never_stored()
    
    print("\n✅ All SEAL-999 tests passed!")
