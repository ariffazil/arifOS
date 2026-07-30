"""
mcp_prompt_rpc_fix — Missing prompt args → JSON-RPC -32602 Invalid params.

Discovery (2026-07-30 v5, server-side): FastMCP 3.x dispatches
`prompts/get` through `FastMCP._render_prompt` (server.py:1635) — NOT
through the lowlevel `request_handlers[GetPromptRequest]`. The render
path is `render_prompt → prompt._render(arguments, task_meta=...) →
FunctionPrompt.render`.

Prior patches on `Prompt.render` and the lowlevel handler are inert
under FastMCP 3.x because that path is no longer used.

Working strategy: replace `FastMCP._render_prompt` with a wrapper that
pre-validates required arguments from `prompt.arguments` BEFORE
calling the original. The wrapper raises `McpError(code=INVALID_PARAMS)`
at the boundary; the existing `except McpError: raise` clause in
`render_prompt` propagates the code unchanged.

Reversible: `FastMCP._arifos_render_prompt_fix_installed` is the marker.
Uninstall by restoring the original method.

DITEMPA BUKAN DIBERI — 2026-07-30 A3A correction.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_APPLIED = False


def apply_prompt_missing_args_rpc_fix() -> bool:
    """Patch FastMCP._render_prompt so missing prompt args return
    JSON-RPC -32602 Invalid params (per MCP / JSON-RPC 2.0)."""
    global _APPLIED
    print("[mcp_prompt_rpc_fix] apply() called, _APPLIED=", _APPLIED, flush=True)
    if _APPLIED:
        return True

    try:
        import mcp.types as mcp_types
        from mcp.shared.exceptions import McpError
    except Exception as e:  # pragma: no cover
        logger.warning("prompt RPC fix: mcp import failed: %s", e)
        return False

    try:
        # FastMCP 3.x lives in `fastmcp.server.server`; the legacy
        # `mcp.server.fastmcp.server` re-export points at the older
        # class which does NOT have `render_prompt`. Patch the actual
        # class the running service uses (the one with `render_prompt`).
        from fastmcp.server.server import FastMCP
    except Exception as e:  # pragma: no cover
        logger.warning("prompt RPC fix: FastMCP import failed: %s", e)
        return False

    if getattr(FastMCP, "_arifos_render_prompt_fix_installed", False):
        _APPLIED = True
        return True

    original_render_prompt = FastMCP.render_prompt

    async def render_prompt_with_invalid_params(
        self: Any, *args: Any, **kwargs: Any
    ) -> Any:
        # FastMCP 3.x render_prompt signature is broad (name, arguments,
        # version, task_meta, ...). Be tolerant of all positional and
        # keyword forms so we don't break future call sites.
        name = kwargs.pop("name", args[0] if args else None)
        arguments = kwargs.pop("arguments", args[1] if len(args) > 1 else None)
        version = kwargs.pop("version", args[2] if len(args) > 2 else None)
        try:
            arguments = arguments or {}
            prompt = await self.get_prompt(name, version=version)
            if prompt is not None:
                args_spec = getattr(prompt, "arguments", None) or []
                required: set[str] = set()
                for a in args_spec:
                    a_name = (
                        getattr(a, "name", None)
                        if not isinstance(a, dict)
                        else a.get("name")
                    )
                    a_req = (
                        getattr(a, "required", False)
                        if not isinstance(a, dict)
                        else bool(a.get("required"))
                    )
                    if a_name and a_req:
                        required.add(str(a_name))
                missing = required - set(
                    arguments.keys() if isinstance(arguments, dict) else []
                )
                if missing:
                    raise McpError(
                        mcp_types.ErrorData(
                            code=mcp_types.INVALID_PARAMS,  # -32602
                            message=(
                                f"Invalid params: Missing required arguments: "
                                f"{sorted(missing)}"
                            ),
                        )
                    )
        except McpError:
            raise
        return await original_render_prompt(self, *args, **kwargs)

    FastMCP.render_prompt = render_prompt_with_invalid_params  # type: ignore[method-assign]
    FastMCP._arifos_render_prompt_fix_installed = True  # type: ignore[attr-defined]

    _APPLIED = True
    msg = (
        "Applied prompts/get missing-args fix: -> JSON-RPC -32602 Invalid params "
        "(patched FastMCP._render_prompt)"
    )
    logger.warning(msg)
    print(msg, flush=True)
    return True
