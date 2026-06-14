"""
Transport Airlock structured errors — replace bare -32602 with constitutional semantics.

Every error carries: stage, transport, protocol versions, received vs expected shape,
retryability, and a next_probe hint. Failures must reduce uncertainty.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class AirlockStage(StrEnum):
    TRANSPORT_HANDSHAKE = "transport_handshake"
    PROTOCOL_VERSION = "protocol_version"
    DIALECT_DETECTION = "dialect_detection"
    SCHEMA_NORMALIZATION = "schema_normalization"
    ENVELOPE_CONSTRUCT = "envelope_construction"
    TOOL_DISPATCH = "tool_dispatch"
    RESPONSE_SERIALIZATION = "response_serialization"
    SESSION_INIT = "session_init"
    PROBE = "probe"


class AirlockErrorCode(StrEnum):
    ARIF_TRANSPORT_HANDSHAKE = "ARIF_TRANSPORT_HANDSHAKE"
    ARIF_PROTOCOL_VERSION_MISMATCH = "ARIF_PROTOCOL_VERSION_MISMATCH"
    ARIF_DIALECT_UNKNOWN = "ARIF_DIALECT_UNKNOWN"
    ARIF_SCHEMA_MISMATCH = "ARIF_SCHEMA_MISMATCH"
    ARIF_ENVELOPE_INCOMPLETE = "ARIF_ENVELOPE_INCOMPLETE"
    ARIF_AUTHORITY_MISSING = "ARIF_AUTHORITY_MISSING"
    ARIF_SESSION_MISSING = "ARIF_SESSION_MISSING"
    ARIF_TOOL_UNKNOWN = "ARIF_TOOL_UNKNOWN"
    ARIF_TOOL_LOCKED = "ARIF_TOOL_LOCKED"
    ARIF_TOOL_MUTATION_WITHOUT_LEASE = "ARIF_TOOL_MUTATION_WITHOUT_LEASE"
    ARIF_AIRLOCK_INTERNAL = "ARIF_AIRLOCK_INTERNAL"


class AirlockError(Exception):
    """Base transport airlock error with structured context."""

    def __init__(
        self,
        code: AirlockErrorCode,
        message: str,
        *,
        stage: AirlockStage = AirlockStage.TRANSPORT_HANDSHAKE,
        jsonrpc_code: int = -32602,
        transport: str = "unknown",
        protocol_version_received: str | None = None,
        protocol_versions_supported: list[str] | None = None,
        expected_shape: str = "",
        received_shape: str = "",
        retryable: bool = True,
        next_probe: str = "arif_ping",
        detail: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.stage = stage
        self.jsonrpc_code = jsonrpc_code
        self.transport = transport
        self.protocol_version_received = protocol_version_received
        self.protocol_versions_supported = protocol_versions_supported or ["2025-11-25", "2025-03-26"]
        self.expected_shape = expected_shape
        self.received_shape = received_shape
        self.retryable = retryable
        self.next_probe = next_probe
        self.detail = detail or {}

    def to_jsonrpc_error(self) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "data": {
                "jsonrpc_code": self.jsonrpc_code,
                "stage": self.stage.value,
                "transport": self.transport,
                "protocol_version_received": self.protocol_version_received,
                "protocol_versions_supported": self.protocol_versions_supported,
                "expected_shape": self.expected_shape,
                "received_shape": self.received_shape,
                "retryable": self.retryable,
                "next_probe": self.next_probe,
                "detail": self.detail,
            },
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "error_code": self.code.value,
            "error_message": self.message,
            "stage": self.stage.value,
            "jsonrpc_code": self.jsonrpc_code,
            "transport": self.transport,
            "protocol_version_received": self.protocol_version_received,
            "protocol_versions_supported": self.protocol_versions_supported,
            "expected_shape": self.expected_shape,
            "received_shape": self.received_shape,
            "retryable": self.retryable,
            "next_probe": self.next_probe,
            "detail": self.detail,
        }

    def __repr__(self) -> str:
        return (
            f"AirlockError(code={self.code.value}, stage={self.stage.value}, "
            f"retryable={self.retryable}, next_probe={self.next_probe})"
        )


def schema_mismatch(
    expected: str,
    received: str,
    transport: str = "streamable_http",
    next_probe: str = "arif_schema_echo",
    detail: dict[str, Any] | None = None,
) -> AirlockError:
    return AirlockError(
        code=AirlockErrorCode.ARIF_SCHEMA_MISMATCH,
        message=f"Schema mismatch: expected {expected}, received {received}",
        stage=AirlockStage.SCHEMA_NORMALIZATION,
        transport=transport,
        expected_shape=expected,
        received_shape=received,
        retryable=True,
        next_probe=next_probe,
        detail=detail,
    )


def protocol_mismatch(
    client_version: str,
    transport: str = "streamable_http",
) -> AirlockError:
    return AirlockError(
        code=AirlockErrorCode.ARIF_PROTOCOL_VERSION_MISMATCH,
        message=f"Protocol version mismatch: client={client_version}, server supports 2025-11-25",
        stage=AirlockStage.PROTOCOL_VERSION,
        transport=transport,
        protocol_version_received=client_version,
        protocol_versions_supported=["2025-11-25", "2025-03-26"],
        expected_shape="2025-11-25",
        received_shape=client_version,
        retryable=True,
        next_probe="arif_initialize_probe",
    )


def dialect_unknown(
    transport_hint: str = "unknown",
    next_probe: str = "arif_ping",
) -> AirlockError:
    return AirlockError(
        code=AirlockErrorCode.ARIF_DIALECT_UNKNOWN,
        message=f"Unable to classify client dialect from transport hint: {transport_hint}",
        stage=AirlockStage.DIALECT_DETECTION,
        transport=transport_hint,
        retryable=True,
        next_probe=next_probe,
    )


def authority_missing(transport: str = "streamable_http") -> AirlockError:
    return AirlockError(
        code=AirlockErrorCode.ARIF_AUTHORITY_MISSING,
        message="Authority lease or actor identity missing",
        stage=AirlockStage.ENVELOPE_CONSTRUCT,
        transport=transport,
        retryable=True,
        next_probe="arif_session_init",
    )


def tool_locked(action_class: str = "", reason: str = "") -> AirlockError:
    return AirlockError(
        code=AirlockErrorCode.ARIF_TOOL_LOCKED,
        message=f"888_HOLD: {reason or 'Irreversible action requires explicit human confirmation'}",
        stage=AirlockStage.TOOL_DISPATCH,
        jsonrpc_code=-32001,
        retryable=False,
        next_probe="request_human_confirmation",
        detail={"action_class": action_class, "hold_reason": reason},
    )


class TransportFaultCode(StrEnum):
    ARIF_SCHEMA_MISMATCH = "ARIF_SCHEMA_MISMATCH"
    ARIF_TRANSPORT_DIALECT_MISMATCH = "ARIF_TRANSPORT_DIALECT_MISMATCH"
    ARIF_VERSION_NEGOTIATION_FAILED = "ARIF_VERSION_NEGOTIATION_FAILED"
    ARIF_INIT_DIALECT_MISMATCH = "ARIF_INIT_DIALECT_MISMATCH"
    ARIF_SESSION_NOT_FOUND = "ARIF_SESSION_NOT_FOUND"
    ARIF_ENVELOPE_MISSING = "ARIF_ENVELOPE_MISSING"
    ARIF_LEASE_EXPIRED = "ARIF_LEASE_EXPIRED"


def build_transport_error_envelope(
    code: TransportFaultCode | str,
    message: str | None = None,
    *,
    stage: str = "000_INIT",
    transport: str = "unknown",
    protocol_version_received: str | None = None,
    protocol_versions_supported: list[str] | None = None,
    expected_shape: str = "",
    received_shape: str = "",
    retryable: bool = True,
    next_probe: str | None = None,
    session_id: str | None = None,
    trace_id: str | None = None,
    request_id: Any | None = None,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # Resolve code string to enum if possible
    if isinstance(code, str):
        try:
            code = TransportFaultCode(code)
        except ValueError:
            pass

    # Default mappings based on code
    m = {
        TransportFaultCode.ARIF_SCHEMA_MISMATCH: (-32602, "schema_echo"),
        TransportFaultCode.ARIF_TRANSPORT_DIALECT_MISMATCH: (-32602, "arif_transport_echo"),
        TransportFaultCode.ARIF_VERSION_NEGOTIATION_FAILED: (-32602, "arif_version_echo"),
        TransportFaultCode.ARIF_INIT_DIALECT_MISMATCH: (-32602, "arif_initialize_probe"),
        TransportFaultCode.ARIF_SESSION_NOT_FOUND: (-32001, "arif_session_init(mode='resume')"),
        TransportFaultCode.ARIF_ENVELOPE_MISSING: (-32602, "arif_ping"),
        TransportFaultCode.ARIF_LEASE_EXPIRED: (-32000, "arif_lease_issue"),
    }

    jsonrpc_code, default_next_probe = m.get(code, (-32602, "arif_ping"))
    if next_probe is None:
        next_probe = default_next_probe

    if message is None:
        message = f"Transport Airlock error: {code.value if hasattr(code, 'value') else code}"

    code_str = code.value if hasattr(code, "value") else str(code)

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": jsonrpc_code,
            "message": message,
            "data": {
                "code": code_str,
                "stage": stage,
                "transport": transport,
                "protocol_version_received": protocol_version_received,
                "protocol_versions_supported": protocol_versions_supported or ["2025-11-25", "2025-03-26"],
                "expected_shape": expected_shape,
                "received_shape": received_shape,
                "retryable": retryable,
                "next_probe": next_probe,
                "session_id": session_id or "",
                "trace_id": trace_id or "",
                "detail": detail or {},
            }
        }
    }


def arif_error_data(
    code: str,
    stage: str = "000_INIT",
    transport: str = "unknown",
    protocol_version_received: str | None = None,
    expected_shape: str = "",
    received_shape: str = "",
    retryable: bool = True,
    next_probe: str | None = None,
    request_id: Any | None = None,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    envelope = build_transport_error_envelope(
        code=code,
        stage=stage,
        transport=transport,
        protocol_version_received=protocol_version_received,
        expected_shape=expected_shape,
        received_shape=received_shape,
        retryable=retryable,
        next_probe=next_probe,
        request_id=request_id,
        detail=detail,
    )
    return envelope["error"]["data"]


def arif_error(
    code: str,
    message: str | None = None,
    *,
    stage: str = "000_INIT",
    jsonrpc_code: int = -32602,
    transport: str = "unknown",
    protocol_version_received: str | None = None,
    expected_shape: str = "",
    received_shape: str = "",
    retryable: bool = True,
    next_probe: str | None = None,
    request_id: Any | None = None,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_transport_error_envelope(
        code=code,
        message=message,
        stage=stage,
        transport=transport,
        protocol_version_received=protocol_version_received,
        expected_shape=expected_shape,
        received_shape=received_shape,
        retryable=retryable,
        next_probe=next_probe,
        request_id=request_id,
        detail=detail,
    )


# Aliases for backwards compatibility with __init__.py imports
ArifError = AirlockError
ERRORS: dict[str, Any] = {}
