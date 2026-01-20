#!/usr/bin/env python3
"""Test script for constitutional governance system with compliant metrics"""

from arifos.core.system.apex_prime import apex_review
from arifos.core.enforcement.metrics import Metrics

def test_compliant_constitutional_governance():
    """Test constitutional governance with compliant metrics"""
    print("Testing constitutional governance with compliant metrics...")
    
    # Create compliant metrics (all above thresholds)
    compliant_metrics = Metrics(
        truth=0.995,  # Above 0.99 threshold
        delta_s=0.1,  # Positive clarity
        peace_squared=1.0,  # Perfect peace
        kappa_r=0.97,  # Above 0.95 threshold
        omega_0=0.04,  # Within [0.03, 0.05] band
        amanah=True,  # Trust enabled
        tri_witness=0.96,  # Above 0.95 threshold
        rasa=True,  # RASA compliance
        anti_hantu=True  # No soul-claims
    )
    
    print(f"Created metrics with psi: {compliant_metrics.psi}")
    
    try:
        result = apex_review(
            query="test compliant query",
            response="test compliant response", 
            lane="SOFT",  # Use SOFT lane for more forgiving truth threshold
            user_id="test_user",
            metrics=compliant_metrics
        )
        
        print(f"Verdict: {result.verdict}")
        print(f"Reason: {result.reason}")
        
        if hasattr(result, 'violated_floors'):
            print(f"Violated floors: {result.violated_floors}")
        
        if hasattr(result, 'floors') and result.floors is not None:
            print(f"Floor details available: {len(result.floors)} floors checked")
        else:
            print("Floor details: None (basic verdict)")
            
        print(f"Return value check: verdict='{result.verdict}', type={type(result.verdict)}")
        return str(result.verdict) == "SEAL"
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_compliant_constitutional_governance()
    print(f"\nCompliant test {'PASSED' if success else 'FAILED'}")