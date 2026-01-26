"""
Demo script for SEAL-999 canonical vault.
Shows basic functionality without pytest.
"""

import sys
import os

# Add canonical vault to path
vault_path = os.path.dirname(os.path.abspath(__file__))
if vault_path not in sys.path:
    sys.path.insert(0, vault_path)

from datetime import datetime
from vault import SEAL999, VaultEntry
from state import VaultConfig
import tempfile


def test_basic_flow():
    """Test basic storage and sealing flow."""
    print("Creating test vault...")
    test_dir = tempfile.mkdtemp(prefix="vault_demo_")
    config = VaultConfig(base_path=test_dir)
    vault = SEAL999(config=config)
    
    print("Creating vault entry...")
    entry = VaultEntry(
        entry_id="demo_001",
        session_id="demo_session_123",
        stage=888,
        timestamp=datetime.utcnow(),
        verdict="SEAL",
        merkle_root="test_root_123456",
        floor_scores={"F12_Injection": 0.15},
    )
    
    print("Sealing entry...")
    merkle_root = vault.seal_entry(entry)
    print(f"Merkle root: {merkle_root}")
    print(f"Cooling tier: {entry.cooling_tier}")
    
    print("\n[OK] SEAL-999 canonical demo completed successfully!")
    print(f"Test data stored in: {test_dir}")


if __name__ == "__main__":
    test_basic_flow()
