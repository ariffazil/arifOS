"""CLI entrypoint for arifOS AAA MCP."""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import select
import signal
import sys
import types
from typing import TYPE_CHECKING, Any

_fcntl_mod: types.ModuleType | None
try:
    import fcntl as _fcntl_mod
except ImportError:
    _fcntl_mod = None

fcntl = _fcntl_mod  # alias: if fcntl is not None: ... (None on Windows)

from .fastmcp_ext.transports import run_server  # noqa: E402

if TYPE_CHECKING:
    from fastmcp.server import FastMCP as FastMCPT  # noqa: I001
    from arifosmcp.runtime.session import get_session_identity as _gsi  # noqa: F401,I001


def _bootstrap_environment() -> None:
    try:
        mode = (
            sys.argv[1] if len(sys.argv) > 1 else os.getenv("AAA_MCP_TRANSPORT", "stdio")
        ).lower()
        if mode == "stdio":
            # Suppress ALL Python warnings in stdio mode — any text written to stdout
            # before the JSON-RPC handshake corrupts the stream and causes the MCP
            # client to close with EOF (e.g. requests urllib3 version mismatch,
            # memory_engine.py deprecation notice).
            import warnings

            warnings.filterwarnings("ignore")
            # Redirect stderr to devnull so deprecation prints don't bleed through
            sys.stderr = open(os.devnull, "w")  # noqa: SIM115
            os.environ.setdefault("ARIFOS_MINIMAL_STDIO", "1")
            for logger_name in (
                "fastmcp",
                "mcp",
                "uvicorn",
                "uvicorn.error",
                "uvicorn.access",
            ):
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
        {
            "law_id": "F1",
            "name": "Amanah",
            "doctrine": "Reversible or auditable action",
        },
        {
            "law_id": "F2",
            "name": "Haqq",
            "doctrine": "Truth and information fidelity",
        },
        {
            "law_id": "F3",
            "name": "Tri-Witness",
            "doctrine": "Consensus across witnesses",
        },
        {
            "law_id": "F4",
            "name": "Clarity",
            "doctrine": "Entropy must not increase destructively",
        },
        {"law_id": "F5", "name": "Peace2", "doctrine": "Stability before force"},
        {
            "law_id": "F6",
            "name": "Empathy",
            "doctrine": "Protect weakest stakeholder",
        },
        {
            "law_id": "F7",
            "name": "Humility",
            "doctrine": "Uncertainty admitted explicitly",
        },
        {
            "law_id": "F8",
            "name": "Wisdom",
            "doctrine": "Governed intelligence quality threshold",
        },
        {
            "law_id": "F9",
            "name": "Anti-Hantu",
            "doctrine": "No deceptive shadow behavior",
        },
        {
            "law_id": "L10",
            "name": "Ontology Lock",
            "doctrine": "Category precision enforced",
        },
        {
            "law_id": "L11",
            "name": "Command Authority",
            "doctrine": "Identity and authority boundary",
        },
        {
            "law_id": "L12",
            "name": "Injection Defense",
            "doctrine": "Prompt and input defense",
        },
        {
            "law_id": "L13",
            "name": "Sovereign Override",
            "doctrine": "Human final authority",
        },
    ]


