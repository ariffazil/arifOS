"""
MCP 2026-07-28 resultType ASGI middleware.
Injects resultType into tools/list JSON-RPC responses.
Raw ASGI — no request body consumption. Proxies app attributes.
Also injects per-tool annotations.cacheScope ("public"/"private") and
annotations.ttlMs (number) required by MCP 2026-07-28 client-side schema.
"""
from __future__ import annotations
import json
import logging

logger = logging.getLogger(__name__)


class ResultTypeASGIMiddleware:
    """ASGI middleware that injects resultType into tools/list responses."""

    def __init__(self, app):
        self._app = app

    def __getattr__(self, name):
        return getattr(self._app, name)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"].rstrip("/") != "/mcp":
            return await self._app(scope, receive, send)

        # Check protocol version from headers
        protocol_version = ""
        for k, v in scope.get("headers", []):
            if k == b"mcp-protocol-version":
                protocol_version = v.decode()
                break

        if protocol_version < "2026-07-28":
            return await self._app(scope, receive, send)

        # Buffer the response and inject resultType
        response_started = False
        response_body = bytearray()
        status_code = 200
        response_headers = []

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
                    try:
                        data = json.loads(bytes(response_body))
                        if "result" in data and isinstance(data["result"], dict):
                            if "resultType" not in data["result"]:
                                data["result"]["resultType"] = "complete"
                                logger.debug("Injected resultType=complete")
                            # MCP 2026-07-28: each tool requires annotations.cacheScope
                            # ("public"/"private") and annotations.ttlMs (number).
                            # Client-side schema validation fails if absent.
                            tools = data["result"].get("tools")
                            if isinstance(tools, list):
                                for tool in tools:
                                    if not isinstance(tool, dict):
                                        continue
                                    ann = tool.get("annotations")
                                    if not isinstance(ann, dict):
                                        ann = {}
                                        tool["annotations"] = ann
                                    if "cacheScope" not in ann:
                                        ann["cacheScope"] = "private"
                                    if "ttlMs" not in ann:
                                        ann["ttlMs"] = 0
                                response_body = bytearray(json.dumps(data).encode())
                                logger.debug(
                                    "Injected cacheScope/ttlMs into %d tools", len(tools)
                                )
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass

                    # Update content-length
                    new_headers = []
                    for k, v in response_headers:
                        if k == b"content-length":
                            new_headers.append((k, str(len(response_body)).encode()))
                        else:
                            new_headers.append((k, v))
                    response_headers[:] = new_headers

                    await send({
                        "type": "http.response.start",
                        "status": status_code,
                        "headers": response_headers,
                    })
                    await send({
                        "type": "http.response.body",
                        "body": bytes(response_body),
                        "more_body": False,
                    })
                    response_body = bytearray()

        await self._app(scope, receive, send_wrapper)
