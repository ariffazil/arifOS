"""
arifos_core.metrics - BACKWARD COMPATIBILITY SHIM (v42)

This file provides backward compatibility for imports from:
    from arifos_core.metrics import ...

The actual implementation has moved to:
    arifos_core/enforcement/metrics.py

This shim will be removed in v43.0.
"""

import warnings

# Emit deprecation warning on import (can be disabled in production)
# warnings.warn(
#     "arifos_core.metrics is deprecated. Use 'from arifos_core.enforcement.metrics import ...' instead. "
#     "This shim will be removed in v43.0.",
#     DeprecationWarning,
#     stacklevel=2
# )

# Re-export everything from the new location
from arifos_core.enforcement.metrics import *
from arifos_core.enforcement.metrics import (
    # Dataclasses
    Metrics,
    FloorsVerdict,
    ConstitutionalMetrics,
    # Threshold constants
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    KAPPA_R_THRESHOLD,
    OMEGA_0_MIN,
    OMEGA_0_MAX,
    TRI_WITNESS_THRESHOLD,
    PSI_THRESHOLD,
    # Floor check functions
    check_truth,
    check_delta_s,
    check_peace_squared,
    check_kappa_r,
    check_omega_band,
    check_tri_witness,
    check_psi,
    check_anti_hantu,
    # v38.1 Gandhi Patch
    calculate_peace_squared_gandhi,
    # Anti-Hantu helpers
    ANTI_HANTU_FORBIDDEN,
    ANTI_HANTU_ALLOWED,
    # v38 spec loader (private but needed by pipeline.py)
    _load_floors_spec_v38,
)

# v42: Backward compat aliases for renamed functions
check_truth_floor = check_truth
