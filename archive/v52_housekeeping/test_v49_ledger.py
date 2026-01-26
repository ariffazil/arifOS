#!/usr/bin/env python3
"""
Test script for v49 Constitutional Ledger Infrastructure

Usage:
    python scripts/test_v49_ledger.py

Tests:
- Ledger initialization
- Sample entry writing
- Hash-chain verification
- Head state tracking

Version: v49.0.2
Authority: 888 Judge (APEX)
"""

import sys
from pathlib import Path

# Add arifos to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos.ledger.v49_config import (
    init_v49_ledger,
    write_constitutional_entry,
    V49_LEDGER_PATH,
    V49_HASH_CHAIN_PATH,
    V49_HEAD_STATE_PATH
)
from arifos.core.memory.ledger.cooling_ledger import verify_chain


def test_ledger_initialization():
    """Test 1: Verify ledger infrastructure initializes correctly"""
    print("=" * 70)
    print("TEST 1: Ledger Initialization")
    print("=" * 70)

    try:
        ledger = init_v49_ledger()
        print(f"[OK] Ledger initialized successfully")
        print(f"   Path: {V49_LEDGER_PATH}")
        print(f"   Exists: {V49_LEDGER_PATH.exists()}")
        print(f"   Head state: {V49_HEAD_STATE_PATH.exists()}")
        print(f"   Hash chain: {V49_HASH_CHAIN_PATH.exists()}")

        if V49_HASH_CHAIN_PATH.exists():
            genesis_hash = V49_HASH_CHAIN_PATH.read_text()
            print(f"   Genesis hash: {genesis_hash}")

        return True
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_write_sample_entry():
    """Test 2: Write a sample SEAL verdict to ledger"""
    print("\n" + "=" * 70)
    print("TEST 2: Write Sample Constitutional Entry")
    print("=" * 70)

    floor_scores = {
        "F1_amanah": True,
        "F2_truth": 0.99,
        "F3_triwitness": 0.97,
        "F4_clarity": -0.18,
        "F5_peace": 1.0,
        "F6_empathy": 0.96,
        "F7_humility": 0.04,
        "F8_genius": 0.85,
        "F9_cdark": 0.15,
        "F10_ontology": True,
        "F11_authority": True,
        "F12_injection": 0.98,
        "F13_curiosity": 0.87
    }

    trinity_indices = {
        "vitality_psi": 1.2,
        "genius_g": 0.82,
        "dark_cleverness_c": 0.12
    }

    try:
        success, entry_hash, error = write_constitutional_entry(
            verdict="SEAL",
            floor_scores=floor_scores,
            trinity_indices=trinity_indices,
            session_id="TEST_20260119_001",
            cooling_tier=0
        )

        if success:
            print(f"[OK] Entry written successfully")
            print(f"   Entry hash: {entry_hash}")
            print(f"   Ledger size: {V49_LEDGER_PATH.stat().st_size} bytes")

            # Read the entry
            with open(V49_LEDGER_PATH, 'r') as f:
                lines = f.readlines()
                print(f"   Total entries: {len(lines)}")

            return True
        else:
            print(f"[FAIL] Write failed: {error}")
            return False

    except Exception as e:
        print(f"[FAIL] Write failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hash_chain_verification():
    """Test 3: Verify hash-chain integrity"""
    print("\n" + "=" * 70)
    print("TEST 3: Hash-Chain Verification")
    print("=" * 70)

    try:
        valid, message = verify_chain(V49_LEDGER_PATH)

        if valid:
            print(f"[OK] Hash-chain verified: {message}")
            return True
        else:
            print(f"[FAIL] Hash-chain broken: {message}")
            return False

    except Exception as e:
        print(f"[FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_head_state_tracking():
    """Test 4: Verify head state tracking"""
    print("\n" + "=" * 70)
    print("TEST 4: Head State Tracking")
    print("=" * 70)

    try:
        ledger = init_v49_ledger()
        head_state = ledger.get_head_state()

        print(f"[OK] Head state loaded:")
        print(f"   Entry count: {head_state.entry_count}")
        print(f"   Last hash: {head_state.last_entry_hash[:16] if head_state.last_entry_hash else 'None'}...")
        print(f"   Last timestamp: {head_state.last_timestamp}")
        print(f"   Epoch: {head_state.epoch}")

        # Quick verification
        valid, message = ledger.verify_chain_quick()
        if valid:
            print(f"[OK] Quick verify passed: {message}")
            return True
        else:
            print(f"[FAIL] Quick verify failed: {message}")
            return False

    except Exception as e:
        print(f"[FAIL] Head state tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_write_multiple_entries():
    """Test 5: Write multiple entries and verify chain continuity"""
    print("\n" + "=" * 70)
    print("TEST 5: Multiple Entries & Chain Continuity")
    print("=" * 70)

    floor_scores = {
        "F1_amanah": True,
        "F2_truth": 0.99,
        "F3_triwitness": 0.96,
        "F4_clarity": -0.12,
        "F5_peace": 1.0,
        "F6_empathy": 0.95,
        "F7_humility": 0.04,
        "F8_genius": 0.82,
        "F9_cdark": 0.18,
        "F10_ontology": True,
        "F11_authority": True,
        "F12_injection": 0.97,
        "F13_curiosity": 0.88
    }

    verdicts = ["SEAL", "PARTIAL", "SEAL"]
    cooling_tiers = [0, 1, 0]

    try:
        hashes = []
        for i, (verdict, tier) in enumerate(zip(verdicts, cooling_tiers), start=2):
            success, entry_hash, error = write_constitutional_entry(
                verdict=verdict,
                floor_scores=floor_scores,
                session_id=f"TEST_20260119_{i:03d}",
                cooling_tier=tier
            )

            if success:
                hashes.append(entry_hash)
                print(f"[OK] Entry {i} written: {verdict} (tier {tier}) -> {entry_hash[:16]}...")
            else:
                print(f"[FAIL] Entry {i} failed: {error}")
                return False

        # Verify chain after multiple writes
        valid, message = verify_chain(V49_LEDGER_PATH)
        if valid:
            print(f"\n[OK] Chain still valid after {len(hashes)} additional entries")
            print(f"   {message}")
            return True
        else:
            print(f"\n[FAIL] Chain broken after multiple writes: {message}")
            return False

    except Exception as e:
        print(f"[FAIL] Multiple entry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  arifOS v49 Constitutional Ledger Infrastructure Test")
    print("  DITEMPA BUKAN DIBERI")
    print("=" * 70)

    tests = [
        ("Initialization", test_ledger_initialization),
        ("Write Sample Entry", test_write_sample_entry),
        ("Hash-Chain Verification", test_hash_chain_verification),
        ("Head State Tracking", test_head_state_tracking),
        ("Multiple Entries", test_write_multiple_entries),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status:10s} {name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Ledger infrastructure is operational.")
        print("\nv49 Constitutional Ledger Status: OPERATIONAL")
        print(f"Ledger location: {V49_LEDGER_PATH}")
        print(f"Entries logged: {len(open(V49_LEDGER_PATH).readlines()) if V49_LEDGER_PATH.exists() else 0}")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
