"""
Organ Proxy Middleware — Federation Single-Door Enforcement
═══════════════════════════════════════════════════════════

ASGI middleware that intercepts requests bearing the X-Arifos-Organ-Target
header (set by Caddy) and proxies them to the correct domain organ backend.

Without this header, requests pass through to normal arifOS handling.

Design:
- Caddy sets X-Arifos-Organ-Target header → this middleware intercepts
- Proxies to organ backend on 127.0.0.1
- Supports SSE streaming (bidirectional)
- FAIL-CLOSED: any error → 502, never forwards ungoverned
- Logs every proxied request for audit trail
- Non-organ requests pass through transparently

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import logging

import httpx
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("arifosmcp.organ_proxy")

# ── Organ Backend Map ──────────────────────────────────────────────────────
ORGAN_BACKENDS: dict[str, str] = {
    "geox": "http://127.0.0.1:8081",
    "wealth": "http://127.0.0.1:18082",
    "well": "http://127.0.0.1:18083",
    "forge": "http://127.0.0.1:7072",
    "aforge": "http://127.0.0.1:7072",
}

# Timeouts
BACKEND_CONNECT_TIMEOUT = 5.0
BACKEND_READ_TIMEOUT = 120.0
BACKEND_POOL_TIMEOUT = 10.0

# Shared httpx client
_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is not None and not _client.is_closed:
        return _client
    async with _client_lock:
        if _client is not None and not _client.is_closed:
            return _client
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=BACKEND_CONNECT_TIMEOUT,
                read=BACKEND_READ_TIMEOUT,
                write=BACKEND_READ_TIMEOUT,
                pool=BACKEND_POOL_TIMEOUT,
            ),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
            follow_redirects=False,
        )
        logger.info("organ_proxy: httpx client created")
        return _client


class OrganProxyMiddleware:
    """
    ASGI middleware: intercepts X-Arifos-Organ-Target → proxy to organ backend.

    Mount before all other middleware so organ traffic is intercepted early.
    Requests WITHOUT the header pass through to the inner ASGI app (arifOS).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check for organ target header (Caddy-injected)
        organ_name = None
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-arifos-organ-target":
                organ_name = value.decode().lower().strip()
                break

        if not organ_name:
            # Not an organ request — pass through to arifOS
            await self.app(scope, receive, send)
            return

        # Validate organ
        backend = ORGAN_BACKENDS.get(organ_name)
        if not backend:
            logger.warning("organ_proxy: unknown organ '%s'", organ_name)
            await self._send_error(send, 404, f"unknown organ: {organ_name}")
            return

        # Build target URL from scope
        path = scope.get("path", "/")
        qs = scope.get("query_string", b"").decode()
        target_url = f"{backend}{path}"
        if qs:
            target_url += f"?{qs}"

        logger.info("organ_proxy: %s %s → %s", scope.get("method", "?"), path, target_url)

        try:
            await self._proxy(scope, receive, send, target_url, organ_name)
        except httpx.ConnectError:
            logger.error("organ_proxy: %s unreachable at %s", organ_name, backend)
            await self._send_error(
                send, 502, f"organ '{organ_name}' unreachable — service may be down"
            )
        except httpx.TimeoutException:
            logger.error("organ_proxy: %s timed out", organ_name)
            await self._send_error(send, 504, f"organ '{organ_name}' request timed out")
        except Exception as exc:
            logger.error("organ_proxy: %s proxy error: %s", organ_name, exc, exc_info=True)
            await self._send_error(send, 502, f"proxy error: {type(exc).__name__}")

    async def _proxy(
        self, scope: Scope, receive: Receive, send: Send, target_url: str, organ_name: str
    ) -> None:
        """Forward the request to the organ backend and stream the response back."""
        client = await _get_client()

        # Build forward headers from scope
        forward_headers: dict[str, str] = {}
        hop_by_hop = {
            "host", "connection", "transfer-encoding",
            "x-arifos-organ-target",
        }
        for key_bytes, value_bytes in scope.get("headers", []):
            key = key_bytes.decode().lower()
            if key not in hop_by_hop:
                forward_headers[key] = value_bytes.decode()

        forward_headers["host"] = f"{organ_name}.arif-fazil.com"
        forward_headers["x-forwarded-by"] = "arifos-organ-proxy"

        # Read body from ASGI receive stream
        body_chunks: list[bytes] = []
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                chunk = message.get("body", b"")
                if chunk:
                    body_chunks.append(chunk)
                more_body = message.get("more_body", False)
            elif message["type"] == "http.disconnect":
                return

        body = b"".join(body_chunks)
        method = scope.get("method", "GET")

        # Proxy request
        req = client.build_request(
            method=method,
            url=target_url,
            headers=forward_headers,
            content=body if body else None,
            timeout=httpx.Timeout(
                connect=BACKEND_CONNECT_TIMEOUT,
                read=BACKEND_READ_TIMEOUT,
                write=BACKEND_READ_TIMEOUT,
                pool=BACKEND_POOL_TIMEOUT,
            ),
        )

        backend_resp = await client.send(req, stream=True)

        # Build response headers
        response_headers: list[tuple[bytes, bytes]] = []
        skip_resp = {"transfer-encoding", "connection", "keep-alive"}
        for key, value in backend_resp.headers.items():
            if key.lower() not in skip_resp:
                response_headers.append((key.encode(), value.encode()))
        response_headers.append((b"x-arifos-organ-proxy", organ_name.encode()))

        # Send response start
        await send({
            "type": "http.response.start",
            "status": backend_resp.status_code,
            "headers": response_headers,
        })

        # Stream body
        try:
            async for chunk in backend_resp.aiter_raw():
                if chunk:
                    await send({
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    })
        except Exception as exc:
            logger.warning("organ_proxy: stream interrupted for %s: %s", organ_name, exc)
        finally:
            await backend_resp.aclose()
            await send({
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            })

    async def _send_error(self, send: Send, status_code: int, detail: str) -> None:
        import json
        body = json.dumps({
            "error": "organ_proxy_error",
            "detail": detail,
            "principle": "FAIL_CLOSED — governance gate must not forward ungoverned traffic",
        }).encode()
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"x-arifos-organ-proxy", b"error"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        })
