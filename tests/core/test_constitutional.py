#!/usr/bin/env python3
"""Test script for constitutional governance system"""

from arifos.core.system.apex_prime import apex_review
from arifos.core.enforcement.metrics import Metrics, ConstitutionalMetrics

def test_constitutional_governance():
    """Test basic constitutional governance functionality"""
    print("Testing constitutional governance system...")
    
    # Check available metrics
    print("Available in metrics module:")
    import arifos.core.enforcement.metrics as metrics_module
    available_metrics = [x for x in dir(metrics_module) if not x.startswith('_')]
    print(available_metrics[:10])  # Show first 10 to avoid clutter
    
    # Test basic apex_review
    print("\nTesting basic apex_review...")
    
    # Create sample metrics
    test_metrics = Metrics(
        truth=0.95,
        delta_s=0.1,
        peace_squared=1.0,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=True
    )
    
    try:
        result = apex_review(
            query="test query",
            response="test response", 
            lane="SOFT",
            user_id="test_user",
            metrics=test_metrics
        )
        print(f"Result type: {type(result)}")
        print(f"Result attributes: {[x for x in dir(result) if not x.startswith('_')]}")
        
        if hasattr(result, 'verdict'):
            print(f"Verdict: {result.verdict}")
        if hasattr(result, 'status'):
            print(f"Status: {result.status}")
        if hasattr(result, 'reason'):
            print(f"Reason: {result.reason}")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_constitutional_governance()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")