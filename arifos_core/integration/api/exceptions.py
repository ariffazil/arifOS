"""
arifOS API Exceptions - Custom exception handling for the API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class APIError(Exception):
    """
    Base API error with status code and structured response.

    Usage:
        raise APIError(
            status_code=400,
            code="INVALID_REQUEST",
            message="Missing required field: user_id"
        )
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class PipelineError(APIError):
    """Error during pipeline execution."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            code="PIPELINE_ERROR",
            message=message,
            details=details,
        )


class MemoryError(APIError):
    """Error during L7 memory operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=500,
            code="MEMORY_ERROR",
            message=message,
            details=details,
        )


class ValidationError(APIError):
    """Request validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=f"{resource} not found: {resource_id}",
            details={"resource": resource, "id": resource_id},
        )


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle APIError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Logs the full error but returns a safe message to the client.
    """
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "details": None,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers with the FastAPI app."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
