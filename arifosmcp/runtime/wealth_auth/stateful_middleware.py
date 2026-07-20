"""
Stateful middleware that wraps any protected tool.

Audit-4 rule: every protected tool goes through ONE middleware layer.
Tool implementations MUST NOT repeat the auth logic (verified by
tests/runtime/test_no_inline_auth.py).

Use:

    from arifosmcp.runtime.wealth_auth import bound_call, extract_envelope

    @bound_call(audience="wealth", required_capability="wealth_npv_reward",
                minimum_authority="OPERATOR", public_simulation=True)
    def wealth_npv_reward(input: dict, **ctx) -> dict:
        ...

The decorator validates the bearer token BEFORE the tool body runs, and
exposes the bound actor + session via `ctx`.
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import Any

from .exceptions import AuthError

logger = logging.getLogger(__name__)


def extract_envelope(*, request_headers: dict[str, str] | None = None, **_) -> dict[str, Any]:
    """Pull the standard governance envelope from request headers.

    The audit says every tool carries session_id, actor_id, trace_id, request_id
    in a uniform envelope. This function pulls them from headers (or, when the
    audit's WEALTH side requires the body envelope, the caller may also pass
    a body dict containing _envelope).
    """
    request_headers = request_headers or {}
    return {
        "session_id": request_headers.get("X-ArifOS-Session-ID", ""),
        "actor_id": request_headers.get("X-ArifOS-Actor-ID", ""),
        "trace_id": request_headers.get("X-ArifOS-Trace-ID", ""),
        "request_id": request_headers.get("X-ArifOS-Request-ID", ""),
    }


def bound_call(
    *,
    audience: str,
    required_capability: str,
    minimum_authority: str = "OPERATOR",
    public_simulation: bool = False,
) -> Callable:
    """Decorator: validate the bearer token, then call the wrapped tool."""

    from .authorize import authorize, error_to_envelope

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            # Accept headers from a "request" object if the tool passed one in kwargs.
            req_headers: dict[str, str] = kwargs.pop("_request_headers", None) or {}
            auth = req_headers.get("authorization") or req_headers.get("Authorization")
            try:
                claims = authorize(
                    authorization_header=auth,
                    audience=audience,
                    required_capability=required_capability,
                    minimum_authority=minimum_authority,
                    public_simulation=public_simulation,
                )
            except AuthError as exc:
                return error_to_envelope(exc)
            except Exception as exc:
                logger.exception("authorize failed unexpectedly")
                return error_to_envelope(exc)
            ctx = {
                "envelope": extract_envelope(request_headers=req_headers),
                "claims": claims,
            }
            try:
                result = fn(*args, **kwargs, _ctx=ctx)
            except AuthError as exc:
                return error_to_envelope(exc)
            except Exception as exc:
                logger.exception("tool body raised unexpectedly")
                return {
                    "status": "ERROR",
                    "error_code": "INTERNAL_ERROR",
                    "message": f"{type(exc).__name__}: {exc}",
                    "retryable": False,
                    "mutation_occurred": False,
                }
            return result

        return wrapper

    return decorator
