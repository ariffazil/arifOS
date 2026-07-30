"""
mcp_prompt_rpc_fix — Missing prompt args → JSON-RPC -32602 Invalid params.

FastMCP raises ValueError("Missing required arguments: …") then wraps it in
PromptError. Unhandled non-McpError exceptions become ErrorData(code=0) or
-32603 INTERNAL_ERROR in the low-level MCP server.

MCP clients expect -32602 (Invalid params) for missing prompt arguments.
This boot-time patch raises McpError(-32602) at the validation site so the
error never collapses into INTERNAL_ERROR / code 0.

Applied once from arifosmcp.runtime.__main__ (or server boot).

DITEMPA BUKAN DIBERI — 2026-07-30 A3A correction.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_APPLIED = False


def apply_prompt_missing_args_rpc_fix() -> bool:
    """Monkeypatch FunctionPrompt.render to emit -32602 on missing required args.

    Returns True if patch applied, False if already applied or import failed.
    """
    global _APPLIED
    if _APPLIED:
        return False

    try:
        import mcp.types as mcp_types
        from mcp.shared.exceptions import McpError
    except Exception as e:  # pragma: no cover
        logger.warning("prompt RPC fix: mcp import failed: %s", e)
        return False

    import importlib

    try:
        mod = importlib.import_module("fastmcp.prompts.function_prompt")
        FunctionPrompt = getattr(mod, "FunctionPrompt", None)
    except Exception as e:  # pragma: no cover
        logger.warning("prompt RPC fix: import FunctionPrompt failed: %s", e)
        return False

    if FunctionPrompt is None or not hasattr(FunctionPrompt, "render"):
        logger.warning("prompt RPC fix: FunctionPrompt.render not found")
        return False

    original_render = FunctionPrompt.render

    async def render_with_invalid_params(
        self: Any,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        # Pre-validate required args → MCP Invalid params (-32602)
        # Must raise McpError before FastMCP wraps ValueError as PromptError
        # (PromptError becomes ErrorData code=0 / -32603 in low-level handler).
        args_spec = getattr(self, "arguments", None) or []
        if args_spec:
            required: set[str] = set()
            for a in args_spec:
                name = getattr(a, "name", None) if not isinstance(a, dict) else a.get("name")
                req = (
                    getattr(a, "required", False)
                    if not isinstance(a, dict)
                    else bool(a.get("required"))
                )
                if name and req:
                    required.add(str(name))
            provided = set((arguments or {}).keys())
            missing = required - provided
            if missing:
                raise McpError(
                    mcp_types.ErrorData(
                        code=mcp_types.INVALID_PARAMS,  # -32602
                        message=f"Invalid params: Missing required arguments: {sorted(missing)}",
                    )
                )
        return await original_render(self, arguments)

    FunctionPrompt.render = render_with_invalid_params  # type: ignore[method-assign]
    _APPLIED = True
    logger.info(
        "Applied prompts/get missing-args fix: → JSON-RPC -32602 Invalid params"
    )
    return True
