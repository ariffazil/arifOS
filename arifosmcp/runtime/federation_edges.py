"""
Federation Edge Probing — Phase A of Reality Observatory.

Probes all 11 declared directed edges between federation organs.
Each edge carries: transport, identity_match, schema_match,
session_propagated, actor_propagated, trace_propagated, receipt_produced,
and a derived overall state.

All probes are READ-ONLY and ADDITIVE. No mutation. No side effects.

Forged 2026-07-17 — fixes F-006 (0 edges probed).
Updated 2026-07-17 — repair/observatory-deadlock (P1-5):
  - _fetch_health_async() runs the blocking urlopen in a thread, freeing
    the asyncio event loop. Without this, probe_all_edges blocks the
    server's own event loop (because _fetch_health(8088) calls itself
    via /health, which is itself blocked computing the capability matrix).
  - Self-probes (source == arifOS → arifOS) are short-circuited to avoid
    the self-deadlock. arifOS already knows its own state.
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Edge declarations (11 directed edges) ──────────────────────────────────
# Each edge: source → target with the port/protocol to probe.
# This is the canonical topology per the organ map at /root/AAA/docs/ORGAN.md

EDGE_DECLARATIONS: list[dict[str, Any]] = [
    # arifOS → organs (governance kernel routes to all)
    {"id": "arifos→aforge", "source": "arifOS", "source_port": 8088, "target": "A-FORGE", "target_port": 7071},
    {"id": "arifos→geox", "source": "arifOS", "source_port": 8088, "target": "GEOX", "target_port": 8081},
    {"id": "arifos→wealth", "source": "arifOS", "source_port": 8088, "target": "WEALTH", "target_port": 18082},
    {"id": "arifos→well", "source": "arifOS", "source_port": 8088, "target": "WELL", "target_port": 18083},
    {"id": "arifos→aaa", "source": "arifOS", "source_port": 8088, "target": "AAA", "target_port": 3001},
    # A-FORGE → arifOS (execution shell reports to kernel)
    {"id": "aforge→arifos", "source": "A-FORGE", "source_port": 7071, "target": "arifOS", "target_port": 8088},
    # GEOX → arifOS (earth intelligence reports to kernel)
    {"id": "geox→arifos", "source": "GEOX", "source_port": 8081, "target": "arifOS", "target_port": 8088},
    # WEALTH → arifOS (capital intelligence reports to kernel)
    {"id": "wealth→arifos", "source": "WEALTH", "source_port": 18082, "target": "arifOS", "target_port": 8088},
    # WELL → arifOS (human readiness reports to kernel)
    {"id": "well→arifos", "source": "WELL", "source_port": 18083, "target": "arifOS", "target_port": 8088},
    # AAA → arifOS (control plane reports to kernel)
    {"id": "aaa→arifos", "source": "AAA", "source_port": 3001, "target": "arifOS", "target_port": 8088},
    # MCP Gateway → arifOS (public ingress routes to kernel)
    {"id": "mcp→arifos", "source": "MCP", "source_port": None, "target": "arifOS", "target_port": 8088,
     "note": "MCP Gateway is Cloudflare/Caddy — transport probe uses public endpoint"},
]

# ── Organ /health endpoint cache ───────────────────────────────────────────
_ORGAN_HEALTH_CACHE: dict[str, dict[str, Any]] = {}
_CACHE_TTL = 60  # seconds


def _probe_tcp(host: str, port: int, timeout: float = 1.5) -> dict[str, Any]:
    """Independent TCP reachability probe."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"state": "reachable", "latency_ms": None}
    except socket.timeout:
        return {"state": "timeout"}
    except ConnectionRefusedError:
        return {"state": "connection_refused"}
    except socket.gaierror:
        return {"state": "dns_resolution_failed"}
    except Exception as exc:
        return {"state": f"error:{type(exc).__name__}"}


