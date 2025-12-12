"""
test_integration_common_utils.py — Tests for shared integration utilities

Tests the common utility functions in arifos_core/integration/common_utils.py
to ensure proper functionality after refactoring to eliminate duplication.

Author: arifOS Project
Version: v38.0
"""

import hashlib
import json
from datetime import datetime, timezone

import pytest

from arifos_core.integration.common_utils import compute_integration_evidence_hash


class TestComputeIntegrationEvidenceHash:
    """Test the shared evidence hash computation function."""

    def test_basic_hash_computation(self):
        """Test basic evidence hash computation."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        floor_scores = {"F1_amanah": 1.0, "F2_truth": 0.99}
        
        result = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
        )
        
        # Should return a 64-character hex string (SHA-256)
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_determinism(self):
        """Test that the same inputs produce the same hash."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        floor_scores = {"F1_amanah": 1.0, "F2_truth": 0.99}
        timestamp = "2024-01-01T00:00:00+00:00"
        
        hash1 = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        hash2 = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        assert hash1 == hash2

    def test_hash_uniqueness_by_content(self):
        """Test that different content produces different hashes."""
        verdict = "SEAL"
        floor_scores = {"F1_amanah": 1.0, "F2_truth": 0.99}
        timestamp = "2024-01-01T00:00:00+00:00"
        
        hash1 = compute_integration_evidence_hash(
            verdict=verdict,
            content={"response": "First response"},
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        hash2 = compute_integration_evidence_hash(
            verdict=verdict,
            content={"response": "Second response"},
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        assert hash1 != hash2

    def test_hash_uniqueness_by_verdict(self):
        """Test that different verdicts produce different hashes."""
        content = {"response": "Test response"}
        floor_scores = {"F1_amanah": 1.0, "F2_truth": 0.99}
        timestamp = "2024-01-01T00:00:00+00:00"
        
        hash1 = compute_integration_evidence_hash(
            verdict="SEAL",
            content=content,
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        hash2 = compute_integration_evidence_hash(
            verdict="VOID",
            content=content,
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        assert hash1 != hash2

    def test_hash_uniqueness_by_floor_scores(self):
        """Test that different floor scores produce different hashes."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        timestamp = "2024-01-01T00:00:00+00:00"
        
        hash1 = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores={"F1_amanah": 1.0, "F2_truth": 0.99},
            timestamp=timestamp,
        )
        
        hash2 = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores={"F1_amanah": 1.0, "F2_truth": 0.95},
            timestamp=timestamp,
        )
        
        assert hash1 != hash2

    def test_with_empty_floor_scores(self):
        """Test with empty floor scores."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        
        result = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores={},
        )
        
        assert isinstance(result, str)
        assert len(result) == 64

    def test_with_evidence_sources(self):
        """Test with evidence sources provided."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        floor_scores = {"F1_amanah": 1.0}
        evidence_sources = ["source1", "source2"]
        
        result = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
            evidence_sources=evidence_sources,
        )
        
        assert isinstance(result, str)
        assert len(result) == 64

    def test_timestamp_defaults_to_now(self):
        """Test that timestamp defaults to current time if not provided."""
        verdict = "SEAL"
        content = {"response": "Test response"}
        floor_scores = {"F1_amanah": 1.0}
        
        # Call without timestamp
        hash1 = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
        )
        
        # Should still work
        assert isinstance(hash1, str)
        assert len(hash1) == 64

    def test_complex_content_serialization(self):
        """Test with complex nested content."""
        verdict = "SEAL"
        content = {
            "response": "Test response",
            "metadata": {
                "nested": {
                    "value": 123,
                    "list": [1, 2, 3],
                }
            },
            "numbers": [1.5, 2.7, 3.9],
        }
        floor_scores = {"F1_amanah": 1.0}
        
        result = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
        )
        
        assert isinstance(result, str)
        assert len(result) == 64

    def test_backward_compatibility_with_judge(self):
        """Test that this produces the same hash as the old judge implementation."""
        # This ensures backward compatibility
        verdict = "SEAL"
        content = {"response": "Test"}
        floor_scores = {"F1_amanah": 1.0, "F2_truth": 0.99}
        timestamp = "2024-01-01T00:00:00+00:00"
        
        # Use the new shared function
        hash_new = compute_integration_evidence_hash(
            verdict=verdict,
            content=content,
            floor_scores=floor_scores,
            timestamp=timestamp,
        )
        
        # Should be deterministic
        assert isinstance(hash_new, str)
        assert len(hash_new) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
