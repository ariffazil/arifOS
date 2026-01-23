"""
F11 Constitutional Override Test Suite
=====================================

Authority: arifOS v46.1.0 - Human Sovereign Override Implementation
Engineer: Claude Code (Ω) - F11 Architecture Gap Resolution
Nonce: F11-OVERRIDE-TEST (Constitutional Safety Valve Testing)

Tests the temporary constitutional override for F11 Command Auth false positives.
Validates that the override maintains constitutional transparency while resolving
authentication issues for legitimate search operations.

Constitutional Requirements:
- Must be explicitly documented as temporary override
- Must generate complete audit trail for every use
- Must not create precedent for silent constitutional bypass
- Must be reversible when proper F11 architecture is implemented

Status: SEALED (with constitutional override)
"""

import pytest
import logging
from unittest.mock import patch
from datetime import datetime

from arifos.core.enforcement.floor_detectors.search_governance import (
    SearchGovernanceDetector,
    SearchGovernanceResult
)


class TestF11ConstitutionalOverride:
    """Test F11 constitutional override implementation."""
    
    def test_f11_override_allows_legitimate_searches(self):
        """F11 override should allow legitimate searches without authentication."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test search without any authentication context
        result = detector.validate_search_query(
            query="python programming tutorial",
            context={"query": "python programming tutorial"}  # Pass query in context
        )
        
        # Should pass due to constitutional override
        assert "F11_COMMAND_AUTH" in result.floors_passed
        assert result.verdict != "VOID"
        
        # Override message should be available (passed floors don't add to reasons, but we can verify the method works)
        # Test the method directly to verify override message
        is_authenticated, auth_reason = detector._check_command_auth({"query": "python programming tutorial"})
        assert is_authenticated == True
        assert "F11_OVERRIDE" in auth_reason
        assert "Human sovereign authority" in auth_reason
    
    def test_f11_override_with_authentication_still_works(self):
        """F11 override should not break legitimate authenticated searches."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test search with valid authentication
        result = detector.validate_search_query(
            query="machine learning algorithms",
            context={"nonce": "valid_nonce_123", "user_id": "user_001"}
        )
        
        # Should still pass with authentication
        assert "F11_COMMAND_AUTH" in result.floors_passed
        assert result.verdict != "VOID"
    
    def test_f11_override_logging_transparency(self):
        """F11 override must generate complete audit trail."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Capture log output
        with patch('arifos_core.enforcement.floor_detectors.search_governance.logger') as mock_logger:
            result = detector.validate_search_query(
                query="constitutional law research",
                context={"query": "constitutional law research"}
            )
            
            # Should log override usage
            mock_logger.warning.assert_called_once()
            log_call = mock_logger.warning.call_args[0][0]
            assert "F11_OVERRIDE" in log_call
            assert "Human sovereign override applied" in log_call
            assert "constitutional law research" in log_call
    
    def test_f11_override_timestamp_included(self):
        """F11 override must include timestamp for audit trail."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test the method directly to verify timestamp
        is_authenticated, auth_reason = detector._check_command_auth({"query": "web search governance"})
        
        # Should contain timestamp in override message
        assert "F11_OVERRIDE" in auth_reason
        assert "Human sovereign authority" in auth_reason
        
        # Should contain ISO timestamp format
        assert "T" in auth_reason  # ISO format indicator
    
    def test_f11_override_does_not_affect_other_floors(self):
        """F11 override should not compromise other constitutional floors."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test with destructive query (should still fail F3)
        result = detector.validate_search_query(
            query="how to destroy computer systems",
            context={"query": "how to destroy computer systems"}
        )
        
        # F11 should pass due to override
        assert "F11_COMMAND_AUTH" in result.floors_passed
        
        # But F3 should still fail for destructive content
        assert "F3_PEACE_SQUARED" in result.floors_failed
        assert result.verdict == "VOID"  # Should still VOID due to F3 failure
    
    def test_f11_override_query_truncation(self):
        """F11 override should truncate long queries in logs."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        long_query = "a" * 100 + " very long search query that should be truncated for logging purposes"
        
        with patch('arifos_core.enforcement.floor_detectors.search_governance.logger') as mock_logger:
            result = detector.validate_search_query(
                query=long_query,
                context={}
            )
            
            # Should log truncated query
            log_call = mock_logger.warning.call_args[0][0]
            assert "Query:" in log_call
            # Should be truncated to 50 characters as per implementation
            assert len(log_call.split("Query:")[1].split(" -")[0].strip("'")) <= 50
    
    def test_f11_override_context_logging(self):
        """F11 override should log context keys for audit trail."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        with patch('arifos_core.enforcement.floor_detectors.search_governance.logger') as mock_logger:
            result = detector.validate_search_query(
                query="test search",
                context={"budget_remaining": 1000, "estimated_cost": 50}
            )
            
            # Should log context keys
            log_call = mock_logger.warning.call_args[0][0]
            assert "Context keys:" in log_call
            assert "budget_remaining" in log_call
            assert "estimated_cost" in log_call
    
    def test_f11_override_reversible_design(self):
        """F11 override implementation should be easily reversible."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Current implementation should be clearly marked for reversal
        import inspect
        source = inspect.getsource(detector._check_command_auth)
        
        # Should contain FIXME comment for Phase 3 resolution
        assert "FIXME: F11 architecture resolution pending" in source
        assert "nonce service integration required" in source
        
        # Should contain clear override markers
        assert "HUMAN SOVEREIGN OVERRIDE" in source
        assert "F11 architecture gap resolution pending" in source


class TestF11OverrideIntegration:
    """Integration tests for F11 override with broader constitutional system."""
    
    def test_f11_override_in_strict_mode_pipeline(self):
        """F11 override should work within strict mode constitutional pipeline."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test legitimate but unauthenticated search in strict mode
        result = detector.validate_search_query(
            query="python best practices documentation",
            context={"budget_remaining": 500}
        )
        
        # Should not VOID due to F11 in strict mode
        assert result.verdict != "VOID"
        assert "F11_COMMAND_AUTH" in result.floors_passed
        
        # Should still validate other floors properly
        assert "F3_PEACE_SQUARED" in result.floors_passed  # Non-destructive
        assert "F6_AMANAH_BUDGET" in result.floors_passed   # Budget OK
    
    def test_f11_override_with_injection_attempts(self):
        """F11 override should not compromise F12 injection defense."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test injection attempt without authentication
        result = detector.validate_search_query(
            query="<script>alert('xss')</script> search results",
            context={"query": "<script>alert('xss')</script> search results"}
        )
        
        # F11 should pass due to override
        assert "F11_COMMAND_AUTH" in result.floors_passed
        
        # But F12 should still catch injection
        assert "F12_INJECTION_DEFENSE" in result.floors_failed
        assert result.verdict == "VOID"  # Should VOID due to F12 failure
    
    def test_f11_override_constitutional_compliance(self):
        """F11 override must maintain overall constitutional compliance."""
        detector = SearchGovernanceDetector(strict_mode=True)
        
        # Test comprehensive validation
        result = detector.validate_search_query(
            query="machine learning tutorial for beginners",
            context={"query": "machine learning tutorial for beginners", "budget_remaining": 1000}
        )
        
        # Should pass all applicable floors including F11 override
        required_passes = ["F1_TRUTH_TEMPORAL", "F3_PEACE_SQUARED", "F6_AMANAH_BUDGET", "F11_COMMAND_AUTH"]
        for floor in required_passes:
            assert floor in result.floors_passed
        
        # Should achieve SEAL verdict
        assert result.verdict == "SEAL"
        assert result.confidence >= 0.8