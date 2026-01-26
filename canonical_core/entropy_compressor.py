"""
Entropy Compressor - Minimal Implementation for ASI Room
Based on: 000_THEORY/000_LAW.md (ΔS ≤ 0)
"""

from typing import Dict, Any, Tuple
import json
import hashlib


class EntropyCompressor:
    """Compress constitutional bundles, extract entropy (ΔS ≥ 0)."""
    
    def __init__(self, baseline_entropy: float = 1.0):
        self.baseline = baseline_entropy
        self.total_compressed = 0.0
    
    def compress(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], float]:
        """
        Compress bundle and return entropy delta.
        ΔS must be ≥ 0 (entropy extracted from system)
        """
        # Serialize deterministically
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        
        # Remove redundant fields
        compressed = self._remove_redundancy(data)
        
        # Calculate entropy delta
        original_size = len(serialized)
        compressed_size = len(json.dumps(compressed, sort_keys=True, separators=(',', ':')))
        entropy_delta = (original_size - compressed_size) / original_size
        
        # Enforce ΔS ≥ 0
        if entropy_delta < 0:
            raise ValueError(f"ΔS violation: {entropy_delta} (must be ≥ 0)")
        
        self.total_compressed += entropy_delta
        
        return compressed, entropy_delta
    
    def _remove_redundancy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove redundant fields from bundle."""
        compressed = {}
        
        for key, value in data.items():
            # Skip temporary fields
            if key.startswith("_tmp_"):
                continue
            
            # Skip empty collections
            if isinstance(value, (list, dict)) and not value:
                continue
            
            # Recursively compress nested structures
            if isinstance(value, dict):
                compressed_value = self._remove_redundancy(value)
                if compressed_value:
                    compressed[key] = compressed_value
            elif isinstance(value, list):
                compressed[key] = [item for item in value if item]
            else:
                compressed[key] = value
        
        return compressed
    
    def conflict_measure(self, bundle_a: Dict[str, Any], bundle_b: Dict[str, Any]) -> float:
        """Measure orthogonality between two bundles (0.0=aligned, 1.0=orthogonal)."""
        hash_a = hashlib.sha256(json.dumps(bundle_a, sort_keys=True).encode()).hexdigest()
        hash_b = hashlib.sha256(json.dumps(bundle_b, sort_keys=True).encode()).hexdigest()
        diff_count = sum(1 for a, b in zip(hash_a, hash_b) if a != b)
        return diff_count / len(hash_a)


# Global compressor instance
COMPRESSOR = EntropyCompressor()
