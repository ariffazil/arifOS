import sys
import os
import json

# Setup path for WEALTH (use index 0 to override root server.py)
wealth_dir = r"c:\ariffazil\arifOS\WEALTH"
if wealth_dir in sys.path:
    sys.path.remove(wealth_dir)
sys.path.insert(0, wealth_dir)

try:
    from server import wealth_score_kernel, HarnessEngine
    
    print("--- 🜂 EXECUTING FINAL HARNESS TEST SCENARIO 🜂 ---")
    lineage = HarnessEngine.get_lineage_hash()
    print(f"Harness Lineage Hash: {lineage}")
    
    # User Scenario Parameters:
    # - High EMV (implied by high entropy dS/signals)
    # - Weak burial evidence (implied by low integrity/flags)
    # - maruah_score = 0.55 (Below 0.6 floor)
    # - Reversible = False (Irreversible action)
    
    params = {
        "d_s": 0.45,            # High entropy signal
        "peace2": 0.3,          # Low peace
        "maruah_score": 0.55,    # BELOW FLOOR (0.6) -> CONSTITUTIONAL SNAP
        "base_rate": 0.12,
        "irreversible": True,   # Irreversible action
        "scale_mode": "civilization"
    }
    
    print("\n[STEP 1] Invoking wealth_score_kernel with adversarial parameters:")
    for k, v in params.items():
        print(f"  - {k}: {v}")
        
    # Execute
    envelope = wealth_score_kernel(**params)
    
    print("\n[STEP 2] Resulting Allocation Envelope:")
    print(f"  - Verdict: {envelope['verdict']}")
    print(f"  - Allocation Signal: {envelope['allocation_signal']}")
    print(f"  - Engine Status: {envelope['engine_status']}")
    
    audit = envelope.get("harness_audit", {})
    print(f"\n[STEP 3] Harness Audit Breakdown:")
    print(f"  - Audit Verdict: {audit.get('verdict')}")
    print(f"  - Violations: {audit.get('violations')}")
    print(f"  - Captured Hash: {audit.get('harness_lineage_hash')}")
    
    # Verification Logic
    verdict = envelope['verdict']
    violations = audit.get("violations", [])
    
    if verdict == "VOID" and "CONSTITUTIONAL_HARNESS_FAILURE" in violations:
        print("\n✅ TEST PASSED: Harness Engine intercepted the rogue proposal and issued a VOID verdict.")
    else:
        print("\n❌ TEST FAILED: Harness Engine did not block the proposal correctly.")
        if verdict != "VOID":
            print(f"   Reason: Verdict was {verdict}, expected VOID.")
        if "CONSTITUTIONAL_HARNESS_FAILURE" not in violations:
            print(f"   Reason: Constitutional harness did not report as SNAPPED. Violations: {violations}")

except Exception as e:
    print(f"\n❌ FATAL ERROR DURING TEST: {str(e)}")
    import traceback
    traceback.print_exc()
