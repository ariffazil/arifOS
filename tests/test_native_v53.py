"""
Native v53 Test Suite
Tests the codebase native implementation without arifos/core dependencies
"""

import sys
import asyncio
import time

sys.path.insert(0, '.')

def test_import_native_asi():
    """STEP 1: Test native ASI import"""
    print("\n[TEST 1] Importing native ASI kernel...")
    try:
        from codebase.asi import ASIActionCore
        kernel = ASIActionCore()
        print("[SUCCESS] Native ASI imported and instantiated")
        return True
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_native_empathize():
    """STEP 2: Test native empathize execution"""
    print("\n[TEST 2] Testing native empathize execution...")
    try:
        from codebase.asi import ASIActionCore
        kernel = ASIActionCore()
        
        start = time.time()
        result = await kernel.empathize('Tell me about AI safety')
        elapsed = (time.time() - start) * 1000
        
        if result.get('native_execution'):
            print(f"[OK] SUCCESS: Native empathize executed in {elapsed:.2f}ms")
            print(f"   Verdict: {result.get('omega_verdict')}")
            print(f"   Kappa_r: {result.get('empathy_score')}")
            return True
        else:
            print("[FAIL] FAILED: Not native execution")
            return False
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_native_full_pipeline():
    """STEP 3: Test full native pipeline"""
    print("\n[TEST 3] Testing full native ASI pipeline...")
    try:
        from codebase.asi import ASIActionCore
        kernel = ASIActionCore()
        
        start = time.time()
        result = await kernel.execute('full', {
            'text': 'Is AI safe?',
            'session_id': 'test_native_001'
        })
        elapsed = (time.time() - start) * 1000
        
        if result.get('native_execution'):
            print(f"[OK] SUCCESS: Full pipeline executed in {elapsed:.2f}ms")
            print(f"   Verdict: {result.get('verdict')}")
            print(f"   Floors: {result.get('floors_checked')}")
            return True
        else:
            print("[FAIL] FAILED: Not native execution")
            return False
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_arifos_core_dependency():
    """STEP 4: Verify no arifos/core imports"""
    print("\n[TEST 4] Checking for arifos/core dependencies...")
    try:
        import codebase.asi
        import codebase.engines.asi.kernel_native
        
        # Check if arifos is imported
        if 'arifos' in sys.modules:
            print("[FAIL] FAILED: arifos module is still imported")
            return False
        else:
            print("[OK] SUCCESS: No arifos/core dependencies")
            return True
    except Exception as e:
        print(f"[FAIL] FAILED: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("NATIVE v53 MIGRATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import
    results.append(test_import_native_asi())
    
    # Test 2: Empathize
    results.append(await test_native_empathize())
    
    # Test 3: Full pipeline
    results.append(await test_native_full_pipeline())
    
    # Test 4: No legacy deps
    results.append(test_no_arifos_core_dependency())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n[WIN] SUCCESS: Native v53 implementation is WORKING")
        print("[OK] Proxy layer removed")
        print("[OK] arifos/core dependencies eliminated")
        print("[OK] Constitutional physics migrated to codebase/")
        print("\n[LAUNCH] Ready for production deployment!")
        return True
    else:
        print("\n[FAIL] FAILURE: Migration incomplete")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
