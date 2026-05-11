"""
errors.py — Standardized Error Codes for GEOX
DITEMPA BUKAN DIBERI

Follows MCP error conventions with domain-specific subsurface extensions.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class GeoxErrorCode(Enum):
    # Standard MCP / JSON-RPC Errors
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # GEOX Domain Errors (Physics/Governance)
    PHYSICS_VIOLATION = 1001
    INSUFFICIENT_GROUNDING = 1002
    SCALE_UNKNOWN = 1003
    ANOMALOUS_CONTRAST_RISK_HIGH = 1004
    VERDICT_VOID = 1005

    # Resource Errors
    FILE_NOT_FOUND = 2001
    INVALID_FORMAT = 2002
    STORE_UNAVAILABLE = 2003
    MACROSTRAT_API_ERROR = 2004
    NO_COVERAGE = 2005

    # Process Errors
    INTERPRETATION_FAILED = 3001
    QUERY_FAILED = 3002
    SW_MODEL_ERROR = 3003
    PARAMETER_OUT_OF_RANGE = 3004


class GeoxError(Exception):
    """Base exception for GEOX errors."""

    def __init__(self, code: GeoxErrorCode, message: str, data: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "name": self.code.name,
            "message": self.message,
            "data": self.data,
        }
