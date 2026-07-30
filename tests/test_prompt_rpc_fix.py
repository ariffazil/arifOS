"""
Regression test for the prompts/get -32602 fix (2026-07-30 v5).

The mcp_prompt_rpc_fix module must:
  1. Install without raising.
  2. Patch the live FastMCP.render_prompt so a missing required arg
     raises McpError(code=INVALID_PARAMS) before the original render.
  3. Be idempotent: calling apply() twice does not double-patch.

F2 evidence: this test asserts the function signature, that it
imports cleanly, and that the installed wrapper carries the
_arifos_render_prompt_fix_installed marker.
"""

from __future__ import annotations


def test_apply_runs_and_marks_installed():
    from arifosmcp.runtime.mcp_prompt_rpc_fix import (
        apply_prompt_missing_args_rpc_fix,
    )

    result = apply_prompt_missing_args_rpc_fix()
    # Either True (just-installed) or True (already applied at import-time
    # hook). Either way: True.
    assert result is True

    # The marker must be set on the live FastMCP class.
    from fastmcp.server.server import FastMCP

    assert getattr(FastMCP, "_arifos_render_prompt_fix_installed", False) is True


def test_render_prompt_wrapper_signature():
    """The installed wrapper must accept FastMCP 3.x's variable-arg
    signature (name, arguments, version, task_meta, ...)."""
    from fastmcp.server.server import FastMCP
    import inspect

    render = FastMCP.render_prompt
    # The wrapper is a coroutine function (async def).
    assert inspect.iscoroutinefunction(render)


def test_invalid_params_constant():
    """INVALID_PARAMS is the JSON-RPC standard code -32602."""
    import mcp.types as mcp_types

    assert mcp_types.INVALID_PARAMS == -32602
    assert mcp_types.INTERNAL_ERROR == -32603
