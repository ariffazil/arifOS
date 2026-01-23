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

    # CORS middleware
    # TODO: Tighten origins in production (replace * with actual frontend domains)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permissive for dev; tighten later
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
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
