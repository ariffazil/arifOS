"""
arifos_core.system - Core System Module

Contains the central runtime components of arifOS:
- APEX_PRIME: Judiciary engine (verdicts)
- pipeline: 000-999 metabolic pipeline
- kernel: Time governor, entropy rot
- runtime_manifest: Epoch tracking
- ignition: Startup
- stack_manifest: Stack tracking

Version: v46.3.1Ω (+Toroidal Loop)
"""

from .apex_prime import (
                         APEX_EPOCH,
                         APEX_VERSION,
                         APEXPrime,
                         ApexVerdict,
                         Verdict,
                         apex_review,
                         apex_verdict,  # v42: Convenience shim returning str
                         check_floors,
)

# API Registry (v42)
from .api_registry import (
                         APIEntry,
                         APIRegistry,
                         StabilityLevel,
                         check_module_stability,
                         get_deprecated_exports,
                         get_registry,
                         get_stable_exports,
)

# Pipeline imports deferred to avoid circular imports
# from .pipeline import Pipeline

__all__ = [
    # APEX PRIME (v42)
    "APEXPrime",
    "apex_review",      # Returns ApexVerdict (structured)
    "apex_verdict",     # Convenience shim, returns str
    "ApexVerdict",      # Dataclass
    "Verdict",          # Enum: SEAL, SABAR, VOID, PARTIAL, HOLD_888, SUNSET
    "check_floors",
    "APEX_VERSION",
    "APEX_EPOCH",
    # API Registry (v42)
    "StabilityLevel",
    "APIEntry",
    "APIRegistry",
    "get_registry",
    "get_stable_exports",
    "get_deprecated_exports",
    "check_module_stability",
]
