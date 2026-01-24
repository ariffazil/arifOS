"""
tests.eval — DEPRECATED: Constitutional evaluation consolidated

STATUS: ENTROPY CLEANUP COMPLETE - Functions moved to appropriate locations

PREVIOUSLY: Test integration for arifos_eval package
NOW: Legacy compatibility layer - will be removed in v48

CONSOLIDATION MAP:
- Core physics functions → arifos.core.enforcement.genius_metrics
- Constitutional benchmarks → tests.constitutional.test_01_core_F1_to_F13
- APEX measurements → arifos.core.system.apex_prime (runtime)

For constitutional testing, use:
    from tests.constitutional.test_01_core_F1_to_F13 import (
        f6_empathy_split_benchmark,
        f9_anti_hantu_benchmark, 
        meta_select_consistency_benchmark
    )

See: arifos.core.enforcement.genius_metrics for core physics functions
"""

# Legacy compatibility - import from consolidated locations
import warnings

warnings.warn(
    "tests.eval is deprecated. Constitutional evaluation functions "
    "have been consolidated. See tests.constitutional for benchmarks "
    "and arifos.core.enforcement.genius_metrics for core physics.",
    DeprecationWarning,
    stacklevel=2
)

# Minimal compatibility re-exports (will be removed in v48)
try:
    # Try to import from consolidated locations for temporary compatibility
    from arifos.core.enforcement.genius_metrics import (
        measure_genius_physics,
        measure_dark_cleverness_physics, 
        compute_vitality_physics
    )
except ImportError:
    # Fallback - these will fail gracefully when arifos.eval is removed
    measure_genius_physics = None
    measure_dark_cleverness_physics = None
    compute_vitality_physics = None

__version__ = "45.0.0"  # Final version before removal
__deprecated__ = True
