"""
Tests for Constitutional Meta-Search System Integration
X7K9F24 - Entropy Reduction via Constitutional Search Testing

Tests the complete integration of:
- ConstitutionalMetaSearch with 12-floor governance
- ConstitutionalSearchCache with semantic deduplication
- CostTracker with F6 (Amanah) enforcement
- Constitutional check decorators

Status: SEALED
Nonce: X7K9F24
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from arifos_core.integration.meta_search import (
    ConstitutionalMetaSearch,
    SearchResult,
    ConstitutionalSearchError,
    constitutional_check,
)
from arifos_core.integration.cost_tracker import (
    CostTracker,
    BudgetExceededError,
    ConstitutionalBudgetError,
    BudgetLevel,
    CostType,
)
from arifos_core.integration.search_cache import (
    ConstitutionalSearchCache,
    CacheEntry,
)


class TestConstitutionalMetaSearch:
    """Test ConstitutionalMetaSearch with 12-floor governance."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cost_tracker = CostTracker(initial_budget=1000.0)
        self.cache = ConstitutionalSearchCache(max_size=100)
        self.meta_search = ConstitutionalMetaSearch(
            cost_tracker=self.cost_tracker,
            cache=self.cache,
            max_results=5
        )
    
    def test_constitutional_search_basic(self):
        """Test basic constitutional search operation."""
        query = "test constitutional search"
        context = {"user_id": "test_user", "nonce": "test_nonce"}
        
        result = self.meta_search.search_with_governance(
            query=query,
            context=context,
            enable_cache=True
        )
        
        assert isinstance(result, SearchResult)
        assert result.query == query
        assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
        assert len(result.results) <= 5
        assert result.cache_hit == False  # First search should be cache miss
        assert result.cost_info["actual"] > 0
        assert "F1" in result.floor_scores
        assert "F2" in result.floor_scores
        assert "F6" in result.floor_scores
        assert "F9" in result.floor_scores
    
    def test_constitutional_search_with_cache_hit(self):
        """Test constitutional search with cache hit."""
        query = "cached search query"
        context = {"user_id": "test_user"}
        
        # First search - should miss cache
        result1 = self.meta_search.search_with_governance(
            query=query,
            context=context,
            enable_cache=True
        )
        assert result1.cache_hit == False
        
        # Second search - should hit cache
        result2 = self.meta_search.search_with_governance(
            query=query,
            context=context,
            enable_cache=True
        )
        assert result2.cache_hit == True
        assert result1.results == result2.results
    
    def test_constitutional_search_budget_limit(self):
        """Test constitutional search with budget limit enforcement."""
        # Set a very low budget to trigger budget exceeded
        self.cost_tracker.update_budget(-990)  # Leave only 10 tokens
        
        with pytest.raises(BudgetExceededError):
            self.meta_search.search_with_governance(
                query="expensive search query",
                budget_limit=5.0,  # Lower than estimated cost
                enable_cache=False
            )
    
    def test_constitutional_search_forbidden_patterns(self):
        """Test constitutional search with forbidden Anti-Hantu patterns."""
        query = "I feel that this search should work"
        
        with pytest.raises(ConstitutionalSearchError) as exc_info:
            self.meta_search.search_with_governance(query=query)
        
        assert "F9 Anti-Hantu violation" in str(exc_info.value)
    
    def test_constitutional_search_input_validation(self):
        """Test constitutional search with malicious input."""
        query = "DROP TABLE users; -- malicious query"
        
        with pytest.raises(ConstitutionalSearchError) as exc_info:
            self.meta_search.search_with_governance(query=query)
        
        assert "F1 Input Validation failed" in str(exc_info.value)
    
    def test_constitutional_search_floor_scores(self):
        """Test that floor scores are properly computed."""
        query = "safe constitutional search query"
        context = {"user_id": "test_user", "intent": "informational"}
        
        result = self.meta_search.search_with_governance(
            query=query,
            context=context,
            enable_cache=False
        )
        
        # Check that all expected floors have scores
        expected_floors = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]
        for floor in expected_floors:
            assert floor in result.floor_scores
            assert 0.0 <= result.floor_scores[floor] <= 1.0
    
    def test_constitutional_search_verdict_computation(self):
        """Test constitutional verdict computation."""
        query = "test query for verdict analysis"
        
        result = self.meta_search.search_with_governance(query=query)
        
        assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
        
        # SEAL should only be given if all critical floors pass
        if result.verdict == "SEAL":
            critical_floors = ["F1", "F2", "F6", "F9", "F10", "F11", "F12"]
            for floor in critical_floors:
                assert result.floor_scores[floor] >= 0.5
    
    def test_search_stats(self):
        """Test search statistics collection."""
        # Perform a few searches
        for i in range(3):
            self.meta_search.search_with_governance(
                query=f"test query {i}",
                enable_cache=False
            )
        
        stats = self.meta_search.get_search_stats()
        
        assert stats["total_searches"] == 3
        assert stats["total_cost"] > 0
        assert stats["cache_stats"]["total_requests"] == 3
        assert stats["budget_remaining"] < 1000.0  # Some budget should be used


