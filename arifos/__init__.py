"""
arifOS v49.0.0 — Constitutional AI Operating System
====================================================

**Authority:** 888 Judge (Muhammad Arif bin Fazil)
**Motto:** Ditempa Bukan Diberi (Forged, Not Given)
**Doctrine:** ΔS→0 · Peace²≥1 · Amanah🔐 · Ω₀ ∈ [0.03, 0.05]

This is the root package for arifOS v49, implementing a constitutional governance
framework for AI operations through 13 floors, Trinity engines (AGI/ASI/APEX),
and cryptographic commitment (zkPC + Merkle proofs).

Modules:
    constitutional_constants: Single source of truth for all governance parameters
    core: Core executors and validators
    servers: Trinity servers (AGI, ASI, APEX)
    vault: Memory tower and VAULT-999 management
"""

from arifos.constitutional_constants import (
    VERSION,
    FLOORS,
    VERDICTS,
    ENGINES,
    COVENANT_PRINCIPLES,
)

__version__ = VERSION
__all__ = [
    "VERSION",
    "FLOORS",
    "VERDICTS",
    "ENGINES",
    "COVENANT_PRINCIPLES",
]