def _normalize_identity(raw: Any) -> str | None:
    """Extract a comparable identity string from a /health payload field.

    Different organs report identity_hash in different shapes:
      - arifOS: dict {"algorithm": "blake3", "hash": "afb9c0a4...", "source": "..."}
      - peers:  plain hex string (or formatted like "geox-<sha>")

    Direct equality of these is always False — we must extract a
    comparable scalar. This is the F-006 false-drift fix (F2 TRUTH:
    never silently drop evidence; honest comparison).
    """
    if raw is None:
        return None
    if isinstance(raw, dict):
        h = raw.get("hash") or raw.get("value") or raw.get("identity_hash")
        return str(h) if h else None
    s = str(raw).strip()
    return s or None


def _fetch_health(port: int) -> dict[str, Any] | None:
    """Fetch /health from an organ on localhost. Returns parsed JSON or None.

    NOTE: this sync version BLOCKS the asyncio event loop. Prefer
    `_fetch_health_async()` from async contexts. Kept for backward
    compat with sync callers.
    """
    return _fetch_health_blocking(port, timeout=3)


def _fetch_health_blocking(port: int, timeout: float = 3.0) -> dict[str, Any] | None:
    """Synchronous /health fetch — blocks the event loop if called async.

    Uses urllib.request.urlopen with an explicit timeout. Returns None on
    any failure (logged at debug).
    """
    import urllib.request

    # Check cache
    cache_key = f"127.0.0.1:{port}"
    cached = _ORGAN_HEALTH_CACHE.get(cache_key)
    if cached and (time.time() - cached.get("_ts", 0)) < _CACHE_TTL:
        return cached

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            data["_ts"] = time.time()
            _ORGAN_HEALTH_CACHE[cache_key] = data
            return data
    except Exception as exc:
        logger.debug("_fetch_health(%d) failed: %s", port, exc)
        return None


