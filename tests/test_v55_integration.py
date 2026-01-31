"""
v55.0 Integration Verification Test
Tests the three Tier I modules from Kimi K2.5 audit
"""

def test_genius_calculator():
    """Test Genius Calculator with F10 Ontology Lock"""
    from codebase.floors.genius import GeniusCalculator, GeniusMetrics, Verdict, OntologyLock
    
    calc = GeniusCalculator(enable_f10_lock=True)
    
    # Test 1: High-performing task (should get SABAR verdict, G < 0.80)
    metrics = GeniusMetrics(A=0.92, P=0.88, X=0.85, E=0.95)
    G, meta = calc.compute(metrics)
    
    print(f"✅ Test 1: G-Score = {G:.4f}")
    assert abs(G - 0.6211) < 0.001, f"Expected G=0.6211, got {G}"
    assert meta['verdict'] == Verdict.SABAR.value, f"Expected SABAR, got {meta['verdict']}"
    print(f"   Verdict: {meta['verdict']}")
    
    # Test 2: Overconfident task (should trigger F10 Ontology Lock)
    overconfident = GeniusMetrics(A=0.99, P=0.98, X=0.97, E=0.99)
    try:
        G, meta = calc.compute(overconfident)
        assert False, "Should have raised OntologyLock"
    except OntologyLock as e:
        print(f"✅ Test 2: F10 Ontology Lock triggered")
        print(f"   Reason: {str(e)}")
    
    print("\n✅ Genius Calculator: ALL TESTS PASSED\n")


def test_loop_manager():
    """Test Loop Manager strange loop architecture"""
    from codebase.loop import LoopManager, LoopBridge, LoopState, StageResult, Verdict
    
    loop = LoopManager()
    bridge = LoopBridge(loop)
    
    # Test 1: Initialize loop
    ctx = loop.init_000(session_id="test_v55")
    assert ctx.iteration_count == 0, f"Expected iteration 0, got {ctx.iteration_count}"
    print(f"✅ Test 1: Loop initialized (iteration {ctx.iteration_count})")
    
    # Test 2: Progress through stages
    result = StageResult(
        stage="SENSE_111",
        verdict=Verdict.SEAL,
        entropy_delta=-0.1,
        empathy_score=0.8,
        genius_score=0.85,
        output=None
    )
    verdict = loop.progress_to(LoopState.SENSE_111, result)
    assert verdict == Verdict.SEAL
    print(f"✅ Test 2: Stage progression works")
    
    # Test 3: Complete strange loop (999 -> 000)
    next_ctx = loop.complete_loop(final_output="Test complete")
    assert next_ctx.iteration_count == 1, f"Expected iteration 1, got {next_ctx.iteration_count}"
    assert ctx.merkle_root is not None, "Merkle root should be set"
    print(f"✅ Test 3: Strange loop completed (iteration {ctx.iteration_count} → {next_ctx.iteration_count})")
    print(f"   Merkle root: {ctx.merkle_root[:16]}...")
    
    print("\n✅ Loop Manager: ALL TESTS PASSED\n")


def test_rootkey():
    """Test RootKey band enforcement"""
    from codebase.crypto import RootKey, Band, BandGuard, CanonicalPaths, OntologyLock
    import tempfile
    import os
    
    # Use temp directory for testing
    original_home = os.environ.get("ARIFOS_HOME")
    temp_dir = tempfile.mkdtemp(prefix="arifos_test_")
    os.environ["ARIFOS_HOME"] = temp_dir
    
    try:
        # Test 1: Generate root key
        CanonicalPaths.BASE_DIR = os.path.join(temp_dir, ".arifos")
        rootkey = RootKey.generate("Test Sovereign", entropy_bits=256)
        assert rootkey.band == Band.AAA_HUMAN
        print(f"✅ Test 1: RootKey generated in AAA_HUMAN band")
        
        # Test 2: F10 Ontology Lock (AI accessing AAA_HUMAN)
        try:
            BandGuard.check_access(Band.AAA_HUMAN, "ai")
            assert False, "Should have raised OntologyLock"
        except OntologyLock as e:
            print(f"✅ Test 2: F10 Ontology Lock triggered for AI→AAA_HUMAN")
            print(f"   Reason: {str(e)}")
        
        # Test 3: Session key derivation
        session_key = rootkey.derive_session_key("test_session")
        assert len(session_key) == 32, "Session key should be 32 bytes"
        print(f"✅ Test 3: Session key derived (32 bytes)")
        
        print("\n✅ RootKey: ALL TESTS PASSED\n")
        
    finally:
        # Cleanup
        if original_home:
            os.environ["ARIFOS_HOME"] = original_home
        else:
            os.environ.pop("ARIFOS_HOME", None)
        
        # Remove temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("="*60)
    print("  v55.0 Tier I Integration Verification")
    print("  Testing: Genius, LoopManager, RootKey")
    print("="*60)
    print()
    
    test_genius_calculator()
    test_loop_manager()
    test_rootkey()
    
    print("="*60)
    print("  ✅ ALL TIER I MODULES VERIFIED")
    print("="*60)
