#!/usr/bin/env python3
"""
Quick test to verify ATLAS-333 lane classification.

Per Phase 2.1 Definition of Done:
- "Hello" should classify as SOCIAL
- "Molotov" should classify as CRISIS
"""

from arifos_core.agi.atlas import ATLAS

def test_atlas_classification():
    """Test ATLAS lane classification for Definition of Done."""

    # Test 1: "Hello" should be SOCIAL
    print("Test 1: 'Hello' classification")
    gpv_hello = ATLAS.map("Hello")
    print(f"  Lane: {gpv_hello.lane}")
    print(f"  Truth demand: {gpv_hello.truth_demand}")
    print(f"  Care demand: {gpv_hello.care_demand}")
    print(f"  Risk level: {gpv_hello.risk_level}")
    assert gpv_hello.lane == "SOCIAL", f"Expected SOCIAL, got {gpv_hello.lane}"
    print("  [PASS]\n")

    # Test 2: "Molotov" should be CRISIS
    print("Test 2: 'Molotov' classification")
    gpv_molotov = ATLAS.map("Molotov")
    print(f"  Lane: {gpv_molotov.lane}")
    print(f"  Truth demand: {gpv_molotov.truth_demand}")
    print(f"  Care demand: {gpv_molotov.care_demand}")
    print(f"  Risk level: {gpv_molotov.risk_level}")
    assert gpv_molotov.lane == "CRISIS", f"Expected CRISIS, got {gpv_molotov.lane}"
    print("  [PASS]\n")

    # Additional tests
    print("Test 3: Code query (should be FACTUAL)")
    gpv_code = ATLAS.map("Write a Python function to calculate fibonacci")
    print(f"  Lane: {gpv_code.lane}")
    assert gpv_code.lane == "FACTUAL", f"Expected FACTUAL, got {gpv_code.lane}"
    print("  [PASS]\n")

    print("Test 4: Generic query (should be CARE)")
    gpv_generic = ATLAS.map("Can you help me understand this concept?")
    print(f"  Lane: {gpv_generic.lane}")
    assert gpv_generic.lane == "CARE", f"Expected CARE, got {gpv_generic.lane}"
    print("  [PASS]\n")

    print("=" * 60)
    print("[PASS] All ATLAS classification tests PASSED!")
    print("Definition of Done #2: Verified")
    print("=" * 60)

if __name__ == "__main__":
    test_atlas_classification()
