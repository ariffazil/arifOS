"""
COMPAT SHIM — zkpc_verifier.py → context_coherence.py

This file exists only for backward compatibility.
New code should import from: arifosmcp.runtime.context_coherence

Renamed 2026-06-14 (ZKPC-REALITY-ALIGN).
See /root/arifOS/docs/ZKPC_DISTINCTION.md.
"""
from arifosmcp.runtime.context_coherence import (
    verify_context_coherence as verify_zkpc,
    DIMENSIONS,
    PASS_THRESHOLD,
)
