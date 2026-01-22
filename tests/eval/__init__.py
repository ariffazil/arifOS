"""
tests.eval — Test integration for arifOS evaluation harness

CANONICAL SOURCE: arifos_eval/ (top-level package)
This module re-exports from arifos_eval for backward compatibility and test integration.

For new code, import directly from arifos_eval:
    from arifos_eval.apex import ApexMeasurement  # Correct
    from tests.eval.apex import ApexMeasurement   # Legacy (works but deprecated)

See: arifos_eval/README.md for canonical documentation
"""

# Re-export from canonical arifos.eval package (v49 namespace)
from arifos.eval import *  # noqa: F401, F403

__version__ = "45.0.0"  # Tracks arifos_eval version
