"""
arifOS v49.0.0 — Constitutional AI Operating System
====================================================

**Authority:** 888 Judge (Muhammad Arif bin Fazil)
**Motto:** Ditempa Bukan Diberi (Forged, Not Given)
**Doctrine:** Delta_S->0 * Peace_squared>=1 * Amanah[LOCK] * Omega_0 in [0.03, 0.05]

This is the root package for arifOS v49, implementing a constitutional governance
framework for AI operations through 13 floors, Trinity engines (AGI/ASI/APEX),
and cryptographic commitment (zkPC + Merkle proofs).

Modules:
    constitutional_constants: Single source of truth for all governance parameters
    core: Core executors and validators
    servers: Trinity servers (AGI, ASI, APEX)
    vault: Memory tower and VAULT-999 management
"""

# Force UTF-8 output on all platforms (Windows cp1252 fix)
import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            line_buffering=True
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            line_buffering=True
        )
    except (AttributeError, io.UnsupportedOperation):
        # Running in environment without buffer access (e.g., some IDEs)
        pass

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
