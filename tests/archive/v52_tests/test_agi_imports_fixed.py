"""
Test AGI Import Resolution - v52.6.0

Verifies that all upgraded AGI modules can be imported without errors.
This test validates the fix for: ModuleNotFoundError: cannot import name 'ParsedFact' from 'codebase.agi.stages'
"""

import pytest


def test_parsedfact_import():
    """Test that ParsedFact can be imported from codebase.agi.stages"""
    from codebase.agi.stages import ParsedFact
    assert ParsedFact is not None
    print("✅ ParsedFact imported successfully from codebase.agi.stages")


def test_senseoutput_import():
    """Test that SenseOutput can be imported from codebase.agi.stages"""
    from codebase.agi.stages import SenseOutput
    assert SenseOutput is not None
    print("✅ SenseOutput imported successfully from codebase.agi.stages")


def test_all_stage_exports():
    """Test that all expected stage exports are available"""
    from codebase.agi.stages import (
        execute_stage_111, SenseOutput, ParsedFact,
        execute_stage_222, ThinkOutput,
        execute_stage_333, ReasonOutput,
        build_delta_bundle
    )
    
    # Verify all imports succeeded
    assert execute_stage_111 is not None
    assert SenseOutput is not None
    assert ParsedFact is not None
    assert execute_stage_222 is not None
    assert ThinkOutput is not None
    assert execute_stage_333 is not None
    assert ReasonOutput is not None
    assert build_delta_bundle is not None
    
    print("✅ All stage exports imported successfully")


def test_evidence_kernel_import():
    """Test that EvidenceKernel can be imported (v52.6.0 upgrade)"""
    from codebase.agi.evidence import EvidenceKernel
    assert EvidenceKernel is not None
    print("✅ EvidenceKernel imported successfully from codebase.agi.evidence")


def test_metrics_import():
    """Test that ThermodynamicDashboard can be imported (v52.6.0 upgrade)"""
    from codebase.agi.metrics import ThermodynamicDashboard
    assert ThermodynamicDashboard is not None
    print("✅ ThermodynamicDashboard imported successfully from codebase.agi.metrics")


def test_parallel_import():
    """Test that ParallelHypothesisMatrix can be imported (v52.6.0 upgrade)"""
    from codebase.agi.parallel import ParallelHypothesisMatrix
    assert ParallelHypothesisMatrix is not None
    print("✅ ParallelHypothesisMatrix imported successfully from codebase.agi.parallel")


def test_parsedfact_instantiation():
    """Test that ParsedFact can be instantiated correctly"""
    from codebase.agi.stages import ParsedFact, FactType
    
    fact = ParsedFact(
        fact_type=FactType.ASSERTION,
        content="Test fact",
        confidence=0.95,
        source_span=(0, 10)
    )
    
    assert fact.fact_type == FactType.ASSERTION
    assert fact.content == "Test fact"
    assert fact.confidence == 0.95
    assert fact.source_span == (0, 10)
    
    # Test to_dict method
    fact_dict = fact.to_dict()
    assert fact_dict["type"] == "assertion"
    assert fact_dict["content"] == "Test fact"
    assert fact_dict["confidence"] == 0.95
    
    print("✅ ParsedFact instantiation and serialization working correctly")


if __name__ == "__main__":
    # Run all tests manually if executed directly
    print("Running AGI Import Resolution Tests (v52.6.0)\n")
    
    try:
        test_parsedfact_import()
        test_senseoutput_import()
        test_all_stage_exports()
        test_evidence_kernel_import()
        test_metrics_import()
        test_parallel_import()
        test_parsedfact_instantiation()
        
        print("\n🎉 All import tests passed! v52.6.0 upgrades are properly integrated.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