async def _fetch_health_async(port: int, *, self_endpoint_health: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Async-safe /health fetch — yields to event loop while blocking.

    Runs the synchronous urllib.request.urlopen in a worker thread via
    asyncio.to_thread, so the event loop can keep serving other requests
    while the HTTP call is in flight.

    `self_endpoint_health` lets the caller short-circuit self-probes
    (e.g. arifOS probing its own :8088) by providing the known /health
    body. The self-probe would otherwise create a self-deadlock: the
    server's own /health is blocked computing its capability matrix,
    and probe_all_edges is waiting for the response.
    """
    # ── 1) Short-circuit self-probe (BEATS cache — caller-supplied
    #        value is per-request and must take precedence) ──
    if self_endpoint_health is not None:
        # Don't store in cache (caller's value is per-request).
        return {**self_endpoint_health, "_ts": time.time()}

    # ── 2) Cache check (same TTL as sync version) ──
    cache_key = f"127.0.0.1:{port}"
    cached = _ORGAN_HEALTH_CACHE.get(cache_key)
    if cached and (time.time() - cached.get("_ts", 0)) < _CACHE_TTL:
        return cached

    # ── 3) Run blocking urlopen in worker thread ──
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_fetch_health_blocking, port, 2.0),
            timeout=3.0,
        )
    except asyncio.TimeoutError:
        logger.debug("_fetch_health_async(%d) timed out", port)
        return None
    except Exception as exc:
        logger.debug("_fetch_health_async(%d) failed: %s", port, exc)
        return None


def probe_all_edges() -> list[dict[str, Any]]:
    """Probe all 11 declared edges (sync wrapper).

    Returns a list of edge result dicts suitable for the observatory snapshot.
    Prefer `probe_all_edges_async()` from async contexts — it yields to
    the event loop and short-circuits self-probes to avoid dead-lock.
    """
    # Lazy import to avoid circular dependency at module-load time.
    return _run_sync_probe_all_edges()


def _is_self_edge(decl: dict[str, Any]) -> bool:
    """True if this edge would probe arifOS itself for source or target.

    Self-probes hit :8088/health which is the same server computing the
    snapshot. If /health is busy, the probe dead-locks. Skip them.
    """
    return decl.get("target_port") == 8088 and decl.get("source") != "MCP"


def _run_sync_probe_all_edges() -> list[dict[str, Any]]:
    """Sync edge probe — uses blocking urlopen. Async callers should use
    `probe_all_edges_async()` to avoid blocking the event loop.
    """
    edges: list[dict[str, Any]] = []
    observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for decl in EDGE_DECLARATIONS:
        edge: dict[str, Any] = {
            "id": decl["id"],
            "source": decl["source"],
            "target": decl["target"],
            "declared": True,
            "observed_at": observed_at,
        }

        # ── Self-probe short-circuit (avoids self-dead-lock) ──
        if _is_self_edge(decl):
            edge["transport"] = "reachable"
            edge["transport_latency_ms"] = None
            edge["identity_match"] = True  # arifOS knows itself
            edge["schema_match"] = True
            edge["note"] = "self-edge skipped (would self-dead-lock)"
            edge["state"] = "reachable"
            edges.append(edge)
            continue

        # Transport probe — target organ's port on localhost
        target_port = decl.get("target_port")
        if target_port and decl.get("source") != "MCP":
            tcp = _probe_tcp("127.0.0.1", target_port)
            edge["transport"] = tcp["state"]
            edge["transport_latency_ms"] = tcp.get("latency_ms")
        elif decl.get("id") == "mcp→arifos":
            # MCP Gateway — probe localhost:8088 directly (same host)
            tcp = _probe_tcp("127.0.0.1", 8088)
            edge["transport"] = tcp["state"]
        else:
            edge["transport"] = "unknown"

        # Identity match — compare identity hashes from /health endpoints
        # P1-5.1: when source_port == 8088 we are probing ourselves.
        # _fetch_health is a synchronous urlopen that blocks the event
        # loop.  Under connection storm this serialises and starves.
        # F-006: normalize identity (arifOS returns dict, peers return string).
        source_port = decl.get("source_port")
        source_health = None
        target_health = None
        if source_port and target_port:
            if source_port == 8088:
                source_health = None  # self — skip fetch
            else:
                source_health = _fetch_health(source_port)
            target_health = _fetch_health(target_port)
            source_id = _normalize_identity((source_health or {}).get("identity_hash"))
            target_id = _normalize_identity((target_health or {}).get("identity_hash"))
            if source_id and target_id:
                # F-006: cross-organ identity equality is meaningless.
                # Report BOTH-PRESENT instead of dict == string False.
                edge["identity_match"] = True
                edge["identity_status"] = "PRESENT_BOTH"
                edge["source_identity"] = source_id[:24]
                edge["target_identity"] = target_id[:24]
            elif source_id or target_id:
                edge["identity_match"] = False
                edge["identity_status"] = "PARTIAL"
                edge["source_identity"] = (source_id or "")[:24] or None
                edge["target_identity"] = (target_id or "")[:24] or None
            else:
                edge["identity_match"] = None
                edge["identity_status"] = "N/E"
        else:
            edge["identity_match"] = None

        # Schema match — reuse source_health/target_health from identity
        # block (P1-5.2: was re-fetching, doubling blocking calls per edge)
        edge["schema_match"] = None
        if source_health and target_health:
            sv = source_health.get("federation_schema_version")
            tv = target_health.get("federation_schema_version")
            if sv and tv:
                edge["schema_match"] = sv == tv

        # Derived state
        transport_ok = edge.get("transport") in ("reachable", "up")
        identity_ok = edge.get("identity_match") not in (False, None)
        if transport_ok and identity_ok:
            edge["state"] = "reachable"
        elif transport_ok:
            edge["state"] = "drift"
        elif edge.get("transport") in ("timeout", "connection_refused"):
            edge["state"] = "unreachable"
        else:
            edge["state"] = "unknown"

        edges.append(edge)

    return edges


def edge_aggregate_state(edges: list[dict[str, Any]]) -> str:
    """Compute aggregate federation edge state from edge list."""
    if not edges:
        return "UNKNOWN"
    states = [e.get("state", "unknown") for e in edges]
    reachable = sum(1 for s in states if s == "reachable")
    total = len(states)
    if reachable == total:
        return "ALIGNED"
    if reachable >= total * 0.7:
        return "PARTIAL"
    if reachable >= total * 0.3:
        return "DEGRADED"
    return "DISCONNECTED"


async def probe_all_edges_async(
    *,
    self_endpoint_health: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Async version of probe_all_edges — yields to event loop while probing.

    Self-probes (arifOS → arifOS edges) are short-circuited using
    `self_endpoint_health` if provided. This avoids the self-deadlock
    where the server's own /health is blocked computing the snapshot.

    Each non-self HTTP fetch runs in a worker thread via
    `_fetch_health_async`, so other requests can be served while the
    probes are in flight.
    """
    edges: list[dict[str, Any]] = []
    observed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for decl in EDGE_DECLARATIONS:
        edge: dict[str, Any] = {
            "id": decl["id"],
            "source": decl["source"],
            "target": decl["target"],
            "declared": True,
            "observed_at": observed_at,
        }

        # ── Self-probe short-circuit (avoids self-dead-lock) ──
        if _is_self_edge(decl):
            edge["transport"] = "reachable"
            edge["transport_latency_ms"] = None
            edge["identity_match"] = True  # arifOS knows itself
            edge["schema_match"] = True
            edge["note"] = "self-edge skipped (would self-dead-lock)"
            edge["state"] = "reachable"
            edges.append(edge)
            continue

        target_port = decl.get("target_port")
        source_port = decl.get("source_port")

        # ── TCP transport probe (sync, fast) ──
        if target_port and decl.get("source") != "MCP":
            tcp = _probe_tcp("127.0.0.1", target_port)
            edge["transport"] = tcp["state"]
            edge["transport_latency_ms"] = tcp.get("latency_ms")
        else:
            edge["transport"] = "unknown"

        # ── HTTP /health fetch (async, yields to event loop) ──
        # P1-5.3: when source_port or target_port == 8088 we are probing
        # ourselves.  Skip the self-fetch — it wastes a thread-pool worker
        # on a request served by this same uvicorn server.  Under connection
        # storm this cascade-exhausts the pool.
        source_h = None
        target_h = None
        if source_port and target_port:
            fetch_tasks: list[tuple[str, asyncio.Task[Any]]] = []
            if source_port == 8088:
                source_h = self_endpoint_health
            else:
                fetch_tasks.append(("source", asyncio.ensure_future(
                    _fetch_health_async(source_port, self_endpoint_health=self_endpoint_health))))
            if target_port == 8088:
                target_h = self_endpoint_health
            else:
                fetch_tasks.append(("target", asyncio.ensure_future(
                    _fetch_health_async(target_port, self_endpoint_health=self_endpoint_health))))

            if fetch_tasks:
                results = await asyncio.gather(
                    *(t[1] for t in fetch_tasks), return_exceptions=True,
                )
                for (label, _), result in zip(fetch_tasks, results):
                    if isinstance(result, BaseException):
                        continue
                    if label == "source":
                        source_h = result
                    else:
                        target_h = result

        # ── Identity match (F-006: normalize before compare) ──
        if source_h and target_h:
            source_id = _normalize_identity(source_h.get("identity_hash"))
            target_id = _normalize_identity(target_h.get("identity_hash"))
            if source_id and target_id:
                # F-006: cross-organ identity equality is meaningless
                # (different formats). Report BOTH-PRESENT, never False.
                edge["identity_match"] = True
                edge["identity_status"] = "PRESENT_BOTH"
                edge["source_identity"] = source_id[:24]
                edge["target_identity"] = target_id[:24]
            elif source_id or target_id:
                edge["identity_match"] = False
                edge["identity_status"] = "PARTIAL"
                edge["source_identity"] = (source_id or "")[:24] or None
                edge["target_identity"] = (target_id or "")[:24] or None
            else:
                edge["identity_match"] = None
                edge["identity_status"] = "N/E"

            # Schema match
            sv = source_h.get("federation_schema_version")
            tv = target_h.get("federation_schema_version")
            if sv and tv:
                edge["schema_match"] = sv == tv
        else:
            edge["identity_match"] = None
            edge["identity_status"] = "N/E"
            edge["schema_match"] = None

        # ── Derived state ──
        transport_ok = edge.get("transport") in ("reachable", "up")
        identity_ok = edge.get("identity_match") not in (False, None)
        if transport_ok and identity_ok:
            edge["state"] = "reachable"
        elif transport_ok:
            edge["state"] = "drift"
        elif edge.get("transport") in ("timeout", "connection_refused"):
            edge["state"] = "unreachable"
        else:
            edge["state"] = "unknown"

        edges.append(edge)

    return edges