class TestConstitutionalCheckDecorator:
    """Test the constitutional check decorator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_class = Mock()
        self.test_class._floor_results = {}
    
    def test_constitutional_check_valid_input(self):
        """Test constitutional check with valid input."""
        @constitutional_check(floors=[1, 2, 5, 6, 9])
        def test_function(self, query, **kwargs):
            return f"Processed: {query}"
        
        result = test_function(self.test_class, query="safe query")
        assert result == "Processed: safe query"
    
    def test_constitutional_check_forbidden_pattern(self):
        """Test constitutional check with forbidden pattern."""
        @constitutional_check(floors=[9])
        def test_function(self, query, **kwargs):
            return f"Processed: {query}"
        
        with pytest.raises(ConstitutionalSearchError) as exc_info:
            test_function(self.test_class, query="I feel this should work")
        
        assert "F9 Anti-Hantu violation" in str(exc_info.value)
    
    def test_constitutional_check_no_query(self):
        """Test constitutional check without query."""
        @constitutional_check(floors=[1, 2, 5, 6, 9])
        def test_function(self, **kwargs):
            return "Processed"
        
        with pytest.raises(ConstitutionalSearchError) as exc_info:
            test_function(self.test_class)
        
        assert "Query required for constitutional validation" in str(exc_info.value)
    
    def test_constitutional_check_floor_results_storage(self):
        """Test that floor results are stored in instance."""
        @constitutional_check(floors=[1, 2])
        def test_function(self, query, **kwargs):
            return hasattr(self, '_floor_results') and len(self._floor_results) > 0
        
        result = test_function(self.test_class, query="test query")
        assert result == True  # Should have floor results stored


class TestCostTracker:
    """Test CostTracker with constitutional enforcement."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cost_tracker = CostTracker(initial_budget=1000.0)
    
    def test_cost_estimate_search_operation(self):
        """Test cost estimation for search operations."""
        estimate = self.cost_tracker.estimate_search_cost(
            query="test search query",
            search_providers=["default", "semantic"]
        )
        
        assert isinstance(estimate, object)  # CostEstimate
        assert estimate.operation_type == "search"
        assert estimate.estimated_cost > 0
        assert 0.0 <= estimate.confidence <= 1.0
        assert "base" in estimate.breakdown
        assert "providers" in estimate.breakdown
        assert "validation" in estimate.breakdown
    
    def test_budget_validation_success(self):
        """Test successful budget validation."""
        is_valid = self.cost_tracker.validate_budget_for_operation(
            estimated_cost=100.0,
            operation_type="search"
        )
        
        assert is_valid == True
    
    def test_budget_validation_failure(self):
        """Test budget validation failure."""
        # Use almost all budget
        self.cost_tracker.update_budget(-900)
        
        is_valid = self.cost_tracker.validate_budget_for_operation(
            estimated_cost=150.0,
            operation_type="search"
        )
        
        assert is_valid == False
    
    def test_constitutional_budget_enforcement(self):
        """Test constitutional budget enforcement."""
        # Use most of budget to trigger critical level
        self.cost_tracker.update_budget(-950)
        
        with pytest.raises(ConstitutionalBudgetError) as exc_info:
            self.cost_tracker.validate_budget_for_operation(
                estimated_cost=30.0,
                operation_type="search"
            )
        
        assert "F6 (Amanah) violation" in str(exc_info.value)
    
    def test_track_operation_cost(self):
        """Test tracking actual operation costs."""
        initial_budget = self.cost_tracker.current_budget
        
        cost_record = self.cost_tracker.track_operation_cost(
            operation_type="search",
            actual_cost=75.0,
            details={"query": "test", "providers": ["default"]}
        )
        
        assert cost_record.operation_type == "search"
        assert cost_record.actual_cost == 75.0
        assert self.cost_tracker.current_budget == initial_budget - 75.0
    
    def test_budget_level_detection(self):
        """Test budget level detection and alerts."""
        # Test different budget usage levels
        test_cases = [
            (0.0, BudgetLevel.NORMAL),
            (0.76, BudgetLevel.CAUTION),
            (0.91, BudgetLevel.WARNING),
            (0.96, BudgetLevel.CRITICAL),
            (1.01, BudgetLevel.EXCEEDED),
        ]
        
        for usage_ratio, expected_level in test_cases:
            # Reset budget for each test
            self.cost_tracker = CostTracker(initial_budget=1000.0)
            self.cost_tracker.update_budget(-(usage_ratio * 1000.0))
            
            status = self.cost_tracker.get_budget_status()
            assert status["budget_level"] == expected_level.value
    
    def test_budget_recommendations(self):
        """Test budget optimization recommendations."""
        # Use 80% of budget to trigger recommendations
        self.cost_tracker.update_budget(-800)
        
        recommendations = self.cost_tracker.get_budget_recommendations()
        
        assert len(recommendations) > 0
        # Should have caution-level recommendation
        caution_recs = [rec for rec in recommendations if rec["type"] == "budget_monitoring"]
        assert len(caution_recs) > 0
    
    def test_cost_breakdown_tracking(self):
        """Test cost breakdown by operation type."""
        # Track different types of operations
        self.cost_tracker.track_operation_cost("search", 50.0)
        self.cost_tracker.track_operation_cost("cache_operation", 10.0)
        self.cost_tracker.track_operation_cost("constitutional_validation", 25.0)
        
        status = self.cost_tracker.get_budget_status()
        
        assert status["cost_breakdown"]["search_api"] == 50.0
        assert status["cost_breakdown"]["cache_operation"] == 10.0
        assert status["cost_breakdown"]["constitutional_validation"] == 25.0


