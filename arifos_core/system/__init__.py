"""
arifos_core.system - Core System Module

Contains the central runtime components of arifOS:
- APEX_PRIME: Judiciary engine (verdicts)
- pipeline: 000-999 metabolic pipeline
- kernel: Time governor, entropy rot
- runtime_manifest: Epoch tracking
- ignition: Startup
- stack_manifest: Stack tracking

Version: v42.0.0
"""

from .apex_prime import (
    APEXPrime,
    apex_review,
    ApexVerdict,
    Verdict,
    check_floors,
    APEX_VERSION,
    APEX_EPOCH,
)

# Pipeline imports deferred to avoid circular imports
# from .pipeline import Pipeline

__all__ = [
    # APEX PRIME
    "APEXPrime",
    "apex_review",
    "ApexVerdict",
    "Verdict",
    "check_floors",
    "APEX_VERSION",
    "APEX_EPOCH",
]
