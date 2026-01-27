"""
Codebase System Module - Core constitutional system components.

Components:
- apex_prime: APEX Prime governance engine
- constitution: Constitutional physics implementation
- immutable_ledger: Hash-chained audit trail
- pipeline: Processing pipeline
- metrics_utils: Prometheus metrics helpers
"""

from .metrics_utils import safe_counter, safe_histogram, safe_gauge

__all__ = [
    "safe_counter",
    "safe_histogram",
    "safe_gauge",
]
