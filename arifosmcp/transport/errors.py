"""
ARIF Transport Airlock — Structured Error Codes
═══════════════════════════════════════════════════

Replaces ALL bare -32602 responses with ARIF_* structured errors.
Every error reduces uncertainty — never increases it.

DITEMPA BUKAN DIBERI — Bound by execution, not by string.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ArifError:
    """Single canonical error envelope."""
    code: str
    message: str
    stage: str
    retryable: bool = False
    supported_versions: list[str] | None = None
    expected_shape: str | None = None
    received_shape: str | None = None
    next_probe: str | None = None
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["DITEMPA_BUKAN_DIBERI"] = True
        return d

    def to_jsonrpc_error(self, jsonrpc_code: int = -32602) -> dict[str, Any]:
        """Wrap as JSON-RPC 2.0 error response."""
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": jsonrpc_code,
                "message": self.code,
                "data": self.to_dict(),
            },
        }


ERRORS: dict[str, ArifError] = {
    "ARIF_SCHEMA_MISMATCH": ArifError(
        code="ARIF_SCHEMA_MISMATCH",
        message="Argument shape does not match expected tool schema.",
        stage="tool_call",
        retryable=True,
        next_probe="schema_echo",
    ),
    "ARIF_SESSION_NOT_FOUND": ArifError(
        code="ARIF_SESSION_NOT_FOUND",
        message="MCP session ID not found in active state.",
        stage="session_resume",
        retryable=True,
        next_probe="initialize",
    ),
    "ARIF_AUTH_MISSING": ArifError(
        code="ARIF_AUTH_MISSING",
        message="Required authentication header or credential absent.",
        stage="pre_init",
        retryable=False,
        next_probe="schema_echo",
    ),
    "ARIF_FLOOR_VIOLATION": ArifError(
        code="ARIF_FLOOR_VIOLATION",
        message="Constitutional floor (F1-F13) breached. Action refused.",
        stage="judge",
        retryable=False,
        next_probe="status",
    ),
    "ARIF_LEASE_EXPIRED": ArifError(
        code="ARIF_LEASE_EXPIRED",
        message="Authority lease TTL exceeded. Re-lease required.",
        stage="mutation",
        retryable=True,
        next_probe="lease_inspect",
    ),
    "ARIF_TRANSPORT_MISMATCH": ArifError(
        code="ARIF_TRANSPORT_MISMATCH",
        message="Client dialect or transport mode not recognised.",
        stage="initialize",
        retryable=False,
        next_probe="transport_echo",
    ),
    "ARIF_VERSION_MISMATCH": ArifError(
        code="ARIF_VERSION_MISMATCH",
        message="Protocol version not in supported list.",
        stage="initialize",
        retryable=False,
        supported_versions=["2025-11-25", "2025-03-26"],
        next_probe="schema_echo",
    ),
    "ARIF_INTERNAL": ArifError(
        code="ARIF_INTERNAL",
        message="Unexpected kernel error. Check kernel health.",
        stage="kernel",
        retryable=True,
        next_probe="ping",
    ),
    "ARIF_TRANSPORT_UNAVAILABLE": ArifError(
        code="ARIF_TRANSPORT_UNAVAILABLE",
        message="Requested transport dialect not available.",
        stage="initialize",
        retryable=False,
        next_probe="transport_echo",
    ),
    "ARIF_LEASE_INSUFFICIENT": ArifError(
        code="ARIF_LEASE_INSUFFICIENT",
        message="Lease scope insufficient for requested action.",
        stage="mutation",
        retryable=False,
        next_probe="lease_inspect",
    ),
}


def arif_error(code: str, **overrides: Any) -> dict[str, Any]:
    """Get a canonical error response, with optional field overrides."""
    base = ERRORS.get(code)
    if base is None:
        base = ArifError(
            code="ARIF_UNKNOWN",
            message=f"Unknown error code: {code}",
            stage="unknown",
        )
    for k, v in overrides.items():
        if hasattr(base, k):
            setattr(base, k, v)
    return base.to_jsonrpc_error()


def arif_error_data(code: str, **overrides: Any) -> dict[str, Any]:
    """Return only the data payload (for embedding in existing responses)."""
    base = ERRORS.get(code)
    if base is None:
        base = ArifError(code="ARIF_UNKNOWN", message=f"Unknown: {code}", stage="unknown")
    for k, v in overrides.items():
        if hasattr(base, k):
            setattr(base, k, v)
    return base.to_dict()
