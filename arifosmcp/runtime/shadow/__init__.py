"""
Shadow Mode — A/B Comparison for V2 Validation

Executes v1 and v2 backends in parallel, compares results.
"""

from .comparator import ShadowComparator, run_shadow_comparison

__all__ = ["ShadowComparator", "run_shadow_comparison"]
