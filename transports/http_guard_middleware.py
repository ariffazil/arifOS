"""
Constitutional Guard HTTP Middleware for FastMCP.

Intercepts HTTP /mcp responses at the ASGI level and applies
constitutional_guard floor enforcement to tool outputs.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
from typing import AsyncIterator
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

try:
    from arifos.runtime.middleware.constitutional_guard import constitutional_guard
except ImportError:
    try:
        from arifos.core.middleware.constitutional_guard import constitutional_guard
    except ImportError:
        constitutional_guard = None


async def _guard_sse_iterator(iterator: AsyncIterator[bytes], constitutional_guard_fn) -> AsyncIterator[bytes]:
    """
    Transform SSE stream by applying constitutional_guard to each tool result.
    """
    buffer = b""

    async for chunk in iterator:
        buffer += chunk
        while b"\n" in buffer:
            line_bytes, buffer = buffer.split(b"\n", 1)
            line = line_bytes.decode("utf-8")

            if not line.startswith("data: "):
                yield line_bytes + b"\n"
                continue

            data_str = line[6:].strip()
            if not data_str:
                yield line_bytes + b"\n"
                continue

            try:
                parsed = json.loads(data_str)
                tool_name = None

                if parsed.get("result", {}).get("content"):
                    content = parsed["result"]["content"]
                    if isinstance(content, list):
                        for block in content:
                            if block.get("type") == "text":
                                try:
                                    tool_output = json.loads(block["text"])
                                    if isinstance(tool_output, dict):
                                        tool_name = tool_output.get("tool", "unknown")
                                        guarded = constitutional_guard_fn(tool_name, tool_output)
                                        block["text"] = json.dumps(guarded, ensure_ascii=False)
                                        break
                                except (json.JSONDecodeError, TypeError, KeyError):
                                    continue

                guarded_line = "data: " + json.dumps(parsed, ensure_ascii=False)
                yield (guarded_line + "\n").encode("utf-8")

            except (json.JSONDecodeError, KeyError, TypeError):
                yield line_bytes + b"\n"

    if buffer:
        yield buffer


class ConstitutionalGuardHTTPMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that intercepts MCP /mcp streaming responses,
    parses tool output JSON, applies constitutional_guard floor enforcement,
    and returns the guarded response.
    """

    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/mcp":
            return await call_next(request)

        if request.method != "POST":
            return await call_next(request)

        response = await call_next(request)

        if response.status_code != 200:
            return response

        if constitutional_guard is None:
            return response

        try:
            body_iterator = response.body_iterator

            if hasattr(response, "body"):
                body = response.body
            else:
                body = b""
                async for chunk in body_iterator:
                    body += chunk

            text = body.decode("utf-8")
            lines = text.strip().split("\n")
            guarded_lines = []

            for line in lines:
                if not line.startswith("data: "):
                    guarded_lines.append(line)
                    continue

                data_str = line[6:].strip()
                if not data_str:
                    guarded_lines.append(line)
                    continue

                try:
                    parsed = json.loads(data_str)

                    tool_name = None
                    if parsed.get("result", {}).get("content"):
                        content = parsed["result"]["content"]
                        if isinstance(content, list):
                            for block in content:
                                if block.get("type") == "text":
                                    try:
                                        tool_output = json.loads(block["text"])
                                        if isinstance(tool_output, dict):
                                            tool_name = tool_output.get("tool", "unknown")
                                            guarded = constitutional_guard(tool_name, tool_output)
                                            block["text"] = json.dumps(guarded, ensure_ascii=False)
                                            break
                                    except (json.JSONDecodeError, TypeError, KeyError):
                                        continue

                    guarded_lines.append("data: " + json.dumps(parsed, ensure_ascii=False))

                except (json.JSONDecodeError, KeyError, TypeError):
                    guarded_lines.append(line)

            guarded_body = "\n".join(guarded_lines).encode("utf-8")

            return Response(
                content=guarded_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as exc:
            logger.warning("ConstitutionalGuardHTTPMiddleware error: %s", exc)
            return response

        return response