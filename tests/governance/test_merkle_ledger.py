"""
Tests for v45 Merkle Ledger
Verify chain integrity and tampering detection.
"""
import pytest
from arifos_core.governance.merkle_ledger import MerkleLedger

def test_ledger_append_consistency():
    """Verify appending updates root deterministically."""
    ledger = MerkleLedger()
    initial_root = ledger.get_root()
    
    # Entry 1
    id1 = ledger.append("hash_payload_1")
    root1 = ledger.get_root()
    assert root1 != initial_root
    
    # Entry 2
    id2 = ledger.append("hash_payload_2")
    root2 = ledger.get_root()
    assert root2 != root1
    
    # Verify IDs are distinct
    assert id1 != id2
    
def test_integrity_check_pass():
    """Verify valid chain passes integrity check."""
    ledger = MerkleLedger()
    ledger.append("p1")
    ledger.append("p2")
    ledger.append("p3")
    
    assert ledger.verify_integrity() is True

def test_tamper_detection_chain_break():
    """Verify modifying a previous link fails integrity check."""
    ledger = MerkleLedger()
    ledger.append("p1")
    ledger.append("p2")
    
    # Tamper: Change the previous_hash link of the second entry
    ledger.entries[1].previous_hash = "TAMPERED_HASH"
    
    assert ledger.verify_integrity() is False

def test_tamper_detection_root_mismatch():
    """Verify modifying a stored root snapshot fails integrity check."""
    ledger = MerkleLedger()
    ledger.append("p1")
    
    # Tamper: Change the stored root snapshot
    ledger.entries[0].merkle_root_snapshot = "FAKE_ROOT"
    
    assert ledger.verify_integrity() is False
