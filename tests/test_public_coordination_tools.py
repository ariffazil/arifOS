"""Post-retirement surface tests for the coordination lane (F13 2026-10-29).

Failure class (measured 2026-10-29, public path https://mcp.arif-fazil.com/mcp):
five coordination channels sat on the public wire — read_resource,
search_resources, arif_research, arif_recall, arif_delegate — and after the
envelope fix three of them were still facades with nothing behind them
(keputusan probe luar 02:21: research/recall/delegate mati, memory recall sampah).

Decision (recommended by external probe 2026-10-29 02:21; ratified by Arif
11:46 MYT, F13): the public wire is exactly 9 tools =
KERNEL_ABI_8 + arif_report.

  * read_resource / search_resources → absorbed as arif_observe modes
    resource_read / resource_search (the bridge functions remain the internal
    implementation behind those modes).
  * arif_research / arif_recall / arif_delegate → retired; jobs owned by
    arif_observe / arif_memory / arif_route.

These tests pin the new contract:
  1. the five names are NOT on the wire (public_exposed_tool_names);
  2. a wire call to a retired name fails honestly (unknown tool);
  3. the observe modes exist and answer;
  4. the surviving bridge/facade functions keep their envelope tolerance and
     honesty contracts.
"""

from __future__ import annotations

import inspect

import pytest

from arifosmcp.tools.copilot_facade import arif_delegate, arif_recall, arif_research
from arifosmcp.tools.resource_bridge import read_resource, search_resources

ENVELOPE_FIELDS = {"_envelope", "actor_id", "session_id"}

RETIRED_FIVE = (
    "read_resource",
    "search_resources",
    "arif_research",
    "arif_recall",
    "arif_delegate",
)


def test_retired_names_are_not_on_the_public_wire():
    from arifosmcp.runtime.public_surface import public_exposed_tool_names

    exposed = set(public_exposed_tool_names())
    for name in RETIRED_FIVE:
        assert name not in exposed, f"{name} was retired (F13 2026-10-29) but is still exposed"


@pytest.mark.asyncio
@pytest.mark.parametrize("name", sorted(RETIRED_FIVE))
async def test_wire_call_to_retired_name_fails_honestly(name):
    """A retired tool must be unknown on the wire — never advertised-but-broken."""
    from arifosmcp.server import mcp

    args = {"uri": "arifos://vitals"} if name == "read_resource" else {"query": "probe"}
    try:
        result = await mcp.call_tool(name, args, run_middleware=True)
    except Exception:
        return  # raised = not served = honest absence
    is_error = getattr(result, "is_error", getattr(result, "isError", False))
    assert is_error, f"{name} is retired but the wire still serves it"


def test_observe_resource_modes_answer():
    """The absorbed modes must answer through the observe envelope."""
    from arifosmcp.tools.sense import arif_observe

    read_res = arif_observe(
        mode="resource_read",
        uri="arifos://vitals",
        actor_id="probe",
        session_id="probe",
    )
    assert isinstance(read_res, dict)
    # Kernel envelope normalizes status to upper case — compare honestly.
    assert str(read_res.get("status", "")).upper() == "OK", (
        f"resource_read did not answer ok: {str(read_res)[:300]}"
    )
    payload_r = read_res.get("result", read_res)
    assert str(payload_r.get("resource", {}).get("status", "")).upper() == "OK", (
        "resource_read inner bridge not ok"
    )

    search_res = arif_observe(
        mode="resource_search", query="vitals", actor_id="probe", session_id="probe"
    )
    assert isinstance(search_res, dict)
    assert str(search_res.get("status", "")).upper() == "OK", (
        f"resource_search did not answer ok: {str(search_res)[:300]}"
    )
    payload = search_res.get("result", search_res)
    assert str(payload.get("resource", {}).get("status", "")).upper() == "OK", (
        "resource_search lost its registry"
    )
    assert payload["resource"].get("count", 0) >= 1


def test_observe_resource_read_requires_uri():
    """F2: a resource_read without a URI must HOLD, not fabricate."""
    from arifosmcp.tools.sense import arif_observe

    res = arif_observe(mode="resource_read", actor_id="probe", session_id="probe")
    assert isinstance(res, dict)
    assert str(res.get("status", "")).upper() == "HOLD", f"missing uri must hold: {str(res)[:300]}"
    assert res.get("meta", {}).get("violated_laws") == ["F2"] or res.get("verdict"), (
        "hold must name F2"
    )


def test_bridge_signatures_still_tolerate_injected_envelope():
    """The bridge functions are the implementation behind the observe modes."""
    for fn in (read_resource, search_resources):
        params = set(inspect.signature(fn).parameters.keys())
        missing = ENVELOPE_FIELDS - params
        assert not missing, f"{fn.__name__} would die with CONTRACT_VIOLATION on: {sorted(missing)}"


@pytest.mark.asyncio
async def test_facade_never_report_ok_on_empty_truth():
    """Honesty contract survives retirement: degraded, never a false ok."""
    result = await arif_recall(query="housekeeping-regression-probe")
    assert result["status"] in ("ok", "degraded", "error")
    if result["status"] == "ok":
        assert result["entries"], "reported ok with zero entries"
    else:
        assert result.get("degraded_reasons"), "degraded without a machine-readable reason"
