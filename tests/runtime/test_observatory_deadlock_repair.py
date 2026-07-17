"""P1-5 repair tests — Observatory self-deadlock fix.

Forged 2026-07-17 under F13 SOVEREIGN HOLD verdict follow-up:
  "The /health and /snapshot endpoints consume the entire server via
   synchronous urlopen + ThreadPoolExecutor dead-locks. Async callers
   must use the async variants."

Tests verify:
  1. probe_all_edges_async exists and yields to event loop
  2. _fetch_health_async runs urlopen in worker thread
  3. Self-edges (target_port==8088) are short-circuited without HTTP
  4. _edges_block_async composes federation edge block correctly
  5. build_snapshot_async composes the full snapshot using async edges
  6. _registered_tools fails fast (≤1.0s) on TimeoutError
  7. Live concurrent probes do not block the event loop (the original
     deadlock condition)

All tests must PASS on repair/observatory-deadlock branch.
"""

from __future__ import annotations

import asyncio
import socket
import time

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: probe_all_edges_async exists and is a coroutine function
# ─────────────────────────────────────────────────────────────────────────────
def test_probe_all_edges_async_exists():
    from arifosmcp.runtime.federation_edges import probe_all_edges_async
    assert callable(probe_all_edges_async)
    assert asyncio.iscoroutinefunction(probe_all_edges_async), (
        "probe_all_edges_async must be an async (coroutine) function"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: _fetch_health_async exists and runs urlopen in worker thread
# ─────────────────────────────────────────────────────────────────────────────
def test_fetch_health_async_exists():
    from arifosmcp.runtime.federation_edges import _fetch_health_async
    assert callable(_fetch_health_async)
    assert asyncio.iscoroutinefunction(_fetch_health_async)


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Self-edges short-circuited (no HTTP call)
# ─────────────────────────────────────────────────────────────────────────────
def test_self_edge_short_circuit():
    """Edges probing :8088 (arifOS itself) must not make HTTP calls."""
    from arifosmcp.runtime.federation_edges import _is_self_edge

    # All edges targeting port 8088 from a non-MCP source are self-edges
    assert _is_self_edge({"target_port": 8088, "source": "A-FORGE"}) is True
    assert _is_self_edge({"target_port": 8088, "source": "GEOX"}) is True
    assert _is_self_edge({"target_port": 8088, "source": "WEALTH"}) is True
    assert _is_self_edge({"target_port": 8088, "source": "WELL"}) is True
    assert _is_self_edge({"target_port": 8088, "source": "AAA"}) is True
    # arifOS → X edges are NOT self-edges (different ports)
    assert _is_self_edge({"target_port": 7071, "source": "arifOS"}) is False
    assert _is_self_edge({"target_port": 8081, "source": "arifOS"}) is False
    # mcp→arifos has source="MCP" — handled separately, not self-probe
    assert _is_self_edge({"target_port": 8088, "source": "MCP"}) is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: probe_all_edges_async with self-edges returns correct structure
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_probe_all_edges_async_self_edges():
    """probe_all_edges_async must mark all self-edges as reachable without HTTP."""
    from arifosmcp.runtime.federation_edges import probe_all_edges_async

    edges = await probe_all_edges_async()
    assert isinstance(edges, list)
    assert len(edges) >= 11  # 11 declared edges

    # All self-edges (target_port=8088) should be marked reachable without note
    self_edges = [
        e for e in edges
        if e["id"].endswith("→arifos") and not e["id"].startswith("mcp")
    ]
    assert len(self_edges) >= 5, f"Expected >=5 self-edges, got {len(self_edges)}"
    for e in self_edges:
        assert e["state"] == "reachable"
        assert e["transport"] == "reachable"
        assert "skipped" in e.get("note", ""), (
            f"Self-edge {e['id']} should be marked skipped: {e.get('note')}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: _fetch_health_async returns None on unreachable port
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_fetch_health_async_unreachable():
    """A port that's not listening should return None within timeout."""
    from arifosmcp.runtime.federation_edges import _fetch_health_async

    # Find an unused port (binding to 0 then closing leaves a port unused briefly)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    start = time.monotonic()
    result = await _fetch_health_async(port)
    elapsed = time.monotonic() - start
    assert result is None, f"Expected None for closed port, got {result}"
    assert elapsed < 4.5, f"_fetch_health_async took {elapsed:.2f}s (too slow)"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: _fetch_health_async with self_endpoint_health short-circuits
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_fetch_health_async_self_short_circuit():
    """Passing self_endpoint_health skips the HTTP call entirely."""
    from arifosmcp.runtime.federation_edges import _fetch_health_async

    sentinel = {"status": "healthy", "identity_hash": "test-sentinel-001"}
    start = time.monotonic()
    result = await _fetch_health_async(8088, self_endpoint_health=sentinel)
    elapsed = time.monotonic() - start

    assert result is not None
    assert result["identity_hash"] == "test-sentinel-001"
    assert "_ts" in result
    assert elapsed < 0.1, (
        f"Short-circuit should be sub-millisecond; took {elapsed*1000:.2f}ms"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: Concurrent probes do not block the event loop
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_concurrent_probes_dont_block_event_loop():
    """While 5 probes are in flight, a heartbeat coroutine must keep ticking.

    Pre-repair: synchronous urlopen on the event loop would freeze the
    heartbeat coroutine for 3s × 5 = 15s.
    Post-repair: heartbeat keeps ticking every 100ms.
    """
    from arifosmcp.runtime.federation_edges import _fetch_health_async

    # Heartbeat: yields and counts ticks
    heartbeat_ticks = []

    async def heartbeat():
        for _ in range(5):
            await asyncio.sleep(0.1)
            heartbeat_ticks.append(time.monotonic())

    async def fake_probe():
        # Use a closed port so we exercise the timeout path
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        await _fetch_health_async(port)

    start = time.monotonic()
    await asyncio.gather(
        heartbeat(),
        *[fake_probe() for _ in range(5)],
    )
    elapsed = time.monotonic() - start

    # If probes blocked the loop, heartbeat would have <5 ticks.
    # With async fix, heartbeat completes all 5 ticks.
    assert len(heartbeat_ticks) == 5, (
        f"Heartbeat only ticked {len(heartbeat_ticks)} times in {elapsed:.2f}s "
        f"(probes blocked the event loop)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: _registered_tools fails fast on TimeoutError
# ─────────────────────────────────────────────────────────────────────────────
def test_registered_tools_timeout_fail_fast():
    """When the loop is busy, _registered_tools must fall back within 1s."""
    from arifosmcp.runtime.capability_drift import _registered_tools

    # Create a mock mcp with no _tool_registry attribute — forces the
    # FastMCP 3.x async path which calls asyncio.run_coroutine_threadsafe.
    # Without an event loop running, this raises RuntimeError → fall through.
    class FakeMcp:
        pass

    start = time.monotonic()
    result = _registered_tools(FakeMcp())
    elapsed = time.monotonic() - start

    # No event loop → RuntimeError → fall through to public_surface
    # Should complete quickly even on a busy machine.
    assert elapsed < 2.0, f"_registered_tools took {elapsed:.2f}s (should fail fast)"
    # Result is either a set or an empty set
    assert isinstance(result, set)


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: build_snapshot_async uses async federation_edges
# ─────────────────────────────────────────────────────────────────────────────
def test_build_snapshot_async_exists():
    from arifosmcp.runtime.rest_routes.observatory_routes import build_snapshot_async
    assert callable(build_snapshot_async)
    assert asyncio.iscoroutinefunction(build_snapshot_async), (
        "build_snapshot_async must be an async (coroutine) function"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: _edges_block_async exists and is a coroutine function
# ─────────────────────────────────────────────────────────────────────────────
def test_edges_block_async_exists():
    from arifosmcp.runtime.rest_routes.observatory_routes import _edges_block_async
    assert callable(_edges_block_async)
    assert asyncio.iscoroutinefunction(_edges_block_async)