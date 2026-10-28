"""G3 — invalid-mode guard on the PUBLIC MCP path (Arif ratified 2026-10-29).

Failure class closed
--------------------
An undeclared ``mode`` used to fall through to a default branch:

* ``arif_observe(mode=<undeclared>)`` → ``UnboundLocalError`` (a crash, and an
  error the calling model cannot act on)
* ``arif_judge(mode=<undeclared>)``   → silently entered the judgment path and
  returned a verdict the caller never asked for

MCP SEP-1303 ("Input Validation Errors as Tool Execution Errors", Final)
requires input validation errors to be reported as TOOL EXECUTION ERRORS —
``isError: true`` with an actionable message — so the calling model can read
the error and self-correct.

Why these tests drive the MCP client
-------------------------------------
The 2026-10-28 failure class was exactly "passes every in-process unit test,
dies on the public path" (CONTRACT_VIOLATION on the public path while every
in-process test was green). A handler-level assertion would not have caught
this. These tests register the real surface and call it the way a remote
client calls it.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import inspect
import os

import pytest

from arifosmcp.runtime.input_contract import allowed_modes, invalid_mode

INVALID_MODE = "totally_invalid_mode_xyz"


@pytest.fixture(scope="module")
def mcp_server():
    """The real public surface, registered the way the kernel registers it."""
    from fastmcp import FastMCP

    from arifosmcp.runtime.tools import register_tools

    mcp = FastMCP("g3-mode-guard-test")
    register_tools(mcp)
    return mcp


async def _call(client, name: str, arguments: dict):
    """Call a tool and return the MCP result WITHOUT raising on tool errors.

    FastMCP's client re-raises tool execution errors by default; the wire
    shape we care about (SEP-1303) is ``isError: true`` on the result.
    """
    kwargs: dict = {}
    if "raise_on_error" in inspect.signature(client.call_tool).parameters:
        kwargs["raise_on_error"] = False
    try:
        return await client.call_tool(name, arguments, **kwargs)
    except Exception as exc:  # older clients without raise_on_error
        return exc


def _is_error(result) -> bool:
    return bool(getattr(result, "is_error", False) or getattr(result, "isError", False))


def _text(result) -> str:
    try:
        return "\n".join(getattr(c, "text", "") or "" for c in (result.content or []))
    except Exception:
        return str(result)


@pytest.mark.asyncio
async def test_invalid_mode_is_tool_execution_error_on_public_path(mcp_server):
    """arif_observe (sync handler) — undeclared mode must be isError:true."""
    from fastmcp import Client

    async with Client(mcp_server) as client:
        result = await _call(
            client,
            "arif_observe",
            {"mode": INVALID_MODE, "query": "g3 probe"},
        )

    assert _is_error(result), (
        "G3: an undeclared mode must be reported as a TOOL EXECUTION ERROR "
        f"(SEP-1303, isError:true). Got: {_text(result)[:300]}"
    )
    assert "INVALID_MODE" in _text(result)
    assert INVALID_MODE in _text(result)


@pytest.mark.asyncio
async def test_invalid_mode_is_tool_execution_error_on_public_path_async_tool(mcp_server):
    """arif_judge (async handler) — the path that silently judged before."""
    from fastmcp import Client

    async with Client(mcp_server) as client:
        result = await _call(
            client,
            "arif_judge",
            {"mode": INVALID_MODE, "candidate": "g3 probe"},
        )

    assert _is_error(result), (
        "G3: an undeclared mode on arif_judge must be isError:true, not a "
        f"verdict the caller never requested. Got: {_text(result)[:300]}"
    )
    assert "INVALID_MODE" in _text(result)


@pytest.mark.asyncio
async def test_invalid_mode_error_names_the_valid_modes(mcp_server):
    """SEP-1303 exists so the model can self-correct — the message must say
    which modes are valid, not merely that the mode was wrong."""
    from fastmcp import Client

    async with Client(mcp_server) as client:
        result = await _call(
            client,
            "arif_observe",
            {"mode": INVALID_MODE, "query": "g3 probe"},
        )

    text = _text(result)
    for mode in allowed_modes("arif_observe"):
        assert mode in text, f"G3: valid mode '{mode}' not named in the error: {text[:300]}"


@pytest.mark.asyncio
async def test_valid_mode_is_not_rejected(mcp_server):
    """The guard must not become a new blocker for admissible calls."""
    from fastmcp import Client

    async with Client(mcp_server) as client:
        result = await _call(client, "arif_observe", {"mode": "vitals"})

    assert "INVALID_MODE" not in _text(result), (
        f"G3: a valid mode was rejected by the guard: {_text(result)[:300]}"
    )


@pytest.mark.asyncio
async def test_advertised_enum_matches_the_guard(mcp_server):
    """Anti-drift: the guard may only reject what the wire does not offer.

    The advertised input_schema enum and the guard's allowed set must be the
    same list — otherwise a client that obeys the schema could still be
    rejected, or a mode the wire dropped could still be accepted.
    """
    from fastmcp import Client

    async with Client(mcp_server) as client:
        tools = {t.name: t for t in await client.list_tools()}

    for name in ("arif_observe", "arif_judge"):
        schema = (tools[name].inputSchema or {}).get("properties", {}).get("mode", {})
        advertised = tuple(schema.get("enum") or ())
        guarded = allowed_modes(name)
        assert advertised == guarded, (
            f"G3 drift on {name}: wire advertises {advertised} but the guard "
            f"allows {guarded}. Schema and guard must read one source."
        )


@pytest.mark.asyncio
async def test_guard_is_kill_switchable(mcp_server):
    """Reversibility (F1 AMANAH): ARIFOS_MODE_GUARD=0 disables it with no
    code change, so the ratified behaviour can be turned off at deploy time."""
    from fastmcp import Client

    previous = os.environ.get("ARIFOS_MODE_GUARD")
    os.environ["ARIFOS_MODE_GUARD"] = "0"
    try:
        async with Client(mcp_server) as client:
            result = await _call(
                client,
                "arif_observe",
                {"mode": INVALID_MODE, "query": "g3 probe"},
            )
        assert "INVALID_MODE" not in _text(result), (
            f"G3: kill switch did not disable the guard: {_text(result)[:300]}"
        )
    finally:
        if previous is None:
            os.environ.pop("ARIFOS_MODE_GUARD", None)
        else:
            os.environ["ARIFOS_MODE_GUARD"] = previous


def test_guard_only_covers_the_ratified_scope():
    """Arif scoped G3 to observe + judge. Other verbs stay untouched."""
    from arifosmcp.runtime.input_contract import GUARDED_TOOLS

    assert GUARDED_TOOLS == frozenset({"arif_observe", "arif_judge"})
    assert invalid_mode("arif_think", {"mode": "not_a_mode"}) is None
    assert invalid_mode("arif_route", {"mode": "not_a_mode"}) is None
