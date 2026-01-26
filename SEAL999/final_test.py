"""
Final test - SEAL999 verification
"""
import sys
sys.path.insert(0, "C:\\Users\\User\\arifOS")

from SEAL999 import SEAL999, VaultEntry, VaultConfig
from datetime import datetime

print("Testing SEAL999...")

vault = SEAL999()
print(f"Created: {type(vault).__name__}")

entry = VaultEntry(
    entry_id="test_final",
    session_id="test_sess",
    stage=888,
    timestamp=datetime.utcnow(),
    verdict="SEAL",
    merkle_root="test",
    floor_scores={}
)
print(f"Entry created: {entry.entry_id}")

print("\n[SUCCESS] SEAL999 working!")
