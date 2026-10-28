"""Public-surface regression tests for the five coordination tools.

Failure class (measured 2026-10-29, public path https://mcp.arif-fazil.com/mcp):
all five coordination tools — read_resource, search_resources, arif_research,
arif_recall, arif_delegate — returned "Error calling tool 'X'" for EVERY caller.

Cause (source-read, not inferred):
  * arifosmcp/runtime/ingress_middleware.py assigns `msg.arguments["_envelope"]`
    and setdefaults `actor_id` / `session_id` for every tool call, BEFORE
    FastMCP validates the input.
  * The middleware strips unknown fields only for tools whose parameter set is
    known (`_tool_param_sets`, populated by `register_tool_params`).
  * The canonical tools register their params. The five coordination tools are
    registered on a different path and never did — so the filter was skipped
    AND their signatures rejected the injected envelope fields.

  => ValueError: CONTRACT_VIOLATION: _envelope / actor_id / session_id:
     Unexpected keyword argument.

These tests pin both halves of the fix:
  1. the five tools declare the envelope fields in their signature, and
  2. their parameter sets are registered with the ingress middleware, so a
     caller-supplied extra field (e.g. session_token) is absorbed instead of
     killing the call.
"""

from __future__ import annotations

import inspect

import pytest

from arifosmcp.tools.copilot_facade import arif_delegate, arif_recall, arif_research
from arifosmcp.tools.resource_bridge import read_resource, search_resources

ENVELOPE_FIELDS = {"_envelope", "actor_id", "session_id"}

FIVE = {
    "read_resource": read_resource,
    "search_resources": search_resources,
    "arif_research": arif_research,
    "arif_recall": arif_recall,
    "arif_delegate": arif_delegate,
}


@pytest.mark.parametrize("name", sorted(FIVE))
def test_tool_signature_tolerates_injected_envelope(name):
    """Every coordination tool must accept what the ingress middleware injects."""
    params = set(inspect.signature(FIVE[name]).parameters.keys())
    missing = ENVELOPE_FIELDS - params
    assert not missing, f"{name} would die with CONTRACT_VIOLATION on: {sorted(missing)}"


@pytest.mark.parametrize("name", sorted(FIVE))
def test_tool_param_set_is_registered_with_ingress_middleware(name):
    """Unknown-field filtering only runs for tools with a registered param set.

    An unregistered tool skips the filter entirely, so any extra field a caller
    sends reaches FastMCP unfiltered and raises CONTRACT_VIOLATION.
    """
    from arifosmcp.runtime import ingress_middleware as _im

    # Importing the server module is what runs register_tools(), which is what
    # registers the param sets. Without it the middleware instance does not exist.
    import arifosmcp.server  # noqa: F401

    middleware = getattr(_im, "_ARIFOS_INGRESS_INSTANCE", None)
    assert middleware is not None, "ingress middleware instance not published"

    known = getattr(middleware, "_tool_param_sets", {})
    assert name in known, f"{name} has no registered param set — unknown-field filter would be skipped"

    expected = set(inspect.signature(FIVE[name]).parameters.keys())
    assert known[name] == expected, f"{name} param set drifted from its signature"


@pytest.mark.asyncio
async def test_coordination_tools_survive_an_undeclared_caller_field():
    """A caller that sends session_token must not kill the call.

    session_token is what the canonical tools accept; a client that sends the
    standard envelope to every tool would previously crash all five.
    """
    from arifosmcp.server import mcp

    calls = [
        ("read_resource", {"uri": "arifos://vitals", "session_token": "act_v1.test"}),
        ("search_resources", {"query": "vitals", "session_token": "act_v1.test"}),
        ("arif_recall", {"query": "housekeeping", "session_token": "act_v1.test"}),
        ("arif_delegate", {"query": "probe organ health", "session_token": "act_v1.test"}),
        ("arif_research", {"query": "probe federation", "session_token": "act_v1.test"}),
    ]
    for name, args in calls:
        result = await mcp.call_tool(name, args, run_middleware=True)
        is_error = getattr(result, "is_error", getattr(result, "isError", False))
        assert not is_error, f"{name} returned an error with an undeclared field"
        assert result.content, f"{name} returned no content"


@pytest.mark.asyncio
async def test_coordination_tools_survive_the_injected_envelope():
    """The exact payload the ingress middleware injects must be tolerated."""
    from arifosmcp.server import mcp

    envelope = {"_envelope": {"trace_id": "t"}, "actor_id": "probe", "session_id": "probe"}
    for name, extra in (
        ("read_resource", {"uri": "arifos://vitals"}),
        ("search_resources", {"query": "vitals"}),
        ("arif_recall", {"query": "housekeeping"}),
        ("arif_delegate", {"query": "probe organ health"}),
        ("arif_research", {"query": "probe federation"}),
    ):
        result = await mcp.call_tool(name, {**extra, **envelope}, run_middleware=True)
        is_error = getattr(result, "is_error", getattr(result, "isError", False))
        assert not is_error, f"{name} returned an error with the injected envelope"
        assert result.content, f"{name} returned no content"


@pytest.mark.asyncio
async def test_coordination_tools_never_report_ok_on_empty_truth():
    """Honesty contract: degraded, never a false 'ok' on empty evidence.

    The live providers were exhausted during the 2026-10-29 probe (Groq 429,
    Cerebras 402, Gemini transport error, Postgres auth failure). A facade that
    reported 'ok' with zero facts in that state would be lying.
    """
    from arifosmcp.tools.copilot_facade import arif_recall as recall_fn

    result = await recall_fn(query="housekeeping-regression-probe")
    assert result["status"] in ("ok", "degraded", "error")
    if result["status"] == "ok":
        assert result["entries"], "reported ok with zero entries"
    else:
        assert result.get("degraded_reasons"), "degraded without a machine-readable reason"
