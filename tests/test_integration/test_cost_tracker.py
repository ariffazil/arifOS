"""
Constitutional Budget Enforcement Tests
X7K9F24 - F1 (Amanah) and F6 (Amanah) Compliance Verification

Tests the critical budget logic enforcement to ensure constitutional compliance.
Status: SEALED
Nonce: X7K9F24
"""

import pytest
from arifos.integration.cost_tracker import CostTracker


class TestBudgetEnforcementConstitutional:
    """Test constitutional budget enforcement with F1 and F6 compliance."""
    
    def test_budget_enforcement_constitutional_within_budget(self):
        """Test that operations within budget return ALLOW (F6 Amanah compliance)."""
        tracker = CostTracker(initial_budget=1000.0)
        
        # Test case: cost within budget
        result = tracker.enforce_budget_limit(current_cost=500.0, budget=1000.0)
        
        assert result == "ALLOW", f"Expected ALLOW for within-budget operation, got {result}"
        print("✅ F6 Amanah: Within budget mandate - ALLOW verdict correct")
    
    def test_budget_enforcement_constitutional_exceeds_budget(self):
        """Test that operations exceeding budget return VOID (F1 Amanah compliance)."""
        tracker = CostTracker(initial_budget=1000.0)
        
        # Test case: cost exceeds budget
        result = tracker.enforce_budget_limit(current_cost=1500.0, budget=1000.0)
        
        assert result == "VOID", f"Expected VOID for over-budget operation, got {result}"
        print("✅ F1 Amanah: Reversible veto for overspending - VOID verdict correct")
    
    def test_budget_enforcement_constitutional_exact_budget(self):
        """Test that operations at exact budget return ALLOW (boundary condition)."""
        tracker = CostTracker(initial_budget=1000.0)
        
        # Test case: cost exactly at budget
        result = tracker.enforce_budget_limit(current_cost=1000.0, budget=1000.0)
        
        assert result == "ALLOW", f"Expected ALLOW for exact-budget operation, got {result}"
        print("✅ F6 Amanah: Exact budget boundary - ALLOW verdict correct")
    
    def test_budget_enforcement_constitutional_zero_budget(self):
        """Test that operations with zero budget return VOID for any cost."""
        tracker = CostTracker(initial_budget=0.0)
        
        # Test case: zero budget with any cost
        result = tracker.enforce_budget_limit(current_cost=1.0, budget=0.0)
        
        assert result == "VOID", f"Expected VOID for zero-budget operation, got {result}"
        print("✅ F1 Amanah: Zero budget protection - VOID verdict correct")
    
    def test_budget_enforcement_constitutional_negative_cost(self):
        """Test that negative costs return ALLOW (special case handling)."""
        tracker = CostTracker(initial_budget=1000.0)
        
        # Test case: negative cost (refund/correction)
        result = tracker.enforce_budget_limit(current_cost=-100.0, budget=1000.0)
        
        assert result == "ALLOW", f"Expected ALLOW for negative cost operation, got {result}"
        print("✅ F6 Amanah: Negative cost handling - ALLOW verdict correct")
    
    def test_budget_enforcement_constitutional_reversibility_principle(self):
        """Test that VOID verdicts are reversible (F1 Amanah principle)."""
        tracker = CostTracker(initial_budget=1000.0)
        
        # First call: exceed budget (should return VOID)
        result1 = tracker.enforce_budget_limit(current_cost=1500.0, budget=1000.0)
        assert result1 == "VOID", "First call should return VOID"
        
        # Second call: within budget (should return ALLOW)
        result2 = tracker.enforce_budget_limit(current_cost=500.0, budget=1000.0)
        assert result2 == "ALLOW", "Second call should return ALLOW"
        
        # Verify the tracker state is unchanged (reversible)
        assert tracker.current_budget == 1000.0, "Tracker state should be unchanged"
        print("✅ F1 Amanah: Reversibility principle verified - state preserved")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])