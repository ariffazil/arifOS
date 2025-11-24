"""arifos_core
===========
Minimal Python reference implementation for ArifOS AAA Runtime v33Ω.
"""

# Import base types first
from .metrics import Metrics, FloorsVerdict

# Import APEX components
from .APEX_PRIME import apex_review, ApexVerdict, Verdict, check_floors, APEXPrime

# Import memory components (optional - graceful fallback if not available)
try:
    from .memory.cooling_ledger import log_cooling_entry
except (ImportError, AttributeError):
    # Fallback if memory module not available or function not exported
    def log_cooling_entry(*args, **kwargs):
        """Fallback stub for log_cooling_entry when memory module unavailable."""
        import logging
        logging.getLogger("arifos_core").warning(
            "log_cooling_entry unavailable - using stub. Install full arifos package."
        )
        return {
            "status": "stub",
            "job_id": kwargs.get("job_id", "unknown"),
            "verdict": kwargs.get("verdict", "UNKNOWN"),
        }

# Import guard LAST (after all its dependencies are loaded)
try:
    from .guard import apex_guardrail, GuardrailError
except ImportError:
    # Guard requires memory module, make it optional
    apex_guardrail = None
    GuardrailError = None

__all__ = [
    # Metrics
    "Metrics",
    "FloorsVerdict",
    # APEX
    "apex_review",
    "check_floors",
    "ApexVerdict",
    "Verdict",
    "APEXPrime",
    # Memory
    "log_cooling_entry",
    # Guard (may be None if memory unavailable)
    "apex_guardrail",
    "GuardrailError",
]