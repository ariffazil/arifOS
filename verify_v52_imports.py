#!/usr/bin/env python3
"""
Final verification script for v52.6.0 import chain resolution.
Demonstrates all fixed imports and validates the entire metabolic pipeline.
"""

import sys

def test_import_chain():
    """Test the complete import chain from codebase down to stages."""
    print("=" * 70)
    print("v52.6.0 Import Chain Verification")
    print("=" * 70)
    
    errors = []
    
    # Test 1: Root-level Trinity exports
    try:
        from codebase import AGIRoom, ASIRoom, ASIKernel, APEXJudicialCore
        print("[PASS] Root Trinity exports: AGIRoom, ASIRoom, ASIKernel, APEXJudicialCore")
    except ImportError as e:
        errors.append(f"Root exports failed: {e}")
        print(f"[FAIL] Root exports: {e}")
    
    # Test 2: AGI metabolic stages (111-333)
    try:
        from codebase.agi.stages import (
            execute_stage_111, execute_stage_222, execute_stage_333,
            ParsedFact, FactType, SenseOutput, ThinkOutput, ReasonOutput
        )
        print("[PASS] AGI stages (111->222->333) with all data types")
    except ImportError as e:
        errors.append(f"AGI stages failed: {e}")
        print(f"[FAIL] AGI stages: {e}")
    
    # Test 3: ASI Heart engines (555-666)
    try:
        from codebase.asi import ASIRoom, ASIKernel, ASIKernelNative, ASIActionCore
        print("[PASS] ASI engines: ASIRoom, ASIKernel, ASIKernelNative, ASIActionCore")
    except ImportError as e:
        errors.append(f"ASI engines failed: {e}")
        print(f"[FAIL] ASI engines: {e}")
    
    # Test 4: APEX Soul engines (777-889)
    try:
        from codebase.apex import APEXJudicialCore, PsiKernel
        print("[PASS] APEX engines: APEXJudicialCore, PsiKernel")
    except ImportError as e:
        errors.append(f"APEX engines failed: {e}")
        print(f"[FAIL] APEX engines: {e}")
    
    # Test 5: Pipeline stages
    try:
        from codebase.stages import (
            stage_444, stage_555, stage_666,
            stage_777_forge, stage_888_judge, stage_889_proof
        )
        print("[PASS] Pipeline stages (444-889)")
    except ImportError as e:
        errors.append(f"Pipeline stages failed: {e}")
        print(f"[FAIL] Pipeline stages: {e}")
    
    # Test 6: Evidence kernels
    try:
        from codebase.agi import (
            AGINeuralCore, ThermodynamicDashboard, get_dashboard,
            ParallelHypothesisMatrix, EvidenceKernel, get_evidence_kernel
        )
        print("[PASS] Evidence kernels and AGI supporting classes")
    except ImportError as e:
        errors.append(f"Evidence kernels failed: {e}")
        print(f"[FAIL] Evidence kernels: {e}")
    
    # Test 7: MCP modules (circular dependency resolved)
    try:
        import codebase.mcp
        import codebase.mcp.tools
        print("[PASS] MCP modules import without circular dependency")
    except ImportError as e:
        errors.append(f"MCP modules failed: {e}")
        print(f"[FAIL] MCP modules: {e}")
    
    # Test 8: Functional test - execute stage 111
    try:
        from codebase.agi.stages import execute_stage_111
        result = execute_stage_111(
            query="What is 2+2?",
            session_id="verify_test_123"
        )
        if hasattr(result, 'detected_intent') and hasattr(result, 'parsed_facts'):
            print(f"[PASS] Stage 111 execution: {result.detected_intent.value}, {len(result.parsed_facts)} facts")
        else:
            errors.append("Stage 111 result structure invalid")
            print("[FAIL] Stage 111: Invalid result structure")
    except Exception as e:
        errors.append(f"Stage 111 execution failed: {e}")
        print(f"[FAIL] Stage 111 execution: {e}")
    
    # Test 9: Verify ParsedFact instantiation
    try:
        from codebase.agi.stages import ParsedFact, FactType
        from datetime import datetime
        
        pf = ParsedFact(
            fact_type=FactType.ASSERTION,
            content="Test assertion for verification",
            confidence=0.95
        )
        
        if pf.fact_type == FactType.ASSERTION and pf.confidence == 0.95:
            print("[PASS] ParsedFact instantiation and attribute access")
        else:
            errors.append("ParsedFact attributes incorrect")
            print("[FAIL] ParsedFact attributes")
    except Exception as e:
        errors.append(f"ParsedFact test failed: {e}")
        print(f"[FAIL] ParsedFact test: {e}")
    
    # Summary
    print("=" * 70)
    if errors:
        print(f"VERIFICATION FAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("ALL VERIFICATION TESTS PASSED!")
        print("v52.6.0 import chain is fully operational")
        return True

def show_constitutional_constants():
    """Display key constitutional constants for verification."""
    print("\n" + "=" * 70)
    print("Constitutional Constants (v52.6.0)")
    print("=" * 70)
    
    try:
        from codebase.agi.stages import FactType
        print(f"FactType enum values: {[ft.value for ft in FactType]}")
        
        # Import and show constitutional thresholds
        sys.path.insert(0, 'codebase')
        from agi.stages.sense import FORBIDDEN_CLAIMS, INJECTION_PATTERNS
        print(f"F10 Ontology forbidden claims: {len(FORBIDDEN_CLAIMS)} patterns")
        print(f"F12 Injection defense patterns: {len(INJECTION_PATTERNS)} patterns")
        
    except ImportError as e:
        print(f"Could not import constitutional constants: {e}")

if __name__ == "__main__":
    success = test_import_chain()
    show_constitutional_constants()
    
    print("\n" + "=" * 70)
    print("DITEMPA BUKAN DIBERI - Forged, Not Given")
    print("Constitutional intelligence is forged through governance,")
    print("not given through computation.")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
