"""
arifos_core.genius_metrics - DEPRECATED SHIM (v45Ω)

DEPRECATED: Import from arifos_core.enforcement.genius_metrics instead.

This backward compatibility shim was scheduled for removal in v43.0.
It remains for legacy code compatibility but will be removed in a future major release.

Usage:
    # OLD (deprecated)
    from arifos_core.genius_metrics import evaluate_genius_law

    # NEW (correct)
    from arifos_core.enforcement.genius_metrics import evaluate_genius_law
"""
import warnings

warnings.warn(
    "Importing from arifos_core.genius_metrics is deprecated. "
    "Use arifos_core.enforcement.genius_metrics instead. "
    "This shim will be removed in a future major release.",
    DeprecationWarning,
    stacklevel=2,
)

from arifos_core.enforcement.genius_metrics import *