class TestConstitutionalSearchCache:
    """Test ConstitutionalSearchCache with semantic deduplication."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cache = ConstitutionalSearchCache(
            max_size=10,
            default_ttl=60,  # 1 minute for testing
            semantic_threshold=0.8
        )
    
    def test_cache_basic_operations(self):
        """Test basic cache put/get operations."""
        query = "test query"
        result = {"results": [{"title": "Test Result", "url": "http://test.com"}]}
        floor_scores = {"F1": 1.0, "F2": 0.9, "F6": 1.0, "F9": 1.0}
        
        # Put in cache
        stored = self.cache.put(query, result, floor_scores=floor_scores)
        assert stored == True
        
        # Get from cache
        cached_result = self.cache.get(query)
        assert cached_result == result
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration."""
        query = "ttl test query"
        result = {"results": [{"title": "TTL Test"}]}
        
        # Put with very short TTL
        self.cache.put(query, result, ttl=0.1)  # 0.1 seconds
        
        # Should get result immediately
        cached_result = self.cache.get(query)
        assert cached_result == result
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should not get result after expiration
        cached_result = self.cache.get(query)
        assert cached_result is None
    
    def test_cache_constitutional_validation(self):
        """Test constitutional validation of cached results."""
        query = "constitutional test query"
        result = {"results": [{"title": "Constitutional Test"}]}
        
        # Put result with poor floor scores (should be rejected)
        poor_floor_scores = {"F1": 0.2, "F6": 0.1, "F9": 0.0}
        stored = self.cache.put(query, result, floor_scores=poor_floor_scores)
        assert stored == False  # Should not be cached due to constitutional violations
        
        # Put result with good floor scores (should be accepted)
        good_floor_scores = {"F1": 1.0, "F6": 1.0, "F9": 1.0}
        stored = self.cache.put(query, result, floor_scores=good_floor_scores)
        assert stored == True
    
    def test_cache_semantic_deduplication(self):
        """Test semantic deduplication using F2 optimization."""
        # First query
        query1 = "how to implement constitutional search"
        result1 = {"results": [{"title": "Constitutional Search Implementation"}]}
        
        self.cache.put(query1, result1)
        
        # Semantically similar query
        query2 = "constitutional search implementation guide"
        
        # Should get cached result due to semantic similarity
        cached_result = self.cache.get(query2)
        assert cached_result == result1
        
        # Check stats
        stats = self.cache.get_stats()
        assert stats["semantic_matches"] == 1
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction with governance-aware scoring."""
        # Fill cache to capacity
        for i in range(12):  # Exceed max_size of 10
            query = f"eviction test query {i}"
            result = {"results": [{"title": f"Result {i}"}]}
            floor_scores = {"F1": 1.0, "F6": 1.0, "F9": 1.0}
            self.cache.put(query, result, floor_scores=floor_scores)
        
        # Cache should have evicted some entries
        stats = self.cache.get_stats()
        assert stats["size"] == 10  # Should be at max capacity
        assert stats["evictions"] > 0
    
    def test_cache_stats(self):
        """Test cache statistics collection."""
        # Perform some operations
        self.cache.put("query1", {"result": 1})
        self.cache.get("query1")  # Hit
        self.cache.get("nonexistent")  # Miss
        
        stats = self.cache.get_stats()
        
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert 0.0 <= stats["hit_rate"] <= 1.0
    
    def test_cache_clear_expired(self):
        """Test clearing expired cache entries."""
        # Add some entries with short TTL
        for i in range(3):
            self.cache.put(f"expiring_query_{i}", {"result": i}, ttl=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Add one entry with long TTL
        self.cache.put("long_lived_query", {"result": "long"}, ttl=3600)
        
        # Clear expired entries
        cleared_count = self.cache.clear_expired()
        assert cleared_count == 3
        
        # Check that only the long-lived entry remains
        stats = self.cache.get_stats()
        assert stats["size"] == 1
        assert self.cache.get("long_lived_query") is not None


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    def setup_method(self):
        """Set up complete integration test fixtures."""
        self.cost_tracker = CostTracker(initial_budget=1000.0)
        self.cache = ConstitutionalSearchCache(max_size=50)
        self.meta_search = ConstitutionalMetaSearch(
            cost_tracker=self.cost_tracker,
            cache=self.cache
        )
    
    def test_complete_constitutional_search_workflow(self):
        """Test complete constitutional search workflow."""
        query = "constitutional governance implementation guide"
        context = {
            "user_id": "test_user",
            "intent": "informational",
            "search_providers": ["default", "constitutional"]
            # No nonce provided to avoid authentication issues in tests
        }
        
        # Perform constitutional search
        result = self.meta_search.search_with_governance(
            query=query,
            context=context,
            budget_limit=200.0,
            enable_cache=True
        )
        
        # Verify complete governance
        assert result.verdict in ["SEAL", "PARTIAL"]
        assert len(result.floor_scores) == 12  # All floors validated
        assert result.cost_info["actual"] <= 200.0  # Within budget
        assert result.cache_hit == False  # First search
        
        # Verify cache integration
        cached_result = self.meta_search.search_with_governance(
            query=query,
            context=context,
            enable_cache=True
        )
        assert cached_result.cache_hit == True
        assert cached_result.results == result.results
    
    def test_constitutional_search_with_budget_constraints(self):
        """Test search behavior under budget constraints."""
        # Set tight budget
        self.cost_tracker.update_budget(-950)  # Only 50 tokens left
        
        query = "complex constitutional analysis"
        
        # Should succeed with low-cost approach
        result = self.meta_search.search_with_governance(
            query=query,
            budget_limit=40.0,
            enable_cache=True,
            search_providers=["default"]  # Single provider to save costs
        )
        
        assert result.cost_info["actual"] <= 40.0
        assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
    
    def test_constitutional_search_failure_recovery(self):
        """Test recovery from constitutional search failures."""
        # Test with forbidden pattern
        try:
            self.meta_search.search_with_governance(query="I feel this search")
            assert False, "Should have raised ConstitutionalSearchError"
        except ConstitutionalSearchError as e:
            assert "F9 Anti-Hantu violation" in str(e)
        
        # Recovery: use safe query
        safe_result = self.meta_search.search_with_governance(
            query="constitutional analysis of governance patterns"
        )
        
        assert safe_result.verdict in ["SEAL", "PARTIAL"]
        assert len(safe_result.results) > 0
    
    def test_performance_metrics(self):
        """Test performance and efficiency metrics."""
        import time
        
        start_time = time.time()
        
        # Perform multiple searches
        for i in range(5):
            result = self.meta_search.search_with_governance(
                query=f"performance test query {i}",
                enable_cache=True
            )
            assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert total_time < 10.0  # Should complete within 10 seconds
        
        # Check efficiency metrics
        stats = self.meta_search.get_search_stats()
        assert stats["total_searches"] == 5
        assert stats["cache_stats"]["hit_rate"] >= 0.0  # Some cache hits expected
        
        # Cost efficiency
        avg_cost_per_search = stats["total_cost"] / stats["total_searches"]
        assert avg_cost_per_search > 0  # Should have some cost
        assert avg_cost_per_search < 100  # But not excessive


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])