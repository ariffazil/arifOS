"""
arifosmcp/runtime/fault_codes.py — VOID Memanjang Elimination: Fault Code Taxonomy

THE VOID MEMANJANG FAILURE MODE (what this module eliminates):
  Legacy behaviour: any network error, timeout, or missing dependency would
  cause the system to emit a VOID verdict. This is catastrophically wrong.
  VOID means constitutional collapse (F2/L11/L12/L13 violation). It is terminal.
  A missing Qdrant collection is not a constitutional collapse. It is plumbing.

THE HARD INVARIANT (from Grand Unified Technical Specification, FORGED-2026.03):
  - Mechanical faults (infrastructure) → 888_HOLD with machine.fault_code set
  - Constitutional failures (floor breach) → VOID with governance.void_reason set
  - Epistemic failures (insufficient evidence) → SABAR

FAULT CODE TAXONOMY:
  INFRA_* codes:     Service unavailable, degraded, or timing out
  TOOL_*  codes:     Endpoint not found, not exposed, schema invalid
  RATE_*  codes:     Rate limits, quota exhaustion
  VOID_*  codes:     Constitutional violations ONLY (hard floors)

classifier(exception) → FaultClassification tells the kernel which verdict to issue.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# FAULT CLASS ENUM
# ─────────────────────────────────────────────────────────────────────────────
class FaultClass(StrEnum):
    MECHANICAL = "MECHANICAL"  # Infrastructure fault → 888_HOLD
    EPISTEMIC = "EPISTEMIC"  # Insufficient evidence → SABAR
    CONSTITUTIONAL = "CONSTITUTIONAL"  # Hard floor breach → VOID (terminal)


# ─────────────────────────────────────────────────────────────────────────────
# FAULT CODES
# ─────────────────────────────────────────────────────────────────────────────
class MechanicalFaultCode(StrEnum):
    """Infrastructure faults. ALWAYS → 888_HOLD, NEVER → VOID."""

    TOOL_NOT_EXPOSED = "TOOL_NOT_EXPOSED"  # 404 / endpoint not registered
    INFRA_DEGRADED = "INFRA_DEGRADED"  # service unreachable / 5xx
    TIMEOUT_EXCEEDED = "TIMEOUT_EXCEEDED"  # network/compute timeout
    RATE_LIMITED = "RATE_LIMITED"  # 429 / quota exceeded
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"  # Qdrant/Redis/Postgres offline
    DNS_FAIL = "DNS_FAIL"  # DNS resolution failure
    TLS_FAIL = "TLS_FAIL"  # SSL/TLS handshake failure
    WAF_BLOCK = "WAF_BLOCK"  # WAF/CDN blocked request
    PARSE_FAIL = "PARSE_FAIL"  # Response parse error
    RENDER_FAIL = "RENDER_FAIL"  # Headless browser render failure
    NO_RESULTS = "NO_RESULTS"  # Search returned empty (→ SABAR not VOID)
    PLATFORM_INTERVENTION = "PLATFORM_INTERVENTION"
    # MCP host platform (ChatGPT connector, Claude hosted client, Grok platform client, etc.)
    # intercepted or blocked the tool call due to safety/policy layer.
    # This is host governance over the pipe, not arifOS constitution.
    # Always 888_HOLD + evidence. Recommend raw stdio / direct localhost transport.
    # Signature examples: "blocked by ... safety checks", "safety", opaque host policy.
    # Wired from mcp_transport_bridge.get_host_platform + detect_platform_intervention
    # and used to force PLATFORM_FILTERED trust in host_scope + ingress.


class ConstitutionalFaultCode(StrEnum):
    """Constitutional violations. ALWAYS → VOID (terminal). Cannot be retried."""

    F1_AMANAH_BREACH = "F1_AMANAH_BREACH"  # Integrity violation
    F2_TRUTH_BELOW_THRESHOLD = "F2_TRUTH_BELOW_THRESHOLD"  # Evidence score < 0.99
    F3_CONSENSUS_SHATTERED = "F3_CONSENSUS_SHATTERED"  # Tri-witness failure
    F4_CLARITY_VIOLATION = "F4_CLARITY_VIOLATION"  # Entropy dS > 0
    F5_PEACE_VIOLATION = "F5_PEACE_VIOLATION"  # Peace² < 1.0
    F6_EMPATHY_VIOLATION = "F6_EMPATHY_VIOLATION"  # κᵣ < 0.7
    F7_HUMILITY_VIOLATION = "F7_HUMILITY_VIOLATION"  # Omega outside [0.03, 0.05]
    F8_GENIUS = "F8_GENIUS"  # Genius G* < 0.80
    F9_SHADOW_VIOLATION = "F9_SHADOW_VIOLATION"  # Shadow load > 0.3
    L10_ONTOLOGY = "L10_ONTOLOGY"  # Personhood/consciousness claim
    L11_AUDIT_FAILURE = "L11_AUDIT_FAILURE"  # Actor not in whitelist
    L11_TOKEN_INVALID = "L11_TOKEN_INVALID"  # Signature mismatch
    L11_TOKEN_EXPIRED = "L11_TOKEN_EXPIRED"  # Bucket stale → re-anchor
    L11_SESSION_MISMATCH = "L11_SESSION_MISMATCH"  # session_id mismatch
    L11_SOVEREIGN_SIG_INVALID = "L11_SOVEREIGN_SIG_INVALID"  # Ratification sig invalid
    L12_INJECTION = "L12_INJECTION"  # Prompt injection detected
    L13_SOVEREIGN_VETO = "L13_SOVEREIGN_VETO"  # Human rejected via ratify


class TransportFaultCode(StrEnum):
    """Transport-layer faults. ALWAYS → 888_HOLD, NEVER → VOID. Retryable.
    Phase 0 transport hardening (2026-06-14): structured JSON-RPC error semantics.

    Every transport fault includes stage, transport type, protocol versions,
    expected vs received shape, retryable flag, and recommended next_probe.

    Principle: every failure must reduce uncertainty about WHERE the break is.
    """

    ARIF_SCHEMA_MISMATCH = "ARIF_SCHEMA_MISMATCH"
    # Tool call arguments don't match expected schema. The transport bridge
    # delivered the call but the payload shape is wrong. jsonrpc_code: -32602.
    # Next probe: arif_schema_echo

    ARIF_TRANSPORT_DIALECT_MISMATCH = "ARIF_TRANSPORT_DIALECT_MISMATCH"
    # Client sent a call in a dialect the kernel can't parse (e.g. OpenAI-style
    # function call instead of MCP tools/call). jsonrpc_code: -32602.
    # Next probe: arif_transport_echo

    ARIF_VERSION_NEGOTIATION_FAILED = "ARIF_VERSION_NEGOTIATION_FAILED"
    # Client requested a protocol version the server doesn't support.
    # jsonrpc_code: -32602. Server advertises supported versions.
    # Next probe: arif_version_echo

    ARIF_INIT_DIALECT_MISMATCH = "ARIF_INIT_DIALECT_MISMATCH"
    # arif_init received args that don't match any supported mode.
    # Transport works, but the init schema is wrong.
    # Next probe: arif_initialize_probe

    ARIF_SESSION_NOT_FOUND = "ARIF_SESSION_NOT_FOUND"
    # The Mcp-Session-Id doesn't resolve to an active session. Either the session
    # expired, the worker restarted (lost in-memory state), or the client sent a
    # stale ID. jsonrpc_code: -32001.
    # Next probe: arif_init(mode='resume')

    ARIF_ENVELOPE_MISSING = "ARIF_ENVELOPE_MISSING"
    # A governed tool was called without the required FederationEnvelope.
    # The transport bridge must inject the envelope via ingress middleware.
    # jsonrpc_code: -32602.
    # Next probe: arif_ping (then ensure ingress middleware is configured)

    ARIF_LEASE_EXPIRED = "ARIF_LEASE_EXPIRED"
    # The authority lease has expired. Must re-issue before mutation.
    # jsonrpc_code: -32000.
    # Next probe: arif_lease_issue


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFICATION RESULT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class FaultClassification:
    fault_class: FaultClass
    fault_code: str
    verdict: str  # VOID | 888_HOLD | SABAR
    recoverable: bool
    retry_hint: str = ""

    @property
    def is_void(self) -> bool:
        return self.verdict == "VOID"

    @property
    def is_hold(self) -> bool:
        return self.verdict == "888_HOLD"

    @property
    def is_sabar(self) -> bool:
        return self.verdict == "SABAR"


# ─────────────────────────────────────────────────────────────────────────────
# CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────
def classify_exception(exc: Exception) -> FaultClassification:
    """
    Classify a Python exception into a FaultClassification.

    This is the VOID Memanjang elimination function.
    Every call site that previously did 'except Exception: return VOID'
    must be replaced with this classifier.

    Returns FaultClassification with correct verdict (888_HOLD or SABAR, never VOID).
    """
    try:
        import httpx

        if isinstance(exc, httpx.ConnectError):
            return FaultClassification(
                FaultClass.MECHANICAL,
                MechanicalFaultCode.DNS_FAIL,
                "888_HOLD",
                True,
                "Check network connectivity and DNS resolution",
            )
        if isinstance(exc, httpx.TimeoutException):
            return FaultClassification(
                FaultClass.MECHANICAL,
                MechanicalFaultCode.TIMEOUT_EXCEEDED,
                "888_HOLD",
                True,
                "Increase timeout or retry with backoff",
            )
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            if code == 404:
                return FaultClassification(
                    FaultClass.MECHANICAL,
                    MechanicalFaultCode.TOOL_NOT_EXPOSED,
                    "888_HOLD",
                    True,
                    "Verify endpoint is registered and deployed",
                )
            if code == 429:
                return FaultClassification(
                    FaultClass.MECHANICAL,
                    MechanicalFaultCode.RATE_LIMITED,
                    "888_HOLD",
                    True,
                    "Apply exponential backoff and retry",
                )
            if 500 <= code < 600:
                return FaultClassification(
                    FaultClass.MECHANICAL,
                    MechanicalFaultCode.INFRA_DEGRADED,
                    "888_HOLD",
                    True,
                    "Service returned 5xx — wait and retry",
                )
    except ImportError:
        pass

    err_str = str(exc).lower()
    if "ssl" in err_str or "certificate" in err_str or "tls" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL,
            MechanicalFaultCode.TLS_FAIL,
            "888_HOLD",
            True,
            "Check TLS certificates and CA bundle",
        )
    if "qdrant" in err_str or "connect" in err_str or "refused" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL,
            MechanicalFaultCode.DEPENDENCY_UNAVAILABLE,
            "888_HOLD",
            True,
            "Check dependent service health (Qdrant/Redis/Postgres)",
        )
    if "timeout" in err_str:
        return FaultClassification(
            FaultClass.MECHANICAL,
            MechanicalFaultCode.TIMEOUT_EXCEEDED,
            "888_HOLD",
            True,
            "Retry with longer timeout",
        )

    # PLATFORM_INTERVENTION: host safety / policy layer block (OpenAI, Claude, etc.)
    platform_markers = ["safety check", "blocked by", "safety checks", "platform policy", "host policy", "tool call was blocked"]
    if any(m in err_str for m in platform_markers):
        return FaultClassification(
            FaultClass.MECHANICAL,
            MechanicalFaultCode.PLATFORM_INTERVENTION,
            "888_HOLD",
            True,
            "Retry via raw stdio transport or direct localhost MCP endpoint; host pipe is policy-contaminated",
        )

    # Default: unknown mechanical fault — still 888_HOLD, not VOID
    logger.warning(
        "classify_exception: unknown exception type %s → INFRA_DEGRADED",
        type(exc).__name__,
    )
    return FaultClassification(
        FaultClass.MECHANICAL,
        MechanicalFaultCode.INFRA_DEGRADED,
        "888_HOLD",
        True,
        f"Unexpected error: {type(exc).__name__}",
    )


def classify_network_errors(errors: list[dict]) -> str:
    """
    Classify a list of error dicts from multi-engine search into a single fault code.

    Returns:
        "INFRA_DEGRADED" if all engines failed with infrastructure errors.
        "NO_RESULTS" if engines succeeded but returned no content.
    """
    if not errors:
        return "NO_RESULTS"
    infra_codes = {
        MechanicalFaultCode.DNS_FAIL,
        MechanicalFaultCode.TIMEOUT_EXCEEDED,
        MechanicalFaultCode.INFRA_DEGRADED,
        MechanicalFaultCode.TLS_FAIL,
    }
    infra_count = sum(1 for e in errors if e.get("code") in {c.value for c in infra_codes})
    return "INFRA_DEGRADED" if infra_count > len(errors) // 2 else "NO_RESULTS"


__all__ = [
    "FaultClass",
    "FaultClassification",
    "MechanicalFaultCode",
    "TransportFaultCode",
    "ConstitutionalFaultCode",
    "classify_exception",
    "classify_network_errors",
    "build_transport_error_envelope",
    "ARIF_JSONRPC_ERROR_MAP",
]

# ═══════════════════════════════════════════════════════════════════════════════
# JSON-RPC ERROR CODE MAP — transport fault → JSON-RPC error code
# ═══════════════════════════════════════════════════════════════════════════════

ARIF_JSONRPC_ERROR_MAP: dict[str, int] = {
    TransportFaultCode.ARIF_SCHEMA_MISMATCH: -32602,
    TransportFaultCode.ARIF_TRANSPORT_DIALECT_MISMATCH: -32602,
    TransportFaultCode.ARIF_VERSION_NEGOTIATION_FAILED: -32602,
    TransportFaultCode.ARIF_INIT_DIALECT_MISMATCH: -32602,
    TransportFaultCode.ARIF_ENVELOPE_MISSING: -32602,
    TransportFaultCode.ARIF_SESSION_NOT_FOUND: -32001,
    TransportFaultCode.ARIF_LEASE_EXPIRED: -32000,
}

_MCP_SPEC_VERSION = "2025-06-18"
_MCP_SUPPORTED_VERSIONS = ("2025-06-18", "2025-11-25", "2025-03-26")


def build_transport_error_envelope(
    fault_code: TransportFaultCode,
    *,
    stage: str = "000_INIT",
    transport: str = "unknown",
    protocol_version_received: str | None = None,
    protocol_versions_supported: tuple[str, ...] = _MCP_SUPPORTED_VERSIONS,
    expected_shape: str = "",
    received_shape: str = "",
    retryable: bool = True,
    next_probe: str = "arif_ping",
    detail: str = "",
    session_id: str | None = None,
    trace_id: str | None = None,
) -> dict:
    """
    Build a structured JSON-RPC error envelope for transport faults.

    Every failure must reduce uncertainty. This envelope tells the client:
    1. WHAT went wrong (fault_code + message)
    2. WHERE in the protocol stack (stage + transport)
    3. WHY (expected vs received shapes)
    4. WHAT to do next (next_probe + retryable)
    5. HOW to correlate (session_id + trace_id)

    Use this instead of bare -32602 "Invalid request parameters".
    """
    jsonrpc_code = ARIF_JSONRPC_ERROR_MAP.get(fault_code, -32602)

    error_data: dict = {
        "arif_fault_code": fault_code.value,
        "stage": stage,
        "transport": transport,
        "protocol_versions_supported": list(protocol_versions_supported),
        "retryable": retryable,
        "next_probe": next_probe,
    }

    if protocol_version_received:
        error_data["protocol_version_received"] = protocol_version_received
    if expected_shape:
        error_data["expected_shape"] = expected_shape
    if received_shape:
        error_data["received_shape"] = received_shape
    if session_id:
        error_data["session_id"] = session_id
    if trace_id:
        error_data["trace_id"] = trace_id
    if detail:
        error_data["detail"] = detail

    return {
        "jsonrpc": "2.0",
        "error": {
            "code": jsonrpc_code,
            "message": str(fault_code.value),
            "data": error_data,
        },
    }
