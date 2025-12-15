"""
arifos_core.APEX_PRIME - BACKWARD COMPATIBILITY SHIM (v42)
Moved to: arifos_core/system/apex_prime.py
This shim will be removed in v43.0.
"""
from arifos_core.system.apex_prime import *
from arifos_core.system.apex_prime import (
    APEXPrime, ApexVerdict, Verdict, check_floors, apex_review,
    APEX_VERSION, APEX_EPOCH, apex_prime_judge,
)
