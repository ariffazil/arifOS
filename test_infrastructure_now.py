#!/usr/bin/env python
"""Quick infrastructure test - run immediately to verify Phase 1 setup."""

import sys
import os
sys.path.insert(0, "C:\\Users\\User\\arifOS")

try:
    # Test 1: Can import modules
    from canonical_core import EntropyCompressor, BundleStore
    print("[OK] Imports successful")
    
    # Test 2: EntropyCompressor works
    compressor = EntropyCompressor()
    test_data = {"field": "value", "_tmp": "remove", "empty": {}}
    compressed, delta_s = compressor.compress(test_data)
    assert "_tmp" not in compressed
    assert delta_s >= 0
    print(f"[OK] EntropyCompressor works (ΔS: {delta_s:.3f})")
    
    # Test 3: BundleStore works
    store = BundleStore("test_session")
    store.store("bundle_111", {"test": "data"})
    retrieved = store.get("bundle_111")
    assert retrieved["test"] == "data"
    print("[OK] BundleStore works")
    
    # Test 4: Bundle isolation
    store2 = BundleStore("session_2")
    store2.store("bundle_111", {"test": "data2"})
    assert store.get("bundle_111")["test"] == "data"
    assert store2.get("bundle_111")["test"] == "data2"
    print("[OK] Bundle isolation works")
    
    print("\n✅ ALL TESTS PASSED - Phase 1 ready for Phase 2")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
