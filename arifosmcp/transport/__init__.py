"""
ARIF Transport Airlock v0.1 — normalize client dialects into canonical transactions.

Accepts: ChatGPT, Claude, OpenAI Agents SDK, FastMCP, Cursor, stdio, Streamable HTTP, SSE, raw JSON-RPC
Normalizes into: CanonicalEnvelope (actor, intent, evidence, authority, action_class, reversibility, session_state, trace_id)
Routes to: kernel INIT → SENSE → MIND → HEART → JUDGE → FORGE → VAULT

Quick start:
    from arifosmcp.transport import enter_airlock
    result = enter_airlock(request_data)

Module layout:
    errors.py              — ARIF_* structured error codes
    canonical_envelope.py  — CanonicalEnvelope, ActionClass, AirlockResult
    airlock.py             — dialect detection, normalization, response shaping
    conformance.py         — conformance test matrix + reporting

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from arifosmcp.transport.airlock import (
    DIALECT_REGISTRY,
    AirlockASGIMiddleware,
    AirlockResult,
    classify_authority,
    classify_reversibility,
    detect_dialect,
    enter_airlock,
    get_airlock_metrics,
    handle,
    normalize_response,
    normalize_to_canonical_envelope,
    preserve_raw_request,
    process_request,
    refuse_with_888_hold,
    register_dialect,
    reset_airlock_metrics,
    route_to_kernel,
    validate_minimum_fields,
)
from arifosmcp.transport.canonical_envelope import (
    ActionClass,
    AuthLevel,
    CanonicalEnvelope,
    new_envelope,
)
from arifosmcp.transport.conformance import (
    print_matrix,
    run_all,
)
from arifosmcp.transport.conformance_spine import run_spine as run_conformance_spine
from arifosmcp.transport.errors import (
    ERRORS,
    ArifError,
    TransportFaultCode,
    arif_error,
    arif_error_data,
    build_transport_error_envelope,
)

__all__ = [
    "enter_airlock",
    "process_request",
    "handle",
    "AirlockASGIMiddleware",
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
    "run_conformance_spine",
    "arif_error",
    "arif_error_data",
    "ArifError",
    "ERRORS",
    "TransportFaultCode",
    "build_transport_error_envelope",
    "get_airlock_metrics",
    "reset_airlock_metrics",
    "preserve_raw_request",
    "detect_dialect",
    "normalize_to_canonical_envelope",
    "validate_minimum_fields",
    "classify_authority",
    "classify_reversibility",
    "refuse_with_888_hold",
    "route_to_kernel",
]
