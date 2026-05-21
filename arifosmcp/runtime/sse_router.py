"""
arifosmcp/runtime/sse_router.py — Observatory SSE Feed
═══════════════════════════════════════════════════════════════════════════════

Server-Sent Events endpoint for live governance observability.
Emits sanitized webhook intake events to connected dashboards.

SECURITY CONTRACT:
- Observation ONLY. No control signals flow through SSE.
- No secrets, HMAC, tokens, or private payloads are emitted.
- Clients cannot influence governance via this stream.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from arifosmcp.runtime.event_bus import (
    get_recent_events,
    subscribe,
    unsubscribe,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["events"])

_SSE_HEARTBEAT_INTERVAL = 15  # seconds


@router.get("/stream")
async def events_stream(request: Request) -> StreamingResponse:
    """
    Observatory SSE stream.

    Emits JSON-encoded governance events as they occur.
    Heartbeat pings every 15s to keep connection alive.

    Example event:
        event: webhook_intake\n
        data: {"trace_id":"wh-20260511-abc1","verdict":"QUALIFY",...}\n\n
    """
    queue = await subscribe()

    async def event_generator():
        try:
            # Send initial connection ack
            yield _sse_line(
                event="connected",
                data={
                    "status": "observatory_live",
                    "source": "arifOS-event-bus",
                    "observation_only": True,
                },
            )

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=_SSE_HEARTBEAT_INTERVAL)
                    yield _sse_line(event="webhook_intake", data=event)
                except TimeoutError:
                    yield _sse_line(event="heartbeat", data={"ping": True})
        except asyncio.CancelledError:
            logger.info("SSE client disconnected")
        finally:
            await unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-ArifOS-Observation-Only": "true",
        },
    )


@router.get("/recent")
async def events_recent(limit: int = 100) -> dict[str, Any]:
    """Return recent sanitized events (polling fallback for non-SSE clients)."""
    events = get_recent_events(min(limit, 500))
    return {
        "events": events,
        "count": len(events),
        "source": "arifOS-event-bus",
        "observation_only": True,
    }


def _sse_line(event: str, data: dict[str, Any]) -> str:
    """Format a single SSE event line."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# lazy import to avoid circular deps at module level
import asyncio  # noqa: E402
