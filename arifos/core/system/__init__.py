"""
arifos.core.system - Core System Module

Contains the central runtime components of arifOS:
- APEX_PRIME: Judiciary engine (verdicts)
- pipeline: 000-999 metabolic pipeline
- kernel: Time governor, entropy rot
- runtime_manifest: Epoch tracking
- ignition: Startup
- stack_manifest: Stack tracking

Version: v47.0.0 (+Toroidal Loop)
"""

def get_system_apex():
    """Lazy import for System APEX symbols."""
    from .apex_prime import (
        APEX_VERSION,
        APEX_EPOCH,
        APEXPrime,
        ApexVerdict,
        Verdict,
        normalize_verdict_code,
        check_floors,
        apex_review
    )
    return (
        APEX_VERSION,
        APEX_EPOCH,
        APEXPrime,
        ApexVerdict,
        Verdict,
        normalize_verdict_code,
        check_floors,
        apex_review
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
    # "apex_verdict",   # TODO: Convenience shim not yet implemented
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
