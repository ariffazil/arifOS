"""
arifOS v49 Canonical Package
Single Body Runtime

NOTE: During single-body consolidation, heavy imports (core, protocol) are wrapped
in try/except to allow lightweight subpackages (orchestrator, utils) to work
independently without requiring full spec file infrastructure.
"""

# Core enforcement and system components (requires spec files)
try:
    from .core import *
    _CORE_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    # Spec files not available - orchestrator can still work independently
    import warnings
    warnings.warn(
        f"arifOS core unavailable (likely missing spec files): {e}. "
        "Orchestrator subpackage will work independently.",
        ImportWarning,
        stacklevel=2
    )
    _CORE_AVAILABLE = False

# Protocol components
try:
    from .protocol import *
    _PROTOCOL_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    import warnings
    warnings.warn(
        f"arifOS protocol unavailable: {e}",
        ImportWarning,
        stacklevel=2
    )
    _PROTOCOL_AVAILABLE = False
