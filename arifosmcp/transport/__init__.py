"""
ARIF Transport Airlock v0.1 — normalize client dialects into canonical transactions.

Accepts: ChatGPT, Claude, OpenAI Agents SDK, FastMCP, Cursor, stdio, Streamable HTTP, SSE, raw JSON-RPC
Normalizes into: CanonicalEnvelope (actor, intent, evidence, authority, action_class, reversibility)
Routes to: kernel INIT → SENSE → MIND → HEART → JUDGE → FORGE → VAULT

Quick start:
    from arifosmcp.transport import process_request
    result = process_request(request_data, transport="streamable_http")

Module layout:
    errors.py              — ARIF_* structured error codes
    canonical_envelope.py  — CanonicalEnvelope, ActionClass, AirlockResult
    airlock.py             — dialect detection, normalization, response shaping
    conformance.py         — conformance test matrix + reporting

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from arifosmcp.transport.airlock import (
    process_request,
    detect_dialect,
    normalize_response,
    register_dialect,
    DIALECT_REGISTRY,
)
from arifosmcp.transport.canonical_envelope import (
    ActionClass,
    CanonicalEnvelope,
    AirlockResult,
    AuthLevel,
    new_envelope,
)
from arifosmcp.transport.conformance import (
    run_all,
    print_matrix,
)
from arifosmcp.transport.errors import (
    arif_error,
    arif_error_data,
    ArifError,
    ERRORS,
)

__all__ = [
    "process_request",
    "detect_dialect",
    "normalize_response",
    "register_dialect",
    "DIALECT_REGISTRY",
    "ActionClass",
    "CanonicalEnvelope",
    "AirlockResult",
    "AuthLevel",
    "new_envelope",
    "run_all",
    "print_matrix",
    "arif_error",
    "arif_error_data",
    "ArifError",
    "ERRORS",
]
