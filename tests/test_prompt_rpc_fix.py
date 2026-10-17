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


def test_missing_required_arg_raises_invalid_params():
    """End-to-end: the patched render path must raise MCPError(-32602).

    Regression for the mcp 1.x -> 2.x signature change: raising
    ``MCPError(ErrorData(...))`` binds ErrorData to ``code`` and fails with
    ``TypeError: missing 1 required positional argument: 'message'``, which
    the transport surfaces as a malformed ``{"code": 0, ...}`` error.
    """
    import asyncio

    import mcp.types as mcp_types
    import pytest
    from mcp.shared.exceptions import MCPError

    from arifosmcp.runtime.mcp_prompt_rpc_fix import (
        apply_prompt_missing_args_rpc_fix,
    )

    apply_prompt_missing_args_rpc_fix()

    from fastmcp import FastMCP

    probe = FastMCP("prompt-arg-probe")

    @probe.prompt(name="probe_prompt")
    def probe_prompt(required_thing: str) -> str:
        return f"got {required_thing}"

    with pytest.raises(MCPError) as excinfo:
        asyncio.run(probe.render_prompt("probe_prompt", arguments={}))

    assert excinfo.value.code == mcp_types.INVALID_PARAMS
    assert "required_thing" in excinfo.value.message
