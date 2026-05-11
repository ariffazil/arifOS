"""
arifosmcp/runtime/webhook_router.py — FastAPI Webhook Routes
═══════════════════════════════════════════════════════════════════════════════

Exposes POST /api/webhook/forge as the canonical constitutional intake surface.
Mounts onto the main arifOS FastAPI app.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from arifosmcp.runtime.webhook_intake import (
    SOURCE_REGISTRY,
    process_webhook,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["webhook"])


@router.post("/forge")
async def webhook_forge(request: Request) -> JSONResponse:
    """
    Canonical constitutional webhook intake.

    Accepts signed webhook events from registered sources.
    Returns adjudication result with trace_id and verdict.

    Headers expected (varies by source):
        x-source:            github | grafana | manual
        x-hub-signature-256:  HMAC-SHA256 (GitHub)
        x-grafana-signature:  HMAC-SHA256 (Grafana)
        x-arifos-signature:   HMAC-SHA256 (Manual)
        x-event-type:         push | release | alert | deploy_signal | ...
    """
    body = await request.body()
    headers = {k.lower(): v for k, v in request.headers.items()}

    source = headers.get("x-source", "unknown")
    client_key = request.client.host if request.client else "unknown"

    result = process_webhook(source, body, headers, client_key)

    verdict = result.get("verdict", "VOID")
    trace_id = result.get("trace_id", "unknown")

    logger.info(
        "Webhook intake: trace=%s source=%s verdict=%s issues=%d",
        trace_id,
        source,
        verdict,
        len(result.get("issues", [])),
    )

    status_code = _verdict_to_status(verdict)
    return JSONResponse(content=result, status_code=status_code)


@router.get("/forge/status")
async def webhook_status() -> JSONResponse:
    """Public status of the webhook intake surface."""
    return JSONResponse(
        {
            "surface": "/api/webhook/forge",
            "status": "ACTIVE",
            "sources": list(SOURCE_REGISTRY.keys()),
            "authentication": "HMAC-SHA256",
            "replay_protection": True,
            "rate_limit": "10 req / 300s per IP",
            "policy_pinning": True,
            "approval_boundary": (
                "Irreversible actions require a fresh human approval artifact "
                "bound to trace, event, payload hash, action, and policy version."
            ),
            "authority_rule": ("Webhook may trigger adjudication. Webhook may not bypass APEX."),
        }
    )


def _verdict_to_status(verdict: str) -> int:
    """Map constitutional verdict to HTTP status code."""
    return {
        "SEAL": 200,
        "QUALIFY": 202,
        "888-HOLD": 202,
        "VOID": 403,
    }.get(verdict, 403)