async def _invoke_stdio_tool(handler: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    handler_name = getattr(handler, "__name__", "")

    # Lazy imports — placed here to avoid loading heavy deps at module init.
    # TYPE_CHECKING stubs (_gsi, _av) give the LSP name resolution;
    # the actual imports provide the runtime callable.
    from arifosmcp.runtime.session import get_session_identity as _gsi  # type: ignore[import]

    if not arguments.get("actor_id"):
        sid = arguments.get("session_id")
        if sid:
            session_info = _gsi(sid)
            if session_info:
                arguments["actor_id"] = session_info.get("actor_id")

    if handler_name == "vault_seal":
        # vault_seal maps to arif_vault_seal (handler_name would be _arif_vault_seal_tool).
        # The legacy "vault_seal" branch is unreachable — kept for traceability only.
        return dict(await handler(**arguments))  # type: ignore[arg-type]

    result = handler(**arguments)
    if inspect.isawaitable(result):
        result = await result
    if result.__class__.__name__ == "RuntimeEnvelope":
        from .output_formatter import format_output

        result.platform_context = "stdio"
        return dict(format_output(result, {"verbose": False, "debug": False}))  # type: ignore[arg-type]
    if hasattr(result, "model_dump"):
        envelope: dict[str, Any] = result.model_dump(mode="json")
    elif isinstance(result, dict):
        envelope = result
    else:
        envelope = {"ok": True, "payload": result}

    return envelope


def _run_minimal_stdio_server() -> None:

    from .dispatcher import get_tool_handler  # type: ignore[import]

    # Phase 2 — Federation bridge imports
    from .federation_bridge import (
        call_wealth_tool,
        call_well_tool,
        list_wealth_tools,
        list_well_tools,
    )
    from .geox_bridge import call_geox_tool, list_geox_tools
    from .server import create_aaa_mcp_server
    from .tool_spec import LEGACY_NAME_MAP, TOOLS, normalize_tool_name
    from .tools import CANONICAL_TOOL_HANDLERS

    # FastMCP instance for resources + prompts (all three surfaces)
    _mcp: FastMCPT = create_aaa_mcp_server()  # type: ignore[assignment]

    # Persistent event loop — shared across all async bridge calls (resources/prompts)
    _async_loop = asyncio.new_event_loop()

    # ── Federation surface: discover remote tools (Phase 2) ────────────────
    async def _discover_remote_tools() -> dict[str, dict[str, Any]]:
        _remote_tools: dict[str, dict[str, Any]] = {}

        async def _load_organ(list_fn, organ_name: str) -> None:
            try:
                tools = await list_fn()
                for tool in tools:
                    name = tool.get("name", "")
                    if not name:
                        continue
                    _remote_tools[name] = {
                        "organ": organ_name,
                        "schema": {
                            "name": name,
                            "description": tool.get("description", ""),
                            "inputSchema": tool.get(
                                "inputSchema",
                                {
                                    "type": "object",
                                    "properties": {},
                                    "additionalProperties": True,
                                },
                            ),
                        },
                    }
                logging.getLogger("arifosmcp").info(
                    f"Federation surface: discovered {len(tools)} tools from {organ_name}"
                )
            except Exception as exc:
                logging.getLogger("arifosmcp").warning(
                    f"Federation surface: {organ_name} discovery failed: {exc}"
                )

        await asyncio.gather(
            _load_organ(list_wealth_tools, "WEALTH"),
            _load_organ(list_well_tools, "WELL"),
            _load_organ(list_geox_tools, "GEOX"),
        )
        return _remote_tools

    _remote_tools: dict[str, dict[str, Any]] = _async_loop.run_until_complete(
        _discover_remote_tools()
    )

    # tool_handlers uses arif_* names (CANONICAL_TOOL_HANDLERS keys)
    tool_handlers: dict[str, Any] = CANONICAL_TOOL_HANDLERS.copy()

    # Build spec lookup from canonical TOOLS tuple
    _spec_by_name = {spec.name: spec for spec in TOOLS}

    # ── Memory Janitor (Phoenix-72) ──────────────────────────────────────────
    try:
        from .workers.memory_janitor import MemoryJanitor

        # Using the same loop if possible, or start it in background
        _async_loop.create_task(MemoryJanitor(interval_seconds=3600).run_loop())
        logging.getLogger("arifosmcp").info("Phoenix-72 Memory Janitor: ACTIVE (stdio)")
    except Exception as e:
        logging.getLogger("arifosmcp").warning(f"Failed to start Memory Janitor in stdio: {e}")

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
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            },
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
                    contents.append(
                        {
                            "uri": str(c.uri),  # type: ignore[attr-defined]
                            "mimeType": getattr(c, "mime_type", "text/plain") or "text/plain",
                            "text": c.text,  # type: ignore[attr-defined]
                        }
                    )
                elif hasattr(c, "data"):
                    contents.append(
                        {
                            "uri": str(c.uri),  # type: ignore[attr-defined]
                            "mimeType": "application/octet-stream",
                            "data": c.data,  # type: ignore[attr-defined]
                        }
                    )
        return {"contents": contents}

    async def _list_prompts() -> list[dict[str, Any]]:
        prompts = await _mcp.list_prompts()
        return [
            {
                "name": p.name,
                "description": p.description or "",
                "arguments": [
                    {
                        "name": a.name,
                        "description": a.description or "",
                        "required": getattr(a, "required", False),
                    }
                    for a in (getattr(p, "arguments", []) or [])
                ],
            }
            for p in prompts
        ]

    async def _get_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Fetch a prompt by name. Raises LookupError if not found (MCP code -32602)."""
        prompt = await _mcp.get_prompt(name, arguments or {})  # type: ignore[arg-type]
        # FastMCP returns None when prompt not found
        if prompt is None:
            raise LookupError(f"Unknown prompt: '{name}'")
        messages = []
        if hasattr(prompt, "messages"):  # type: ignore[attr-defined]
            for m in prompt.messages:  # type: ignore[attr-defined]
                if hasattr(m, "role"):
                    role = m.role
                elif hasattr(m, "_role"):
                    role = m._role
                else:
                    role = "system"
                content: object = getattr(m, "content", "")
                if hasattr(content, "text"):
                    content = (content).text  # type: ignore[union-attr]
                elif hasattr(content, "texts"):
                    content = "".join(getattr(t, "text", str(t)) for t in (content).texts)  # type: ignore[union-attr]
                messages.append({"role": role, "content": {"type": "text", "text": content}})
        return {
            "description": getattr(prompt, "description", "") or "",
            "messages": messages,
        }

    # PHOENIX-73C: Keepalive stdio lifecycle.
    # Tests may close stdin before the client connects (EOF on readline).
    # Instead of exiting on first EOF, the server stays alive until:
    #   - SIGTERM/SIGINT is received
    #   - ARIFOS_STDIO_SHUTDOWN_FD is writable (shutdown signal from test harness)
    #   - An explicit exit message is received
    _shutdown = False

    def _handle_signal(signum, frame):
        nonlocal _shutdown
        _shutdown = True

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    # stdin_fd must be defined unconditionally — used by select.select on all platforms.
    stdin_fd = sys.stdin.buffer.fileno()
    if fcntl is not None:
        # Non-blocking stdin: Linux/macOS only (fcntl is None on Windows).
        old_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)  # type: ignore[attr-defined]
        fcntl.fcntl(stdin_fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)  # type: ignore[attr-defined]

    _shutdown_fd_str = os.getenv("ARIFOS_STDIO_SHUTDOWN_FD")
    _shutdown_fd = int(_shutdown_fd_str) if _shutdown_fd_str else None

    while not _shutdown:
        # Wait for stdin with 1-second timeout — keeps server alive for late-connecting clients.
        r, _, _ = select.select([stdin_fd], [], [], 1.0)
        if not r:
            continue  # timeout — check shutdown flag and loop

        line = sys.stdin.buffer.readline()
        if not line:
            # EOF received — stdin closed by test harness.
            # Check if shutdown is explicitly requested via fd, else keep alive.
            if _shutdown_fd is not None:
                try:
                    w, _, _ = select.select([], [_shutdown_fd], [], 0)
                    if w:
                        os.read(_shutdown_fd, 1)  # consume shutdown signal
                        break
                except OSError:
                    pass
            # No explicit shutdown signal — stay alive (late client may still connect).
            continue

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
            client_version = params.get("protocolVersion")
            supported_versions = ["2024-11-05", "2025-11-25"]

            # Dynamic negotiation: use client's version if supported,
            # otherwise fallback to "2024-11-05"
            if client_version in supported_versions:
                negotiated_version = client_version
            else:
                negotiated_version = "2024-11-05"

            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": negotiated_version,
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
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"resources": resources},
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

        # ── resources/read ───────────────────────────────────────────────────
        if method == "resources/read":
            uri = params.get("uri")
            if not uri:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "Missing uri"},
                    }
                )
                continue
            try:
                result = _async_loop.run_until_complete(_read_resource(uri))
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except Exception as exc:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                )
            continue

        # ── prompts/list ─────────────────────────────────────────────────────
        if method == "prompts/list":
            try:
                prompts = _async_loop.run_until_complete(_list_prompts())
                send({"jsonrpc": "2.0", "id": request_id, "result": {"prompts": prompts}})
            except Exception as exc:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32000, "message": str(exc)},
                    }
                )
            continue

        # ── prompts/get ─────────────────────────────────────────────────────
        if method == "prompts/get":
            name = params.get("name")
            if not name:
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": "Missing name"},
                    }
                )
                continue
            try:
                arguments = params.get("arguments") or {}
                result = _async_loop.run_until_complete(_get_prompt(name, arguments))
                send({"jsonrpc": "2.0", "id": request_id, "result": result})
            except LookupError as exc:
                # MCP code -32602: Invalid params / Unknown resource
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32602, "message": str(exc)},
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

        # ── tools/list ───────────────────────────────────────────────────────
        if method == "tools/list":
            local_tools = [tool_descriptor(name) for name in tool_handlers]
            remote_tools = [rt["schema"] for rt in _remote_tools.values()]
            send(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": local_tools + remote_tools},
                }
            )
            continue

        # ── tools/call ──────────────────────────────────────────────────────
        if method == "tools/call":
            name = normalize_tool_name(params.get("name", ""))
            name = LEGACY_NAME_MAP.get(name, name)
            arguments = params.get("arguments") or {}

            # ── Remote tool proxy (Phase 2 — federated surface) ──────────────
            if name in _remote_tools:
                organ = _remote_tools[name]["organ"]
                try:
                    if organ == "WEALTH":
                        coro = call_wealth_tool(name, arguments)
                    elif organ == "WELL":
                        coro = call_well_tool(name, arguments)
                    elif organ == "GEOX":
                        coro = call_geox_tool(name, arguments)
                    else:
                        raise RuntimeError(f"Unknown organ: {organ}")

                    raw_result = _async_loop.run_until_complete(coro)

                    # Normalise response format per organ
                    if organ == "GEOX":
                        # GEOX returns raw dict — wrap in standard MCP content
                        result_payload = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(raw_result, default=_json_default),
                                }
                            ],
                        }
                    else:
                        # WEALTH / WELL return standard FastMCP ToolResult dict
                        result_payload = raw_result

                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": result_payload,
                        }
                    )
                except Exception as exc:
                    send(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": f"{organ} proxy error: {exc}",
                            },
                        }
                    )
                continue

            # ── Local tool ───────────────────────────────────────────────────
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
                local_payload: dict[str, Any] = {
                    "content": [{"type": "text", "text": json.dumps(envelope)}],
                }
                # MCP spec: isError only present when true (omitted on success)
                if not envelope.get("ok", True):
                    local_payload["isError"] = True
                send(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": local_payload,
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

        from .server import app  # type: ignore[import]

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
