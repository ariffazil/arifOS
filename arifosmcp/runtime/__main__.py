"""CLI entrypoint for arifOS AAA MCP."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import sys
from typing import Any

from .fastmcp_ext.transports import run_server


def _bootstrap_environment() -> None:
    try:
        mode = (
            sys.argv[1] if len(sys.argv) > 1 else os.getenv("AAA_MCP_TRANSPORT", "stdio")
        ).lower()
        if mode == "stdio":
            os.environ.setdefault("ARIFOS_MINIMAL_STDIO", "1")
            for logger_name in ("fastmcp", "mcp", "uvicorn", "uvicorn.error", "uvicorn.access"):
                logging.getLogger(logger_name).setLevel(logging.CRITICAL)
            logging.getLogger().setLevel(logging.CRITICAL)
    except Exception:
        return


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _stdio_constitutional_floors() -> list[dict[str, str]]:
    return [
        {"floor_id": "F1", "name": "Amanah", "doctrine": "Reversible or auditable action"},
        {"floor_id": "F2", "name": "Haqq", "doctrine": "Truth and information fidelity"},
        {"floor_id": "F3", "name": "Tri-Witness", "doctrine": "Consensus across witnesses"},
        {
            "floor_id": "F4",
            "name": "Clarity",
            "doctrine": "Entropy must not increase destructively",
        },
        {"floor_id": "F5", "name": "Peace2", "doctrine": "Stability before force"},
        {"floor_id": "F6", "name": "Empathy", "doctrine": "Protect weakest stakeholder"},
        {"floor_id": "F7", "name": "Humility", "doctrine": "Uncertainty admitted explicitly"},
        {"floor_id": "F8", "name": "Wisdom", "doctrine": "Governed intelligence quality threshold"},
        {"floor_id": "F9", "name": "Anti-Hantu", "doctrine": "No deceptive shadow behavior"},
        {"floor_id": "F10", "name": "Ontology Lock", "doctrine": "Category precision enforced"},
        {
            "floor_id": "F11",
            "name": "Command Authority",
            "doctrine": "Identity and authority boundary",
        },
        {"floor_id": "F12", "name": "Injection Defense", "doctrine": "Prompt and input defense"},
        {"floor_id": "F13", "name": "Sovereign Override", "doctrine": "Human final authority"},
    ]


async def _invoke_stdio_tool(handler: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    handler_name = getattr(handler, "__name__", "")

    from arifosmcp.runtime.sessions import get_session_identity

    if not arguments.get("actor_id"):
        sid = arguments.get("session_id")
        if sid:
            session_info = get_session_identity(sid)
            if session_info:
                arguments["actor_id"] = session_info.get("actor_id")

    if handler_name == "vault_seal":
        from arifosmcp.runtime.tools import arifos_vault

        return await arifos_vault(**arguments)

    result = handler(**arguments)
    if inspect.isawaitable(result):
        result = await result
    if result.__class__.__name__ == "RuntimeEnvelope":
        from .output_formatter import format_output

        result.platform_context = "stdio"
        return format_output(result, {"verbose": False, "debug": False})
    if hasattr(result, "model_dump"):
        envelope = result.model_dump(mode="json")
    elif isinstance(result, dict):
        envelope = result
    else:
        envelope = {"ok": True, "payload": result}

    return envelope


def _run_minimal_stdio_server() -> None:
    from mcp import types as mcp_types

    from .server import create_aaa_mcp_server
    from .tool_spec import LEGACY_NAME_MAP, TOOLS, normalize_tool_name
    from .tools import CANONICAL_TOOL_HANDLERS
    from .tools_hardened_dispatch import get_tool_handler

    # FastMCP instance for resources + prompts (all three surfaces)
    _mcp = create_aaa_mcp_server()

    # Persistent event loop — shared across all async bridge calls (resources/prompts)
    _async_loop = asyncio.new_event_loop()

    # tool_handlers uses arif_* names (CANONICAL_TOOL_HANDLERS keys)
    tool_handlers: dict[str, Any] = CANONICAL_TOOL_HANDLERS.copy()

    # Build spec lookup from canonical TOOLS tuple
    _spec_by_name = {spec.name: spec for spec in TOOLS}

    def tool_descriptor(name: str) -> dict[str, Any]:
        spec = _spec_by_name.get(name)
        if spec is not None:
            return {
                "name": name,
                "description": spec.description,
                "inputSchema": spec.input_schema,
            }
        return {
            "name": name,
            "description": name,
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": True},
        }

    def send(message: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(message, default=_json_default) + "\n")
        sys.stdout.flush()

    # ── Async helpers for resources + prompts (delegate to FastMCP) ──────────

    async def _list_resources() -> list[dict[str, Any]]:
        resources = await _mcp.list_resources()
        return [
            {
                "uri": str(r.uri),
                "name": r.name,
                "description": r.description or "",
                "mimeType": getattr(r, "mime_type", None) or "text/plain",
            }
            for r in resources
        ]

    async def _read_resource(uri: str) -> dict[str, Any]:
        result = await _mcp.read_resource(uri)
        contents = []
        if hasattr(result, "contents"):
            for c in result.contents:
                if hasattr(c, "text"):
                    contents.append({"uri": str(c.uri), "mimeType": getattr(c, "mime_type", "text/plain") or "text/plain", "text": c.text})
                elif hasattr(c, "data"):
                    contents.append({"uri": str(c.uri), "mimeType": "application/octet-stream", "data": c.data})
        return {"contents": contents}

    async def _list_prompts() -> list[dict[str, Any]]:
        prompts = await _mcp.list_prompts()
        return [
            {
                "name": p.name,
                "description": p.description or "",
                "arguments": [
                    {"name": a.name, "description": a.description or "", "required": getattr(a, "required", False)}
                    for a in (getattr(p, "arguments", []) or [])
                ],
            }
            for p in prompts
        ]

    async def _get_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        prompt = await _mcp.get_prompt(name, arguments or {})
        messages = []
        if hasattr(prompt, "messages"):
            for m in prompt.messages:
                if hasattr(m, "role"):
                    role = m.role
                elif hasattr(m, "_role"):
                    role = m._role
                else:
                    role = "system"
                content = getattr(m, "content", "")
                if hasattr(content, "text"):
                    content = content.text
                elif hasattr(content, "texts"):
                    content = "".join(getattr(t, "text", str(t)) for t in content.texts)
                messages.append({"role": role, "content": {"type": "text", "text": content}})
        return {"description": getattr(prompt, "description", "") or "", "messages": messages}

    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            break

        raw = line.decode("utf-8", errors="replace").strip()
        if not raw:
            continue

        try:
            request = json.loads(raw)
        except json.JSONDecodeError:
            continue

        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params") or {}

        if method == "notifications/initialized":
            continue

        # ── initialize — declare ALL THREE surfaces ───────────────────────────
        if method == "initialize":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": mcp_types.LATEST_PROTOCOL_VERSION,
                        "capabilities": {
                            "tools": {"listChanged": True},
                            "resources": {"subscribe": True, "listChanged": True},
                            "prompts": {"listChanged": True},
                        },
                        "serverInfo": {
                            "name": "arifOS Sovereign Intelligence Kernel",
                            "version": "2026.03.24-HARDENED",
                        },
                    },
                }
            )
            continue

        # ── resources/list ───────────────────────────────────────────────────
        if method == "resources/list":
            try:
                resources = _async_loop.run_until_complete(_list_resources())
                send({"jsonrpc": "2.0", "id": request_id, "result": {"resources": resources}})
            except Exception as exc:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}})
            continue

        # ── resources/read ───────────────────────────────────────────────────
        if method == "resources/read":
            uri = params.get("uri")
            if not uri:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing uri"}})
                continue
            try:
                result = _async_loop.run_until_complete(_read_resource(uri))
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except Exception as exc:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}})
            continue

        # ── prompts/list ─────────────────────────────────────────────────────
        if method == "prompts/list":
            try:
                prompts = _async_loop.run_until_complete(_list_prompts())
                send({"jsonrpc": "2.0", "id": request_id, "result": {"prompts": prompts}})
            except Exception as exc:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}})
            continue

        # ── prompts/get ─────────────────────────────────────────────────────
        if method == "prompts/get":
            name = params.get("name")
            if not name:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing name"}})
                continue
            try:
                arguments = params.get("arguments") or {}
                result = _async_loop.run_until_complete(_get_prompt(name, arguments))
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except Exception as exc:
                send({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32000, "message": str(exc)}})
            continue

        # ── tools/list ───────────────────────────────────────────────────────
        if method == "tools/list":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": [tool_descriptor(name) for name in tool_handlers]},
                }
            )
            continue

        # ── tools/call ──────────────────────────────────────────────────────
        if method == "tools/call":
            name = normalize_tool_name(params.get("name", ""))
            name = LEGACY_NAME_MAP.get(name, name)
            arguments = params.get("arguments") or {}
            handler = tool_handlers.get(name) or get_tool_handler(name)
            if handler is None:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {name}"},
                    }
                )
                continue

            try:
                envelope = asyncio.run(_invoke_stdio_tool(handler, arguments))
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": json.dumps(envelope)}],
                            "isError": not envelope.get("ok", True),
                        },
                    }
                )
            except Exception as exc:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                )
            continue

        if request_id is not None:
            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"},
                }
            )


def main() -> None:
    # Accept ARIFOS_MCP_* env vars as deployment-friendly aliases
    if not os.getenv("AAA_MCP_TRANSPORT") and os.getenv("ARIFOS_MCP_TRANSPORT"):
        os.environ["AAA_MCP_TRANSPORT"] = os.environ["ARIFOS_MCP_TRANSPORT"]
    if not os.getenv("HOST") and os.getenv("ARIFOS_MCP_HOST"):
        os.environ["HOST"] = os.environ["ARIFOS_MCP_HOST"]
    if not os.getenv("PORT") and os.getenv("ARIFOS_MCP_PORT"):
        os.environ["PORT"] = os.environ["ARIFOS_MCP_PORT"]

    _bootstrap_environment()

    # P0 FIX: Robust mode detection
    mode = os.getenv("AAA_MCP_TRANSPORT", "stdio")
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        mode = sys.argv[1]

    mode = mode.lower()
    os.environ["AAA_MCP_TRANSPORT"] = mode
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    # For HTTP mode, use the pre-configured app from server.py (includes dashboard)
    if mode in ("http", "streamable-http"):
        import uvicorn

        from .server import app

        uvicorn.run(app, host=host, port=port, log_level="info")
        return

    if mode == "stdio":
        os.environ.setdefault("ARIFOS_MINIMAL_STDIO", "1")
        _run_minimal_stdio_server()
        return
    else:
        from .server import create_aaa_mcp_server

        mcp = create_aaa_mcp_server()

    try:
        run_server(mcp, mode=mode, host=host, port=port)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
