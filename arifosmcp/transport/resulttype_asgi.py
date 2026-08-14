"""
MCP 2026-07-28 resultType ASGI middleware.
Injects resultType into all JSON-RPC collection/read responses (G1).
Also injects per-result annotations.cacheScope and annotations.ttlMs (G2).

Covers: tools/list, resources/list, resources/templates/list,
        prompts/list, resources/read

Raw ASGI — no request body consumption. Proxies app attributes.
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

# ── G2: Method → (cacheScope, ttlMs) for result-level annotations ──
# Tools are private (can mutate state), resources/prompts are public (static).
_RESULT_CACHE: dict[str, tuple[str, int]] = {
    "tools/list": ("private", 0),
    "resources/list": ("public", 300_000),  # 5 min
    "resources/templates/list": ("public", 300_000),
    "resources/read": ("public", 60_000),  # 1 min
    "prompts/list": ("public", 3600_000),  # 1 hour
}

# Keys inside the result that hold the item list (for cacheScope/ttlMs injection)
_LIST_KEYS: dict[str, str] = {
    "tools/list": "tools",
    "resources/list": "resources",
    "resources/templates/list": "resourceTemplates",
    "prompts/list": "prompts",
}


class ResultTypeASGIMiddleware:
    """ASGI middleware that injects resultType into MCP 2026-07-28 responses."""

    def __init__(self, app):
        self._app = app

    def __getattr__(self, name):
        return getattr(self._app, name)

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"].rstrip("/") != "/mcp"
        ):
            return await self._app(scope, receive, send)

        # Check protocol version from headers
        protocol_version = ""
        for k, v in scope.get("headers", []):
            if k == b"mcp-protocol-version":
                protocol_version = v.decode()
                break

        if protocol_version < "2026-07-28":
            return await self._app(scope, receive, send)

        # ── Capture request body to determine method (G1) ──
        # We need the method to decide which annotations to inject.
        # Buffer the request body and re-inject for downstream.
        req_body = await _drain_body(scope, receive)
        method = _extract_method(req_body)

        async def _replay_receive():
            return {"type": "http.request", "body": req_body, "more_body": False}

        # Buffer the response and inject resultType + annotations
        response_started = False
        response_body = bytearray()
        status_code = 200
        response_headers: list[tuple[bytes, bytes]] = []

        async def send_wrapper(message):
            nonlocal response_started, response_body, status_code, response_headers

            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                response_headers = list(message.get("headers", []))

            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_body.extend(body)

                more_body = message.get("more_body", False)
                if not more_body and response_body:
                    # _inject_all's contract expects `out` pre-cleared; without
                    # the snapshot+clear the injected doc is appended after the
                    # original, yielding two concatenated JSON-RPC documents.
                    raw = bytes(response_body)
                    response_body.clear()
                    _inject_all(raw, method, response_body)
                    if not response_body:
                        response_body.extend(raw)

                    # Update content-length
                    new_headers = []
                    for k, v in response_headers:
                        if k == b"content-length":
                            new_headers.append((k, str(len(response_body)).encode()))
                        else:
                            new_headers.append((k, v))
                    response_headers[:] = new_headers

                    await send(
                        {
                            "type": "http.response.start",
                            "status": status_code,
                            "headers": response_headers,
                        }
                    )
                    await send(
                        {
                            "type": "http.response.body",
                            "body": bytes(response_body),
                            "more_body": False,
                        }
                    )
                    response_body = bytearray()

        await self._app(scope, _replay_receive, send_wrapper)


# ── Helpers ──────────────────────────────────────────────────────────


async def _drain_body(scope, receive) -> bytes:
    """Read the full request body from the ASGI receive callable."""
    chunks: list[bytes] = []
    while True:
        msg = await receive()
        chunks.append(msg.get("body", b""))
        if not msg.get("more_body", False):
            break
    return b"".join(chunks)


def _extract_method(body: bytes) -> str | None:
    """Extract the JSON-RPC method from a request body."""
    try:
        obj = json.loads(body)
        return obj.get("method") if isinstance(obj, dict) else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _inject_all(raw: bytes, method: str | None, out: bytearray) -> None:
    """Inject resultType + cacheScope/ttlMs into the response in-place.

    Writes the rewritten JSON into *out* (a pre-cleared bytearray).
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return

    result = data.get("result") if isinstance(data, dict) else None
    if not isinstance(result, dict):
        return

    dirty = False

    # G1: resultType on every result
    if "resultType" not in result:
        result["resultType"] = "complete"
        dirty = True

    # G2: cacheScope + ttlMs on result-level annotations
    if method and method in _RESULT_CACHE:
        scope, ttl = _RESULT_CACHE[method]

        # Inject result-level cache annotations
        if "cacheScope" not in result:
            result["cacheScope"] = scope
            dirty = True
        if "ttlMs" not in result:
            result["ttlMs"] = ttl
            dirty = True

        # Inject per-item annotations for list methods
        list_key = _LIST_KEYS.get(method)
        if list_key:
            items = result.get(list_key)
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    ann = item.get("annotations")
                    if not isinstance(ann, dict):
                        ann = {}
                        item["annotations"] = ann
                    if "cacheScope" not in ann:
                        ann["cacheScope"] = scope
                        dirty = True
                    if "ttlMs" not in ann:
                        ann["ttlMs"] = ttl
                        dirty = True
                if dirty:
                    logger.debug(
                        "Injected cacheScope/ttlMs into %d %s items",
                        len(items),
                        list_key,
                    )

    if dirty:
        out.extend(json.dumps(data).encode())
        logger.debug("Injected resultType=%s for method=%s", result["resultType"], method)
    else:
        out.extend(raw)
