"""
arifOS API Middleware - CORS, logging, and request processing.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


# =============================================================================
# LOGGING MIDDLEWARE
# =============================================================================

async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log incoming requests and response status.

    Logs: method, path, status code, and duration.
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} "
        f"({duration:.3f}s)"
    )

    return response


# =============================================================================
# SETUP FUNCTION
# =============================================================================

def setup_middleware(app: FastAPI) -> None:
    """
    Configure middleware for the FastAPI app.

    Includes:
    - CORS middleware (permissive for now, TODO: tighten in production)
    - Request logging middleware
    - Auth placeholder (TODO: implement real auth)
    """

    # CORS middleware - F1 (Amanah) SECURITY: Strict origin validation
    # NEVER use ["*"] with allow_credentials=True (security breach)
    import os

    allowed_origins_str = os.getenv("ARIFOS_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

    # F1 Amanah check: Prevent wildcard CORS with credentials
    if "*" in allowed_origins:
        raise ValueError(
            "F1 (Amanah) VIOLATION: Cannot use wildcard CORS origins with credentials. "
            "Set ARIFOS_CORS_ORIGINS env var to explicit domains."
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Explicit whitelist only
        allow_credentials=True,
        allow_methods=["GET", "POST"],  # Restrict methods (no OPTIONS needed - auto-handled)
        allow_headers=["Content-Type", "Authorization"],  # Explicit headers only
    )

    # Request logging
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> Response:
        return await logging_middleware(request, call_next)

    # TODO: Auth middleware placeholder
    # When implementing auth:
    # 1. Extract token from Authorization header
    # 2. Validate token (JWT, API key, etc.)
    # 3. Set user info in request.state
    # 4. For now, all requests are unauthenticated
