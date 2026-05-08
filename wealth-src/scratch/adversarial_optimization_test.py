import sys
import os
import json
import hashlib

# Setup path for WEALTH
wealth_dir = r"c:\ariffazil\arifOS\WEALTH"
sys.path.insert(0, wealth_dir)

try:
    from server import wealth_score_kernel, HarnessEngine, LAST_RECEIPT_HASH, create_envelope
    
    print("--- 🜂 EXECUTING ADVERSARIAL OPTIMIZATION TEST 🜂 ---")
    lineage = HarnessEngine.get_lineage_hash()
    print(f"Harness Lineage Hash: {lineage}")
    doc_hash = HarnessEngine.get_doctrine_hash()
    print(f"Doctrine Hash:        {doc_hash}")
    
    print(f"\n[INIT] Initial Parent Hash: {LAST_RECEIPT_HASH}")
    
    # 1. Systemic Stress Accumulation (Cumulative Rule)
    # We trigger:
    # - Epistemic Stress (0.8 via SYSTEMIC_CORRELATION_RISK)
    # - Entropy Stress (0.8 via HIGH_ENTROPY_SIGNAL)
    # - Reality Stress (1.0 via STALE_DATA) -> This snaps Reality
    # Cumulative stress should be ~2.6
    
    print("\n[STEP 1] Simulating high cumulative stress (Threshold Gapping Attempt)...")
    result = create_envelope(
        tool="wealth_score_kernel",
        dimension="Constitutional",
        primary={"npv": 1000000, "maruahScore": 0.61},
        flags=["SYSTEMIC_CORRELATION_RISK", "HIGH_ENTROPY_SIGNAL", "STALE_DATA"], 
        scale_mode="civilization"
    )
    
    stress = result.get("harness_audit", {}).get("systemic_stress", 0.0)
    verdict = result['verdict']
    alloc = result['allocation_signal']
    
    print(f"\n[STEP 2] Resulting Allocation Envelope:")
    print(f"  - Verdict: {verdict}")
    print(f"  - Allocation Signal: {alloc}")
    print(f"  - Systemic Stress: {stress}")
    
    audit = result.get("harness_audit", {})
    violations = audit.get("violations", [])
    print(f"\n[STEP 3] Harness Violations: {violations}")
    
    # Logic: stress 2.6 > 2.0 FAIL -> VOID
    if verdict == "VOID" and "SYSTEMIC_INSTABILITY_FAILURE" in violations:
        print("\n✅ TEST PASSED: No APPROVE verdict possible under cumulative stress.")
    else:
        print("\n❌ TEST FAILED: System returned APPROVE or missed systemic instability.")

    # 2. Identity Chaining
    print(f"\n[STEP 4] Verifying Identity Chaining...")
    first_receipt = result["receipt_hash"]
    # We call from within the script, simulating a chain
    result2 = create_envelope(
        tool="wealth_record_transaction",
        dimension="Identity",
        primary={"tx_id": "001"},
        parent_hash=first_receipt,
        scale_mode="civilization"
    )
    print(f"  - Result 2 Verdict: {result2['verdict']}")
    print(f"  - Result 2 Violation: {result2.get('harness_audit', {}).get('violations')}")
    
    # 3. Chain Breakage
    print("\n[STEP 5] Verifying Chain Breakage...")
    result3 = create_envelope(
        tool="wealth_record_transaction",
        dimension="Identity",
        primary={"tx_id": "hack_attempt"},
        parent_hash="INVALID_CHAIN_LINK_404",
        scale_mode="civilization"
    )
    print(f"  - Result 3 Verdict: {result3['verdict']}")
    audit3 = result3.get("harness_audit", {})
    if "IDENTITY_CHAIN_VIOLATION" in audit3.get("violations", []):
        print("✅ CHAIN BREAKAGE DETECTED: Illegal bypass attempt blocked.")
    else:
        print("❌ CHAIN BREAKAGE NOT DETECTED.")

    # 4. Civilization Thresholds
    print("\n[STEP 6] Verifying Civilization Thresholds...")
    result_civ = create_envelope(
        tool="wealth_civilization_stewardship",
        dimension="Civilization",
        primary={"carbon_intensity": 0.05, "collapse_risk": 0.1, "sustainable_growth_rate": 0.02},
        scale_mode="civilization"
    )
    print(f"  - Carbon Intensity: 0.05 (Floor: 0.04)")
    print(f"  - Result Verdict: {result_civ['verdict']}")
    if "CIVILIZATION_HARNESS_FAILURE" in result_civ.get("harness_audit", {}).get("violations", []):
        print("✅ CIVILIZATION FLOOR ENFORCED: Carbon budget exceeded.")
    else:
        print("❌ CIVILIZATION FLOOR NOT ENFORCED.")

except Exception as e:
    print(f"\n❌ FATAL ERROR DURING TEST: {str(e)}")
    import traceback
    traceback.print_exc()
